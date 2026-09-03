---
kind: plan|implementation|investigation|decision|operation
status: current
topic: <kebab-case-join-key>
tickets: []
prs: []
supersedes: []
---

# <Ticket or area> — <the finding, not the task>

REQUIRED. One paragraph, before any heading: the durable thing a reader who
stops here must walk away with. Not what the work was — what turned out to be
true about the codebase.

## Mechanism

REQUIRED for every kind except `operation`. How the thing actually works, at the
level that cost time to establish. The framework callback that fires after
validation, the dependency that is inert on this platform, the field whose
default gets persisted and then overrides the code default. Written so the next
reader does not have to re-derive it.

## Decisions

OPTIONAL. The choice made, and the alternative rejected with the reason it lost.
Record the constraint that killed the alternative, not the preference — a
constraint is reusable. Omit when there were no real alternatives; an obvious
fix is not a decision.

## Deliberately not done

OPTIONAL, and the highest-value section of any harden or review note. Reviewed
and left alone, with why. This is the only place a negative result is recorded:
there is no diff, no PR, and no commit for the thing that was considered and
correctly skipped.

## Anchors

REQUIRED. Every claim the note makes about code, pinned to a line.

- `path/to/file:64` — what is true at that line
- `path/to/other:100` — the check this bypasses

## Still open

OPTIONAL. Known gaps, deferred work, and tickets opened. Omit the heading
entirely when there are none — never write "None".
