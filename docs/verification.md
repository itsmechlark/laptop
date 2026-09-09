# Verifying the payload

The commands, and what CI runs for you, are in `AGENTS.md` under
[Testing instructions](../AGENTS.md#testing-instructions). This file is the
reference behind them: what `scripts/check-payload` settles and what it leaves
to a person, how the fixtures under `spec/` are kept honest, which skills earn a
trigger eval, and how spelling is enforced.

Read it before adding a check, a fixture, or an eval set, and when a failure's
reason isn't obvious from the message it prints.

## What `check-payload` covers, and what it deliberately doesn't

**Scope is the published payload**: `skills/`, `rules/`, and the client configs.
Bodies under `.agents/skills/` are not scanned directly — what is linked from
`skills/` gets checked through that symlink, and what isn't linked is
project-only and off the checker's books. Vendored skills are the one asymmetry:
they're reachable through `skills/`, but their content isn't ours to edit, so
shape findings about them are warnings rather than failures. Re-vendor upstream
instead of splitting a long vendored `SKILL.md` in place.

Within that scope it mechanizes the half of the `agent-skills` review checklist
a machine can settle, plus cross-file invariants this document declares:
handoff invocability, `## Attribution` ↔ provenance-record agreement for both
skills and rules,
vendored-edit discipline, secret-path parity across clients, frontmatter and
size limits, resource links in both directions, anchor fragments (`#section`
must match a heading or `<a id>`), global-standards section citations
(`AGENTS.md §N` must resolve and name the section correctly), the `bin/srt`
shim's disambiguated npx form (`--package=`, not a bare positional that makes srt
wrap itself) plus valid `srt-settings.json`, and which
`rules/` load for a given path (`spec/rules-cases.txt`).

The vendored-edit rule is the single check that looks past `skills/`, and only
at *which paths a commit touches* — never at a body's content. A vendored skill
edited by either its real or its symlinked path desynchronizes the hash
recorded in `skills-lock.json`, so the diff has to touch both or neither.

Handoff invocability is the one check that reads `rules/` as well as `skills/`,
because a rule can name a skill exactly the way a skill can, and `rules/rspec.md`
does. It fires only on a name written as `` `X` skill `` or `` skill `X` `` — a
bare backticked word is too often a filename to read as a handoff.

The anchor check complements the resource-link check, which resolves the file
but discards the `#fragment`. Fragments resolve against heading slugs
(lowercased, punctuation dropped, spaces hyphenated) plus any explicit
`<a id="…">`. Use the explicit form when a heading opens with punctuation —
``## `## Attribution` `` slugs to `-attribution`, not `attribution`.

Four checks self-test against fixtures carrying deliberate violations:
invocability against `spec/invocability-fixture/SKILL.md` (four kinds),
reference-reachability and anchors against `spec/orphan-fixture/` (two each), and
the srt shim form against `spec/srt-shim-fixture/srt` (two). A
different count fails the run. Don't "fix" those fixtures; their violations are
the assertion.

Three things stay human by design: **prose judgment** (whether a description
carries WHAT and WHEN, whether a body teaches something non-obvious), **rule
applicability** (it verifies which rules load for a path, never which ought to —
`rules/ember.md` claims a deliberately broad `**/*.js` and delegates the call to
the reading agent), and **trigger behavior**. Why the line sits there:
[ADR 0005](adr/0005-verification-stops-where-judgment-starts.md).

Trigger behavior belongs to the eval sets in `spec/trigger-evals/`, which need
`claude -p` (credentials, network, tokens) — run from a terminal before
shipping a description change, never in CI. `sh scripts/run-trigger-evals`
checks `claude auth status` first, drives `scripts/lib/run_eval_local.py`
(installs a real temp skill under a fresh `CLAUDE_CONFIG_DIR`, detects `Skill`
tool firing), and writes to git-ignored `artifacts/trigger-evals/`.
`check-payload --collisions` is the cheap neighbor: a vocabulary-overlap report,
not a trigger prediction.

## `spec/` — the fixtures, and how they're kept honest

`spec/` holds everything `check-payload` reads rather than derives. Fixtures are
themselves validated, because a fixture that silently stops asserting is worse
than no fixture: it reports success.

| Fixture | Asserts | Validated by |
| --- | --- | --- |
| `spec/rules-cases.txt` | `<path> <rules that load, comma-separated, or `-`>` | Every named rule must exist as `rules/<name>.md`; a missing case file is a warning |
| `spec/invocability-fixture/SKILL.md` | One deliberate violation of each invocability kind | Must yield exactly 4 detections, or the run fails |
| `spec/orphan-fixture/skills/alpha/` | An unlinked reference and a fence-only one, beside a legally one-hop file | Must yield exactly 2 detections, or the run fails |
| `spec/orphan-fixture/skills/alpha/SKILL.md` | A stale intra-file anchor and a stale cross-file one, beside an anchor that resolves | Must yield exactly 2 detections, or the run fails |
| `spec/srt-shim-fixture/srt` | A bare-positional npx form (srt wraps itself) and no version pin | Must yield exactly 2 detections, or the run fails |
| `spec/trigger-evals/<skill>.json` | `[{"query": …, "should_trigger": …}, …]` | Shape, labels, and target skill — see below |

