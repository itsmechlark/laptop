# The spec template

Section order is fixed. Every section appears, even when the honest content is
one line — a missing section reads as an oversight, and a reader can't tell
"nothing is out of scope" from "nobody thought about scope".

```markdown
---
name: <the slice, kebab-case>
description: <one line, under 120 characters — when a reader should open this>
metadata:
  status: draft
  topic: <the join key, same as the PRD and slice list this came from>
  tickets: []
  adrs: []
---

## Problem Statement

The problem the user is facing, from the user's perspective.

## Solution

The solution to that problem, from the user's perspective.

## User Stories

1. As an <actor>, I want a <feature>, so that <benefit>

## Implementation Decisions

- The modules or boundaries being built or changed
- The interfaces or contracts that change
- Architectural decisions, and the ADR constraints they sit under
- Schema or data changes, and their compatibility requirements
- API contracts and specific interactions
- Rollout, observability, security, or idempotency constraints

## Alternatives Considered

Options the conversation raised and declined, one line each, with the reason:
cost, technical complexity, or extensibility for a phase already anticipated.

## Testing Decisions

- Which boundaries get tested, and why those
- The happy path, edge cases, failure states, authorization boundaries, and
  compatibility cases that matter
- Prior art: the test types, helpers, fixtures, or conventions already used here

## Out of Scope

What this spec explicitly does not cover, including adjacent slices that must
not be pulled into the implementation.

## Further Notes

Assumptions, unresolved questions, dependencies, and rollout notes a future
implementer needs.
```

## The frontmatter

Three keys, the same block a PRD, a plan, an ADR, and a lore note carry.
`metadata.topic` is what threads them: a spec inherits it from the PRD or slice
list it came from, and the plan written under this spec repeats it.

`description` is required and short — one line, under 120 characters, no
wrapping. It says when someone should open the spec, not what it is titled.

Two rules bound it. **The block belongs to the file, never to the delivered
text** — it renders as literal junk in a Jira or GitHub issue body, so it is
stripped at every tracker boundary ([PUBLISHING.md](PUBLISHING.md)). And **the
output directory's existing convention wins**: read what is already in the specs
directory, and where those files carry a different shape or none, match them and
say so rather than leaving two conventions in one directory.

## What each section holds

**Problem Statement / Solution.** Both in the user's terms, both describing a
visible outcome. "The nightly job is O(n²)" is not a problem statement; "the
report takes 40 minutes and the manager gives up waiting for it" is. If the
solution can only be stated as an implementation task, the frame was wrong —
go back to it before writing the rest.

**User Stories.** Numbered, every one in the `As an <actor>, I want a <feature>,
so that <benefit>` form, and extensive enough to cover the happy path,
boundaries, permissions, failure states, and operational consequences that the
conversation actually supports. Cover, don't pad: a speculative story is an
invented requirement, and the implementer can't tell it from a real one.

Prefer the actor the glossary names. "As a user" usually means the actor was
never pinned down — and two different actors hiding inside one word is the
cheapest requirements bug there is to find at this stage.

**Implementation Decisions.** Boundaries, contracts, data, interactions, and
rollout constraints — enough that an implementer knows what is already decided,
without turning into a code plan. Technical clarifications the developer gave
during the conversation belong here rather than in the narrative, which keeps the
product-facing sections readable on a tracker (AGENTS.md §3, *Jira vs. Pull
Requests — audience separation*).

No file paths, no diffs, no code snippets. A compact prototype-derived state
machine, reducer, schema, or type shape is allowed when it states the decision
more precisely than prose can — include only the decision-rich part, and say it
came from a prototype.

**Alternatives Considered.** Only options the conversation actually weighed. An
invented alternative is padding, and the reader can't tell it from a real one.
Give the option and which of cost, technical complexity, or future-phase
extensibility ruled it out — "it felt wrong" is not a reason; find the one
underneath it or leave the option out. When nothing was weighed, say so: "the
approach was the only one considered" tells a reviewer the design was never
compared, which is worth knowing. A rejection that is hard to reverse and
surprising without context outgrows this section — that's an ADR
(`domain-modeling`), and the spec cites it rather than restating it.

**Testing Decisions.** Name what gets verified in terms of external behavior
through the highest useful seam, not implementation detail. Prior art is the
half most often skipped and the half that saves the most time: point at the
existing test type, helper, or fixture the new tests should look like. When there
genuinely is no prior art, say that — it is a finding, not a blank.

**Out of Scope.** This section is what stops a slice from becoming an epic
during implementation. It should contain at least one thing the conversation
raised and deliberately set aside; if nothing comes to mind, the boundary was
never actually agreed.

**Further Notes.** Everything that is true but unresolved: assumptions you had
to invent, open questions, dependencies on other work, rollout sequencing. An
assumption recorded here is cheap to correct; the same assumption stated
confidently in the Solution is expensive.

## Self-check before showing the draft

- [ ] `description` is one line under 120 characters, and `metadata.topic`
      matches the PRD or slice list this came from rather than being reinvented
- [ ] Problem and Solution both describe a user-visible outcome, not a task
- [ ] Every story is in the `As an <actor>, I want a <feature>, so that
      <benefit>` form, and every actor is a real one — not "the user" standing
      in for two different people
- [ ] Every story traces to something in the conversation or the repository
- [ ] Implementation Decisions cover boundaries, contracts, data, interactions,
      and rollout without becoming a code plan
- [ ] No file paths, diffs, or code snippets — except a prototype-derived shape,
      labeled as one
- [ ] Alternatives Considered names only options the conversation raised, each
      with a reason a reviewer could argue with — or says none were weighed
- [ ] Testing Decisions name observable behavior and identify prior art, or say
      none exists
- [ ] Out of Scope names something the conversation actually set aside
- [ ] Every invented assumption is in Further Notes, labeled — nothing you
      supplied yourself is presented as decided
- [ ] The project's own vocabulary is used throughout, no synonyms
- [ ] No decision here contradicts an existing ADR without saying so

This checks the document's shape. When the spec came out of a design
conversation, run the other pass too — `brainstorming`'s
`references/SPEC-REVIEW.md` measures the draft against the conversation that
produced it and catches what the document lost: a decision that was settled and
never written down, an internal contradiction, a placeholder. Shape and
completeness are different failures, and this checklist only finds the first.
