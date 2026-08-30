---
name: draft-spec
description: Turn an already-settled conversation or approved design into a formal, agent-ready spec document for triage and implementation planning. Use when asked to spec something out, write a discussion up as an issue, or formalize a design that has been agreed — including when an approved design is handed over ready to write up. Synthesizes what is already decided; not for opening a requirements interview.
argument-hint: "[feature, decision, or conversation to specify]"
---

# Draft spec

Write down a decision that has already been made, in a form another person or agent can implement without coming back to ask. This skill is synthesis, not an interview: everything it writes should be traceable to the conversation, the repository, or an explicit assumption it labels as one.

Subject: `$ARGUMENTS` — when the conversation settled several things, this names which one to write up. Empty means the conversation itself is the subject.

## When to use this skill

- The design is agreed and the user wants it in writing — a spec, an issue body, a ticket description a contractor or agent can pick up
- An upstream design conversation has produced an approved design that now needs formalizing
- A decision has to survive a handoff: to someone else, to an unattended agent, or to the user's own future self
- Not while the change is in flight — a spec written over half-built code documents the guess rather than the decision
- Not to settle what is still open: pressure-testing a plan is `grilling`'s work, and choosing what to build at all is `brainstorming`'s
- Not for splitting work into shippable pieces (`slice`), working an item that already exists on a tracker (`triage`), or judging code against a spec that already exists (`code-review`, whose third axis is exactly that)

## Is it settled enough to write?

Run this before drafting anything. All three must hold:

1. **The outcome is stated, not implied.** You can say in one sentence what someone can do afterwards that they cannot do now, with no conditional in it.
2. **No rival option is still live.** Every "or maybe we could" in the conversation has a resolution you can point at — not a preference you would be supplying yourself.
3. **The boundary holds.** You can name something adjacent that is *out*, and the user would agree without thinking about it.

When one fails, say which, and name what is open — that sentence is more useful than a spec built over the gap. If the user wants the draft anyway after hearing it, write it, and mark every assumption you had to invent in **Further Notes** rather than letting it read as settled. Deeper ambiguity than one question can close is `grilling`'s to work through first — invoke it and let it run to a confirmed understanding, rather than opening the interview here.

## Workflow

### 1. Ground the spec in the repository

Read enough of the code to know what already exists before describing anything as new:

- The project's glossary or `CONTEXT.md` — use its vocabulary exactly, not a synonym you prefer
- Relevant ADRs — respect settled decisions, and surface a conflict rather than quietly overwriting one
- Existing behavior and similar features — never spec something the code already does
- The rejection knowledge bases — the repo's `.out-of-scope/` and `~/.agents/out-of-scope/`. A spec for something already declined needs the earlier reasoning answered, not ignored; surface the hit before drafting
- Test seams and prior art — prefer the highest seam already in use over inventing one

With no glossary, ADR, or prior art to lean on, don't manufacture a project-specific convention. New domain terms, or a vocabulary conflict the spec exposes, go to `domain-modeling` to settle in `CONTEXT.md` before drafting — a spec written in words the project hasn't agreed on gets re-litigated in review.

### 2. Confirm the frame, once

Before drafting, show the frame in a few lines and ask whether it matches: the **actors**, the **outcome** each one gets, and **where the behavior is verified**. Name seams by observable behavior, not by file — one high seam covering the user-visible contract, plus lower ones only where they expose independent behavior or make a failure diagnosable.

This is the only confirmation gate before the draft, and it is deliberately cheap: three lines the user can correct in one reply beats a 400-word spec built on a misread actor. Don't turn it into a requirements questionnaire. One targeted question is allowed when a missing answer genuinely blocks a defensible spec — ask it, and say what decision it changes.

### 3. Synthesize, don't interview

The conversation, the repository, the glossary, the ADRs, and the confirmed frame are the source of truth. Preserve uncertainty honestly: unresolved choices go in **Further Notes**, not into a confident sentence. Keep what the user wants separate from how the code will do it, and on a product-facing tracker keep the narrative in outcome language with implementer detail confined to its own section (AGENTS.md §3, *Jira vs. Pull Requests — audience separation*).

### 4. Write the spec

Use the fixed template and keep its section order: [TEMPLATE.md](references/TEMPLATE.md), which also carries what belongs in each section and the self-check to run before showing the draft.

### 5. Publish only where asked

The spec is a draft until the user has seen the exact Markdown and confirmed it. Where it goes after that — conversation, a file at a path the user named or the `docs/specs/<YYYYMMDDHHMMSS>-<kebab-slug>.md` fallback they accept, an existing tracker item, a new one — is [PUBLISHING.md](references/PUBLISHING.md). Assume no tracker, no project key, and no label vocabulary until you have read the real ones.

A user who wants the draft challenged rather than confirmed goes to `grilling`, which interviews a document claim by claim — what each one implies, where it is weak, what was weighed against it. Only when they ask for it. This is not the reopened interview [Gotchas](#gotchas) warns about: that one asks requirements questions instead of writing the spec, where this one questions a document that already exists. Running it unprompted turns synthesis back into an interview, just at the end rather than the start.

## Gotchas

- **Don't reopen the interview.** The failure mode this skill exists to avoid is answering a request to write things down with a fresh round of requirements questions. If the conversation converged, the questions are already answered; if it didn't, say so (see [Is it settled enough to write?](#is-it-settled-enough-to-write)) instead of drafting around the gap one question at a time.

- **An invented detail is indistinguishable from a decided one once it's in the document.** Actors, edge-case behavior, API shapes, schema fields, rollout plans — a spec is read as authoritative by exactly the people who weren't in the conversation. Anything you supplied yourself belongs in **Further Notes**, labeled.

- **No file paths, diffs, or code snippets.** They are stale before the first commit and they turn a spec into a plan the implementer can't argue with. The single exception is a compact type, state machine, reducer, or payload shape when the shape *is* the decision — include only the decision-rich part, and say it came from a prototype.

- **The spec fixes what to build, never how it splits into pull requests.** Decomposition into PRs is settled later, once the code makes the real boundaries visible; deciding it here freezes a guess about the codebase into a document people treat as agreed. When the spec reveals several independently shippable pieces, hand them to `slice` rather than sequencing them inline.

- **Never invent tracker vocabulary.** No assumed project key, label name, workflow status, or `ready-for-agent` decision. Those are real state in someone else's system — resolve them against the tracker, and never apply a label or close an item merely because the spec says so.

- **A spec is not an ADR, and doesn't replace one.** A decision that is hard to reverse and surprising without context needs its own record that outlives this document (AGENTS.md §7, *Engineering leverage & judgment*) — that's `domain-modeling`'s. Cite it from the spec; don't bury it here.

- **Rollout constraints belong in the spec, not in the implementer's head.** A behavior change that ships behind a default-off flag, or a migration that has to stay backward-compatible, is a requirement (AGENTS.md §5, *Safe rollout, feature flags & migrations*) — write it into **Implementation Decisions** where review can see it.

## Tone

Precise, collaborative, and honest about uncertainty. The goal is a spec that survives handoff into a codebase that keeps changing — not paperwork that makes an underspecified request look complete.

## References

Read these as needed for the task in hand, not both upfront.

- [TEMPLATE.md](references/TEMPLATE.md) — the spec template, what each section holds, and the self-check before showing a draft
- [PUBLISHING.md](references/PUBLISHING.md) — where a finished spec goes, tracker handoff, and shipping the spec as its own pull request

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-spec) - to-spec, MIT
- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
