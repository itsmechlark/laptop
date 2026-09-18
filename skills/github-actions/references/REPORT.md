# Report format

One report per audit, whichever axes ran. Say which files it covers and which
axes it covers in the first line — a security-only pass that reads like a full
review leaves the user believing the cost axis came back clean.

## 1. Summary, always first

```
GitHub Actions audit — .github/workflows/{ci,release}.yml
Axes: security, cost. Static analysis only; no run history available.

| Severity | Count |
| --- | --- |
| CRITICAL | 1 |
| HIGH | 2 |
| MEDIUM | 1 |
| LOW | 1 |
| INFO | 0 |
```

Nothing found is a result worth stating precisely, because it says what was
actually covered:

> No issues found. Checked: trigger privilege, injection sinks, `permissions:`
> scope, action pinning, secret handling, caching, concurrency, matrix breadth.

## 2. Findings, grouped by issue type

Group by issue type, not by file — three instances of the same injection sink
are one finding with three locations, and a reader fixes them in one pass.

```
### CRITICAL — Script injection via PR title on a privileged trigger

File: .github/workflows/triage.yml:14
Trigger: pull_request_target

Offending code:
    - run: echo "New PR: ${{ github.event.pull_request.title }}"

Risk: pull_request_target runs with a read/write token and repository
secrets, and any contributor can open a PR titled  "; <attacker-command> #
which is executed as shell. That allows secret exfiltration and pushes
with the workflow token.

Fix:
    - env:
        PR_TITLE: ${{ github.event.pull_request.title }}
      run: echo "New PR: $PR_TITLE"

Confidence: High
```

Cost findings take the same card with the risk line replaced by the evidence
and the estimate:

```
### HIGH — Full test matrix runs on documentation-only changes

File: .github/workflows/ci.yml:8
Evidence: 6 matrix legs × ~4 min, no paths filter; 14 of the last 20 runs
touched only docs/.

Fix:
    on:
      pull_request:
        paths-ignore:
          - "docs/**"
          - "**/*.md"

Impact: ~24 runner-minutes per docs PR avoided. PR wall-clock unchanged
for code PRs. Estimated from run history, not measured before/after.

Confidence: Medium
```

## 3. Remediation

Every CRITICAL and HIGH carries a concrete before/after. Preserve the author's
indentation, step names, and surrounding structure — change only what fixes the
issue, and add a one-line comment where the change is not self-evident. A
snippet the user has to re-indent is a snippet they will retype wrong.

## 4. Closing line

End with exactly this, so there is no ambiguity about what was touched:

> Review each change before committing. Nothing has been modified.

## Style

- Quote the offending line and give `file:line`. A finding without a location
  is a lecture.
- Explain risk as what an attacker does, or what the waste costs — not the name
  of the rule.
- Per-finding confidence: High / Medium / Low. A MEDIUM finding you are certain
  about and a CRITICAL you are guessing at are different things, and severity
  alone cannot say so.
- Don't inflate severity. A fork `pull_request` running untrusted code has a
  read-only token and no secrets; that is the design working.
- Don't average across axes. A workflow can be clean on security and wasteful
  on cost, and one blended verdict hides both.
