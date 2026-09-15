---
paths:
  - "**/*.prisma"
  - "**/db/migrate/**/*.rb"
  - "**/db/schema.rb"
  - "**/db/structure.sql"
  - "**/prisma/schema.md"
  - "**/db/schema.md"
---

# Schema reference documents

A schema reference is the prose companion beside a machine-readable schema — `prisma/schema.md` beside `schema.prisma`, or whatever a repository names its equivalent — recording what each model is *for*. The schema states shape and states intent nowhere; that gap is the whole reason the document exists. Migration mechanics are in `rails-migration.md`.

**Nothing below is imposed.** The shape is worth offering, not applying. Match the document you find, keep your own change from making it wrong, and where the document disagrees with the standard, say so once and let the owner decide. Most repositories belong to other people, and a document silently converted to someone else's format is worse than an inconsistent one.

- **The document existing is how a repository opts in.** Where there is none this rule is inert: don't create one, don't offer to generate one from the schema, and don't scatter the prose it would have held into schema comments instead.
- **Keep your own change from making it wrong.** A model you added, renamed, or dropped belongs in the document in the same commit, written in the shape the document already uses — not the shape below.
- **Offer the rest; don't apply it.** Where the document drifts from the standard, surface it as a finding with the cost attached and stop there. Restructuring a schema reference is its own change, and it needs a yes.

The standard worth offering:

- **Named sections, not numbered ones.** `## Identity and auth`, not `### 1. Identity and auth layer`. Numbering encodes the order sections were written and breaks every anchor the moment one is inserted.
- **The same five parts in every section, in order**: purpose (including what the section is *not*), models, invariants, integration, and what to review when changing it — omitting a part only where it is genuinely empty.
- **Model coverage in both directions.** Every model in the schema named in the document, and nothing named that the schema no longer has. Both drift in silence: a whole subsystem can go undocumented while the document still reads as complete.
- **Intent and invariants, not runtime behavior.** What a model is for, what must stay true of it (constraints, uniqueness, which table is the source of truth), and which models it composes rather than reproduces. Route behavior, filter ordering, and scoring rules belong to the API's own docs and go stale here within a sprint.
- **Sections budgeted against their neighbors.** One that outgrows the rest is usually carrying an investigation; that belongs in `lore/` or an ADR, linked. The document earns its place only while it still fits in a working context.
- **Undated prose.** Sprint numbers, "as of", and "currently" turn a reference into a changelog nobody trusts. Git already holds the history.

Restructuring a document that has drifted, deciding which models earn prose over a table row, and adding a coverage check are in the `schema-reference` skill.
