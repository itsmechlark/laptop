---
name: scaffolds-are-templates
description: Files the agent copies and fills in move from assets/ to templates/, the tier the spec defines for them.
metadata:
  status: accepted
  topic: skill-layout
---

# Scaffolds live in `templates/`, not `assets/`

**Context:** `AGENTS.md` described two bundled-resource subdirectories and split
them by whether the agent has to *read* the file: `references/` for prose it
reasons about, `assets/` for everything else. A file the agent "copies and fills
in rather than reasons about" was routed to `assets/` on the grounds that it
stays out of the discovery budget.

The Agent Skills specification splits the same space four ways, and the line it
draws is different: `assets/` holds files used **as-is** in output, while
`templates/` holds scaffolds the agent **modifies** and builds on. The `agent-skills`
skill states the test directly — if the agent reads a file and builds on it, it
is a template; if it is emitted unchanged, it is an asset.

Under that test every first-party file in `assets/` was misfiled. All six are
skeletons with placeholders, and every one of them is described by its own skill
as something to fill: `standup/references/FORMATS.md` calls its three "skeletons
… ready to copy and fill", `lore` says to copy its note "and delete the sections",
`brainstorming` says to "start from" its mockup, and `agent-handoff` says to
"copy and fill it". Not one is emitted byte-for-byte.

The local rule was not a considered divergence from the spec. It was written
around the property that mattered at the time — these files stay out of context —
and that property is true of both tiers, so it could not distinguish them.

**Decision:** Classify by what the agent does with the file, as the spec does.
A scaffold the agent completes goes in `templates/`; `assets/` is reserved for
output that ships unchanged. Every existing file moves:

| From | To |
| --- | --- |
| `skills/lore/assets/lore-note.md` | `skills/lore/templates/lore-note.md` |
| `skills/brainstorming/assets/mockup-template.html` | `skills/brainstorming/templates/mockup-template.html` |
| `skills/standup/assets/update-block.md` | `skills/standup/templates/update-block.md` |
| `skills/standup/assets/update-terse.md` | `skills/standup/templates/update-terse.md` |
| `skills/standup/assets/update-spoken.txt` | `skills/standup/templates/update-spoken.txt` |

`agent-handoff`'s template is the sixth of its kind and appears in no row: it is
being authored alongside this decision, so it is written to `templates/` from the
start rather than moved there.

**Where the spec governs, the spec wins.** Bundled-resource layout is
`agent-skills`' domain, and it conforms to a published specification that other
hosts read. A local convention that contradicts it buys nothing and costs
portability the moment one of these skills is published or vendored elsewhere.
This is narrower than it sounds: it settles layout the spec actually defines, and
leaves untouched everything the spec is silent on — where skills live, the
vendored/first-party split, the provenance records, the flagging convention.

**Consequences:** No skill has an `assets/` directory any more. The tier stays
documented because the distinction is real and the first genuinely unchanged
artifact — a logo, a fixture, a config nobody edits — belongs there.

`templates/` is loaded "when referenced" rather than never, which is the honest
description of what already happened: an agent about to fill a skeleton reads it.
Nothing about the context cost changes, because a file is only read when a step
points at it either way.

`check-payload` needed no change. Its bundled-resource link check already
accepted `templates/` alongside `assets/`, so the moved links validate as they
stood — the checker was closer to the spec than the instruction file was.

[ADR 0013](0013-one-frontmatter-shape-for-authored-artifacts.md) refers to "the
templates under `skills/*/assets/`" when listing what it could mechanize. That
sentence now names a path that does not exist. It is left as written — an
accepted ADR records what was decided when it was decided — and this ADR is the
correction.

The moves are `git mv`, so history follows the files and no content changes.

**Rejected:** Keeping `assets/` and documenting the divergence. It is the
cheapest option and no file changes. It was rejected because the divergence was
never argued for in the first place — there is nothing to preserve, only an
inaccuracy to keep explaining — and because a reader who knows the spec would
have to learn that this repository means something else by a word the spec
defines.

Also rejected: collapsing the two tiers into one and calling everything
`templates/`. It matches today's contents exactly, since nothing is emitted
unchanged. It was rejected because the tier that disappears is the one the spec
names first, and re-adding it later for a single logo would be a second
migration to avoid one unused directory.

**Evidence:** `AGENTS.md` bundled-resource table,
`skills/lore/templates/lore-note.md`,
`skills/agent-handoff/templates/handoff.md`,
`skills/standup/references/FORMATS.md`,
`skills/brainstorming/references/VISUAL-COMPANION.md`
