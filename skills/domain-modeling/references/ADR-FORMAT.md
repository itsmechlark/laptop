# The ADR format

ADRs live in `docs/adr/`, numbered sequentially: `0001-slug.md`, `0002-slug.md`. Scan the directory for the highest number and increment — and in `~/.agents/adr/`, scan **only the files carrying this repository's prefix**, since that directory holds several projects and the highest number in it usually belongs to someone else.

**Creating `docs/adr/` is the repository's call, not this skill's.** Where the directory exists, write there. Where it doesn't, say so and ask — an ADR is the one artifact here written entirely for other people, and one filed outside the repository is a decision the team cannot read, which is not a recorded decision. Offer both: adopting `docs/adr/` in this repo, or `~/.agents/adr/` as your own record until they do. A global ADR carries `metadata.repo` (the repository's name) and is filed as `~/.agents/adr/<repo>-NNNN-slug.md`. The prefix is load-bearing: numbering stays per-repository, so the file can be moved into `docs/adr/` later by dropping the prefix, but one flat directory would otherwise hold two different `0001` — and the number is an address, which the next section says may never be shared.

The number is an address, so two ADRs may never share one. Two branches open at once will each scan the same directory and claim the same next number, and the collision is invisible until both land — after which every `ADR NNNN` citation in the repo points at two files. Renumber on rebase, before merge, fixing the inbound references in the same commit.

When a duplicate reaches the main branch anyway, the later of the two moves to the next free number rather than a recycled one, taking its references with it. It then sits out of chronological order, which is the price of treating the number as an address rather than a date. Otherwise a merged number is spent: never reuse it, not even for an ADR that turned out wrong.

## Template

```markdown
---
name: event-sourced-orders
description: Why order history comes for free and every read path can lag.
metadata:
  status: accepted
  topic: order-history
  repo: billing-api     # only in ~/.agents/adr/ — omit in a repo's own docs/adr/
---

# Event-sourced write model for orders

**Context:** Orders are amended repeatedly before dispatch and the support team
needs to answer "what did this order look like on Tuesday?"

**Decision:** The write model is event-sourced; the read model is projected into
Postgres.

**Consequences:** Full history comes for free, but every read path now depends on
a projection that can lag, and schema changes mean replaying.

**Rejected:** A mutable orders table with an audit trigger — cheaper, but the
audit rows can't reconstruct intermediate states.

**Evidence:** `app/models/order/`, `db/migrate/20260112_add_order_events.rb`,
`docs/guides/order-history.md`
```

Context, decision, and consequences are the record; **Rejected** and **Evidence** are additions that earn their place case by case. One to three sentences each, and a single paragraph covering the first three is fine when that reads better. The value is in recording *that* a decision was made and *why*, not in filling out a form. Context → decision → consequences, plus the alternatives you rejected and why, is the house shape (AGENTS.md §7).

Drop **Rejected** when there was no real alternative worth remembering.

## Frontmatter

Three keys, the same shape a spec, a plan, and a lore note carry, so one artifact leads to the next by `metadata.topic` rather than by grep.

| Field | Purpose |
| --- | --- |
| `name` | The decision's stable slug. Deliberately **not** the filename: the number is an address that a rebase can force you to change, and `name` is what survives renumbering |
| `description` | Required, and short: one line, under 120 characters, no wrapping. Say when a reader should open this ADR — the title already says what it decided |
| `metadata.status` | `proposed` · `accepted` · `deprecated` · `superseded` |
| `metadata.topic` | Kebab-case join key, shared with the spec, plan, and lore notes for the same work |
| `metadata.supersedes` | The ADR number this one replaces, when it replaces one |
| `metadata.repo` | The repository's name — `billing-api`, not a path and not an owner-qualified slug like `acme/web`. Required in `~/.agents/adr/`, where one flat directory holds several projects' numbering; omitted in a repo's own `docs/adr/` |
| `metadata.superseded-by` | The ADR number that replaced this one, added when it happens. Flipping `status` and adding this is the only *decision-bearing* edit an accepted ADR takes — correcting the record is separate, and covered below |

