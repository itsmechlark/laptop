---
name: domain-modeling
description: Build and sharpen a project's domain model while designing — challenge fuzzy terms, invent edge-case scenarios, and write the glossary and architectural decisions down the moment they hold still. Use when pinning down domain terminology or a ubiquitous language, recording an ADR, or when another skill needs the domain model maintained.
argument-hint: "[topic, term, or decision to model]"
---

# Domain modeling

Build and sharpen the project's domain model *while* designing, not afterward. This is the active discipline — challenging terms, inventing the scenarios that break them, and capturing the glossary and the decisions the moment they hold still.

Reading `CONTEXT.md` for vocabulary isn't this skill; that's a habit any skill should have. This is for when the model itself is changing.

## Reference docs

- [CONTEXT-FORMAT.md](CONTEXT-FORMAT.md) — what belongs in `CONTEXT.md`, and how to write it
- [ADR-FORMAT.md](ADR-FORMAT.md) — the ADR template, numbering, and what earns one

## Where the model lives

Most repos have a single context:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

A `CONTEXT-MAP.md` at the root means there are several, and the map says where each one lives:

```
/
├── CONTEXT-MAP.md
├── docs/
│   └── adr/                    ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── CONTEXT.md
│   │   └── docs/adr/           ← decisions local to this context
│   └── billing/
│       ├── CONTEXT.md
│       └── docs/adr/
```

Create files lazily — only when there's something to put in them. No `CONTEXT.md`? Create it when the first term is settled. No `docs/adr/`? Create it when the first ADR is warranted.

## During the session

**Challenge terms against the glossary.** When a term contradicts what `CONTEXT.md` already says, say so immediately: *"Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"*

**Sharpen fuzzy language.** When a word is vague or carrying two meanings at once, propose a precise one: *"You're saying 'account' — do you mean the Customer or the User? Those are different things."*

**Stress-test with concrete scenarios.** Invent specific cases that probe the edges and force a decision about where one concept ends and the next begins. A relationship that survives a scenario is real; one that doesn't was wishful.

**Cross-reference with the code.** When the user states how something works, check whether the code agrees, and surface the contradiction: *"The code cancels whole Orders, but you just said partial cancellation is possible — which is right?"*

**Write it down inline.** The moment a term is settled, update `CONTEXT.md` ([CONTEXT-FORMAT.md](CONTEXT-FORMAT.md)). Don't batch them — a batch is a thing you forget. Keep it a glossary: no implementation detail, no spec, no scratch pad.

**Offer ADRs sparingly.** Only when all three hold — hard to reverse, surprising without context, and the result of a real trade-off. If any is missing, skip it. When one qualifies, write it per [ADR-FORMAT.md](ADR-FORMAT.md); that's also the house rule (AGENTS.md §7 — durable decisions belong in an ADR, not buried in a PR description that rots).

## Tone

Precise, and willing to be pedantic about words. Two people using the same term for two different things is the failure this skill exists to catch.

---

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (`skills/engineering/domain-modeling`, MIT).
