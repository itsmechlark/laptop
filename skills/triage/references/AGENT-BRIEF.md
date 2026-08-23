# Writing agent briefs

An agent brief is the comment posted when an item moves to `ready-for-agent`. The original report and its discussion are context; **the brief is the contract**. Whoever picks the work up — an unattended agent or a human — should be able to start from the brief alone.

A brief says what should be *true when the work is done*. For an issue that means building the behavior; for a PR it means what is left to do to the existing diff — finish it, close the gaps, address the review points.

## Principles

**Durable over precise.** The item may sit in `ready-for-agent` for weeks while the codebase moves. Describe interfaces, types, and behavioral contracts; name the types, signatures, and config shapes to look for. Do not reference file paths or line numbers, and do not assume today's structure survives.

**Behavioral, not procedural.** Say what the system should do; the implementer explores the codebase fresh and makes its own calls.

* Good: "`SkillConfig` should accept an optional `schedule` field of type `CronExpression`"
* Bad: "Open `src/types/skill.ts` and add a schedule field on line 42"

**Acceptance criteria that can fail.** Every criterion must be independently checkable and phrased so an implementer can tell done from nearly done. "Triage should work correctly" is not a criterion; "`gh issue list --label needs-triage` returns only items past initial classification" is.

**Explicit scope boundaries.** Name what not to touch. Without boundaries, an unattended agent may gold-plate adjacent work that only looked related.

**A brief for a bug or a PR carries its repro.** The artifact from step 3 of triage goes in the brief verbatim — the failing test and the branch it lives on, the exact command and its unedited output, or, for a UI bug, the exact browser steps (URL, navigation, clicks) and the screenshot they produced — whichever browser-automation tool captured them.

Prose decays. A week later, "confirmed" does not say whether anyone actually ran anything. An artifact gives the implementer its first move, which is TDD's starting point handed over at the moment someone had the repro in hand.

For a bug or a PR, the first acceptance criterion re-runs that artifact.

## Acceptance criteria

Acceptance criteria are the ticket's pass/fail contract: how an implementer, reviewer, or unattended agent proves the work is done without relying on intent, code inspection, or tribal knowledge. Each one must be independently checkable and phrased so someone can tell done from nearly done.

Default to `given <state/input>, when <action>, then <observable result>` when a criterion has a state, an action, and a result. When it doesn't, a flat assertion is clearer — the repro line usually is one. Don't force the ceremony where it adds nothing.

For bugs and PRs, the first criterion re-runs the captured repro artifact from the `Repro` block:

```markdown
**Acceptance criteria:**
- [ ] the repro passes — <exact branch, test, command, UI path, screenshot, or recorded output from Repro>
- [ ] given <state/input>, when <action>, then <observable result>
- [ ] given <edge case>, when <action>, then <expected result>
- [ ] given <invalid input or failure condition>, when <action>, then <safe result>
```

For enhancements, which have nothing to reproduce, the first criterion proves the smallest complete happy path:

```markdown
**Acceptance criteria:**
- [ ] given <valid starting state>, when <new behavior is used>, then <expected user- or system-visible result>
- [ ] given <important edge case>, when <same behavior is used>, then <expected result>
- [ ] given <unsupported or invalid case>, when <same behavior is attempted>, then <clear failure, empty result, no-op, rollback, or unchanged state>
```

### Lead with the repro

For bugs and PRs, the first criterion reuses the exact proof captured during triage — the same branch, test, command, UI path, or output from the `Repro` block. The implementer should not have to guess which one proved the problem, so name the exact invocation rather than gesturing at it.

Good:

```markdown
- [ ] the repro passes — on `triage/42-repro`, `bundle exec rspec spec/services/publish_remaining_spec.rb` passes
- [ ] the repro command prints `published_remaining: 0` for booking `B-123`
```

Bad:

```markdown
- [ ] focused tests pass
- [ ] the bug is fixed
```

When the repro exercises only one branch, name the rest so they aren't left unproven:

```markdown
- [ ] the repro test covers the duplicate-booking case
- [ ] given a booking appears only in the web view, when remaining quantity is calculated, then it is deducted once
- [ ] given a booking appears only in the admin view, when remaining quantity is calculated, then it is deducted once
```

### Tie every claim to a case

Let someone verify the outcome without reading the implementation first. Prefer input → output over structural description, and pin every invariant or negative to at least one concrete case — an abstract "never double-counts" can't be run.

Good:

```markdown
- [ ] given qty 3 and one table blocked in both availability views, when remaining quantity is calculated, then the result is 2, not 1
```

Bad:

```markdown
- [ ] the three call sites share one calculation
```

Negatives need the same treatment — a specific case, not a blanket "does not":

Good:

```markdown
- [ ] given the same donation webhook is received twice with event id `evt_123`, when both deliveries are processed, then only one acknowledgement email is sent
```

Bad:

```markdown
- [ ] does not send duplicate emails
```

Structure may be reviewed later, but it is not the acceptance contract — unless the ticket is explicitly about a public interface, schema, migration, package boundary, compatibility surface, or other structural contract.

### Sweep for uncaptured claims

Every concrete behavior mentioned in `Desired behavior` and `Key interfaces` must appear in the acceptance criteria or be named as out of scope. A sharp behavior stated in prose but missing from the checklist is the usual way "done" becomes under-specified. Before finalizing, sweep for claims like:

* "does not double-count"
* "preserves existing behavior"
* "remains backward compatible"
* "records an audit event"
* "does not notify twice"
* "handles missing config"

Each becomes either a criterion (`given <case>, when <action>, then <result>`) or an explicit entry under `Out of scope`.

### Cover what matters

