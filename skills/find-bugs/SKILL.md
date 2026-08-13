---
name: find-bugs
description: Adversarial defect hunt over a change — map its attack surface, hunt each surface for injection, IDOR, race conditions, SSRF, path traversal, silent failures, and resource exhaustion, then prove each finding is reachable before reporting it. Produces evidence, never a patch and never a merge verdict. Trigger with "find bugs in this branch", "security audit these changes", "did I introduce a vulnerability?", "audit this before I push", "look for security holes in what I just wrote", or a pre-PR self-audit of unreviewed local work.
argument-hint: "[fixed point (branch/tag/SHA) to audit since — omit for uncommitted work] [focus or threat model, e.g. \"the webhook path\"]"
---

# Find Bugs

Hunt for real, reachable defects in a change: map what the change exposes, hunt each surface for the bug classes that can actually live there, and prove every finding is reachable before reporting it.

**Report, don't repair.** Even when the fix is obvious, write it as a suggestion. The person who asked decides what changes.

## When to use this skill

- Auditing what you just wrote, before pushing or opening a PR
- A deep security pass on a change touching auth, money, tenancy, or untrusted input
- Re-auditing a change that a lighter review already waved through
- "Find bugs in this branch", "security audit these changes", "did I introduce a vulnerability?"

Not for deciding whether a change should merge, checking it against the repo's conventions or its originating spec, or fixing what you find — that three-axis merge gate is the `code-review` skill. This skill produces evidence: not a verdict, not a patch.

## 1. Establish the review set

A hunt over the wrong or empty diff reports "no issues found" and looks like success. Pin the set down before reading any code.

Resolve the base, stopping at the first that works:

1. A ref in the argument (`$1`) — a branch, tag, or SHA.
2. `git symbolic-ref --short refs/remotes/origin/HEAD` — the remote's default branch.
3. Whichever of `main`, `master`, `develop` that `git rev-parse --verify` resolves.
4. Nothing resolves → ask. Don't guess, and don't let a failed lookup expand into an empty ref.

```sh
git diff <base>...HEAD --stat     # three dots: compare against the merge base
git log <base>..HEAD --oneline
```

Then account for every file in the set:

- **An empty `--stat` is a stop, not a pass.** It means the base is wrong or the work is uncommitted. Resolve it before reading anything.
- **Uncommitted work:** `git diff HEAD` for tracked changes, *plus* `git status --porcelain` — a new file that was never `git add`ed appears in no diff at all, and is the easiest whole file to miss.
- **Truncated output:** work from `git diff <base>...HEAD --name-status` and read files individually until the number you reviewed matches the number that changed.

Hunt auth, money, and tenancy first; logging and config last. If context runs short, it should run short on the cheap surfaces. A focus supplied with the argument — "the webhook path", "assume a hostile tenant" — reorders that priority; it never narrows the review set.

## 2. Map the attack surface

Enumerate before you check. Matching a checklist against a diff finds the bugs that look like the checklist; building a model of what the code exposes finds the ones that don't.

Across the review set, list every instance of:

- **Untrusted input** — request params, headers, cookies, body, URL components; webhook and queue payloads; CLI args and env; file contents; third-party API responses
- **Data access** — queries, ORM calls, raw SQL, cache reads and writes
- **Authentication and authorization** — identity checks, permission checks, tenancy and ownership scoping
- **Shared mutable state** — read-then-write pairs, counters, balances, inventory, job handlers, anything retried
- **Outbound and dynamic operations** — HTTP calls, shell execution, filesystem paths, deserialization, template rendering, dynamic eval
- **Secrets and crypto** — key material, randomness, hashing, token generation and comparison, and anything that logs them

The map is the contract for the rest of the hunt: every surface you list is a check you owe, and every check with no surface behind it is one you may skip — **say you skipped it rather than reporting it clean**. A file that maps to no surface at all is not exempt, only cheaper: it still owes *State and arithmetic* and *Error paths* below, which need no attacker to go wrong.

## 3. Hunt each surface

