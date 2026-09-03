# Kinds, frontmatter, and finding a note again

## The five kinds

One per note. The kind tells a reader whether to trust the note before reading
it, which is the single most useful bit in the frontmatter.

| `kind` | Records | Trust it? |
| --- | --- | --- |
| `plan` | What the work intends to do, written before it happens | **Predictive.** Usually wrong in part by the end; expect a successor |
| `implementation` | What shipping the work taught about the code | Descriptive — probably still true |
| `investigation` | A question answered: root cause, gap analysis, a standing known issue | True as of its date; the bug may since be fixed |
| `decision` | A choice with real alternatives, below the ADR threshold | Durable until something reverses it |
| `operation` | Mechanical repository work — backport, cherry-pick, release | Expires with the release. Rarely earns a note at all |

**A harden or assessment pass is not its own kind.** It lands as
`investigation` when it only reviewed, or `implementation` when it also changed
code. Either way its most valuable section is *Deliberately not done*, which is
the part a diff can never hold.

**A known issue is `investigation` with `status: current`.** It needs no special
kind — it is findable because its status says it still describes reality.

## Frontmatter

Three keys at the top level, the same shape every artifact these skills author
uses — a spec, a plan, an ADR, and a lore note all open identically, and
`metadata.topic` is what threads them together.

```yaml
---
name: rate-limiting
description: Why the limiter counts requests after auth, not before.
metadata:
  kind: implementation
  status: current
  topic: rate-limiting
  tickets: [PROJ-482]
  prs: [1174]
  supersedes: []
---
```

| Field | Purpose |
| --- | --- |
| `name` | Stable identity, deliberately **not** the filename slug — the filename leads with a timestamp nobody cites, and a note that gets renamed keeps its `name` |
| `description` | Required, and short: one line, under 120 characters, no wrapping. It says when a reader should open the note, which is a different job from the title that says what it records |
| `metadata.kind` | One of the five above |
| `metadata.status` | `current` (still describes the code) · `historical` (was true at its date, the code has moved) · `superseded` (a later note replaces it) |
| `metadata.topic` | Kebab-case join key. **The most important field** — it is what clusters plan → implementation → harden for one piece of work, which filenames only do by accident. Shared with the spec, plan, and ADRs for the same work |
| `metadata.tickets` | Ticket keys, so the note is reachable from the tracker |
| `metadata.prs` | PR numbers. Load-bearing: this is the *pointer* to where the change narrative lives, which is how the note avoids restating it |
| `metadata.supersedes` | Filenames this note replaces. Empty list when none |

`status` is the only one of these you may edit after merge, and `historical` is
the reader's call — both below. Everything under `metadata` is this note's own;
only `topic` is shared, and it is copied from the spec or plan rather than
invented here.

### The lore directory's existing convention wins

Read what is already in `lore/` before writing the first note. Where the notes
there carry a different frontmatter shape, or none, **match them and say so** —
a directory holding two conventions gives a future reader no way to tell which
one to follow, and this shape is not worth that. Adopt it in a directory these
skills established, or one holding nothing that contradicts it. Migrating a
directory you own is a deliberate change of its own, never a side effect of
writing the next note.

### Two fields deliberately absent

Both are near-universal in notes written before this convention, and both are
waste:

- **`date`** — the filename already begins with `YYYYMMDD-HHMM`. A second copy
  is one more thing that can disagree with the first.
- **`branch`** — dead within a week of the merge, and `prs` reaches the same
  work without going stale.

### `status` is the only thing you may edit after merge

A merged note's body is frozen. When a later note supersedes it, flip its
`status` and add nothing else. Rewriting the body to hold a newer finding
destroys the dated record, which is the entire reason the file has a timestamp
in its name.

### Who sets `historical`, and when

Nobody sweeps the directory. `status` would be worthless if keeping it accurate
required a scheduled pass, because that pass never happens and every note stays
`current` forever — at which point the query that matters (`status: current`)
returns the whole directory and means nothing.

So the rule is opportunistic, and it belongs to the **reader**: when you open a
note and find its body no longer matches the code, flip that note to
`historical` in the same turn, before doing anything else. You are the only
person who will ever have that information, and you have it exactly once.

Two limits on that:

- **Only when the note already has frontmatter.** A note predating this
  convention has no `status` field, and adding one is restructuring someone
  else's file. Leave it, and say what you found instead.
- **`historical` is not a verdict on the reasoning.** It says the code moved,
  not that the note was wrong. The rejected alternative and the mechanism it
  records usually outlive the lines it points at, which is why the note is kept
  rather than deleted.

A note is never deleted for being stale. `historical` is how a directory stays
honest without anyone maintaining it.

## Filename

```
lore/YYYYMMDD-HHMM-<slug>.md
```

From `date +%Y%m%d-%H%M`, never from memory — leading zeros included. The slug
is lowercase and hyphenated, and names the *subject*, not the genre: `kind`
already carries the genre, so `-plan` and `-harden` suffixes are redundant.

## Finding a note again

There is no index file, on purpose: an index lists filenames and rots the moment
one is added. The frontmatter is the index — which is what `description` is for,
and why it is required. The queries below are unanchored deliberately, so they
match whether the field sits at the top level or nested under `metadata:`.

```sh
# the index: every note, one line each
grep -h 'description:' lore/*.md

# every note on one piece of work, in order
grep -l 'topic: rate-limiting' lore/*.md

# what still describes the code
grep -l 'status: current' lore/*.md

# standing known issues
grep -l 'status: current' lore/*.md | xargs grep -l 'kind: investigation'

# reachable from a ticket
grep -l 'PROJ-482' lore/*.md

# notes predating the convention — honest about what was never converted
grep -L '^---$' lore/*.md

# cross-references that no longer resolve
grep -ho 'lore/[0-9]\{8\}-[0-9]\{4\}-[a-z0-9.-]*\.md' lore/*.md | sort -u |
  while read -r r; do [ -f "$r" ] || echo "missing: $r"; done
```

That last one is worth running before adding a reference to another note. A
cross-reference to a note that was planned and never committed is trivial to
create and invisible afterwards — the link reads fine, and nothing resolves it
until someone tries to follow it.

## The template

Copy [../assets/lore-note.md](../assets/lore-note.md) and delete the sections
that have nothing in them.