An eval set fails when it is invalid JSON, empty, has missing/empty `query` or
non-boolean `should_trigger`, repeats a query, has no positives, has no
negatives, or targets a nonexistent or flagged skill. Each describes a set that
cannot catch anything. The flagged-skill rule is narrower than it sounds: such
a set is *unrunnable* because the runner is `claude -p`
([ADR 0005](adr/0005-verification-stops-where-judgment-starts.md)); on
Codex and Cursor the skill's own body is the only guard
([`skills/<name>/SKILL.md`](../AGENTS.md#skillsnameskillmd)).

Adding a fixture is adding an assertion; the shape rules stop it from being
decorative. When one blocks you, the fixture is usually wrong.

## Trigger-eval coverage

Coverage is prioritized, not uniform: a skill earns a query set when it
**competes** with a sibling for the same requests, or when a **wrong trigger is
expensive**. `check-payload` warns for any first-party invocable skill that has
neither a set nor a place on the script's `evals_exempt` list; vendored skills
are excluded structurally. The rationale, and what moves a name off the exempt
list, is in
[ADR 0007](adr/0007-trigger-eval-coverage-is-prioritized.md).

**Adjacent skills share one query pool** with labels per skill, so a query
proves exactly one fires — `git-commit`/`pull-request`,
`code-review`/`find-bugs`, `codebase-design`/`domain-modeling`,
`grilling`/`review-response`, `agent-skills`/`agent-rules`. Labeling a shared
query should-trigger in both is unfalsifiable, so `check-payload` fails on it.
Pick a partner that can win the query — pairing against a flagged skill measures
nothing on Claude. A skill contested from several directions at once cross-labels
its positives as negatives in every neighbor rather than merging their pools;
`draft-plan` does, and `spec/trigger-evals/README.md` says why.

Two checks are worth understanding before you change them:

- **Secret-path parity derives its subjects** from Claude's own `Read()`
  denials rather than a hardcoded list, so adding a deny to
  `.claude/settings.json` *forces* the Codex and Cursor mirrors instead of
  relying on a reviewer noticing. A subject with no possible counterpart goes in
  the script's `parity_exempt` with its reason — never deleted.
- **The self-tests guard the checks whose clean result is indistinguishable from
  a broken one** — invocability and reference reachability are both silent when
  the payload is fine, and the invocability bug they exist for shipped for
  months with every other check passing. The srt shim self-test is the same
  shape: a self-wrapping shim passes exactly like a correct one, which is how
  that form shipped. Their fixture violations are the
  assertion; don't tidy them
  ([ADR 0006](adr/0006-fixtures-assert-with-deliberate-violations.md)).

Warnings never fail the run. Failures always do.

## Spelling

`cspell` reads `cspell.json` at the root and checks Markdown, shell, JSON, and
TOML alike. Pass `--dot` or you check almost nothing that matters: without it
the payload under `.agents/`, `.claude/`, `.codex/`, `.cursor/`, and `.github/`
is skipped. Git-ignored output stays out via `useGitignore`, and `.git/` itself
via `ignorePaths`.

The `payload` job runs it on every push and PR, so a misspelling fails the build
instead of landing. Run it locally first anyway — `mac` installs `cspell`, and
an editor extension pointed at the same `cspell.json` shows the findings as you
write.

**American spelling, always.** `language` is `en-US` and stays there. A British
spelling is prose to fix, never a word to add: `behavior`, `neighbor`,
`judgment`, `labeled`, `organization`.

An unknown word is one of three things, and each has its own fix:

| It is | Fix |
| --- | --- |
| A typo | Fix the prose |
| Project vocabulary or a recurring identifier | Add to `words` in `cspell.json` — lowercase, alphabetical |
| A deliberate fragment: a truncated example, a regex stem | A `cspell:ignore` directive in that file, adjacent to the line it excuses |

`ignoreWords` in the config is for fragments with no file to live in —
`iskov`, `nterface`, and `ependency` fall out of `**L**iskov`-style bold markup
in `.agents/AGENTS.md`, which ships to every project and shouldn't carry a
directive comment for a local lint.

Vendored skills invert the middle row: their words go in `cspell.json` however
one-off they are, because a directive comment inside a vendored body is a
hand-edit, and a hand-edit desynchronizes the recorded hash.
