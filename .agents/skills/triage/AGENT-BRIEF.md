# Writing agent briefs

An agent brief is the comment posted when an item moves to `ready-for-agent`. The original report and its discussion are context; **the brief is the contract**. Whoever picks the work up — an unattended agent or a human — should be able to start from the brief alone.

A brief says what should be *true when the work is done*. For an issue that means building the behavior; *for a PR* it means what's left to do to the existing diff — finish it, close the gaps, address the review points.

## Principles

**Durable over precise.** The item may sit in `ready-for-agent` for weeks while the codebase moves. Describe interfaces, types, and behavioral contracts; name the types, signatures, and config shapes to look for. Don't reference file paths or line numbers, and don't assume today's structure survives.

**Behavioral, not procedural.** Say *what* the system should do; the implementer explores the codebase fresh and makes its own calls.

- Good: "`SkillConfig` should accept an optional `schedule` field of type `CronExpression`"
- Bad: "Open src/types/skill.ts and add a schedule field on line 42"

**Acceptance criteria that can fail.** Every criterion independently checkable, phrased so an implementer can tell done from nearly-done. "Triage should work correctly" is not a criterion; "`gh issue list --label needs-triage` returns only items past initial classification" is.

**Explicit scope boundaries.** Name what not to touch. Without them, an unattended agent gold-plates the adjacent thing that looked related.

**A brief for a bug or a PR carries its repro.** The artifact from step 3 of triage goes in the brief verbatim — the failing test and the branch it's on, the exact command and its unedited output, or, for a UI bug, the `agent-browser` click path and the screenshot it produced. Prose decays: a week later "confirmed" doesn't say whether anyone actually ran anything. An artifact also gives the implementer its first move, which is TDD's starting point (AGENTS.md §1) handed over at the moment someone had the repro in hand. For a bug, the first acceptance criterion is that the repro passes.

## Template

```markdown
## Agent brief

**Category:** bug / enhancement
**Summary:** one line — what needs to happen

**Repro:** *(bugs and PRs; omit for enhancements)*
The failing test and the branch it lives on, the exact command and its
verbatim output, or (for a UI bug) the `agent-browser` click path and the
screenshot it produced. Enough that the reader can see the problem
themselves without re-deriving it.

**Current behavior:**
What happens today. For a bug, the broken behavior. For an enhancement, the
status quo it builds on. For a PR, the state of the diff.

**Desired behavior:**
What should be true afterward, including edge cases and error conditions.

**Key interfaces:**
- `TypeName` — what changes and why
- `functionName()` — what it returns now vs what it should return
- config / payload shape — any new options

**Acceptance criteria:**
- [ ] specific, checkable criterion
- [ ] specific, checkable criterion

**Out of scope:**
- adjacent thing that must not change
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
- [ ] descriptions under the limit are byte-for-byte unchanged
- [ ] longer ones break at the last word boundary before the limit
- [ ] truncated output ends with "…" and is never longer than 1024 characters
- [ ] a test covers the boundary case at exactly 1024

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

No category. "The triage thing is broken" describes nothing. Paths and line numbers that will be stale within a week. No repro, so there's no way to tell whether the bug was ever observed or just believed. No current-vs-desired split, no criteria, no boundaries — so nobody, agent or human, can tell when it's finished.