**The directory's existing convention wins.** Read `docs/adr/` before writing. Where the ADRs there carry no frontmatter, or a different shape, match them and say so rather than leaving one directory with two conventions and no way to tell which a reader should follow. Adopting the block in a directory that predates it is a deliberate migration — and it is not one you can make, because an accepted ADR is never edited to match a later convention. The block starts at the first ADR written after the change; the ones before it stay as written.

## Evidence

**Evidence** is the only section that points outward: where the decision actually lives. Add it when the decision is spread across places nobody would connect by grep — a schema, a middleware, a migration, and the guide that explains them. Skip it when the decision lives in one module the title already names; a list of one is noise.

Anchor it on directories and long-lived files, never line numbers. A rotted path is worse than no path, because a reader trusts it just long enough to conclude the decision was abandoned. Where a path has moved, updating it is editing the *record*, not the decision — do it, and don't open a new number for it. A superseded ADR is the exception: its Evidence freezes with the rest of the file, because it documents where the decision lived while it held.

Evidence is not a file inventory. It names the load-bearing paths a reader would otherwise have to discover, and stops.

## Where the file goes

With a single context, one `docs/adr/` at the repo root takes everything. With several, the question is whose decision it is: a choice that binds more than one context — how they integrate, a shared technology, a system-wide constraint — belongs in the root `docs/adr/`; a choice nobody outside one context can observe belongs in that context's own `docs/adr/`. When it's genuinely both, write it at the root; a decision found too high costs a reader one hop, and one found too low is never found at all.

## Reversing a decision

**Never edit an accepted ADR to hold the new decision.** The directory's value is the trail — a reader arrives wanting to know what was believed at the time, and rewriting the file in place deletes exactly that.

Instead: write a new ADR at the next number, record the old number in the new one's `metadata.supersedes`, state in its **Context** which ADR it replaces and what changed since, and mark the old one superseded. Where the old ADR carries frontmatter, that is `status: superseded` plus `superseded-by: NNNN`; where it predates the convention, a one-line note under its title does the same job — adding a block to it would be restructuring a record that is supposed to be frozen. The old file otherwise stays as written, wrong conclusion and all.

Correcting a typo, tightening a sentence, or adding a consequence you'd missed is editing the *record*, not the decision — that's fine, and doesn't need a new number.

## When a decision earns an ADR

All three must hold:

1. **Hard to reverse** — changing your mind later carries a meaningful cost.
2. **Surprising without context** — a future reader will look at the code and wonder why on earth it was done this way.
3. **The result of a real trade-off** — there were genuine alternatives and one was picked for specific reasons.

If it's easy to reverse, skip it — you'll just reverse it. If it isn't surprising, nobody will wonder. If there was no alternative, there's nothing to record beyond "we did the obvious thing."

## What qualifies

- **Architectural shape.** "This is a monorepo." "The write model is event-sourced, the read model is projected."
- **Integration patterns between contexts.** "Ordering and Billing talk over domain events, not synchronous HTTP."
- **Technology choices that carry lock-in.** Database, message bus, auth provider, deployment target. Not every library — the ones that would take a quarter to swap.
- **Boundary and scope decisions.** "Customer data is owned by the Customer context; everyone else references it by ID." The explicit *no*s are worth as much as the *yes*es.
- **Deliberate deviations from the obvious path.** "Hand-written SQL instead of the ORM, because X." Anything a reasonable reader would assume the opposite of — this is what stops the next engineer from "fixing" something intentional.
- **Constraints invisible in the code.** "No AWS, for compliance." "Under 200ms, because of the partner API contract."
- **Rejected alternatives whose rejection was subtle.** If GraphQL lost to REST for non-obvious reasons, write it down or it comes back in six months.

## What doesn't

Anything reversible in an afternoon, anything the code already explains, and anything that was never a choice. An ADR directory full of obvious decisions is a directory nobody reads.
