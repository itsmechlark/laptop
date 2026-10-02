# gh CLI: attaching images and videos

> Keep every `gh` below a single bare command — no pipe, redirect, or `$(...)` —
> so it runs unsandboxed and reaches the keychain. `--attach` uploads, so the
> command is a mutating write and is approval-gated. Background:
> [SKILL.md](../SKILL.md) Gotchas and `~/.agents/references/SANDBOX.md`.

`--attach <path>` is available on `gh issue create`, `gh issue edit`, `gh issue
comment`, `gh pr create`, `gh pr edit`, and `gh pr comment` — shared by the
[ISSUES.md](ISSUES.md) and [PULL-REQUESTS.md](PULL-REQUESTS.md) flows.

- Repeat `--attach` to upload multiple files: `gh issue comment 12 --attach
  ./before.png --attach ./after.png`.
- Each command invocation accepts at most 50 `--attach` values total across
  images and videos.
- Supported files are `png`, `jpg`, `jpeg`, `gif`, `webp`, `svg`, `mp4`, `mov`,
  and `webm`.
- For an image, append alt text to the path after `#`. Quote the value so the
  shell does not treat `#` as a comment: `gh pr create --attach './login.png#The
  login error state'`. Without alt text, the filename is used.
- `--attach` paths and local Markdown destinations may be absolute or relative to
  the directory where `gh` runs.
- If the body references an attached path, `gh` rewrites that Markdown reference
  to the uploaded URL, keeping its existing alt text. Otherwise `gh` appends the
  attachment to the body. For example: `gh pr edit 23 --body '![error](./login.png)'
  --attach ./login.png`.
- Videos cannot take alt text. A standalone `![recording](./repro.mp4)` becomes a
  bare player URL, while an inline video image becomes a link. A reference-style
  video image such as `![recording][clip]` with `[clip]: ./repro.mp4` is
  rejected; use a reference-style link instead.
- `gh issue create` and `gh pr create`: `--attach` cannot be used with `--web`.
  `gh pr create --attach` also cannot be used with `--dry-run`.
- `gh issue edit`: `--attach` can edit only one issue at a time.
- `gh issue comment` and `gh pr comment`: `--attach` cannot be used with `--web`
  or `--delete-last`. It works alone, with `--edit-last`, or with one of
  `--body`, `--body-file`, or `--editor`.
- Uploads require GitHub.com or a GHE.com tenant, an OAuth token, classic PAT, or
  fine-grained PAT, and `WRITE`, `MAINTAIN`, or `ADMIN` repository permission.
  GitHub Enterprise Server and most GitHub App tokens are unsupported.
- Uploads stop at the first failure. If earlier files uploaded, `gh` still writes
  those attachments and exits non-zero. Create and edit commands also print the
  issue or pull request URL.
