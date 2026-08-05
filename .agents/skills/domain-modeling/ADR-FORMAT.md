# The ADR format

ADRs live in `docs/adr/`, numbered sequentially: `0001-slug.md`, `0002-slug.md`. Scan the directory for the highest number and increment. Create `docs/adr/` lazily — only when the first ADR is warranted.

## Template

```markdown
# Event-sourced write model for orders

**Context:** Orders are amended repeatedly before dispatch and the support team
needs to answer "what did this order look like on Tuesday?"

**Decision:** The write model is event-sourced; the read model is projected into
Postgres.

**Consequences:** Full history comes for free, but every read path now depends on
a projection that can lag, and schema changes mean replaying.

**Rejected:** A mutable orders table with an audit trigger — cheaper, but the
audit rows can't reconstruct intermediate states.
```

Three to four short sections, one to three sentences each — a single paragraph covering all of them is fine when that reads better. The value is in recording *that* a decision was made and *why*, not in filling out a form. Context → decision → consequences, plus the alternatives you rejected and why, is the house shape (AGENTS.md §7).

Drop **Rejected** when there was no real alternative worth remembering. Add `status:` frontmatter (`proposed | accepted | deprecated | superseded by ADR-NNNN`) only in a repo where decisions get revisited often enough to need it.

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
