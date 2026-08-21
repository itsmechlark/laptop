# Trigger-accuracy eval sets

20-query eval sets in the format the `skill-creator` skill's `run_eval.py` and
`run_loop.py` expect: `[{"query": "...", "should_trigger": true}, …]`.

Those live in *skill-creator's* own `scripts/` directory, which is not this
repo's `scripts/` — the commands below invoke them as the `scripts.run_eval`
module via `PYTHONPATH`, so the two never collide in practice.

| Set | Why it exists |
| --- | --- |
| `draft-spec`, `slice`, `explain` | `disable-model-invocation` was removed, so these can now fire on their own for the first time |
| `git-commit` + `pull-request` | The highest description overlap in the repo (0.188) |
| `code-review` + `find-bugs` | Second highest (0.118), and the boundary between them — verdict vs evidence — has never been tested |
| `tdd`, `fan-out` | A wrong trigger is expensive: one hijacks an implementation turn into red-green-refactor, the other spawns parallel agents |
| `codebase-design` + `domain-modeling` | Both are design-time skills that fire on "this code is the wrong shape" requests, and `domain-modeling` hands work to `codebase-design` explicitly. The boundary — where the seam goes vs. what the words mean — had never been tested |

The three pairs share a single query pool, labelled independently per skill, so
a query establishes which of the two should win rather than testing each in
isolation. `check-payload` fails if any shared query is labelled should-trigger
in both — that would make the pair unfalsifiable.

Skills with no set here are either vendored (no in-repo fix for a bad result) or
on `check-payload`'s `evals_exempt` list — deliberately uncovered because they
have low overlap and are cheap to recover from. See "Trigger-eval coverage" in
`AGENTS.md`.

These are fixtures, so they are tracked. What they measure is not: a trigger
rate depends on the model answering, which means credentials, network egress,
and tokens. That is why this tier is deliberately outside CI and outside the
agent sandbox — see "Testing instructions" in `AGENTS.md`.

## Measure first

`run_eval.py` scores a description as it stands, which answers "does this fire
on the right requests?" without rewriting anything. Each query runs 3× for a
stable rate.

## The runner

`sh scripts/run-trigger-evals` does all of the below with the preflight already wired
in — harness discovery, the auth check, the project-root check — and writes
results to the git-ignored `artifacts/trigger-evals/`:

```sh
sh scripts/run-trigger-evals            # every set
sh scripts/run-trigger-evals slice      # just one
```

`RUNS_PER_QUERY` (default 3), `EVAL_MODEL`, and `SKILL_CREATOR` override the
defaults. The rest of this file is what the runner does, for when you need to
drive `run_eval.py` directly.

## Driving run_eval.py by hand

**Run it from the repository root**, not from the skill-creator directory.
`run_eval.py` locates the project by walking up from the *current directory*
looking for `.claude/`, and writes a temporary command file there so the skill
appears in Claude's `available_skills`. Started from anywhere else, that lands
in `~/.claude/commands/` instead of this repo's — wrong project root, and it
litters your global commands directory. Set `PYTHONPATH` so the package still
imports:

```sh
SC="$HOME/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin/<session>/<run>/skills/skill-creator"
cd ~/Codespace/laptop
PYTHONPATH="$SC" python3 -m scripts.run_eval \
  --eval-set spec/trigger-evals/slice.json \
  --skill-path skills/slice \
  --model claude-opus-5 --verbose
```

Check `find_project_root()` agrees before trusting a result:

```sh
PYTHONPATH="$SC" python3 -c "from scripts.run_eval import find_project_root; print(find_project_root())"
```

It must print the repo path. The two segments under `skills-plugin/` are
per-session and change between runs — list the directory to find the current
pair, or copy `skill-creator` somewhere stable. Reading that tree also requires
`~/Library/Application Support/Claude/local-agent-mode-sessions/skills-plugin`
in `sandbox.filesystem.allowRead`.

**Budget.** Default is 3 runs per query at 10 workers, so one set is 60
`claude -p` invocations and all nine are 540. Run one set first and confirm the
numbers look sane before spending the rest.

## Optimize only what scores badly

`run_loop.py` proposes and tests replacement descriptions (60/40 train/held-out
split, up to 5 iterations, selected on the held-out score). It rewrites a
shipped file, so it earns its run only when the measured rate is poor:

```sh
cd ~/Codespace/laptop
PYTHONPATH="$SC" python3 -m scripts.run_loop \
  --eval-set spec/trigger-evals/slice.json \
  --skill-path skills/slice \
  --model claude-opus-5 --max-iterations 5 --verbose
```

Same cwd rule as above — `run_loop.py` calls the same evaluator, so starting it
from the skill-creator directory misplaces the project root in exactly the same
way.

## The cheap screen, for comparison

`sh scripts/check-payload --collisions` reports term overlap between model-invocable
descriptions with no model involved. It answers a narrower question — which
descriptions compete for the same words — and cannot predict a trigger. Useful
before a run to spot a pair worth adding queries for.

## Queries worth a second look before trusting a score

Three are deliberately contested. If the eval disagrees with the label, the
label may be what's wrong:

- **draft-spec**, "we haven't decided between webhooks and polling yet but write
  the spec anyway" — labelled should-not-trigger, because the description now
  requires an already-settled decision. Defensible either way: the skill's body
  would take it and report what's unresolved. Flip the label if you'd rather it
  fire and push back.
- **slice**, "app/models/reservation.rb is 800 lines, split it into modules" —
  labelled should-not-trigger. Shares "split" with the description but belongs
  to `codebase-design`. The negative most likely to fail.
- **explain**, "explain this stacktrace" — labelled should-not-trigger.
  Debugging, not code explanation, but it leads with the skill's own verb.
- **domain-modeling**, "is a 'table' the physical table or the seating
  assignment? our model treats it as both" — labelled should-trigger for
  `domain-modeling` and not for `codebase-design`. Genuinely contested: one
  fuzzy term hiding two concepts is a modelling problem, but "treats it as both"
  is also a seam in the wrong place. Whichever fires, the other is one handoff
  away — flip the pair if the eval disagrees.
- **codebase-design**, "app/models/reservation.rb is 800 lines, split it into
  smaller modules" — should-trigger here and should-not for `slice`, which is
  the same query that set already carries as its most likely failing negative.

## One hypothesis these sets exist to settle

The exclusion clauses in `slice` and `explain` ("Not for building a slice once
it is defined", "never whether it's good — no review, no edits") import the
vocabulary of what they exclude, so each description now lexically resembles
the queries it means to repel — `slice`'s "build the first slice … tests first"
negative scores double any other. A model probably reads "not for X" as
exclusion rather than as a keyword, but that is a guess. Don't rewrite these
descriptions on lexical evidence alone; run the eval.
