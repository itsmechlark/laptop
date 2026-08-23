# Verification stops where judgment starts, and trigger evals stay out of CI

**Context:** `mac` is verified by shellcheck plus a real run. The payload it
ships had no equivalent. What needs checking splits three ways: invariants a
machine can settle exactly (does this link resolve, does this `AGENTS.md §N`
citation exist), behavior only a model can measure (does this description
actually fire), and prose quality.

**Decision:** `check-payload` covers the first only — deterministic and
file-local — and runs in CI. Whether a description triggers belongs to the query
sets in `spec/trigger-evals/`, run from a terminal against `claude -p`. Prose
judgment and whether a rule *applies* to a file stay human and are not checked
at all.

**Consequences:** The `payload` job needs no credentials, no network, and no
token spend, so it runs in seconds on `ubuntu-latest` and gates every push. The
cost is that trigger evals are skippable — a changed description can ship
unmeasured, and the only mitigation is the convention of saying plainly when
they were skipped. Coverage there is prioritized rather than uniform, which is
its own decision (ADR 0007).

Choosing `claude -p` as the runner also decides what can be measured at all.
`scripts/lib/run_eval_local.py` installs the skill under a temp
`.claude/skills/` and watches Claude's `Skill` tool, and a flagged skill cannot
fire on Claude — so a query set aimed at one is not merely unmotivated but
unrunnable by any engine in this repo, and `check-payload` rejects it. On Codex
and Cursor such a skill *can* misfire, because they ignore the key; measuring
that would take a second runner driving `codex` and `cursor-agent`, which is the
change to propose if it ever matters. Until then the skill's own body is the
only guard on those two clients (ADR 0003).

**Rejected:** Running the evals in CI. It would close the skip, but it needs an
API credential in repository secrets, spends tokens on every push, and imports
model nondeterminism into a required check — a flaky gate on a repo whose other
checks are exact. Scoring prose mechanically was the other option, and a linter
that grades writing manufactures false confidence in exactly the place judgment
is needed.
