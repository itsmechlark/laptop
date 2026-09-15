---
name: schema-reference
description: Write, restructure, and drift-check the prose companion beside a database schema — the `prisma/schema.md` or `db/schema.md` that records what each model is for. Use when asked to standardize, reorganize, or clean up a schema reference or schema design doc, when one has drifted out of sync with the schema it documents, when sections have grown uneven or are numbered in commit order, when deciding what belongs in the schema doc versus the API docs or an ADR, or when adding a check that every model in the schema is documented. Not for designing the schema itself and not for writing migrations.
argument-hint: "[path to the schema reference, or the repo to check]"
---

# Schema reference documents

A schema reference explains **what each model is for**. The schema file beside it already states shape — columns, types, relations — and states intent nowhere. That division is the whole reason the document exists, and nearly every way these documents fail is a drift across it.

Target: `$ARGUMENTS`. Empty means find it — `prisma/schema.md`, `db/schema.md`, or whatever the repo's own context files name as its schema reference.

The standing conventions are in the `schema-reference` rule, which loads whenever a schema file is open. This skill is the work the rule is too short to carry: restructuring a document that has already drifted, and offering a check that keeps it honest afterwards.

**The rule offers the shape; it never imposes it.** Inside this skill someone has asked, so the restructure is on the table — but the document belongs to whoever maintains it, and a large one is a real diff. Present the findings and the plan before rewriting anything.

## When to use this skill

- Standardizing, reorganizing, or cleaning up a schema reference document
- The document has drifted — models missing, models documented that no longer exist, sections at wildly different depths
- Sections are numbered in the order they were written and the numbering is now in the way
- Deciding whether something belongs in the schema doc, the API docs, an ADR, or `lore/`
- Adding a check that every model in the schema is documented
- Not for designing the schema or choosing a model's shape — that is `codebase-design`, and `domain-modeling` for the vocabulary
- Not for writing the migration that lands a schema change
- Not for recording *why* a schema decision was made against the alternatives — that is an ADR, via `domain-modeling`
- Not for what an investigation into the schema turned up — that is `lore`

## The gate

**The document existing is how a repository opts in.** Check before anything else, from the repository root — these live under a package in a monorepo, so a bare `ls` at the root finds nothing and would read as "no document" when there is one:

```sh
find -L . -name node_modules -prune -o -name 'schema.md' -print
```

`find -L` because a pnpm or yarn workspace tree is largely symlinks, and plain `find` walks straight past them. If that comes back empty, check the repo's own `CONTEXT.md` or `AGENTS.md` for a document under a name this doesn't match before concluding there is none.

Where there is none, say so and stop. Do not create one, do not propose one as a side effect of another task, and do not offer to seed it from the schema — a reference generated from the schema restates shape, which is the one thing the schema already says. These documents are worth having only where someone chose to keep one.

## Workflow

### 1. Inventory before editing

Two lists, both mechanical, and the diff between them is most of the work. Set both paths from what the gate found, so this works from the repository root:

```sh
DOC=packages/postgres/prisma/schema.md      # whatever the gate returned
SCHEMA=packages/postgres/prisma/schema.prisma

# models the schema has (Prisma)
grep -oE '^model [A-Za-z0-9_]+' "$SCHEMA" | sed -E 's/^model +//' | sort

# models the document names
grep -oE '`[A-Z][A-Za-z0-9_]+`' "$DOC" | tr -d '`' | sort -u
```

For Rails, read model names from `db/schema.rb`'s `create_table` calls instead — the schema dump rather than `app/models`, so a table with no class still counts. Report both directions — models the schema has and the document doesn't, and names the document carries that the schema has dropped. An undocumented subsystem is the common finding, and it is invisible from inside the document, which reads as complete either way.

### 2. Settle the section list

Sections are domains, not chapters: what the models are collectively *for*. Draft the list named rather than numbered; where the document numbers its sections today, renaming them is part of what step 3 puts up for a decision, not something to slip in alongside a content fix.

Every model in the schema belongs to exactly one section. A model that seems to belong to two usually means the sections are cut wrong.

### 3. Put the plan up before touching the document

Steps 1 and 2 cost nothing and are reversible; step 4 rewrites a document someone else maintains. Show what you found — models missing in each direction, sections to rename, material that should move out — and what the restructure would cost, then get a yes.

Where the answer is no, or only part of it lands, that is a result: the inventory from step 1 is worth having on its own, and a repository that keeps its numbering is keeping a convention it chose.

### 4. Rewrite each section against the template

[templates/section.md](templates/section.md) is the five-part scaffold — purpose, models, invariants, integration, when changing. Copy it per section and fill it in. Omit a part only where it is genuinely empty; never reorder them, because the point of a fixed shape is that a reader learns it once.

Two judgment calls recur:

**Which models earn prose.** A table row — model, one-line intent, source-of-truth note — is the default and is enough for most models. Promote one to its own `####` heading only when it carries an invariant a reader will otherwise violate: a denormalized counter that isn't authoritative, a soft-delete that preserves audit history, a read model that must never decide authorization. Schemas run to a hundred-plus models and a document with a hundred headings is an index, not a reference.

**What is out of scope.** Route behavior, filter ordering, recommendation scoring, and "as of Sprint N" notes are not schema intent. They belong to the API's own docs, an ADR, or `lore/`. This is where these documents put on most of their weight — move the material out and link it rather than deleting it.

### 5. Offer a coverage check

A convention written into a document is advisory, and the restructure decays from the day it lands. A check is what makes the document's claims true — but it is a second change, against the repo's own tooling, and it gets its own yes. [references/DRIFT-CHECK.md](references/DRIFT-CHECK.md) covers what is worth asserting, how to read model names out of Prisma or `db/schema.rb`, where it would wire in, and why the structural assertions cannot land ahead of the restructure.

### 6. Report

Name what moved and what it cost: sections renamed, models newly documented, material relocated to `lore/` or an ADR, and anything left undocumented on purpose. Where the restructure changed only the document and not the schema, say that plainly — it is a documentation change, and it should read as one in the commit.
