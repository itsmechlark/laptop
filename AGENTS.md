# itsmechlark/laptop

Provisions a macOS machine for web and mobile development (`mac`, one POSIX
`sh` script), and carries the maintainer's AI-agent configuration as a second
payload that `mac` links into `~/.agents`, `~/.claude`, `~/.codex`, and
`~/.cursor`. No build step, no package manager, no application code;
verification uses POSIX shell, `jq`, and stdlib Python.

- `AGENTS.md` (this file) is for working on this repository. `.agents/AGENTS.md`
  is cargo: the global standards shipped to every project on the machine, so
  any edit to it changes agent behavior in every repository.
- Root `CLAUDE.md` is a symlink to this file. Edit `AGENTS.md`; writing through
  `CLAUDE.md` silently rewrites it.

## Commands

Run from the repository root. Install the linters with
`brew install shellcheck cspell`; `jq` ships with macOS.

| Task | Command |
| --- | --- |
| Lint the provisioner | `shellcheck mac -e SC2039` (SC2039 excluded deliberately) |
| Lint the scripts | `shellcheck scripts/check-payload scripts/run-trigger-evals scripts/gen-cursor-rules scripts/gen-codex-agents scripts/gen-cursor-agents` (no exclusions) |
| Compile the eval engine | `python3 -m py_compile scripts/lib/run_eval_local.py` |
| Verify the payload | `sh scripts/check-payload` |
| Hook regression tests | `python3 spec/codex_policy_test.py -v` (Python 3.11+ and `jq`) |
| Locale checker tests | `python3 spec/check_locales_test.py -v` (`RUBY=/usr/bin/ruby` for Ruby 2.6) |
| Description overlap report | `sh scripts/check-payload --collisions` |
| Spelling | `cspell lint --no-progress --dot "**/*"` |
| Run the provisioner | `sh mac 2>&1 \| tee ~/laptop.log` — mutates the machine; keep the log |

## Layout

The full tree, every link `mac` creates, and the generated copies are in
[`docs/payload.md`](docs/payload.md).

