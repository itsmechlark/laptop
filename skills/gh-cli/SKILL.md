---
name: gh-cli
description: How to drive the GitHub CLI (`gh`) from an agent — structured output with `--json`/`--jq`/`--template`, pagination and silent truncation, repo targeting, search vs list, issue/PR/discussion subcommands, and the `gh api` fallback for data the typed commands do not expose. Use when running `gh`, parsing its output, fixing a truncated `gh` list, posting an issue/PR/comment with `gh`, or making a `gh api`/GraphQL call.
---

# gh CLI

Patterns for invoking `gh` from an agent harness: how to get structured output,
avoid silently truncated lists, target the right repo, and reach data the typed
commands do not expose.

## When to use this skill

- About to run any `gh` command and want the output machine-readable
- A `gh issue list` / `gh pr list` / `gh search` result may be capped and you need
  all of it
- The data you want (review-thread comments, arbitrary fields) is not on a typed
  command and you need `gh api` or GraphQL
- A `gh` command returns `401` / "Requires authentication" and you need to tell an
  expired token apart from a sandbox failure
- Working with `gh pr`, `gh issue`, `gh discussion`, `gh repo read-file`, or file
  attachments — the flag catalogs are split by topic under `references/`

## Gotchas

- **Never pipe or redirect `gh` under the Claude Code / Codex sandbox.** A pipe,
  redirect, or `$(...)` re-sandboxes the command, which then cannot reach the
  keychain holding the token. Keep it a single bare command and shape output with
  `gh`'s own flags. Full triage: `~/.agents/references/SANDBOX.md`.
- **A field flag turns `gh api` into a POST.** `gh api` is GET by default but
  sends POST the moment you add `-f`/`-F`/`--field`/`--raw-field`/`--input`, so
  `gh api … -f body=…` is a mutating write. Make it explicit — `gh api --method
  POST …` — so it reads as the write it is (the agent sandboxes gate the implicit
  form by requiring this canonical shape).
- **Pass search qualifiers as bare tokens, not one quoted string.** `gh search
  issues repo:cli/cli is:open` works; `gh search issues "repo:cli/cli is:open"` is
  parsed as a single keyword and fails with `Invalid search query`. Quote only
  multi-word free text.
- **Lists truncate silently.** `gh issue list` / `gh pr list` / `gh search`
  default to ~30 rows with no warning. Pass `-L N` (`--limit N`), and for a true
  total use `gh api graphql` to read `totalCount`.
- **`--template`/`-T` collides with a body-template flag** on a few commands
  (`gh pr create -T`, `gh issue create -T`). Check `--help` before assuming which
  `-T` you are hitting.
- **`--author` does not match bots.** Bots author as GitHub Apps, so `--author
  dependabot` matches nothing — use `--app dependabot` or `--author
  "dependabot[bot]"`.
- **A clean GitHub `401` is an expired token, not a permissions problem.**
  Re-authenticate with `gh auth login` (outside the sandbox).

## Interactivity

`gh` already does the right thing in non-TTY contexts: it skips the pager, strips
ANSI color, and errors out fast with a helpful message instead of prompting (e.g.
`must provide --title and --body when not running interactively`). You do not need
to set `GH_PAGER` or pass `--no-pager` (no such flag exists). Set `GH_FORCE_TTY=1`
only if you deliberately want TTY-style output; `NO_COLOR` and `CLICOLOR_FORCE`
are also honored.

## Parsing JSON

Human output from `gh` is column-formatted. For structured data:

- Add `--json field1,field2,...` for structured output.
- Run a command with `--json` and **no field list** to print the full set of
  available fields, then pick what you need.
- Use `--jq '<expr>'` to filter without piping through a separate `jq`.
- Use `--template '<go-template>'` (alongside `--json`) for shaped text output.

## Repo targeting

`gh` infers the repo from the cwd's git remotes. Pass `--repo OWNER/REPO` (`-R`)
to override the resolved repo — required for anything cross-repo.

## Search vs list

- `gh search issues|prs|code|repos|commits|users` uses GitHub's search index and
  the full search syntax (`is:open`, `author:`, `label:`, `repo:owner/name`,
  `in:title`, ...). Most qualifiers also have a dedicated flag (`--repo`,
  `--author`, `--label`, ...). Prefer search for anything cross-repo or filtered
  by author/label.
- `gh issue list --search "..."` and `gh pr list --search "..."` take the query as
  one quoted string (a flag value) and are scoped to one repo.
- `gh search issues` also takes `--search-type <lexical|semantic|hybrid>`
  (github.com/GHEC only, issues only): `semantic` when the user describes a
  problem in natural language, `hybrid` to blend keyword and semantic ranking,
  `lexical` (default) for exact matching.

## Fall back to `gh api` for anything `--json` does not expose

Some useful data is not on the typed commands:

- Review-thread comments on a PR: `gh api repos/{owner}/{repo}/pulls/{n}/comments`
  (the `--comments` flag on `gh pr view` shows issue-level comments only).
- Arbitrary GraphQL: `gh api graphql -f query='...' -F var=value`.
- REST shortcuts: `gh api repos/{owner}/{repo}/...` — the `{owner}/{repo}`
  placeholder is filled in from the detected remotes; pass them literally for
  determinism.
- `gh api --paginate <path>` walks every page; combine with `--jq` and
  (optionally) `--slurp` to assemble one array.

## Authentication

`gh auth status` prints the active host(s), user, and which env var (if any) is
honored; `gh auth status --json` is supported. Under the sandbox, a `gh` command
can fail for either of two unrelated reasons — an expired token or an unreachable
keychain. `~/.agents/references/SANDBOX.md` has the triage; the short version is
in the Gotchas above.

## Other notes

- `gh pr checkout <n>` switches branches; use `gh pr diff <n>` or `gh pr view <n>`
  to only read. `gh pr checkout <n> --worktree <path>` checks the PR out into a
  worktree instead of switching.
- `gh issue develop <n> --checkout` creates a linked branch and checks it out; add
  `--worktree <path>` to use a worktree instead (requires `--checkout`, cannot be
  blank, cannot combine with `--list`).

## References

Read as needed, not upfront.

- [PULL-REQUESTS.md](references/PULL-REQUESTS.md) — reading PRs, review-thread
  comments via `gh api`, writing PRs, checkout
- [ISSUES.md](references/ISSUES.md) — listing and writing issues, issue types,
  sub-issues, and blocked-by/blocking relationships
- [CONTENT.md](references/CONTENT.md) — `gh repo read-file`/`read-dir` and `gh
  discussion`
- [ATTACHMENTS.md](references/ATTACHMENTS.md) — `--attach` for images and videos,
  shared by issues and PRs

## Attribution

- [cli/cli](https://github.com/cli/cli/tree/v2.102.0/skills/gh) - gh, MIT
