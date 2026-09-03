---
name: artifact-frontmatter
description: One three-key frontmatter block for every artifact these skills author.
metadata:
  status: accepted
  topic: artifact-frontmatter
---

# One frontmatter shape for the artifacts these skills author

**Context:** Eight skills write durable Markdown into a repository or a
machine-local directory — `draft-prd`, `slice`, `draft-spec`, `draft-plan`,
`lore`, `standup`, `triage`'s out-of-scope entries, and `domain-modeling`'s
ADRs. Only lore carries frontmatter; the rest
encode their metadata as prose the reader has to parse (draft-plan's `**Spec:**`
and `**Stack:**` lines) or not at all. Three consequences follow. The join key
that would thread a spec to its plan to the lore note that records what building
it taught exists only inside lore, as `topic`. The out-of-scope knowledge base is
read by three skills doing concept-matching, and every one of them opens each
file because there is nothing shorter to read. And identity is carried by the
filename, which is the one thing that moves: ADR-FORMAT describes renumbering on
rebase, a spec migrates from `docs/specs/` into a tracker item, and a lore
filename leads with a timestamp nobody cites.

**Decision:** Every artifact these eight skills author opens with the same
three-key block, borrowed from the shape Claude's memory files use:

```yaml
---
name: deposit-refunds
description: Why the refund path bypasses the gateway's own idempotency key.
metadata:
  kind: implementation
  topic: deposit-refunds
  status: current
---
```

`name` is the stable identity, deliberately not the filename slug — it is what
survives a renumbered ADR or a spec that moved into a tracker. `description` is
required and short: one line, under 120 characters, no wrapping. It says when a
reader should open the file, which is a different job from the H1 title that says
what it is called. `metadata` is a free-form key-value map holding everything
artifact-specific, and the top level stays at exactly three keys — promoting a
fourth turns one recognizable shape into eight schemas that rhyme.

`metadata.topic` is the cross-artifact join key, kebab-case, shared by a spec,
its plan, the ADRs it cites, and the lore notes that follow. Lore invented it;
this generalizes it. Per artifact:

| Artifact | `name` is | `metadata` keys |
| --- | --- | --- |
| PRD | the outcome | `status, topic, tickets` |
| slice list | the feature being cut | `status, topic, tickets` |
| spec | the slice | `status, topic, tickets, adrs` |
| plan | the slice, matching its spec's `topic` | `spec, stack, status, topic` |
| lore note | the topic-scoped slug | `kind, status, topic, tickets, prs, supersedes` — today's six, moved down one level |
| ADR | the decision's slug, surviving renumbering | `status, supersedes, superseded-by, topic` |
| out-of-scope entry | the concept | `scope` (`project`/`cross-repo`), `constraint, prior-requests, adr` |
| standup journal | `<date>-<audience>` | `audience, format, period, repos` |

The first five are one chain — a PRD's `topic` is carried by the slice list cut
from it, the spec written for one of those slices, the plan under that spec, and
the lore note recording what building it taught. That chain is the reason to
standardize at all. The last two carry no `topic` on purpose: a rejection has no
spec, plan, or lore note by definition, and a standup update spans whatever the
stretch touched, so one topic would be a lie on most days.

`status` is deliberately not one shared enum. Each artifact keeps the vocabulary
of its own lifecycle — a PRD and a spec are `draft`, a slice list is `agreed`, a
plan is `ready`, an ADR is `accepted`, a lore note is `current` — because a
single enum spanning all of them would have to be so vague it stopped answering
the question each artifact is actually asked.

No field holds a count. A slice list is re-cut and a plan gains tasks, so a
number in the frontmatter goes stale on the first edit with nothing to catch it;
the list underneath is the count.

The standup journal is the one place `name` does match the filename. The field
earns its keep elsewhere because filenames move — a renumbered ADR, a spec that
migrates into a tracker — and a journal entry never moves and never leaves its
directory, so a second identity for it would be invention rather than address.

A skill is in scope when it authors a durable file. Ruled out by the same test:
`claude-handoff`, whose summary is a temp file consumed once by a subagent;
`domain-modeling`'s `CONTEXT.md`, a singleton whose name is already its index;
`grilling` and `codebase-design`, which delegate every write and author nothing;
`create-agentsmd`, whose output has a host-defined name and loader; and
`agent-skills` and `agent-rules`, whose frontmatter is a host's schema rather
than ours to set.

Two boundary rules bound it.

**Frontmatter belongs to the file, never to the delivered text.** A PRD or spec
published to a Jira issue and a standup update pasted into Slack both render YAML
as literal junk under the user's name. Every skill that has an outward-facing
destination — `draft-prd`, `slice`, `draft-spec`, `standup` — strips the block at
that boundary. This makes standup's journal file no longer byte-identical to the
text that was sent, which Step 6 currently promises; that promise narrows to the
skeleton below the block.

**The output directory's existing convention wins.** Before writing, read what is
already in `lore/`, `docs/adr/`, `.out-of-scope/`, or the specs directory. Where
those files carry a different frontmatter shape or none at all, match them and
say so, rather than leaving a directory with two conventions in it and no way to
tell which one a future reader should follow. This standard governs a directory
these skills established, or one holding nothing that contradicts it. Lore
already states the narrow form — never restructure someone else's note — and it
generalizes to all eight. A directory you own can still be migrated, but that is a
deliberate change, not a side effect of writing the next file.

**Consequences:** A grep over `description:` becomes the index that lore's KINDS.md
deliberately refuses to keep as a file. `triage` dedupes against one line instead
of a body. `standup`'s `metadata.format` names which row of GATHER.md's
promise-and-stall mapping table applies, which Step 2 currently infers from
section names. Lore's existing discovery queries survive the added indentation
unchanged — all but one are unanchored, and the anchored one matches `^---$`.

Three costs. ADR-FORMAT says to add `status:` frontmatter "only in a repo where
decisions get revisited often enough to need it," and this overrides that
judgment for the skills' own output; the guidance changes rather than the
practice diverging silently. Nothing enforces any of it — `check-payload`'s scope
is the published payload, and these artifacts land in other repositories; the
only mechanizable slice is that the templates under `skills/*/assets/` and
`skills/*/references/` open with the block. And the precedence rule guarantees
mixed directories in the field, which is the price of not rewriting files this
repo does not own.

This ADR carries the block, and the twelve before it do not. That is the
precedence rule applied to `docs/adr/` itself: an accepted ADR is never edited to
match a later convention.

**Rejected:** Promoting `topic` to a fourth top-level key. It is the most
load-bearing field in the design, which is the argument for it, but the value of
matching the memory shape is that three keys are recognizable at a glance in
eight different directories — and a fourth key admitted on merit invites the
fifth.
Also rejected: retrofitting existing files. A migration pass over other people's
lore directories is churn that buys the user nothing, and the reader-side rule
already tolerates both shapes.

**Evidence:** `skills/draft-prd/references/TEMPLATE.md`, `skills/slice/SKILL.md`,
`skills/draft-spec/references/TEMPLATE.md`,
`skills/draft-plan/references/TEMPLATE.md`, `skills/lore/references/KINDS.md`,
`skills/standup/references/GATHER.md`,
`skills/domain-modeling/references/ADR-FORMAT.md`,
`skills/triage/references/OUT-OF-SCOPE.md`
