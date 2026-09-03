---
name: artifact-fallback-home
description: Where an authored artifact goes when the repository has no directory for it.
metadata:
  status: accepted
  topic: artifact-frontmatter
---

# Fall back to a global home when the repository has not opted in

Builds on [ADR 0013](0013-one-frontmatter-shape-for-authored-artifacts.md),
which set the frontmatter shape these artifacts share.

**Context:** The eight skills of ADR 0013 write into whatever repository is open.
Most of those repositories are not the maintainer's — a work repository is a
shared codebase with its own conventions and its own team. A skill that creates
`lore/` or `docs/specs/` because it needed somewhere to write has imposed one
person's workflow on everyone who pulls that branch, and the imposition arrives
as a directory nobody agreed to review. The existing directory was already the
signal ADR 0013 leaned on for *shape* — match what is there — but nothing said
what to do when there is nothing there at all, so the skills defaulted to
creating the repo path.

**Decision:** The repository directory's existence is the opt-in. A skill writes
into the repo only where the directory already exists; otherwise it writes to a
per-artifact global root under `~/.agents/`, and never creates the repo
directory to make room for itself.

| Artifact | Repo path (when it exists) | Global fallback |
| --- | --- | --- |
| lore note | `lore/` | `~/.agents/lore/` |
| spec | `docs/specs/` | `~/.agents/specs/` |
| plan | `docs/plans/` | `~/.agents/plans/` |
| PRD | `docs/prds/` | `~/.agents/prds/` |
| slice list | the path the user names | `~/.agents/slices/` |
| ADR | `docs/adr/` | `~/.agents/adr/` |
| out-of-scope entry | `.out-of-scope/` | `~/.agents/out-of-scope/` |
| standup journal | — | `~/.agents/standup/` |

Per-artifact roots rather than one namespaced by repository: the directory says
what kind of thing it holds, and the frontmatter says which project it is about.
That needs one new key.

**`metadata.repo` is the repository's name** — `billing-api`, not a path and not
an owner-qualified slug. Required on every artifact in a global root, because the
roots are flat and a `topic` is only unique within one project; omitted in-repo,
where the file's own location already answers it. Take the name from the
remote's basename when there is a remote, else the toplevel directory's, so a
worktree or a renamed clone does not change it. A path would leak the machine's
layout into a file that may later be committed.

Filenames need no repo prefix, with one exception. Every other artifact is named
from a timestamp, which does not collide across projects. An ADR is named from a
number that restarts at `0001` in every repository and collides immediately, so a
global one is filed as `~/.agents/adr/<repo>-NNNN-slug.md` — the prefix comes off
when the file moves into `docs/adr/`, and the number stays the repository's own.

`mac` provisions all eight as real directories, for the reason
[ADR 0008](0008-provision-agent-state-as-real-directories.md) gives: Codex's
Seatbelt sandbox rejects a symlinked writable root. Each is granted write in all
three client configs under the parity rule. `~/.agents/skills` and
`~/.agents/rules` are pointedly not among them — they resolve into this
repository and are the agent's own instructions.

**Consequences:** A work repository gets a new directory only when someone puts
one there deliberately. The maintainer's notes survive either way, so the choice
is no longer between imposing a convention and losing the work. `~/.agents` gains
six writable roots, which is the cost of per-artifact separation and is bounded:
each is a leaf the payload does not live in.

The failure this accepts is quiet. A spec or an ADR is written for other people,
and one that lands in `~/.agents/specs/` is invisible to them — the document
exists, the team never sees it, and nothing reports that. Two things hold the
line: the skill says which path it wrote to, every time, and `draft-spec`,
`draft-prd`, and `slice` keep asking before they write at all, with the global
root offered rather than assumed. `domain-modeling` keeps the sharpest version —
an ADR the team cannot read is not a recorded decision, so a missing `docs/adr/`
is raised rather than routed around.

**Rejected:** One root namespaced by repository (`~/.agents/notes/<repo>/lore/`).
It needs a single write grant instead of six and separates projects by
construction. It was rejected because the nesting encodes in a path what the
frontmatter already has to carry anyway: `metadata.repo` is needed for any note
that is ever moved into a repository, and having both is two things that can
disagree.

Also rejected: making `~/.agents` writable wholesale. One grant instead of six,
and it hands an agent write access to `~/.agents/skills` and `~/.agents/rules` —
symlinks into this repository, which is to say the agent's own instructions.
