# Branch naming

Name branches `<type>-<short-slug>`, optionally prefixed with an issue key when the project tracks work in an issue tracker: `[<issue-key>-]<type>-<short-slug>`. The whole name is **lowercase**, every segment joined by a single hyphen — no slashes, no `<key>/<slug>` shorthand.

- `<issue-key>` — the tracker key, **lowercased** (Jira `HDR-1190` → `hdr-1190`); dev-panel branch detection matches case-insensitively, so the ticket link still resolves.
- `<type>` — the Conventional Commit type the work maps to (`feat`, `fix`, `chore`, …), lowercase, and **required**: a name with no type segment isn't to convention.
- `<short-slug>` — a few lowercase, hyphen-separated words describing the change.

The shape is `^([a-z0-9]+-[0-9]+-)?(feat|fix|chore|build|ci|docs|style|refactor|perf|test)-[a-z0-9-]+$`. Examples: `feat-getting-started`, `hdr-1190-feat-durable-hydra-allocation-retry`. A `<key>/<slug>` form like `HDR-1190/durable-hydra-allocation-retry` fails it twice — the slash, and the absent type. Branch from the repository's default branch unless told otherwise.

## Renaming a branch that breaks the convention

Offer `git branch -m <corrected>` while the branch is unpushed, and ask before running it. Once it's pushed, say so and leave it: renaming orphans the remote branch and breaks any open PR. Run the rename bare from inside the checkout — in a worktree, `-m` rewrites that worktree's `HEAD` under `.git/worktrees/`, which a sandbox can keep read-only for a wrapped command.
