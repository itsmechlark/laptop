# The CONTEXT.md format

`CONTEXT.md` is a glossary. It says what the project's words mean, and nothing else.

This is the *project's* `CONTEXT.md`, living at the repo root or inside a context's directory. The root context map at `~/.agents/CONTEXT.md` shares the filename and nothing else — it maps the machine and its repos, and no domain term belongs in it.

## Structure

```markdown
# Ordering

Receives customer orders, holds them until they're paid for, and hands them to
Fulfillment.

## Language

**Order**:
A customer's request for a set of items at an agreed price.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

**Be opinionated.** When several words exist for one concept, pick the best one and list the rest under `_Avoid_`. A glossary that accepts every synonym isn't doing its job.

**Keep definitions tight.** One or two sentences. Define what the thing *is*, not what it does.

**Only terms specific to this context.** General programming concepts — timeouts, error types, utility patterns — don't belong, however heavily the project uses them. Before adding a term, ask whether it's unique to this domain or just software. Only the former earns a line.

**No implementation detail.** Not a spec, not a scratch pad, not a home for decisions. Decisions that matter go in an ADR ([ADR-FORMAT.md](ADR-FORMAT.md)).

**Prune as you go.** When a concept leaves the code, its entry leaves the glossary — in the same commit, not in a later cleanup. A stale definition is read with the same authority as a current one.

**Group under subheadings** when natural clusters emerge. A flat list is fine while the terms all belong to one cohesive area.

## The local overlay

A `CONTEXT.local.md` sits beside the tracked `CONTEXT.md` and is never committed. It holds terms that are real but not the team's to receive: a client or project name under NDA, an internal codename, vocabulary you're trying out before proposing it, a word your own tooling uses that the repo's glossary has no business defining. `CONTEXT-MAP.local.md` does the same beside a context map. Both use the structure above, unchanged — a heading, a short description, `## Language`.

```
/
├── CONTEXT.md           ← tracked; the team's glossary
└── CONTEXT.local.md     ← git-ignored; yours
```

**Read both, tracked first.** The overlay layers over the glossary rather than replacing it, so a term defined only in the overlay is simply additional. Where both define the same term, the overlay is what you work from and the disagreement is the news: either the tracked definition has drifted, or your private one has gone stale. Say which, rather than letting the two sit side by side.

**Promotion is the user's call.** A term that has outgrown the overlay — the team now uses it, the NDA lapsed, the experiment won — moves into `CONTEXT.md` and is deleted from the overlay in the same edit. Never make that move unasked: the reason a term is local is rarely visible from the term.

**Exclude it in `.git/info/exclude`**, not in the tracked `.gitignore`:

```sh
printf '%s\n' 'CONTEXT.local.md' 'CONTEXT-MAP.local.md' \
  >> "$(git rev-parse --path-format=absolute --git-common-dir)/info/exclude"
```

That file is per-clone and untracked, which matches the scope of what it hides, and it lives in the common git dir so every linked worktree inherits it. A fleet-wide alternative is the global excludes file (`core.excludesFile`, usually `~/.config/git/ignore`) — same entries, once per machine. The tracked `.gitignore` is correct only once the team has adopted the convention and wants everyone's overlay ignored.

**A fresh worktree won't have it.** Worktrees check out tracked files only, so the overlay is missing until it is linked back to the main checkout — `git-worktree` does this in its setup step, and the `git check-ignore` gate there is why the exclude entry has to exist first.

**No local ADRs.** A decision that isn't the team's yet goes to `~/.agents/adr/<repo>-NNNN-slug.md` ([ADR-FORMAT.md](ADR-FORMAT.md)) — outside the repo, not git-ignored inside it. `SKILL.md` carries why.

## Single vs. multiple contexts

**Single context** — the common case. One `CONTEXT.md` at the repo root, and one `docs/adr/` beside it:

```
/
├── CONTEXT.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

**Multiple contexts** — a `CONTEXT-MAP.md` at the root lists them, and each context carries its own glossary and its own local decisions:

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

Create every one of these lazily — only when there is something to put in it, and for `docs/adr/` only with the repository's agreement, since creating it commits everyone who pulls the branch to a convention ([ADR-FORMAT.md](ADR-FORMAT.md)). Which `docs/adr/` a given decision belongs in is that file's question too.

The map itself says where each context lives and how they relate:

```markdown
# Context map

## Contexts

- [Ordering](./src/ordering/CONTEXT.md) — receives and tracks customer orders
- [Billing](./src/billing/CONTEXT.md) — generates invoices and processes payments
- [Fulfillment](./src/fulfillment/CONTEXT.md) — warehouse picking and shipping

## Relationships

- **Ordering → Fulfillment** — Ordering emits `OrderPlaced`; Fulfillment consumes it to start picking
- **Fulfillment → Billing** — Fulfillment emits `ShipmentDispatched`; Billing consumes it to invoice
- **Ordering ↔ Billing** — shared types for `CustomerId` and `Money`
```

Which structure applies, and which context owns the topic, is settled before you write — `SKILL.md` has the rule. What belongs *here* is the map's own content: one line per context saying what it's for, then the relationships between them.

Keep the relationships in terms of what crosses the line — an event, a shared type, a synchronous call. A relationship described only as "Ordering uses Billing" tells a reader nothing they couldn't guess, and hides the thing that matters: which direction the dependency runs and what is coupled by it. Where the *code* seam for that relationship belongs is `codebase-design`'s question, not this file's.
