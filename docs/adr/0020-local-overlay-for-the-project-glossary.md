---
name: local-overlay-for-the-project-glossary
description: Why a reader's own domain terms go in a git-ignored CONTEXT.local.md excluded through .git/info/exclude, and why ADRs get no equivalent.
metadata:
  status: accepted
  topic: domain-modeling
---

# A git-ignored local overlay for the project glossary

**Context:** `domain-modeling` writes settled terms into a repo's tracked
`CONTEXT.md`, which is the team's file. Terms that can't go there — a client
name under NDA, an internal codename, vocabulary being tried out before it is
proposed — had nowhere to live, so they stayed in the conversation and were
gone by the next session. A per-reader tier needs three things the tracked file
doesn't: a place on disk, a way to stay out of commits, and a way to survive
into a worktree, which checks out tracked files only.

**Decision:** `CONTEXT.local.md` (and `CONTEXT-MAP.local.md`) sits beside the
tracked file in the same format, read as an overlay on top of it rather than a
replacement. `.agents/AGENTS.md` names it so every client reads both, and
`git-worktree` symlinks it from the main checkout alongside
`.claude/settings.local.json`. It is excluded in `.git/info/exclude`, not the
tracked `.gitignore`: that file is per-clone and untracked, matching the scope
of what it hides, and it lives in the common git dir, so a linked worktree
inherits the entry — which is what makes `git-worktree`'s `check-ignore` gate
pass there at all (verified). Promotion into the tracked glossary is always
asked for, never taken on the agent's initiative.

**Consequences:** Unshareable terms outlive the session, and a worktree reads
the same vocabulary as the main checkout. The overlay is untracked, not
private — every agent that opens the repo reads it, so the no-secrets rule
applies to it unchanged. An overlay nobody has excluded yet is skipped silently
by the worktree setup: `check-ignore` fails, the loop moves on, and the
worktree is missing vocabulary with no error, so the exclude entry is a
prerequisite rather than a convenience. Two files can now define one term; the
overlay wins, but the disagreement gets reported, since it means either the
tracked definition drifted or the local one went stale.

**Rejected:** A `docs/adr/` equivalent. The numbers are addresses in a shared
trail, and a git-ignored record would spend one nobody else receives.
`~/.agents/adr/<repo>-NNNN-slug.md` already covers a decision that isn't the
team's yet ([ADR 0014](0014-fall-back-to-a-global-home-when-the-repo-has-not-opted-in.md)).

**Evidence:** `skills/domain-modeling/references/CONTEXT-FORMAT.md`,
`skills/domain-modeling/SKILL.md`, `skills/git-worktree/SKILL.md`,
`.agents/AGENTS.md`
