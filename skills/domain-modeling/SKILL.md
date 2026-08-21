---
name: domain-modeling
description: Build and sharpen a project's domain model while designing — challenge fuzzy terms, invent edge-case scenarios, and write the glossary and architectural decisions down the moment they hold still. Use when pinning down domain terminology or a ubiquitous language, recording an ADR, or when another skill needs the domain model maintained.
argument-hint: "[topic, term, or decision to model]"
---

# Domain modeling

Sharpen what the project's words mean *while* the design is being decided, and write each term and each durable decision down the moment it holds still.

## When to use this skill

- One word is carrying two meanings, or two words are carrying one
- A term needs settling before anyone can implement against it
- The code's vocabulary and the team's vocabulary have drifted apart
- A decision has just been made that a future reader would find surprising
- Another skill needs the domain model maintained as it works

Not for reading `CONTEXT.md` to pick up existing vocabulary — that's a habit every skill should already have, and it needs no skill loaded. Not for deciding where code should live once the words are settled: a misplaced module boundary is `codebase-design`'s, and renaming identifiers to match a settled term is `tdd`'s.

## Glossary

Use these terms exactly — this skill exists because one word meaning two things is expensive.

**Term** — a word the domain uses for one of its concepts, and whose meaning the project has committed to. Not every noun in the codebase: only the ones a reader could get wrong. _Avoid_: keyword, label.

**Context** — a region of the system inside which each term has exactly one meaning. Two contexts may use the same word for different things, which is legal as long as each one's glossary says what it means locally. _Avoid_: module, service. A context bounds *meaning*; `codebase-design`'s **seam** bounds *change*, and the two need not coincide.

**Glossary** — the `## Language` section of a `CONTEXT.md`: one context's terms, each with a definition and its rejected synonyms.

**Context map** — the root `CONTEXT-MAP.md`: which contexts exist, where each glossary lives, and how they relate. Present only when there is more than one context.

**Decision record (ADR)** — a numbered file under `docs/adr/` recording one decision, why it was made, and what it costs.

## Locate the context first

Before writing a term anywhere, work out which glossary owns it. This is the step that gets skipped, and it is three checks:

1. **`CONTEXT-MAP.md` at the root?** Read it, then pick the context the topic belongs to.
2. **Only a root `CONTEXT.md`, or neither?** Single context — the root file is the glossary. Create it when the first term is settled, not before.
3. **Several contexts and the owner isn't obvious?** Ask. A term filed in the wrong context is worse than a term left out: it will be read as authoritative by exactly the people it misleads.

Where these files sit, and what a map contains: [CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md).

## Sharpening the model

Open-ended work, so these are criteria rather than an order to follow.

**Challenge terms against the glossary.** When a term contradicts what `CONTEXT.md` already says, say so immediately: *"Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"*

**Sharpen fuzzy language.** When a word is vague or carrying two meanings at once, propose a precise one: *"You're saying 'account' — do you mean the Customer or the User? Those are different things."*

**Stress-test with concrete scenarios.** Invent specific cases that force a decision about where one concept ends and the next begins. Six probes, roughly in order of how often they find something:

- **Identity** — are these two the same one? What makes them the same? (*"Is a 'table' the physical table or the seating assignment?"*)
- **Partial** — can half of it happen? What is the half called?
- **Lifecycle** — does it exist before X? Does it survive Y? What is it called in between?
- **Cardinality** — zero, one, or many? Is "none" a thing or an absence?
- **Time** — what did it look like on Tuesday? Does the superseded value still exist?
- **Authority** — who may change it, and what happens to the previous state?

A relationship that survives a scenario is real; one that doesn't was wishful.

**Cross-reference with the code.** When the user states how something works, check whether the code agrees, and surface the contradiction: *"The code cancels whole Orders, but you just said partial cancellation is possible — which is right?"*

**Write a settled term down inline.** A term is settled when all three hold: it has been used twice without hedging, no rival candidate is still in play, and you can state its boundary against its nearest neighbour. Then update `CONTEXT.md` immediately — don't batch, because a batch is a thing you forget. Keep it a glossary: no implementation detail, no spec, no scratch pad ([CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md)).

**Offer ADRs sparingly.** Only when all three hold — hard to reverse, surprising without context, and the result of a real trade-off. If any is missing, skip it. When one qualifies, write it per [ADR-FORMAT.md](references/ADR-FORMAT.md); that is also the house rule (AGENTS.md §7 — durable decisions belong in an ADR, not buried in a PR description that rots).

**Be pedantic about words.** Two people using the same term for two different things is the failure this skill exists to catch, and catching it is worth interrupting for.

## Gotchas

- **`CONTEXT.md` here always means the project's glossary.** The root context map that the global standards have you read at session start — `~/.agents/CONTEXT.md`, symlinked into each client's config directory — is a different file with a different format. It maps the machine and its repos, holds no domain terms, and isn't version-controlled. Never write a term into it, and never write through the home symlink; edit the project's own `CONTEXT.md`, at the repo root or in its context's directory.

- **A term the code doesn't use is fiction.** Settling on a word obliges one of two follow-ups: rename the identifiers to match, or record the code's word under `_Avoid_` and accept the gap deliberately. Renaming is a behavior-preserving change — hand it to `tdd` rather than doing it from here. Silence is the one option that isn't available: a glossary that disagrees with the code teaches the next reader the wrong thing, twice.

- **Delete terms when they die.** A concept that leaves the code leaves the glossary in the same commit. A glossary is trusted in proportion to how current it is, and an entry for something that no longer exists costs more than a missing one.

- **Never rewrite an accepted ADR to hold a new decision.** Write the new one and mark the old superseded — the value of the directory is the trail, and editing in place erases exactly the reasoning a future reader came for.

- **A glossary is not a design.** Settling the word "reservation" does not settle where reservation code lives. Hand the second question over rather than answering it here.

## Where the session leads next

Settling vocabulary regularly exposes work this skill doesn't do. Hand it over rather than absorbing it:

- A module boundary that turns out to be wrong — a secret sitting behind the wrong interface — goes to `codebase-design` to place the seam.
- Renaming code to match a settled term goes to `tdd`, which keeps the change behavior-preserving.
- A feature the discussion reveals needs a full specification before anyone implements it goes to `draft-spec`.

Leaving with a sharper glossary and a named next step is a complete outcome.

## References

Read these as needed for the task in hand, not both upfront.

- [CONTEXT-FORMAT.md](references/CONTEXT-FORMAT.md) — what belongs in `CONTEXT.md`, where it and the context map live, and how to write both
- [ADR-FORMAT.md](references/ADR-FORMAT.md) — the ADR template, numbering, which `docs/adr/` a decision belongs in, supersession, and what earns one

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling) - domain-modeling, MIT
- Eric Evans, *Domain-Driven Design* — ubiquitous language, bounded context, context map
- Michael Nygard, [Documenting Architecture Decisions](https://www.cognitect.com/blog/2011/11/15/documenting-architecture-decisions) — the context/decision/consequences shape
