# The CONTEXT.md format

`CONTEXT.md` is a glossary. It says what the project's words mean, and nothing else.

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

**Group under subheadings** when natural clusters emerge. A flat list is fine while the terms all belong to one cohesive area.

## Single vs. multiple contexts

**Single context** — the common case. One `CONTEXT.md` at the repo root.

**Multiple contexts** — a `CONTEXT-MAP.md` at the root lists them, says where each lives, and describes how they relate:

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

Infer which structure applies before writing:

- `CONTEXT-MAP.md` exists → read it to find the contexts.
- Only a root `CONTEXT.md` → single context.
- Neither → single context; create the root `CONTEXT.md` when the first term is settled.

With multiple contexts, work out which one the current topic belongs to. If that isn't clear, ask — putting a term in the wrong context is worse than leaving it out.