| Path | What |
| --- | --- |
| `mac` | The provisioner; `README.md` documents it for people |
| `.agents/AGENTS.md`, `rules/`, `skills/`, `agents/`, `.agents/references/` | Agent configuration `mac` installs on every machine: linked, except the generated copies Codex and Cursor read |
| `.claude/settings.json`, `.codex/`, `.cursor/` | One policy in three client schemas — see [parity](#agent-client-configuration-parity) |
| `.agents/skills/` | Vendored skill bodies, plus project-only skills never linked from `skills/` |
| `.agents/local/` | Git-ignored overlay of internal skills and rules, linked in by `mac` |
| `scripts/`, `spec/` | Verification code and the fixtures it reads |

## Conventions

### Editing the payload

- Edit through the repo path, never the home symlink: the sandbox lets you write
  `.claude/settings.json` or `skills/foo/SKILL.md`, not `~/.claude/…` or
  `~/.agents/…`, though both resolve to the same file.
- Directories are linked, so an edit is live at once. Re-run `sh mac` only
  after adding a top-level link, editing `.codex/config.toml.template`, a
  `rules/*.md`, or an `agents/*.md`, first creating `.agents/CONTEXT.md`, or
  adding or removing an entry under `.agents/local/`.
- Never edit `.codex/config.toml`, `.cursor/rules/`, `.codex/generated-agents/`,
  or `.cursor/generated-agents/`: `mac` regenerates them from their sources.
- A link or provisioned path added to `mac` updates the symlink map in
  `docs/payload.md` and README's matching section in the same commit; a new
  `scripts/` or `spec/` entry updates the tree there.
- Skills and rules that must not be tracked go in `.agents/local/`, never
  `skills/` or `rules/` directly; the overlay is described in
  [`docs/payload.md`](docs/payload.md#local-overlay).

### Agent-client configuration parity

- Claude Code, Codex, and Cursor run one security policy; `.claude/settings.json`
  is canonical. Any change to one client's permission, sandbox, hook, env, or
  network/filesystem policy is mirrored into every other client in the same
  commit. Find each counterpart in
  [`docs/client-parity.md`](docs/client-parity.md) and update its row there.
- When a client has no equivalent, note the gap in the commit message. Model
  choice, reasoning effort, and `enabledPlugins` are per-client tuning, not
  policy.
- The client configs are a security boundary. Widening one is deliberate:
  justify it in the commit message.
- `.env` variants are denied by name (plus `.env.*.*`) because globs cannot
  exempt `.env.example` and `.env.sample`. A new `.env.<name>` needs an entry in
  every client; `check-payload` fails when the lists differ.
- `srt-settings.json` is the whole boundary for an `srt`-wrapped command and is
  read-only in every client
  ([ADR 0015](docs/adr/0015-second-line-sandbox-for-unsafe-commands.md)).

### Shell: `mac` and `scripts/`

- Target `#!/bin/sh`, two-space indent, and announce each phase with
  `fancy_echo` in the `"Doing thing ..."` style.
- Every `mac` operation is idempotent: follow the install-or-update shape
  (`gem_install_or_update`, `add_or_update_asdf_plugin`, `symlink_path`).
- `set -e` and the `trap ... EXIT` abort `mac` on any unguarded non-zero exit;
  guard optional steps explicitly.
- Homebrew packages go in the `brew bundle --file=- <<EOF` heredoc under its
  existing comment headings, and README's "What it sets up" list changes in the
  same commit.
- Scope a `# shellcheck disable=` as narrowly as possible, next to the line it
  excuses. The file-wide SC3043 at the top of `mac` is the deliberate
  exception: `mac` uses `local`.
- User-specific setup belongs in `~/.laptop.local`, never in `mac`.
- `check-payload` has no `set -e` on purpose: it reports every failure in one
  pass. `scripts/run-trigger-evals` stops at the first. Keep Python stdlib-only.
- A new `check-payload` check must be deterministic and file-local; anything
  needing a model or a network call is a trigger eval
  ([`docs/verification.md`](docs/verification.md)).

### Skills, rules, and agents

- A skill's `name` matches its directory; its `description` leads with the
  capability and names concrete trigger phrases. Long material goes in
  `references/*.md`, scaffolds the agent fills in go in `templates/`, and only
  files emitted byte-for-byte go in `assets/`
  ([ADR 0017](docs/adr/0017-scaffolds-are-templates-not-assets.md)).
- First-party skills co-ship, so name each other directly ("that's
  `code-review`"). For a sibling with `disable-model-invocation: true`, say
  "read its `SKILL.md`", never "invoke": the Skill tool refuses it.
- Flag a skill `disable-model-invocation: true` where a wrong auto-invocation is
  expensive. Where the expense is a side effect, the body carries the guard too,
  since Codex and Cursor ignore the flag
  ([ADR 0003](docs/adr/0003-model-invocation-flag-is-claude-only.md)).
- A rule's `paths:` list is the source of truth; author only `rules/*.md` and
  keep the body terse. Cursor's `.mdc` copy is generated
  ([ADR 0018](docs/adr/0018-generate-cursor-rules-from-canonical-rules.md)).
- An agent wraps skills, never restates them, and never needs the user
  ([ADR 0024](docs/adr/0024-subagents-wrap-skills-for-fresh-context-work.md),
  [ADR 0025](docs/adr/0025-per-agent-models-are-claude-only.md)).
- Never hand-edit a vendored skill under `.agents/skills/`; re-vendor it. A
  derived skill or rule changes together with its provenance record and its
  `## Attribution` section ([`docs/provenance.md`](docs/provenance.md)).
- Project-only skills (such as `update-provenance`) live in `.agents/skills/`
  and are never linked from `skills/`, so they don't ship.
- In `.agents/references/SANDBOX.md`, describe each failure by its symptom and
  fix it in plain shell. Client-specific facts go in its "Harness mechanics"
  table, one column per client. A heading names a client only when the
  behavior is wholly that client's; say "verified under X" or "untested"
  rather than imply a claim holds everywhere. Its frontmatter `description` and
  the pointer in `.agents/AGENTS.md` name symptoms, not clients. Its "Excluded
  commands" row copies `sandbox.excludedCommands` verbatim and changes in the
  same commit.

### Docs and commits

- Match the surrounding Markdown: `README.md` uses setext headings and
  reference-style links; `.agents/` and `skills/` use ATX headings. Spelling is
  `en-US`.
- A new check or fixture a contributor must satisfy is documented in README's
  "Testing your changes" and in `docs/verification.md` in the same commit.
- A term that leaves the repo leaves `CONTEXT.md` in the same commit. Never
  rewrite an accepted ADR; supersede it with the next number.
- `CONTEXT.md` at the root is the repo's glossary; `.agents/CONTEXT.md` is the
  git-ignored machine map. Never put a domain term in the map or a machine path
  in the glossary.
- Conventional Commits. The payload and provisioner (`.agents/`, `.claude/`,
  `.codex/`, `.cursor/`, `rules/`, `skills/`, `agents/`, `mac`, and the three
  provenance and lock files) are production code: a code type, never `docs`.
  `docs` is for `README.md`, `AGENTS.md`, `SECURITY.md`, `CONTEXT.md`, and
  `docs/`.
- Scopes: `mac`, `skills`, `agents`, `claude`, `codex`, `cursor`, `srt`, `ci`.
  `check-payload` and `spec/` take a code type under `ci`; a new fixture is
  described by what it now catches.
- No secrets, tokens, or personal paths in tracked files; machine-specific
  values go in `.agents/CONTEXT.md` or `~/.laptop.local`.

## Done

Both CI jobs enforce these; detail is in
[`docs/verification.md`](docs/verification.md#ci).

- `shellcheck mac -e SC2039` and the scripts shellcheck in
  [Commands](#commands) are clean, and the eval engine byte-compiles.
- `sh scripts/check-payload` exits zero. Warnings may stand; failures never
  do, payload included.
- `python3 spec/codex_policy_test.py` and `python3 spec/check_locales_test.py`
  pass, and `cspell lint --no-progress --dot "**/*"` exits zero.
- A change to `mac` is run on a fresh macOS VM. Say so plainly when you only
  linted it; shellcheck passing is not a run.
- A changed skill `description` runs its trigger eval in `spec/trigger-evals/`
  when one exists. It needs a terminal, so say so when you skipped it.

## References

| Need | File |
| --- | --- |
| Glossary | `CONTEXT.md` |
| Decisions | `docs/adr/` |
| Repository tree, symlink map, generated copies, overlay | `docs/payload.md` |
| Policy counterparts across clients, Cursor's gaps | `docs/client-parity.md` |
| Vendored and derived skills, provenance records | `docs/provenance.md` |
| What `check-payload` covers, fixtures, evals, spelling, CI | `docs/verification.md` |
| Installing and customizing the machine | `README.md` |
| Reporting a vulnerability | `SECURITY.md` |
| Commit and PR templates | the `git-commit` and `pull-request` skills |

## Gotchas

- `mac` runs `sudo chsh` and appends to `~/.zshrc`; never run it to "check
  something".
- A worktree or fresh checkout has no `.agents/local/` overlay links; re-run
  `mac`'s linking block to restore them. CI never sees the overlay.
- The nine `~/.agents/` state directories are real directories, not links,
  because Codex's sandbox rejects symlinked writable roots
  ([ADR 0008](docs/adr/0008-provision-agent-state-as-real-directories.md)).
- Those directories other than `standup` are fallbacks: a skill writes into a
  repository only where the matching directory already exists, and otherwise
  records `metadata.repo` (the name, never a path) in the global root
  ([ADR 0014](docs/adr/0014-fall-back-to-a-global-home-when-the-repo-has-not-opted-in.md)).
  A codebase-specific rejection goes in that repo's `.out-of-scope/` when it has
  one, else the global root marked `scope: project`.
- Edit the root `skills-lock.json`, not the git-ignored
  `.agents/.skills-lock.json` link back to it.
- Sandboxed Bash cannot write `~/.claude/projects/**`, even though `~/.claude`
  is writable, so an agent cannot `rm` its own auto-memory. Retire a memory in
  place (tombstone the body, drop its `MEMORY.md` pointer)
  ([ADR 0018](docs/adr/0018-allow-sandboxed-pruning-of-claude-auto-memory.md)).
- asdf goes on `PATH` through `${ASDF_DATA_DIR:-$HOME/.asdf}/shims`, never by
  sourcing `asdf.sh` (commit `0f46cb9`); don't regress it.
- `mac` installs the latest Ruby and Node asdf reports, so runs on different
  days differ by design.
