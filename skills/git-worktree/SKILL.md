---
name: git-worktree
description: How to create git worktrees. Use when setting up, creating, or placing a git worktree for any repo. Covers the recommended sibling-folder location and naming convention.
---

# Git worktrees

Keep worktrees in a dedicated sibling folder next to the repository, never inside the checkout: `<repo-path>.worktrees/<worktree-name>` — e.g. for a repo at `/path/to/repo`, place a worktree at `/path/to/repo.worktrees/feat-getting-started`. Name the worktree after its branch (see the `git-commit` skill for branch naming).

- **Existing branch:** `git worktree add <repo-path>.worktrees/<name> <branch>` (absolute path).
- **New branch:** `git worktree add -b <branch> <repo-path>.worktrees/<name> [<start-point>]`, basing `<start-point>` on the repository's default branch unless told otherwise.
- Never create a worktree inside the repository checkout itself, or in a nonstandard hidden location. Entering an existing worktree by its path is fine.
- **When finished,** remove it with `git worktree remove <path>` (add `--force` only to discard uncommitted changes), and run `git worktree prune` to clear stale entries.

## Building wide in a scratch worktree

A worktree is a good place to build a feature wide — the whole thing, end to end, across every file in the way — without disturbing your main checkout. On that branch, commit freely: the commits are save points for you (a proven step, a rope to pull back to), not milestones for anyone else, so don't fuss over messages or hygiene. This branch's history is scratch paper; it never becomes the record. Once the feature works end to end, cut the real, reviewable pull requests fresh off the default branch and throw the scratch branch away.

## Attribution

- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
