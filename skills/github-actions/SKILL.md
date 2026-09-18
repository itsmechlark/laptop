---
name: github-actions
description: Audit GitHub Actions workflows that already exist and report what is wrong with them, across two axes — Security (script injection through `${{ }}`, privileged triggers running fork code, mutable action refs, over-scoped `GITHUB_TOKEN`) and Cost (missing caches and concurrency cancellation, over-broad triggers, matrix breadth nothing decides). Also writes the prose companion beside `.github/workflows/`. Trigger with "review my CI", "is this workflow safe?", "audit my GitHub Actions", "why is pull_request_target dangerous here?", "reduce our CI minutes", "our Actions bill is too high", "which jobs are wasting runner time", or "document what this pipeline does". Reports findings and never applies them.
argument-hint: "[workflow path, or the axis to audit — security or cost]"
---

# GitHub Actions

Audit workflows that exist. The conventions that apply while *writing* one live
in `rules/github-actions.md`, which auto-loads on `.github/workflows/*.yml` and
`**/action.yml` — this skill assumes them and reports where a workflow departs
from them, with evidence.

## When to use this skill

- "Review my CI", "is this workflow safe?", "audit our GitHub Actions"
- A workflow uses `pull_request_target`, `workflow_run`, or `issue_comment` and
  someone wants to know whether that is safe here
- CI minutes, runner spend, or PR wall-clock time is the complaint
- A pipeline needs its prose companion written or refreshed

Not for writing a new workflow — that is the rule, already in context when you
open the file. Not for a vulnerability hunt across application code, which is
`find-bugs`, and not for a merge verdict on a diff, which is `code-review`.

## The two axes

Both read the same files and produce one report. Run whichever the request
asks for; run both when it just says "review".

| Axis | Asks | Reference |
| --- | --- | --- |
| Security | Can an outside contributor reach a write token or a secret? | [SECURITY.md](references/SECURITY.md) |
| Cost | What runs that nothing decides on? | [COST.md](references/COST.md) |

They fail in opposite directions, which is why they stay separate axes rather
than one list: a security finding is usually *add a constraint*, a cost finding
is usually *remove work*. A fix that does both — narrowing a trigger so a
privileged job stops firing — is worth saying so explicitly.

## Workflow

### 1. Establish what you can actually see

Read every file under `.github/workflows/` and every local `action.yml`. Then
try for run history, because half the cost axis is unprovable without it:

```sh
gh run list --limit 20
gh run view "$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')" --log-failed
```

**Without shell or `gh`, say so in the report's first line** — "Static analysis
only; no run history" — and drop the measured-savings column rather than
estimating it. Partial input gets the same treatment: name which files you had.

### 2. Run the axes

Security is the one to run first when both are in scope: a finding there can
delete a job the cost axis was about to optimize.

### 3. Report

One report, format in [REPORT.md](references/REPORT.md): counts by severity
first, then findings grouped by issue type rather than by file, each quoting the
offending line with its location and pairing anything CRITICAL or HIGH with a
corrected snippet.

**Never apply the fixes.** This skill produces evidence and leaves the change to
the user, the same way `find-bugs` does. Close the report with the line
[REPORT.md](references/REPORT.md) specifies so that is unambiguous.

## Severity

| Severity | Meaning |
| --- | --- |
| CRITICAL | Token or secret theft, or RCE, reachable by an outside contributor |
| HIGH | Exploitable supply-chain or scope problem, or a dominant cost driver |
| MEDIUM | Risk under conditions, or chained with something else |
| LOW | Hardening gap or minor waste |
| INFO | Observation, not a defect |

**Don't inflate.** A fork `pull_request` running untrusted code has a read-only
token and no secrets — that is the design working, not a CRITICAL. Reserve
CRITICAL for the privileged triggers.

## Documenting a pipeline

Where a repository keeps prose beside its workflows, it is two tiers:
`.github/workflows/README.md` maps the pipeline, and a sibling `<name>.md`
carries one workflow's depth. A local action documents itself in its own
directory's `README.md`, which is the file GitHub renders.

A workflow's own file takes a fixed section set — purpose, a mermaid dependency
graph, jobs, secrets and external systems, invariants, failure modes, required
checks, when changing, related. Four are required and the rest appear only with
real content, because an empty heading teaches a reader to skim. Every one of
them earns its place the same way: **if the YAML states it plainly, it does not
go in the document.**

**Where a repository keeps none, say so and stop.** Don't create one, and don't
offer to generate it from the YAML — a companion doc that restates the steps is
the drift it exists to prevent. These are worth having only where someone chose
to keep one. The section set, the diagram conventions, and what belongs in which
tier: [DOCUMENTING.md](references/DOCUMENTING.md).

## Gotchas

- **`${{ }}` is substituted before the shell exists.** It is not a variable
  reference, so quoting inside `run:` does not help and neither does escaping.
  The only fix is binding through `env:`. This is the single most common real
  Actions vulnerability and models generate it constantly.
- **A `pull_request` from a fork is safe by design.** Read-only token, no
  secrets. Maintainers hit "the secrets don't work on fork PRs" and switch to
  `pull_request_target` to get them back — that switch is the vulnerability, and
  flagging the original as dangerous sends them toward it.
- **`npm install` in a privileged job is code execution.** Lifecycle scripts run
  from the PR's own tree. So are `bundle install`, `pip install`, and any build
  that honors a checked-in config.
- **A merged job is not a cheaper job.** Merging two jobs that ran in parallel
  lengthens the critical path even as total runner minutes drop. Separate PR
  wall-clock from runner spend in every claim; a change can improve one and hurt
  the other.
- **Don't claim minutes saved without before/after runs.** Say which mechanism
  changed and what you would measure. Cache warm-up, matrix changes, and an
  unusually small PR all confound a single comparison.
- **The first push to a new branch is not a path-filter test.** It touches
  everything by definition. Validate gating with an incremental change on a
  branch that already exists.
- **A SHA pin goes stale silently.** Pinning is right, and it is also how a
  workflow ends up three years behind on an action with a known advisory —
  recommend Dependabot for the `github-actions` ecosystem alongside any pinning
  finding, never instead of it.

## References

Read these as needed, not upfront.

- [SECURITY.md](references/SECURITY.md) — the trust matrix per trigger, the full
  injection sink list and the `env:` rewrite, `permissions:` recipes, OIDC, SHA
  pinning, artifact and cache poisoning, self-hosted runner exposure
- [COST.md](references/COST.md) — the audit order, the guardrails a fix must
  pass before it is recommended, matrix-breadth reduction, and live validation
- [REPORT.md](references/REPORT.md) — output format for both axes
- [DOCUMENTING.md](references/DOCUMENTING.md) — the two-tier companion doc, its
  fixed section set, and the mermaid conventions

## Attribution

- [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-hardening) - github-actions-hardening, MIT
- [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-efficiency) - github-actions-efficiency, MIT
- [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/create-github-action-workflow-specification) - create-github-action-workflow-specification, MIT
