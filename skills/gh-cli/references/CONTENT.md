# gh CLI: repository content and discussions

> Keep every `gh` below a single bare command — no pipe, redirect, or `$(...)` —
> so it runs unsandboxed and reaches the keychain; shape output with
> `--json`/`--jq`. Mutating commands (and any `gh api` with a field flag) are
> approval-gated; make `gh api` writes explicit with `--method POST`. Background:
> [SKILL.md](../SKILL.md) Gotchas and `~/.agents/references/SANDBOX.md`.

Reading a repo's files without cloning, and the discussion subcommands.

## Reading files and directories (`gh repo read-file` / `read-dir`)

Preview commands, subject to change. They read a repo's contents over the API
without cloning, and honor `--repo OWNER/REPO` (`-R`) and `--ref
<branch|tag|commit>` (default branch when omitted).

- `gh repo read-file <path> [--ref <ref>] [--output <path> [--clobber]]
  [--allow-escape-sequences] [--json <fields>] [--jq <expr>]` prints a file's
  contents. In non-TTY contexts the raw bytes go straight to stdout
  (pipe-friendly); binary files are written as-is when piped but refused on a
  TTY. By default a file containing terminal escape sequences is refused; pass
  `--allow-escape-sequences` to read it anyway. `--output <path>` (`-o`) writes to
  disk instead of stdout (a trailing slash writes under a directory using the
  remote file name; `--clobber` allows overwrite); writing to disk always
  includes the raw bytes regardless of escape sequences. `--output` and `--json`
  are mutually exclusive. `--json` fields include `name`, `path`, `gitSHA`,
  `size`, `type`, `encoding`, and `content` (base64 encoded).
- `gh repo read-dir [<path>] [--ref <ref>] [--json <fields>] [--jq <expr>]` lists
  a directory; with no path it lists the repo root. Non-TTY output is tab
  separated as type, name, octal mode, and byte size. `--json` fields include
  `name`, `path`, `type`, `gitType`, `mode`, `modeOctal`, `gitSHA`, `size`, and
  `submodule`. A path pointing at a file errors and points you at `read-file`
  (and vice versa).

## Discussions (`gh discussion`)

Preview command set, subject to change. `--json`/`--jq`/`--template` are
available on `list` and `view` only; `create` and `edit` print the discussion
URL, and `comment` prints the comment (or reply) URL. The write subcommands are
approval-gated.

- `gh discussion list [--state open|closed|all] [--category <name>] [--author
  <handle>] [--label <name>,...] [--answered] [--search <query>] [--sort
  created|updated] [--order asc|desc] [--limit N] [--after <cursor>] [--json
  <fields>] [--web]` lists a repo's discussions. `--state` defaults to open,
  `--sort` to updated, `--order` to desc. `--answered` is tri-state
  (`--answered=false` for unanswered) for Q&A categories.
- `gh discussion view {<number>|<url>|<comment-id>|<comment-url>} [--comments]
  [--order oldest|newest] [--limit N] [--after <cursor>] [--json <fields>]
  [--web]` shows a discussion's body; add `--comments` for its comments, or pass
  a comment ID/URL as the argument to list that comment's replies (no `--replies`
  flag; `--comments` is rejected with a comment argument). `--order` (default
  newest), `--limit`, and `--after` apply only to comment and reply listings.
- `gh discussion create [--title <t>] [--body <b> | --body-file <path>]
  [--category <name>] [--label <name>,...]` creates a discussion. `--title`, a
  body (`--body` or `--body-file`), and `--category` are required
  non-interactively; omitting any prompts on a terminal.
- `gh discussion edit {<number>|<url>} [--title <t>] [--body <b>] [--body-file
  <path>] [--category <name>] [--add-label <name>,...] [--remove-label
  <name>,...]` edits title, body, category, or labels.
- `gh discussion comment {<number>|<discussion-url>|<comment-id>|<comment-url>}
  [--body <b>] [--body-file <path>] [--edit] [--delete] [--yes]` adds a top-level
  comment (given a discussion) or a reply (given a comment); `--edit` or
  `--delete` updates or removes a comment/reply and needs a comment ID or URL.
  `--yes` skips the `--delete` confirmation.
