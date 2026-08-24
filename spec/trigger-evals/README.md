# Trigger-accuracy eval sets

20-query eval sets, one JSON array per skill:
`[{"query": "...", "should_trigger": true}, …]`.

The engine that reads them is this repo's own `scripts/lib/run_eval_local.py`,
driven by `scripts/run-trigger-evals`. It replaced the `skill-creator` skill's
`run_eval.py`, which measured triggering by dropping a `/slash` *command* file
into `.claude/commands/`. Commands are never offered to the `Skill` tool, so on
Claude Code 2.1.236+ that harness reported 0 triggers for everything. Nothing
here depends on skill-creator any more.

| Set | Why it exists |
| --- | --- |
| `draft-spec`, `slice`, `explain` | `disable-model-invocation` was removed, so these can now fire on their own for the first time |
| `git-commit` + `pull-request` | The highest description overlap in the repo (0.188) |
| `code-review` + `find-bugs` | Second highest (0.118), and the boundary between them — verdict vs evidence — has never been tested |
| `tdd`, `fan-out` | A wrong trigger is expensive: one hijacks an implementation turn into red-green-refactor, the other spawns parallel agents |
| `codebase-design` + `domain-modeling` | Both are design-time skills that fire on "this code is the wrong shape" requests, and `domain-modeling` hands work to `codebase-design` explicitly. The boundary — where the seam goes vs. what the words mean — had never been tested |
| `grilling` + `review-response` | Both fire on "push back on this technical judgment" requests. `grilling` is also an interview primitive that four siblings route into — `triage`, `find-bugs`, `draft-spec`, and `brainstorming` — which changes what a bad result costs: the expensive failure is a *missed* trigger, where the agent improvises an interview instead of loading this one, and term overlap cannot see that |

The four pairs share a single query pool, labeled independently per skill, so
a query establishes which of the two should win rather than testing each in
isolation. `check-payload` fails if any shared query is labeled should-trigger
in both — that would make the pair unfalsifiable.

Skills with no set here are either vendored (no in-repo fix for a bad result) or
on `check-payload`'s `evals_exempt` list — deliberately uncovered because they
have low overlap and are cheap to recover from. See "Trigger-eval coverage" in
`AGENTS.md`.

A third group cannot have one at all: `check-payload` *fails* on a set named for
a skill carrying `disable-model-invocation` — `brainstorming`, `feature-dev`,
`standup`, `triage`. Note what that does and doesn't mean. The key is Claude-only,
so those four do trigger on Codex and Cursor and could misfire there; what makes
the set impossible is the runner, which drives `claude -p` and therefore can only
ever measure the client that refuses them. Their guard is the skill body, not a
query set here — and if the other clients ever need measuring, the missing piece
is a second runner, not a file in this directory.

These are fixtures, so they are tracked. What they measure is not: a trigger
rate depends on the model answering, which means credentials, network egress,
and tokens. That is why this tier is deliberately outside CI and outside the
agent sandbox — see "Testing instructions" in `AGENTS.md`.

## Measure first

The runner scores a description as it stands, which answers "does this fire on
the right requests?" without rewriting anything. Each query runs 3× for a stable
rate.

It measures each skill *where it is already installed*. `skills/` is
`~/.claude/skills` — mac symlinks it — so the shipped description is live and
its adjacent siblings load and compete exactly as they do in real use. That is
what makes the shared query pools above mean anything: a pool proves which of
the pair wins only if both are loaded to compete for it.

## The runner

`sh scripts/run-trigger-evals` is the way in. Its preflight covers everything
that would otherwise waste a run — `python3` 3.10+ (an asdf shim with no version
selected satisfies `command -v` and then dies), `jq`, the CLI, and one cheap
live call, because `loggedIn: true` only proves a credential parsed and a
revoked grant 401s every query while reading as 0% triggers. Results land in the
git-ignored `artifacts/trigger-evals/`:

```sh
sh scripts/run-trigger-evals            # every set
sh scripts/run-trigger-evals slice      # just one
```

`RUNS_PER_QUERY` (default 3), `EVAL_MODEL` (default `sonnet`), and
`QUERY_TIMEOUT` (default 120s per query) override the defaults.

## Driving the engine by hand

`scripts/lib/run_eval_local.py` takes a set and a skill directly. It is
stdlib-only and builds a disposable temp project per query, so there is no
project-root rule to satisfy and nothing to put on `PYTHONPATH`:

```sh
python3 scripts/lib/run_eval_local.py \
  --eval-set spec/trigger-evals/slice.json \
  --skill-path skills/slice \
  --model sonnet --verbose
```

**Do not reach for `CLAUDE_CONFIG_DIR` to keep your installed skills out of a
run.** Credential discovery is scoped to the config dir: `claude -p` under a
fresh one exits `Not logged in · Please run /login` even with a valid keychain
grant, and every query then returns a silent miss that looks like a description
failure. Seeding the throwaway dir with the account state from `~/.claude.json`
does not fix it; only copying the live OAuth token into every temp dir would,
which is not worth doing. The engine's `run_single_query` docstring carries the
longer version.

**Testing a description you have not shipped.** `--description` overrides the
text and installs a temporary probe skill carrying it, so a candidate is
measured against the incumbent rather than in place of it:

```sh
python3 scripts/lib/run_eval_local.py \
  --eval-set spec/trigger-evals/slice.json \
  --skill-path skills/slice \
  --description "$(cat candidate.txt)" --verbose
```

Each artifact records which way it ran, as `mechanism`: `installed-skill` for
the shipped text, `probe-skill` for an override.

**Budget.** Default is 3 runs per query at 10 workers, so a 20-query set is 60
`claude -p` invocations and the whole suite is 60 × the number of sets — on
`sonnet`. Run one set first and confirm the numbers look sane before spending
the rest. `EVAL_MODEL=haiku` is a cheaper smoke pass, but do not read a
description failure off it: haiku answers a fair share of these queries directly
instead of reaching for a skill, and scores them as misses that `sonnet` passes.

## Optimize only what scores badly

There is no automated rewrite loop here. `skill-creator`'s `run_loop.py`
proposed and tested replacement descriptions, but it drives the same command-file
evaluator `run_eval.py` used — so it would optimize against a measurement that
reports nothing, and confidently rewrite a shipped file on the strength of it.

Rewrite by hand and measure the candidate with `--description` above, leaving
the shipped text in place until a candidate beats it. A description that already
scores well earns no rewrite.

## The cheap screen, for comparison

`sh scripts/check-payload --collisions` reports term overlap between model-invocable
descriptions with no model involved. It answers a narrower question — which
descriptions compete for the same words — and cannot predict a trigger. Useful
before a run to spot a pair worth adding queries for.

## Queries worth a second look before trusting a score

Three are deliberately contested. If the eval disagrees with the label, the
label may be what's wrong:

- **draft-spec**, "we haven't decided between webhooks and polling yet but write
  the spec anyway" — labeled should-not-trigger, because the description
  requires an already-settled decision. Genuinely contested, and more so since
  the body gained an explicit readiness test: loading the skill on this query
  produces the *right* answer — name what's still open, draft only if asked, and
  label every invented assumption. Flip the label if you'd rather it fire and
  push back than stay out of the way.
- **slice**, "app/models/reservation.rb is 800 lines, split it into modules" —
  labeled should-not-trigger. Shares "split" with the description but belongs
  to `codebase-design`. The negative most likely to fail.
- **explain**, "explain this stacktrace" — labeled should-not-trigger.
  Debugging, not code explanation, but it leads with the skill's own verb.
- **domain-modeling**, "is a 'table' the physical table or the seating
  assignment? our model treats it as both" — labeled should-trigger for
  `domain-modeling` and not for `codebase-design`. Genuinely contested: one
  fuzzy term hiding two concepts is a modeling problem, but "treats it as both"
  is also a seam in the wrong place. Whichever fires, the other is one handoff
  away — flip the pair if the eval disagrees.
- **codebase-design**, "app/models/reservation.rb is 800 lines, split it into
  smaller modules" — should-trigger here and should-not for `slice`, which is
  the same query that set already carries as its most likely failing negative.
- **grilling**, "help me think through what we should build for group bookings —
  i don't have an approach yet" — labeled should-not-trigger, and the negative
  most likely to fail in that set. The description now says "find what a plan is
  missing", and this query is the case it must repel: there is no plan yet, so
  the subject of the interview doesn't exist. It belongs to `brainstorming`,
  which carries `disable-model-invocation` and therefore cannot win it — nothing
  firing is the correct outcome, which is why the pair is `review-response` and
  not `brainstorming`.
- **tdd**, the two untested-code queries — "that class has no specs at all,
  change it safely" and "pin what DepositCalculator does today" are labeled
  should-trigger, while "backfill specs … i'm not changing its behavior" stays
  should-not. The three are deliberately adjacent: all describe code with no
  coverage, and only the intent to *change* behavior separates them. That is the
  boundary the description has to hold, and the pair exists because `tdd` gained
  an explicit characterization path — pin today's behavior, then drive the
  change red-green-refactor. If the negative starts firing, the description is
  claiming coverage work it doesn't do.
- **tdd**, "rename apply_policy to apply_fee_policy everywhere and keep the specs
  passing" — labeled should-not-trigger. A pure rename has no red available, so
  there is nothing for the cycle to drive; `domain-modeling` used to route
  renames here and no longer does, for that reason. `tdd` still carries a
  Troubleshooting row for the case, which handles the arrival without claiming
  the trigger.
- **grilling** / **review-response**, the five reviewer-feedback queries —
  labeled should-trigger for `review-response` and not for `grilling`.
  Genuinely contested: `grilling`'s body explicitly says to grill feedback from
  a demo or a reviewer before iterating on it, so the skill claims the territory
  even though its description scopes to plans and decisions. The intended line
  is the artifact — feedback on a *plan* is `grilling`, comments on *code in
  review* are `review-response`. If the eval disagrees, the fix is in the
  descriptions, not the labels.

## One hypothesis these sets exist to settle

The exclusion clauses in `slice` and `explain` ("Not for building a slice once
it is defined", "never whether it's good — no review, no edits") import the
vocabulary of what they exclude, so each description now lexically resembles
the queries it means to repel — `slice`'s "build the first slice … tests first"
negative scores double any other. A model probably reads "not for X" as
exclusion rather than as a keyword, but that is a guess. Don't rewrite these
descriptions on lexical evidence alone; run the eval.
