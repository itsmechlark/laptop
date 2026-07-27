---
name: git-worktree
description: How to create git worktrees. Use when setting up, creating, or placing a git worktree for any repo. Covers the recommended sibling-folder location and naming convention.
---

# Git worktrees

Keep worktrees in a dedicated sibling folder next to the repository, never inside the checkout: `<repo-path>.worktrees/<worktree-name>` — e.g. for a repo at `/path/to/repo`, place a worktree at `/path/to/repo.worktrees/feat-getting-started`. Name the worktree after its branch (see the `git-commit` skill for branch naming).

- Create with an absolute path: `git worktree add <repo-path>.worktrees/<name> <branch>`.
- Never create a worktree inside the repository checkout itself, or in a nonstandard hidden location. Entering an existing worktree by its path is fine.
