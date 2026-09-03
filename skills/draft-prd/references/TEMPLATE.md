# The PRD template

Section order is fixed. Cut a section only when it genuinely holds nothing —
and note that **Out of scope** and **Success measures** are never that section.
An empty one there means the boundary or the measure hasn't been agreed yet,
which is a finding to report rather than a blank to leave.

```markdown
---
name: <the outcome, kebab-case>
description: <one line, under 120 characters — when a reader should open this>
metadata:
  status: draft
  topic: <the join key every artifact under this PRD will carry>
  tickets: []
---

# <Outcome, in the user's language>

## Problem

Who is in what situation today, what it costs them, and how often. Two or
three sentences.

## Who this is for

The specific segment, role, or situation — and, where it matters, who this is
explicitly not for.

## Why now

What changed, or what this is blocking. "It's been on the list a while" is an
honest answer and belongs here if it's the true one.

## Outcome

When <situation>, <who> can <what>, so <outcome that matters to them>.

**Done when:** the observable behavior that means this is solved.

## Success measures

- <measure> — from <where it's already tracked>, moving from <today> toward
  <target>

## Out of scope

- <adjacent thing this deliberately does not cover, and why>

## Constraints

Regulatory, contractual, platform, or rollout requirements the solution has to
satisfy whatever it turns out to be. Omit when there are none.

## Open questions

- <question> — decides <what it changes>, owned by <who>

## Assumptions

Anything stated here that came from the author rather than from a person, a
document, or the product. Omit only when the answer is genuinely nothing.
```

## The frontmatter

This PRD is the top of a chain — the slice list cut from it, the specs written
for those slices, the plans under those specs, and the lore notes that follow
all carry the same `metadata.topic`. **Choose it here**, because everything
downstream copies it, and a topic chosen twice is a chain that never joins.

`description` is required and short: one line, under 120 characters, no
wrapping. It says when someone should open the PRD, not what it is titled.

Two rules bound it. **The block belongs to the file, never to the delivered
text** — a PRD published to a tracker or a wiki renders it as literal YAML under
the user's name, so strip it there. And **the output directory's existing
convention wins**: where the documents already in the destination carry a
different shape or none, match them and say so.

## What each section holds

**Title.** The outcome, in the words the affected person would use. Not a
feature name, and no Conventional Commits prefix — this is product vocabulary
(AGENTS.md §3, *Jira vs. Pull Requests — audience separation*), and the title
carries into roadmaps and release notes that engineers do not read.

**Problem.** The situation and its cost, from the perspective of whoever has
it. Two tests it has to pass: it survives deleting the proposed feature, and it
has a number or a frequency in it somewhere. "Reporting is painful" is a
complaint; "the ops lead rebuilds the same weekly report by hand every Monday
and it takes most of the morning" is a problem you could solve three different
ways.

Resist writing the cause here. A cause is a diagnosis, and a diagnosis in the
problem statement narrows the solution before anyone has looked.

**Who this is for.** A real segment — "restaurant staff on the shared iPad",
"finance, at month end" — not "users". Naming who it is *not* for is worth a
line whenever a reader might reasonably assume otherwise, because the
alternative is discovering the assumption in review.

**Why now.** Prioritization context: what changed, what this unblocks, what it
costs to wait. This is the section that stops a PRD being read as urgent by
default.

**Outcome.** One sentence in job-story form — `When <situation>, <who> can
<what>, so <outcome>` — followed by **Done when**, which states the observable
behavior rather than the work. `slice` uses the same form, so a PRD written
this way cuts cleanly.

Still approach-free at this point. If the outcome cannot be stated without
naming a screen, an endpoint, or a data model, the requirement and the design
have been written together, and the design half needs to come back out.

**Success measures.** How anyone will know afterwards. Prefer something already
instrumented; where nothing is, say that the measurement itself is part of the
work rather than quietly assuming a dashboard exists. Two or three real
measures beat six aspirational ones, and a measure that only moves up is
usually not a measure.

**Out of scope.** The section that does the work. It should name at least one
thing somebody has already suggested and that this deliberately does not
include, with the reason. If nothing comes to mind, the boundary was never
agreed — go and agree it rather than leaving the section thin.

**Constraints.** Requirements the solution must satisfy whichever approach
wins: retention rules, contractual commitments, a platform limit, a rollout
that has to stay reversible (AGENTS.md §5, *Safe rollout, feature flags &
migrations*). Where the work has an interface, accessibility belongs here —
keyboard operation, labeled controls, and error states that say what to do next
are requirements, not polish. See AGENTS.md §2, *Quality attributes (always
design for these)*.

**Open questions.** What is still genuinely undecided, each with what it
changes and who can answer it. A question with no consequence attached is
padding; a consequence with no owner never gets answered.

**Assumptions.** Everything the author supplied. This is the section that keeps
a PRD honest: the reader cannot otherwise tell an invented user segment from a
researched one, and both look equally confident on the page.

## Self-check before showing the draft

- [ ] `description` is one line under 120 characters, and `metadata.topic` is a
      key the whole chain under this PRD can carry
- [ ] The Problem survives deleting the proposed feature — something is still
      wrong for somebody
- [ ] The Problem carries a frequency, a volume, or a cost, not just an adverb
- [ ] Who this is for names a real segment, not "users"
- [ ] The Outcome is in job-story form and **Done when** is observable behavior
- [ ] Nothing in the document names a screen, an endpoint, a schema, a library,
      or a vendor — the approach is still open
- [ ] Every success measure identifies where the number comes from, or says the
      instrumentation does not exist yet
- [ ] Out of scope names something actually raised and set aside
- [ ] Accessibility appears in Constraints wherever the work has an interface
- [ ] No effort estimate, sprint, date, or team assignment anywhere
- [ ] Every open question says what it decides and who owns it
- [ ] Everything the author supplied is in Assumptions, labeled — nothing
      invented is presented as researched
- [ ] The project's own vocabulary is used throughout, no synonyms
- [ ] Nothing here re-decides something an existing ADR already settled