Most briefs land at 3–7 criteria. Walk this list and include the ones the ticket actually has — not all seven, only what applies:

1. **Repro or happy path** — the failing artifact now passes, or the new behavior works in the normal case.
2. **Preserved behavior** — existing valid behavior stays unchanged where that matters.
3. **Edge case** — boundary values, empty state, duplicate input, repeated execution, or ordering.
4. **Failure case** — invalid input, missing config, failed dependency, permission failure, or timeout fails safely.
5. **Interface contract** — any public type, API, config, payload, CLI output, event, or backward-compatibility promise.
6. **Observable side effect** — logs, audit events, notifications, emitted jobs, metrics, persisted records, or external calls.
7. **Regression proof** — the test, command, or UI flow that proves the behavior, named explicitly.

### Avoid vague completion words

These pass review while meaning nothing testable; replace each with a concrete observable result:

> correctly · properly · gracefully · efficiently · robustly · as expected · as needed · works · improved · optimized · cleaned up · production-ready

Bad:

```markdown
- [ ] handles invalid config gracefully
```

Better:

```markdown
- [ ] given `schedule` is present but not a valid cron expression, when config is loaded, then validation fails with an error naming `schedule` and no skill is registered
```

### Keep human gates out

Do not list criteria an unattended agent cannot complete or verify:

```markdown
- [ ] CI is green before merge
- [ ] maintainer approves the semantics
- [ ] product confirms this is acceptable
```

Those may be real gates, but they belong in the handoff or the `ready-for-human` rationale, not the behavioral checklist. If the ticket needs a human decision before implementation can continue, it should not be `ready-for-agent` at all.

### Before you ship it

Before moving a ticket to `ready-for-agent`, verify:

* [ ] bugs and PRs have a first criterion that re-runs the exact repro artifact
* [ ] every criterion can fail independently and describes behavior, output, state, or contract — not implementation steps
* [ ] every claim in `Desired behavior` appears in the criteria or under `Out of scope`
* [ ] edge and failure cases are covered where the behavior has meaningful branches
* [ ] commands, branches, test names, UI paths, and expected outputs are quoted where they're needed to verify completion
* [ ] vague terms are replaced with concrete pass/fail outcomes
* [ ] human approval and CI merge gates are not listed as criteria

## Template

```markdown
## Agent brief

**Category:** bug / enhancement
**Summary:** one line — what needs to happen

**Repro:** *(bugs and PRs; omit for enhancements)*
The failing test and the branch it lives on, the exact command and its verbatim
output, or, for a UI bug, the browser steps (URL, navigation, clicks) and the
screenshot they produced, in whatever browser-automation tool captured them.
Enough that the reader can see the problem themselves without re-deriving it.

**Current behavior:**
What happens today. For a bug, the broken behavior. For an enhancement, the
status quo it builds on. For a PR, the state of the diff.

**Desired behavior:**
What should be true afterward, including edge cases, error conditions,
compatibility expectations, and observable side effects.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns now vs what it should return
- config / payload shape — any new options
- emitted event / persisted record / CLI output — any observable contract

**Acceptance criteria:** *(bugs and PRs: first criterion re-runs the repro artifact)*
- [ ] the repro passes — <exact branch, test, command, UI path, screenshot, or recorded output from Repro>
- [ ] given <normal input/state>, when <user or system action>, then <observable result>
- [ ] given <edge case or boundary>, when <same action>, then <expected result>
- [ ] given <invalid input, missing dependency, or unsupported state>, when <action>, then <safe failure, error, no-op, rollback, or unchanged state>
- [ ] <required public interface, payload, config, event, persisted state, notification, metric, or audit behavior is observable and matches the brief>

**Out of scope:**
- adjacent thing that must not change
- related behavior intentionally not covered by this ticket
```

## Example — a good brief

```markdown
## Agent brief

**Category:** bug
**Summary:** Long skill descriptions truncate mid-word

**Repro:**
`triage/42-repro` — a test asserting that a 1,200-character description is cut
at a word boundary. Fails today; the assertion diff shows the output ending
"Use when the user wants to confi".

**Current behavior:**
A description over 1024 characters is cut at exactly 1024 regardless of word
boundaries, producing output that ends mid-word ("Use when the user wants to confi").

**Desired behavior:**
Truncation breaks at the last word boundary before the limit and appends "…",
with the total length still within 1024 characters. Shorter descriptions are
untouched.

**Key interfaces:**
- The frontmatter reader that populates the description field — no type change,
  but its truncation path needs to respect word boundaries
- Any caller that assumes an exact-1024 cut

**Acceptance criteria:**
- [ ] the repro test on `triage/42-repro` passes
- [ ] descriptions under the limit are unchanged, byte for byte
- [ ] given a description over 1024 characters, when the description is rendered, then it breaks at the last word boundary before the limit
- [ ] given a truncated description, when it is rendered, then it ends with "…" and is never longer than 1024 characters
- [ ] given a description of exactly 1024 characters, when it is rendered, then it is left unchanged with no "…" appended

**Out of scope:**
- changing the 1024 limit
- multi-line descriptions
```

## Example — a bad brief

```markdown
## Agent brief

**Summary:** Fix the triage bug

**What to do:**
The triage thing is broken. Look at the main file — the function around line 150
has the issue.

**Files to change:**
- src/triage/handler.ts (line 150)
```

No category. "The triage thing is broken" describes nothing. Paths and line numbers that will be stale within a week. No repro, so there is no way to tell whether the bug was ever observed or just believed. No current-vs-desired split, no criteria, no boundaries — so nobody, agent or human, can tell when it is finished.

<!-- cspell:ignore confi -- the mid-word cut the example brief is quoting -->

