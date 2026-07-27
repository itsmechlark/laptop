---
name: git-worktree
description: How to create git worktrees for TableCheck repos. Use when setting up, creating, or placing a git worktree for Monolith, Hydra, or any TableCheck repo. Covers the required sibling-folder location and naming convention.
---

# Git worktrees

Git worktrees must live in the repo's dedicated sibling folder: `<repo-path>.worktrees/<worktree-name>` — e.g. `~/Codespace/repo.worktrees/ABC-1234-feat-getting-started`. Name the worktree after its branch (see the `git-commit` skill for branch naming).

- Create with `git worktree add ~/Codespace/<repo>.worktrees/<name> <branch>` (absolute path).
- Never create worktrees inside the repo checkout or under `.claude/worktrees/` — do not use the EnterWorktree tool's create mode; entering an existing worktree by `path` is fine.
