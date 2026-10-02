# gh CLI: issues

> Keep every `gh` below a single bare command — no pipe, redirect, or `$(...)` —
> so it runs unsandboxed and reaches the keychain; shape output with
> `--json`/`--jq`. Mutating commands (and any `gh api` with a field flag) are
> approval-gated; make `gh api` writes explicit with `--method POST`. Background:
> [SKILL.md](../SKILL.md) Gotchas and `~/.agents/references/SANDBOX.md`.

The issue surface the triage flow and any issue-filing leans on.

## Reading / listing

- `gh issue list [--state open|closed|all] [--author <h>] [--label <l>] [--type
  <name>] [--search "<q>"] [-L N] [--json <fields>]` — capped (~30) without `-L`.
- `gh issue view <n> [--json <fields>] [--comments]`.
- `--json` fields include `number`, `title`, `state`, `labels`, `assignees`,
  `body`, `comments`, plus the relationship fields below.

## Writing (approval-gated — each prompts)

- `gh issue create --title '<t>' --body '<b>' [--label] [--assignee] [--type
  <name>] [--parent <n|url>] [--blocked-by <n,...>] [--blocking <n,...>]`.
- `gh issue edit <n> [...]`, `gh issue comment <n> --body '<b>'`,
  `gh issue close <n>`, `gh issue reopen <n>`.

## Issue types, sub-issues, and relationships

Newer `gh issue` subcommands model issue types, sub-issue hierarchy, and
blocked-by/blocking relationships.

- `gh issue create`: `--type <name>`, `--parent <number|url>` (creates the new
  issue as a sub-issue), `--blocked-by <number|url,...>`,
  `--blocking <number|url,...>`.
- `gh issue edit` (edits one or more issues in the same repo, e.g. `gh issue edit
  23 34`): `--type <name>` / `--remove-type`, `--parent <n|url>` /
  `--remove-parent`, `--add-sub-issue <n,n>` / `--remove-sub-issue <n,n>`,
  `--add-blocked-by <n,n>` / `--remove-blocked-by <n,n>`, `--add-blocking <n,n>`
  / `--remove-blocking <n,n>`. Relationship and parent refs are issue numbers or
  URLs; a URL may point to another repo on the same host, but a different host is
  rejected. `--add-sub-issue` cannot be used when editing more than one issue.
- `gh issue list --type <name>` filters by issue type.
- `gh issue view` and `gh issue list` accept these as `--json` fields (prefer
  them over scraping the default text output): `issueType`, `parent`,
  `subIssues`, `subIssuesSummary`, `blockedBy`, `blocking`. `subIssues`,
  `blockedBy`, and `blocking` are objects shaped `{"nodes": [...], "totalCount":
  N}` (not flat arrays), and `nodes` is capped (`subIssues` at 100,
  `blockedBy`/`blocking` at 50), so compare the node count against `totalCount`
  to detect truncation.
- GHES: issue types and sub-issues need 3.17+; blocked-by/blocking relationships
  need 3.19+.

See [ATTACHMENTS.md](ATTACHMENTS.md) for `--attach` on `gh issue create`/`edit`/`comment`.
