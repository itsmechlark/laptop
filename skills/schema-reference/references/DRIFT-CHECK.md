# Drift-checking a schema reference

A convention written into a document is advisory. The document that says "every
model is documented here" is the same document that is missing six models, and
it reads identically either way. A check is what makes the claim true.

This is a proposal to put to whoever maintains the repository, not something to
add on your own initiative. It changes what CI fails on, which is the repo
owner's call — and a check nobody agreed to is a check somebody disables.

## What is worth asserting

Split by whether a script can decide it from the files alone. Deterministic and
file-local goes in the check; anything needing judgment about prose stays out,
because a check people learn to override is worse than no check.

| Assertion | Why it holds |
| --- | --- |
| Every model in the schema is named in the document | The drift that actually happens, and the one nobody sees |
| Every model named in the document still exists in the schema | Catches deletions; stale names read as current |
| No numbered section headings | Keeps write-order numbering from coming back |
| Each section carries the five parts, in order | Only after the restructure — see below |
| Section length against a budget | Catches an investigation being pasted into a reference |

Leave alone: whether a section's prose is any good, whether an invariant is
correctly stated, whether a model was filed under the right domain. Those need a
reader.

## Reading the two lists

Prisma — models are declarations, so the schema side is exact:

```sh
grep -oE '^model [A-Za-z0-9_]+' schema.prisma | sed -E 's/^model +//' | sort -u
```

Rails — read `db/schema.rb`, not the models directory, so the check does not
depend on every table having a class:

```sh
grep -oE '^  create_table "[a-z0-9_]+"' db/schema.rb | cut -d'"' -f2 | sort -u
```

The document side is the same either way: backticked identifiers, deduplicated.

```sh
grep -oE '`[A-Za-z][A-Za-z0-9_]*`' schema.md | tr -d '`' | sort -u
```

All three paths are repo-relative; in a monorepo they sit under a package, so
resolve them from the repository root rather than assuming a working directory.

Two cautions on the document side. Match against the schema's own naming (Rails
tables are snake_case in `schema.rb` and CamelCase in the model layer — pick one
and normalize both sides to it). And a bare `grep` counts a model named only
inside a "do not confuse with" aside as documented, so the check passes on a
model nobody actually wrote up. That is worth accepting in a first pass —
restricting the match to headings and table rows is a reasonable second one,
once the document is in a shape where that distinction is real.

## Models that earn no prose

Some models genuinely don't warrant a write-up — join tables, framework-owned
session or cache tables, a generated audit mirror. A check with no way to say so
forces one of two bad outcomes: it fails forever, or someone pads the document
with rows that say nothing.

Give it an explicit exclusion list, in the check itself rather than in the
document, with a one-line reason per entry. Keeping it in the check makes the
list reviewable in a diff and keeps the document free of apologies for what it
omits. A list that starts growing every time the check fails has stopped being
an exclusion list and is worth reading as a signal the document has fallen
behind.

## Where it goes

Wire it into the check task the repo already runs, not a standalone script
someone has to remember:

- npm/pnpm — a `check:*` script, where the root `check` fans out across them
- Rails — a Rake task the default task depends on
- Anything else — whatever CI runs on every pull request

The check belongs to the repo it guards, not to this skill. Write it in that
repo's language, match the surrounding tooling, and let its output name the
missing models rather than just failing a count.

## Sequencing

Model coverage can land immediately — it asserts something true of the document
as it stands, or true once a handful of models are written up.

The structural assertions cannot. A document that has not been restructured yet
fails all of them on every section, which means landing them first produces a
red check that everyone learns to ignore, and that is worse than leaving it
unchecked. Either restructure first and add them after, or add them in the same
change as the restructure.
