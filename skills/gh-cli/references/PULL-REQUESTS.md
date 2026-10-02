# gh CLI: pull requests

> Keep every `gh` below a single bare command — no pipe, redirect, or `$(...)` —
> so it runs unsandboxed and reaches the keychain; shape output with
> `--json`/`--jq`. Mutating commands (and any `gh api` with a field flag) are
> approval-gated; make `gh api` writes explicit with `--method POST`. Background:
> [SKILL.md](../SKILL.md) Gotchas and `~/.agents/references/SANDBOX.md`.

The PR surface the pull-request, review-response, gh-stack, and code-review flows
lean on.

## Reading PRs

- `gh pr list [--state open|closed|merged|all] [--author <h>] [--label <l>]
  [--search "<q>"] [-L N] [--json <fields>]` — the list is capped (~30) without
  `-L`.
- `gh pr view <n> [--json <fields>] [--comments]` — `--comments` shows
  conversation (issue-level) comments only, never review-thread comments (see
  below).
- `gh pr diff <n> [--name-only] [--patch]` — read the diff without checking out.
- `--json` fields worth knowing: `number`, `title`, `state`, `isDraft`,
  `mergeable`, `reviewDecision`, `reviews`, `comments`, `files`, `headRefName`,
  `baseRefName`, `statusCheckRollup`.

## Review-thread comments (the `gh api` fallback)

Inline, file-anchored review comments are not on `gh pr view --comments`. Reach
them through the API:

- List a PR's review comments:
  `gh api repos/{owner}/{repo}/pulls/{n}/comments`
- Reply to one:
  `gh api --method POST repos/{owner}/{repo}/pulls/{n}/comments/{comment_id}/replies -f body='...'`

`--method POST` is not optional here: a field flag (`-f`) already makes the call
a POST, and the agent sandboxes **deny** the implicit form — state the method so
the write is approval-gated rather than blocked.

## Writing PRs (approval-gated — each prompts)

- `gh pr create --title '<t>' --body '<b>' [--base <branch>] [--draft]
  [--reviewer <h>] [--label <l>]` — `--title` and `--body` (or `--fill`) are
  required non-interactively.
- `gh pr edit <n> [--title] [--body] [--add-label] [--add-reviewer] [--milestone]`
- `gh pr comment <n> --body '<b>'` — a conversation comment, not a review-thread
  reply (use the `gh api` reply above for those).
- `gh pr review <n> --approve | --request-changes --body '<b>' | --comment --body '<b>'`
- `gh pr ready <n>`, `gh pr merge <n> [--squash|--merge|--rebase]`,
  `gh pr close <n>`, `gh pr reopen <n>`.

## Checkout

- `gh pr checkout <n>` switches the current branch to the PR.
- `gh pr checkout <n> --worktree <path>` checks it out into a git worktree
  instead of switching, leaving the current branch in place.

See [ATTACHMENTS.md](ATTACHMENTS.md) for `--attach` on `gh pr create`/`edit`/`comment`.
