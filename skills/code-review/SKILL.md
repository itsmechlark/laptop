---
name: code-review
description: Review a change along three axes — Defects (security, performance, correctness, reliability bugs), Standards (does it follow this repo's documented conventions and the code-smell baseline?), and Spec (does it do what the originating issue/PRD asked for?). Trigger with a PR URL, a diff, a file path, a fixed point to review since (a branch/tag/SHA, "review since main"), "review this before I merge", "is this code safe?", or when checking a change for N+1 queries, injection risks, missing edge cases, error-handling gaps, or backwards-compatibility breaks. Returns a merge verdict across all three axes — not a standalone, exhaustive security audit of a change you already wrote.
argument-hint: "[fixed point (branch/tag/SHA), PR URL, diff, or file path]"
---

# Code review

Review a change along three independent axes:

- **Defects** — is the code wrong or unsafe? Security, performance, correctness, and reliability bugs. A real defect is blocking regardless of what the repo documents.
- **Standards** — does it follow this repo's documented conventions, plus the smell baseline below? A breach of a documented standard can be a firm finding; a smell from the baseline is always a judgment call, and the repo overrides.
- **Spec** — does the change implement what the originating issue / PRD asked for? Missing requirements, scope creep, wrong implementation.

Keep the axes separate on purpose. A change can pass one and fail another — clean code that builds the wrong thing (Defects/Standards pass, Spec fail); the right feature built against the conventions (Spec pass, Standards fail). Reporting them together lets one mask the other.

## When to use this skill

- Deciding whether a change is safe to merge — "review this before I merge", "is this code safe?", "is PR #412 good to go?"
- Checking a diff against the repo's own conventions and the code-smell baseline
- Checking a change against its originating issue / PRD — "did I build what the ticket actually asked for?"
- Reviewing a PR URL, a pasted diff, a file, or everything since a fixed point ("review since main", a branch/tag/SHA)

Not for an exhaustive, evidence-first security audit of code you already wrote — attack-surface mapping and per-finding reachability proofs, with no merge verdict attached, are the `find-bugs` skill. This skill returns a verdict; that one returns evidence. For *receiving* a review rather than giving one, see `review-response`.

## Scope the change

Establish exactly what you're reviewing before reading any code. The argument (`$1`) is the review target; if nothing was supplied, ask what to review — don't guess.

- **A fixed point** (branch, tag, SHA, `main`, `HEAD~5`): diff with three dots so the comparison is against the merge-base — `git diff <ref>...HEAD` — and list commits with `git log <ref>..HEAD --oneline`. Confirm the ref resolves (`git rev-parse <ref>`) and the diff is non-empty before going further. A bad ref or empty diff fails here, not inside a sub-agent.
- **A PR URL**: `gh pr diff <url>` for the diff, `gh pr view <url>` for the description and linked issue.
- **A file path or pasted diff**: review it directly.

Account for every file in the set — a review that quietly skipped files reads as a pass it didn't earn. On a large diff, `git diff <ref>...HEAD --numstat` is the checklist to reconcile against, and it carries two facts worth reading off it: which files hold the most changed lines, and how much of the diff is tests versus production. Both set reading order, not a grade — they feed **Spend the review budget where the risk is**. A large production change with no test churn is also the shape the Standards axis asks about under tests. Swap in `--name-status` when you want the add/modify/delete letters instead of the counts — a wholesale deletion is the finding at *Removed safeguards*, and it's easiest to see there.

## Defects axis — hard, blocking

Real bugs. A genuine defect is blocking on its own merit — none are softened because the repo happens not to document them.

**Security**
- Injection: SQL / command / XSS
- Broken authentication or authorization
- Secrets or credentials in code or logs
- SSRF, path traversal, insecure deserialization
- Untrusted input (user, API, file, env) used unvalidated at a boundary

**Performance**
- N+1 queries
- Unbounded queries or loops
- O(n²) or worse on a hot path
- Resource leaks; blocking I/O on a hot path
- Missing index for a new lookup or foreign key

**Correctness & reliability**
- Edge cases: empty / null / overflow / boundary
- Race conditions; non-idempotent retries on jobs or mutating endpoints
- Silent failures: swallowed exceptions, ignored rejected promises, dropped `{:error, _}`
- Error propagation; off-by-one; type-safety holes
- Backwards compatibility: a breaking API / contract or schema change with no migration path (expand/contract)
- Side effects: behavior of components the change didn't set out to touch (unintended regressions)
- Removed safeguards: a validation, authorization check, bound, or test the diff deletes — deletions ride in the same diff as the additions and are the easiest thing to skim past

**Severity** — orders the findings and drives the verdict:
- 🔴 **Critical** — exploitable, data loss or corruption, or a guaranteed production break
- 🟠 **High** — a real bug on a normal path: wrong results, a broken invariant, a silent failure
- 🟡 **Medium** — needs unusual input or state, or has a ready workaround
- 🟢 **Low** — bounded: a defensive gap or a noisy failure, not a functional break

When this axis needs to go deeper than a merge decision — attack-surface mapping, a reachability proof for each finding, findings reported as evidence with no verdict — hand it off to the `find-bugs` skill rather than expanding the hunt here.

## Standards axis — conformance

Does the change follow how this repo writes code?

**Sources**, in priority order:
1. Whatever this repo documents about how its code should be written — a root or nested `AGENTS.md` / `CLAUDE.md`, `CONTRIBUTING.md`, a `CODING_STANDARDS.md` or `docs/` style guide, plus any language- or framework-convention files the project loads. Discover what's actually there; don't assume a fixed set.
2. The **smell baseline** below — applies even when the repo documents nothing.

Two rules bind this axis:
- **The repo overrides.** A documented standard always wins; where it endorses something the baseline would flag, drop the smell.
- **Weight follows the source.** A breach of a *documented* standard can be a firm finding; a **smell** from the baseline is always a judgment call — label it ("possible Feature Envy"), never a hard violation. Either way, skip anything a linter, formatter, or type-checker already enforces.
- **Count what's countable.** Some smells are defined by a number — extent, ratio, length, scatter — and the list below marks each with the count to report. Give the figure: "possible Message Chains (4 hops)" is falsifiable where "possible Message Chains" is an opinion. A count is evidence for a judgment call, never what promotes one to firm; only a documented limit does that, and a linter usually owns the limit already.

**Smell baseline** (Fowler, _Refactoring_ ch.3) — name → fix:
- **Mysterious Name** — name doesn't reveal intent → rename; if no honest name comes, the design is murky.
- **Duplicated Code** — same shape in more than one hunk → extract, call from both. *Count: duplicated lines, and how many sites.*
- **Feature Envy** — a method reaches into another object's data more than its own → move it onto that data. *Count: foreign accesses against own.*
- **Data Clumps** — the same fields keep traveling together → bundle into one type.
- **Primitive Obsession** — a primitive standing in for a domain concept → give the concept a small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on one type recurs → polymorphism, or one shared map.
- **Shotgun Surgery** — one logical change forces scattered edits → gather what changes together. *Count: files the one change touched.*
- **Divergent Change** — one module edited for unrelated reasons → split so each changes for one reason.
- **Speculative Generality** — abstraction for needs the spec doesn't have → delete, inline back.
- **Message Chains** — long `a.b().c().d()` navigation → hide the walk behind one method. *Count: hops.*
- **Middle Man** — a class that mostly delegates onward → cut it, call the target directly. *Count: delegating methods against total.*
- **Refused Bequest** — a subclass ignoring most of what it inherits → prefer composition.

Also on this axis: **tests.** Judge new behavior and bug fixes against how this repo already tests. Missing coverage for new logic is a conformance finding — firm where the repo documents a testing requirement (the repo overrides), a judgment call where it doesn't. When missing coverage is a finding, point to the `tdd` skill for addressing it test-first. For Ruby projects, `rules/rspec.md` documents the testing conventions this axis measures against — it auto-loads for spec files.

**When a Standards finding is really a missing standard, say so.** A smell you're flagging across more than one review, or a convention the code plainly follows but nothing documents, is a finding about the *baseline*, not just this diff. Surface it in the report as a candidate for the repo's own standards — a path-scoped rule (`agent-rules`) or an ADR (`domain-modeling`) — so the next review measures against it instead of rediscovering it. Recording it is the user's call and a separate change; flagging it is this skill's.

## Spec axis — the right thing built

Find the originating spec, in this order:
1. Issue references in commit messages or the PR body (`#123`, `Closes PROJ-45`) — fetch it from your issue tracker (`gh issue view`, the Jira tools, etc.).
2. A path the user passed as an argument.
3. A PRD/spec file under `docs/`, `specs/`, or `.scratch/` matching the branch or feature.
4. If none is found, ask. If there is no spec, skip this axis and say so.

Against the spec, report: (a) requirements missing or only partial; (b) behavior in the diff nobody asked for (scope creep); (c) requirements that look implemented but wrong. Quote the spec line for each finding.

## Long-term impact — escalate high-blast-radius changes

Some changes are correct on every axis yet carry outsized risk. When the diff touches any of these, flag it for deeper review — a second reviewer, or an ADR recording the decision (context → decision → consequences) — even when nothing else fails:

- Database schema migrations
- API or provider-facing contract changes
- A new framework or library dependency
- Performance-critical code paths
- Security-sensitive functionality

This is a judgment call surfaced alongside the verdict, not a blocking finding on its own.

## Running the review

- **Small / single-file diff** — review inline.
- **Larger diff** — run the axes as parallel sub-agents so they don't pollute each other's context: one `general-purpose` agent per axis. Give each agent the diff command and commit list. The Standards agent needs the repo's convention docs (`AGENTS.md` / `CLAUDE.md`, `CONTRIBUTING.md`, any style guide) *and* the smell baseline pasted into its prompt — it has no other access to the baseline. Give the Spec agent the spec path or contents. Aggregate their reports; keep the axes separate.

If your environment offers a deeper multi-agent PR toolkit — for example a `pr-review-toolkit` plugin with a `/review-pr` command and specialist agents (silent-failure hunting, test-coverage analysis, type-design review, comment analysis) — reach for it rather than rebuilding that here.

## Output

```markdown
## Code Review: [PR title / ref range]
_Reviewed N of N changed files — M lines changed, T of them in tests._

### Defects (blocking)
| # | File | Line | Issue | Severity |
|---|------|------|-------|----------|
| 1 | [file] | [line] | [what breaks, and when] | 🔴 Critical |

### Standards (conformance)
| # | File | Line | Finding | Weight |
|---|------|------|---------|--------|
| 1 | [file] | [line] | [cited standard / possible <smell> (count)] | firm (documented) / judgment |

### Spec
[Missing / partial / scope-creep / wrong — spec line quoted. Or "no spec available".]

### What looks good
- [Genuine positives, brief]

### Long-term impact
[High-blast-radius changes to flag for deeper review / an ADR — or "none".]

### Verdict
[Approve / Request changes / Needs discussion] — worst issue per axis; don't rerank across axes.
```

Choosing the verdict:
- **Request changes** — any blocking Defect, a missing or wrong Spec requirement, or a firm (documented) Standards breach.
- **Needs discussion** — a high-blast-radius change to escalate, or a judgment-call finding worth a conversation, with nothing outright blocking.
- **Approve** — none of the above; note smells and nits as non-blocking.

## Gotchas

- **Confirm the ref resolves and the diff is non-empty before reading anything.** A base that silently resolves to nothing yields a confident "nothing to flag" that reads as a pass — resolve it in **Scope the change**, never report on an empty diff.
- **Report each defect once, at its root cause** — not at every call site. The same finding repeated per caller buries the fix that actually matters.
- **Don't rerank findings across axes.** The verdict takes the worst issue *per axis*; a clean Defects pass must not paper over a Spec failure, or the reverse — that masking is exactly what keeping the axes separate prevents.
- **A larger diff needs sub-agents, not skimming.** Skimming a big diff yields a shallow, falsely-clean review; fan out one agent per axis (see **Running the review**).
- **"Is this code safe?" means defects in this diff** — not what an AI agent may do at runtime (tool allowlists, policy files, approval gates). That runtime-governance question is a different concern; don't answer it here.
- **Read beyond the hunk.** Judge each change against its enclosing function and call sites, not the diff lines alone — a diff-shaped view produces diff-shaped misses, especially on error paths and edge cases.
- **Spend the review budget where the risk is.** Read the flagged hot path, PII handling, or focus area first; a review that burns out on nits before it reaches the auth change has failed at the one thing that mattered. Where nothing flags a priority, the `--numstat` ranking from **Scope the change** is a reasonable default order — but line count is not risk. A one-line change to an authorization check outranks a four-hundred-line rename.

## Attribution

- Martin Fowler, *Refactoring* (2nd ed.), ch. 3 — code smells
- [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/requesting-code-review) - requesting-code-review, MIT
- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/code-review) - code-review, MIT
- [getsentry/skills](https://github.com/getsentry/skills/tree/main/skills/code-review) - code-review
