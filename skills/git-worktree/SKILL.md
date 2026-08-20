---
name: git-worktree
description: Create, place, set up, and remove git worktrees with a consistent layout. Use before starting code edits to ensure work happens in an isolated worktree — and when setting up, creating, adding, entering, or cleaning up a git worktree for any repo. Covers detecting whether you are already in a worktree, the sibling-folder location and branch-based naming, symlinking git-ignored local agent config (e.g. .claude/settings.local.json), auto-installing dependencies for the worktree's stack, working inside an isolated session, and the absolute-path requirement.
---

# Git worktrees

Create a worktree in a dedicated sibling folder, wire up its local config and dependencies, work in it by absolute path, and remove it when the work is done.

## When to use this skill

- **Before making code edits** — check if you're already in a worktree; if not, create one so edits land on an isolated branch, not the main checkout
- Setting up or creating a worktree to develop a branch in isolation
- Deciding where a worktree should live and what to name it
- Getting a fresh worktree ready to run — its local agent config and installed dependencies
- Working inside a worktree — especially a session that refuses some shell commands
- Cleaning up a worktree and its stale entries when finished

Not for switching branches inside a single checkout — that's a plain `git switch`, no worktree needed.

## Placement and naming

Keep worktrees in a dedicated sibling folder next to the repository, never inside the checkout: `<repo-path>.worktrees/<worktree-name>` — e.g. for a repo at `/path/to/repo`, place a worktree at `/path/to/repo.worktrees/feat-getting-started`. Name the worktree after its branch, following the branch-naming convention from the `git-commit` skill. Always use an **absolute** path (never `~`-prefixed — it won't match `git worktree list`).

## Workflows

### Pre-edit guard

Before starting code edits, check whether you're already isolated. Run the detection from step 1 of [Set up a worktree](#set-up-a-worktree):

```sh
git_dir="$(git rev-parse --path-format=absolute --git-dir)"
git_common="$(git rev-parse --path-format=absolute --git-common-dir)"
superproject="$(git rev-parse --show-superproject-working-tree 2>/dev/null)"
```

- **Already in a worktree** (git-dir ≠ git-common-dir, superproject empty) → proceed with edits.
- **On the default branch in the main checkout** → create a worktree first, following [Set up a worktree](#set-up-a-worktree), then work there. Name the branch after the task (ask the user if the intent isn't clear enough to pick a name).
- **On a non-default branch in the main checkout** → the user has already switched branches, so a worktree is optional — proceed with edits unless the user prefers isolation.

### Set up a worktree

1. **Detect existing isolation first** — don't nest a worktree inside a worktree:
   ```sh
   git rev-parse --path-format=absolute --git-dir          # …/.git/worktrees/<name> in a worktree
   git rev-parse --path-format=absolute --git-common-dir   # …/.git for the main checkout
   git rev-parse --show-superproject-working-tree          # non-empty ⇒ you're in a submodule
   ```
   You're in a linked worktree when git-dir ≠ git-common-dir **and** the superproject probe is empty — then skip to step 3. A submodule's dirs can differ too, so the probe is the guard: if it's non-empty, treat this as a normal checkout. Otherwise continue to step 2.

2. **Create the worktree** by absolute path, in the sibling folder:
   - Existing branch: `git worktree add <repo>.worktrees/<name> <branch>`
   - New branch: `git worktree add -b <branch> <repo>.worktrees/<name> [<start-point>]`, basing `<start-point>` on the default branch unless told otherwise.

   A native worktree tool works too — Claude Code's `EnterWorktree` takes an absolute `path`, manages its own placement, and enters an isolated session; mind its command vetting under [Gotchas](#gotchas).

3. **Link git-ignored local config** so the agent behaves as it does in the main checkout. A fresh worktree has only tracked files, so machine-local config (e.g. `.claude/settings.local.json`) is missing. Symlink each such file from the main checkout by absolute target — but only when it's git-ignored, so the link never shadows a tracked file or dirties `git status`. Run this from a normal shell (it targets the worktree explicitly, so cwd doesn't matter); inside an isolated session, issue the individual `ln -sfn` links instead — the loop won't pass command vetting:
   ```sh
   wt=<worktree-abs-path>
   main="$(dirname "$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir)")"
   for rel in .claude/settings.local.json; do          # add .env / .env.local only to share them
     [ -e "$main/$rel" ] || continue
     git -C "$wt" check-ignore -q "$rel" || continue   # only ever link git-ignored files
     mkdir -p "$wt/$(dirname "$rel")"
     ln -sfn "$main/$rel" "$wt/$rel"
   done
   ```
   A symlink shares one source of truth; **copy** instead when the worktree needs to diverge (e.g. an `.env` with its own port or database).

4. **Install dependencies** — `cd` into the worktree (a native tool already entered it), then run the install for its stack; see [Project setup](#project-setup). Prefer the repo's own bootstrap script (`bin/setup`, `bin/bootstrap`) when one exists.

### Clean up when done

Run from the main checkout — you can't remove a worktree your shell is sitting inside:
```sh
git worktree remove <path>     # add --force only to discard uncommitted changes
git worktree prune             # clear stale entries
```

## Project setup

Detect the stack by its manifest and run the matching install. Run it **inside the worktree** so asdf resolves versions from the worktree's own `.tool-versions` — never hardcode a runtime version.

| Manifest | Install |
| --- | --- |
| `Gemfile` | `bundle install` |
| `mix.exs` | `mix deps.get` |
| `package.json` + `pnpm-lock.yaml` | `pnpm install` |
| `package.json` + `yarn.lock` | `yarn install` |
| `package.json` + `package-lock.json` | `npm install` |
| `pyproject.toml` | `poetry install` |
| `requirements.txt` | `pip install -r requirements.txt` |
| `Cargo.toml` | `cargo build` |
| `go.mod` | `go mod download` |

## Gotchas

- **Never create a worktree inside the repository checkout** or in a nonstandard hidden location — a nested worktree gets swept into the parent repo's `git status` and tree-walking tooling and can be committed by accident. The sibling `.worktrees/` folder avoids that. (Entering an *existing* worktree by its path is fine.)
- **Always pass an absolute path, never a `~`-prefixed one.** A `~` path doesn't match `git worktree list` and doesn't expand when quoted; use `$HOME/…` or a full `/Users/…` path.
- **Only symlink files that are git-ignored** — run `git check-ignore -q` first. Ignored status is shared with the main checkout, so a file ignored there is ignored in the worktree too; symlink a *tracked* path and you shadow the real file and dirty `git status`.
- **An isolated session vets every Bash command and refuses what it can't prove stays inside the worktree.** Claude Code's `EnterWorktree` rejects even benign, non-git diagnostics that use `env <flag>`, subshells `( … )`, `for`/`while` loops, pipelines, or bare `$VAR` (the refusal reads "runs env with …" or "too complex to verify …", and can't be disabled in settings). When isolated, keep each command plain and atomic — or skip isolation and operate in place with `git -C <worktree> …` / `cd <worktree>`, where complex shell runs normally. The step-3 loop is a normal-shell convenience for exactly this reason.

## Building wide in a scratch worktree

A worktree is a good place to build a feature wide — the whole thing, end to end, across every file in the way — without disturbing your main checkout. On that branch, commit freely: the commits are save points for you (a proven step, a rope to pull back to), not milestones for anyone else, so don't fuss over messages or hygiene. This branch's history is scratch paper; it never becomes the record. Once the feature works end to end, cut the real, reviewable pull requests fresh off the default branch — the `pull-request` skill covers how to split and write them — and throw the scratch branch away.

## Attribution

- [obra/superpowers](https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/SKILL.md) - using-git-worktrees, MIT
- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
