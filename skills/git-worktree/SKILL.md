---
name: git-worktree
description: Create, place, and remove git worktrees with a consistent layout. Use when setting up, creating, adding, entering, or cleaning up a git worktree for any repo — covers the sibling-folder location, branch-based naming, working inside an isolated worktree session, and the absolute-path requirement.
---

# Git worktrees

Create a worktree in a dedicated sibling folder, work in it by absolute path, and remove it when the work is done.

## When to use this skill

- Setting up or creating a worktree to develop a branch in isolation
- Deciding where a worktree should live and what to name it
- Working inside a worktree — especially a session that refuses some shell commands
- Cleaning up a worktree and its stale entries when finished

## Placement and naming

Keep worktrees in a dedicated sibling folder next to the repository, never inside the checkout: `<repo-path>.worktrees/<worktree-name>` — e.g. for a repo at `/path/to/repo`, place a worktree at `/path/to/repo.worktrees/feat-getting-started`. Name the worktree after its branch, following the repository's branch-naming convention.

## Creating a worktree

- **Existing branch:** `git worktree add <repo-path>.worktrees/<name> <branch>` (absolute path).
- **New branch:** `git worktree add -b <branch> <repo-path>.worktrees/<name> [<start-point>]`, basing `<start-point>` on the repository's default branch unless told otherwise.

## Working in the worktree

Portable default (works in any agent): after `git worktree add`, operate on the worktree in place with its **absolute** path — `git -C <worktree> …`, or `cd <worktree>`. Nothing else is needed, and complex shell diagnostics (Ruby/gem env probing, reading shell rc files, etc.) run normally.

Some harnesses can instead *enter* a worktree as an isolated session (Claude Code does this with its `EnterWorktree` tool — pass the absolute `path`; a `~`-prefixed one won't match `git worktree list`). If your agent has such a mode, that session statically vets every Bash command and refuses any it can't prove stays inside the worktree — including benign, non-git diagnostics using `env <flag>`, subshells (`( … )`), `for`/`while` loops, pipelines, or bare `$VAR` (the refusal reads "runs env with …" or "too complex to verify …", and can't be turned off in settings). When isolated, keep each command plain and atomic; or skip entering isolation and work in place as above. Agents without such a mode are unaffected.

## Cleaning up

When finished, remove the worktree with `git worktree remove <path>` (add `--force` only to discard uncommitted changes), then run `git worktree prune` to clear stale entries.

## Gotchas

- **Never create a worktree inside the repository checkout** or in a nonstandard hidden location, because a nested worktree gets swept into the parent repo's `git status` and tree-walking tooling and can be committed by accident. Keeping it in the sibling `.worktrees/` folder avoids that; entering an *existing* worktree by its path is fine.
- **Always pass an absolute path**, never a `~`-prefixed one. A `~` path doesn't match `git worktree list` and doesn't expand when quoted; use `$HOME/…` or a full `/Users/…` path instead.

## Building wide in a scratch worktree

A worktree is a good place to build a feature wide — the whole thing, end to end, across every file in the way — without disturbing your main checkout. On that branch, commit freely: the commits are save points for you (a proven step, a rope to pull back to), not milestones for anyone else, so don't fuss over messages or hygiene. This branch's history is scratch paper; it never becomes the record. Once the feature works end to end, cut the real, reviewable pull requests fresh off the default branch and throw the scratch branch away.

## Attribution

- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
