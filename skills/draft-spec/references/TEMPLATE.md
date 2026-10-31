# The spec template

Section order is fixed. Every section appears, even when the honest content is
one line — a missing section reads as an oversight, and a reader can't tell
"nothing is out of scope" from "nobody thought about scope". The exception is
**Known Gaps** and **Deferred**, which appear only when the conversation
produced something for them: a gap written to fill the heading is an invented
requirement, and an empty heading costs the reader a stop. A spec with a parent
slice in a local slice list carries neither — its entries go in that list, as set out under
[Known Gaps and Deferred in a slice's spec](#known-gaps-and-deferred-in-a-slices-spec).

```markdown
---
name: <the slice, kebab-case>
description: <one line, under 120 characters — when a reader should open this>
metadata:
  status: draft
  topic: <the join key, same as the PRD and slice list this came from>
  part-of: <the parent document, type-qualified: slice/<list-name>#<id>, or spec/<index-name> — omit for a standalone spec>
  tickets: []
  adrs: []
  # supersedes: [spec/old-name, prd/old-name]   # omit when not superseding; type-qualified slugs
  repo: <the repository's name — only in ~/.agents/specs/; delete this line in a repo's own docs/specs/>
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
- The load the design was sized against, and what breaks first beyond it

When a decision section covers several distinct areas (monolith, a frontend, an
API contract, rollout), name each with a `### Sub-section` heading rather than a
standalone bold line. A sub-section heading is discoverable and renders as
structure; a standalone bold line is decoration.

## Alternatives Considered

- **Name of the option**: why it was declined — cost, technical complexity, or
  extensibility for a phase already anticipated.

When nothing was weighed, say so in one sentence rather than leaving the section
empty.

## Testing Decisions

- Which boundaries get tested, and why those
- The happy path, edge cases, failure states, authorization boundaries, and
  compatibility cases that matter
- Prior art: the test types, helpers, fixtures, or conventions already used here

When testing spans multiple engines or repos, name each with a `### Engine`
heading so prior art and cases stay co-located with the boundary they cover.

## Out of Scope

What this spec explicitly does not cover, including adjacent slices that must
not be pulled into the implementation.

## Known Gaps

<optional — omit the heading when there are none, and when part-of names a slice in a local list: those entries go in that list>

- <what a user or operator can still hit, and why it ships anyway>
  Addressed by: <spec/name, or slice/list-name#id — only once something outside this spec handles it>

## Deferred

<optional — omit the heading when there are none, and when part-of names a slice in a local list: those entries go in that list>

- <what is wanted, and why not now>
  Addressed by: <same forms>

## Further Notes

Assumptions, unresolved questions, dependencies, and rollout notes a future
implementer needs.
```

## The frontmatter

Three keys, the same block a PRD, a plan, an ADR, and a lore note carry.
`metadata.topic` is what threads them: a spec inherits it from the PRD or slice
list it came from, and the plan written under this spec repeats it.

The two keys answer different questions, and neither stands in for the other.

- **`topic`** is a cluster key: "show me everything about this work." It is a
  bare kebab-case word, not a pointer to any document, chosen once at the PRD or
  slice list and copied unchanged by every artifact under it — PRD, slice list,
  specs, plans, lore, ADRs. It is the only key that finds them across types.
- **`part-of`** is a parent pointer: "which document do I sit under." It is a
  type-qualified slug with one value, the nearest parent. A spec written for one
  slice of a list points at that slice, `slice/<list-name>#<id>`; a spec that is
  one member of an index spec points at the index, `spec/<index-name>`; a
  standalone spec omits it. It never names the whole slice list when a slice is
  the parent, and it never repeats `topic`.

A link is a locator and nothing else, in frontmatter and in the body. Say what
this spec changes about its parent in Problem Statement and Solution, where it
can be read without the parent — never in a clause after a pointer, and never as
a paragraph explaining the parent's labels to a cold reader. The slice ID in
`part-of` is that explanation.

When the spec is filed as a local file, add `Spec: <name>` to the parent slice's
entry in the slice list, with nothing after it — in the same write the user
confirmed, and named in that confirmation ([PUBLISHING.md](PUBLISHING.md)). A
slice list with no IDs gets them added first, as that edit's only other change;
never cite the whole list as the parent, and never invent an ID the list does
not carry. Keep the dependency and merge order
between members in the index's slice table and the slice list's `Shares files
with:`, not copied into each child's frontmatter, where it goes stale the first
time the set is re-cut.

`metadata.status` moves through the lifecycle every planning artifact shares:
`draft` (written, not yet agreed) → `accepted` (agreed; implementation may
start) → `done` (the work it describes has shipped), with `superseded` for one
a successor replaces.

When superseding, the successor lists each predecessor in `metadata.supersedes`
as a type-qualified slug: `spec/old-name`, `prd/old-name`, `plan/old-name`, or
`slice/old-name`. The field is a list even for a single entry — omit the key
entirely when not superseding. Cross-type entries are allowed: a spec may
supersede a PRD when the spec absorbs its product framing.

On the **superseded** document, add two frontmatter fields reactively (not in
the template — they are added when the document is replaced, never upfront):

```yaml
status: superseded
superseded-by: spec/new-name   # type-qualified slug of the successor
```

The body is frozen from that point; only the frontmatter changes. The two
documents update in the same commit.

Supersede rather than edit in place once the artifact is `accepted` or `done`,
or once work has started against it. While still `draft` with no work underway,
update in place instead.

A spec is born `draft` and becomes `accepted` on confirmation — or when
`feature-dev` starts building from it; the build marks it `done` once its slice
lands. Where the spec is one slice of a set, `done` is that slice shipping, and
the index spec reaches `done` only when its last member does.

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
without turning into a code plan. Where the design was sized against a load,
record the figure and what breaks first past it: a sizing pass that stays in the
conversation is one the implementer has to redo or guess at. Technical
clarifications the developer gave during the conversation belong here rather
than in the narrative, which keeps the product-facing sections readable on a
tracker (AGENTS.md §3, *Jira vs. Pull Requests — audience separation*).

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

**Known Gaps.** A limitation the spec knowingly ships with: a case that behaves
badly or not at all, which a user or operator can still reach, and why that is
acceptable for now. Write it in outcome language, because the people who have to
accept it are the product team — "invitees who sign up under a different address
land in a new account", not "the lookup keys on the original email". It has
three neighbors. Out of Scope is a boundary the spec never claimed to cover, so
nothing is missing there. Further Notes holds what is still undecided, where a
gap has been decided and accepted. And a shortfall the spec is meant to fix is a
requirement, so it belongs in the stories.

**Deferred.** Work the conversation wanted and postponed. It belongs to the
feature's intent and not to this spec's delivery. Name what, and why it waits —
a dependency, a risk, something the first release will teach. Out of Scope is
not expected to come back under this banner; Deferred is. When a deferred item is
big enough to ship alone, cutting it is `slice`'s work. If the result lands in
a different list the entry points at it; if it lands in the list that holds the
entry, the entry is removed.

**Further Notes.** Everything that is true but unresolved: assumptions you had
to invent, open questions, dependencies on other work, rollout sequencing. An
assumption recorded here is cheap to correct; the same assumption stated
confidently in the Solution is expensive.

## Known Gaps and Deferred in a slice's spec

When `part-of` names a slice in a local slice list, the spec has no Known Gaps
or Deferred section. Its entries belong to the list, tagged with the slice's ID,
so the work's shortfalls and postponements are read in one place and not
scattered across every spec written under it. Show them with the draft as the
edit they are — "adds to Known Gaps under S1 in `<path>`" — and file them with
the spec, in the same confirmed write as the `Spec:` line
([PUBLISHING.md](PUBLISHING.md)).

Where the slice list lives on a tracker it is not edited, so the spec keeps the
two sections itself and the rest of this file applies to them.

## Linking a gap or deferral to what handles it

An entry that this same spec handles is removed the moment it is written, never
left in place. A gap the stories now cover is a requirement, and a deferred item
pulled into the decisions is no longer deferred; leaving either behind makes the
spec contradict itself.

The same goes for the spec's parent slice list. An entry in that list which this
spec's slice handles is removed from the list in the edit that files the spec,
whether the entry came before the slice or with it, and it is not linked to
`spec/<name>` or to the slice. The confirmation names that removal as an edit to
the list.

An entry that something outside this spec and its parent list handles — another
spec, or a slice in a different slice list — stays and gains `Addressed by:` with a locator and nothing else:
`spec/<name>` or `slice/<list-name>#<id>`, the type-qualified slugs `part-of`
uses, or the tracker key when the user gave one. What the handler changes goes
in the handler's own Problem Statement, so no clause follows the link, and the
link runs one way only. The entry stays so the spec still shows what it shipped
without and where that went.

The line goes on only once the handler exists. An entry with no link is
unowned, which is an honest state; don't invent a handler to fill it. Adding the
line is a pointer and not a change to the decision, so an `accepted` or `done`
spec takes it without being superseded.

## Self-check before showing the draft

- [ ] `description` is one line under 120 characters, and `metadata.topic`
      matches the PRD or slice list this came from rather than being reinvented,
      with `part-of` naming the index spec when this is one slice of a set
- [ ] `metadata.status` is `draft` while unconfirmed, `accepted` once agreed
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
- [ ] Known Gaps and Deferred appear only when the conversation produced
      entries — no empty heading, no `None` — and each entry was accepted or
      postponed, not undecided (Further Notes) and not excluded (Out of Scope)
- [ ] A spec with a parent slice in a local list has neither section; its
      entries are shown as an edit to that list instead
- [ ] No entry is handled by this same spec or its parent slice list; every
      `Addressed by:` is a locator for a different document that exists, with
      nothing after it
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
Neither pass can see what only a stranger misses; that is the `cold-read` the
skill runs once this check passes.