| Surface | Hunt for |
| --- | --- |
| Untrusted input | Injection — SQL, NoSQL, command, template, header, log; unvalidated at the boundary; type confusion; missing size or rate bounds; a regex that backtracks catastrophically |
| Rendered output | XSS via unescaped interpolation, `html_safe` / `dangerouslySetInnerHTML` / `\|safe`; attacker-controlled URL schemes and attributes |
| Data access | Missing owner or tenant filter (IDOR); N+1; unbounded result set; missing index for a new lookup or foreign key |
| AuthN / AuthZ | Protected operation reachable with no check; authenticated but not authorized; a check that runs after the side effect; identity taken from client input; a state change with no CSRF token; an API path missing the check its UI path has |
| Shared mutable state | TOCTOU between read and write; non-atomic increment; missing lock or unique constraint; a retried job that isn't idempotent — the shape behind double-booking and double-charging |
| Outbound / dynamic | SSRF via attacker-controlled host; path traversal (`..`, absolute paths, symlinks); unsafe deserialization; shell metacharacters; missing timeout |
| Secrets and crypto | Hardcoded credentials; secrets in logs, errors, or telemetry; non-CSPRNG for anything security-bearing; home-rolled crypto; non-constant-time comparison |
| Error paths | Swallowed exception, ignored rejected promise, missing `await` on a fallible call, dropped `{:error, _}`; messages leaking internals or PII; partial failure leaving inconsistent state |
| State and arithmetic | Invalid state transitions; numeric overflow or float money; off-by-one; empty, null, and boundary inputs; a branch that falls out with no return; a closure capturing a stale value |

Two classes sit outside the table, because a diff hides them:

- **What the change removed.** A deleted validation, authorization check, bound, or test is a finding. Added lines attract the eye — the deletions are in the same diff, so read them.
- **What the change never handles.** The missing authz check, the absent CSRF token, the unhandled error branch. An absence occupies no line, so ask what *should* be here, not only what is.

## 4. Verify before reporting

Unverified findings are this skill's failure mode. Every candidate clears all four:

1. **Trace it.** Name the caller, the input, and the privilege level that reaches it. No concrete path means it isn't a finding yet — drop it, or report it under "could not verify" with the gap named.
2. **Look for the guard elsewhere.** Middleware, a base class, a `before_action`, a DB constraint, a validation layer, the caller. The check is often real and simply not in this hunk — but find it. "The framework handles that" is a dismissal, not a guard: confirm the protection is switched on and covers *this* path before dropping a candidate.
3. **Look for a test.** An existing test pinning the behavior is evidence it's handled.
4. **Read the whole enclosing function and its call sites**, not the hunk. A diff-shaped view of the code produces diff-shaped mistakes.

**Severity is reachability × impact:**

| Severity | Means |
| --- | --- |
| Critical | Unauthenticated reach; or data loss or corruption; or exposure of credentials or another tenant's data |
| High | Authenticated reach; or a broken core invariant — double-charge, overbooking, privilege escalation |
| Medium | Needs unusual conditions or elevated privilege; a correctness bug with a workaround |
| Low | Real but bounded — a defensive gap, a noisy failure, a small leak |

State the trigger for anything Critical or High. If you can't say who does what to set it off, it's Medium at most.

**Don't report:** issues with no reachable path; defense-in-depth wishes dressed as vulnerabilities; framework behavior you didn't verify; style, formatting, or naming; anything a linter or type-checker already enforces; a risk the repo documents as accepted.

## Output

```markdown
## Bug Hunt: [ref range, or "working tree"]

[N findings — worst is <severity>: <one line>.  |  No significant issues found.]

### Findings

**1. <Severity> — `path/to/file.rb:42` — [one-line description]**
- **Problem:** what's wrong
- **Trigger:** who reaches it, with what input, at what privilege
- **Evidence:** why it's real — no guard at X, no test covering Y
- **Fix:** concrete suggestion
- **Reference:** OWASP / CWE / RFC, where one applies

### Coverage
- Reviewed N of N changed files. Surfaces mapped: [list]
- Not applicable: [surfaces with no instance in this change]
- **Could not verify:** [what, and why — the honest half of this report]
```

Order findings by severity, not by file, and report a defect once at its root cause rather than at every call site. Found nothing significant? Say so plainly — an empty report is a valid result, and a Medium invented to look thorough costs the reader more than it gives.

## Gotchas

- **An empty diff reads as a clean bill of health.** The classic cause is a base ref that silently resolved to nothing — a missing `gh`, no network, or no `origin`. Verify the diff is non-empty before you hunt, and never report on one that isn't.
- **A secret in the diff is already in git history.** Report the file and line, never the value; the fix is rotation plus history removal, not deleting the line.
- **Untracked files appear in no diff.** When auditing uncommitted work, reconcile `git status --porcelain` against what you read.
- **Large changes: fan out, don't skim.** Run one sub-agent per surface group, give each the diff command and its slice of the map, and aggregate. Skimming a 40-file diff yields a confident, empty report — the worst output this skill can produce.
- **Absence of evidence isn't evidence of absence.** "I didn't see an authz check" and "there is no authz check" are different claims. Put the first under "could not verify".

## Attribution

- [getsentry/skills](https://github.com/getsentry/skills/tree/main/skills/find-bugs) - find-bugs, Apache-2.0
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [ulpi-io/skills](https://github.com/ulpi-io/skills/tree/main/find-bugs) - find-bugs, inspired-by
