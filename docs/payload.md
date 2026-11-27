# The payload: layout, links, and generated outputs

Where everything in this repository lives, where `mac` links it on the machine,
and which client copies are generated rather than linked. The rules for editing
it are in [`AGENTS.md`](../AGENTS.md).

## Repository layout

```
mac                     # the provisioner (POSIX sh, shellcheck-clean)
README.md               # human-facing docs — update alongside `mac`
CONTEXT.md              # this repo's glossary — what its own words mean
docs/verification.md    # what check-payload covers, fixtures, evals, spelling, CI
docs/payload.md         # this file: layout, symlink map, generated outputs, overlay
docs/client-parity.md   # the policy map across Claude Code, Codex, and Cursor
docs/provenance.md      # vendored and derived skills and rules
docs/adr/               # architecture decision records, numbered sequentially
skills-lock.json        # provenance + content hashes for vendored skills (tool-owned)
skills-provenance.json  # source lineage for first-party derived skills (hand-owned)
rules-provenance.json   # source lineage for derived rules (hand-owned)
cspell.json             # spell check: dictionaries, project words, ignore paths
srt-settings.json       # srt (sandbox-runtime) config → ~/.srt-settings.json (global)
trivy.yaml              # global Trivy config → ~/.config/trivy/trivy.yaml (fallback when a repo ships none)
bin/elixir-ls-mcp       # shim → ~/.bin/elixir-ls-mcp: bridges ElixirLS MCP TCP to stdio
bin/srt                 # shim → ~/.bin/srt: npx --package=@anthropic-ai/sandbox-runtime srt
bin/trivy               # shim → ~/.bin/trivy: apply the global Trivy config only when no ./trivy.yaml exists
scripts/                # verification tooling; each relocates to the repo root itself
  check-payload         # static verification of the payload (POSIX sh + jq)
  gen-cursor-rules      # renders .cursor/rules/*.mdc from rules/*.md (mac + check-payload)
  gen-codex-agents      # renders .codex/generated-agents/*.toml from agents/*.md
  gen-cursor-agents     # renders .cursor/generated-agents/*.md: model reset to inherit
  run-trigger-evals     # runs spec/trigger-evals; needs a logged-in claude CLI
  lib/run_eval_local.py # trigger-eval engine: drives claude -p against installed skills
spec/                   # verification tests and fixtures
  codex_policy_test.py   # offline command-hook regressions (Python 3.11+ and jq)
  check_locales_test.py  # translate-locales checker regressions (needs ruby)
  rules-cases.txt       # path -> which rules/ load for it
  agents-fixture/       # every agent-definition violation; proves the check fires
  invocability-fixture/ # deliberate violations; proves the check still fires
  local-overlay-fixture/ # placeholder; local overlay detection is self-tested inline in check-payload
  orphan-fixture/       # unreachable references + stale anchors; proves the checks fire
  srt-shim-fixture/     # a self-wrapping, unpinned bin/srt; proves the shim check fires
  env-parity-fixture/   # .env deny lists drifting within a file; proves the parity check fires
  trigger-evals/*.json  # query sets for skill triggering (run by hand, not CI)
.agents/
  AGENTS.md             # global engineering standards (shipped to ~/.claude/CLAUDE.md)
  CONTEXT.md            # root context map — machine-local, git-ignored (optional)
  local/                # machine-local overlay — git-ignored; see "Local overlay" below
    skills/<name>/      # overlaid skills linked into skills/ by mac
    rules/<name>.md     # overlaid rules linked into rules/ by mac
  references/           # prose shipped to ~/.agents/references, read on demand
    CONTEXT-FORMAT.md   # template for .agents/CONTEXT.md
    SANDBOX.md          # sandbox failure workarounds (gh keychain, pipe trap, pnpm, ps/pgrep)
  skills/               # skill bodies: vendored + project-only (project-only = not linked from skills/)
rules/                  # path-scoped language standards, auto-loaded by glob
agents/                 # subagents → ~/.agents/agents → ~/.claude/agents
skills/                 # published skills → ~/.agents/skills; first-party dirs + symlinks into .agents/skills
.claude/settings.json   # Claude Code settings (permissions, sandbox, hooks, plugins)
.codex/                 # Codex config — mirrors .claude/settings.json
  config.toml.template  # permissions, sandbox, env scrub, hooks — mac renders git-ignored config.toml
  rules/default.rules   # prefix rules — mirror of the Claude deny/ask lists
  generated-agents/     # .toml agents — mac renders from agents/, git-ignored
.cursor/                # Cursor CLI config — mirrors the same policy
  cli-config.json       # permissions.deny lists, approvalMode, attribution-off
  hooks.json            # beforeShellExecution: command log + destructive-command gate
  rules/                # generated .mdc rules — mac renders from rules/, git-ignored
  generated-agents/     # Cursor's copy of agents/ — mac renders it, git-ignored
.github/workflows/      # CI
```

## Symlink map

`mac` (see `symlink_path`, near the end of the script) creates these links.
Directories are linked, not copied, so an edit in the repository is live for
every client at once
([ADR 0001](adr/0001-symlink-the-payload-instead-of-copying.md)).
`symlink_path` moves any pre-existing real file to `<path>.backup` before
linking; check for stray `.backup` files if a link looks wrong.

| Link | Target |
| --- | --- |
| `~/.agents/AGENTS.md` | `.agents/AGENTS.md` |
| `~/.agents/rules` | `rules/` |
| `~/.agents/skills` | `skills/` |
| `~/.agents/references` | `.agents/references/` |
| `~/.agents/.skills-lock.json` | `skills-lock.json` |
| `~/.agents/agents` | `agents/` |
| `~/.agents/CONTEXT.md` | `.agents/CONTEXT.md` (when present) |
| `skills/<name>` | `../.agents/local/skills/<name>` (when present; git-excluded) |
| `rules/<name>.md` | `../.agents/local/rules/<name>.md` (when present; git-excluded) |
| `~/.claude/CLAUDE.md` | `~/.agents/AGENTS.md` |
| `~/.claude/rules` | `~/.agents/rules` |
| `~/.claude/skills` | `~/.agents/skills` |
| `~/.claude/agents` | `~/.agents/agents` |
| `~/.claude/settings.json` | `.claude/settings.json` |
| `~/.claude/CONTEXT.md` | `~/.agents/CONTEXT.md` |
| `~/.codex/AGENTS.md` | `~/.agents/AGENTS.md` |
| `~/.codex/rules` | `.codex/rules/` |
| `~/.codex/skills` | `~/.agents/skills` |
| `~/.codex/agents` | `.codex/generated-agents` (rendered from `agents/`) |
| `~/.codex/config.toml` | `.codex/config.toml` (rendered by `mac` from `.codex/config.toml.template`) |
| `~/.codex/CONTEXT.md` | `~/.agents/CONTEXT.md` |
| `~/.cursor/cli-config.json` | `.cursor/cli-config.json` |
| `~/.cursor/hooks.json` | `.cursor/hooks.json` |
| `~/.cursor/agents` | `.cursor/generated-agents` (rendered from `agents/`) |
| `~/.cursor/rules` | `.cursor/rules` (rendered by `mac` from `rules/` via `scripts/gen-cursor-rules`) |
| `~/.cursor/CONTEXT.md` | `~/.agents/CONTEXT.md` |
| `~/.srt-settings.json` | `srt-settings.json` |
| `~/.config/trivy/trivy.yaml` | `trivy.yaml` |
| `~/.bin/elixir-ls-mcp` | `bin/elixir-ls-mcp` |
| `~/.bin/srt` | `bin/srt` |
| `~/.bin/trivy` | `bin/trivy` |

`mac` also provisions nine real directories under `~/.agents/` — `standup`,
`out-of-scope`, `lore`, `specs`, `plans`, `prds`, `slices`, `adr`, `handoffs` —
not symlinks, because Codex's Seatbelt sandbox rejects symlinked writable roots
([ADR 0008](adr/0008-provision-agent-state-as-real-directories.md)).

## Generated outputs

Four client copies are rendered by `mac`, git-ignored, and overwritten on the
next run. Edit the source and re-run `sh mac`.

| Output | Source | Why generated |
| --- | --- | --- |
| `.codex/config.toml` | `.codex/config.toml.template` | Codex needs an absolute Unix-socket path and does not expand `~` |
| `.cursor/rules/*.mdc` | `rules/*.md` via `scripts/gen-cursor-rules` | Cursor loads only `.mdc` and scopes with a bare `globs:` string, not `paths:` ([ADR 0018](adr/0018-generate-cursor-rules-from-canonical-rules.md)) |
| `.codex/generated-agents/*.toml` | `agents/*.md` via `scripts/gen-codex-agents` | Codex reads TOML agents ([ADR 0025](adr/0025-per-agent-models-are-claude-only.md)) |
| `.cursor/generated-agents/*.md` | `agents/*.md` via `scripts/gen-cursor-agents` | Cursor's copy resets the model to inherit ([ADR 0025](adr/0025-per-agent-models-are-claude-only.md)) |

Claude reads `rules/` and `agents/` through its own live links, so it needs no
re-run.

`.agents/CONTEXT.md` is optional and machine-local. `mac` creates the four
`CONTEXT.md` links only when it exists, so run `sh mac` after you first create
one; copy `.agents/references/CONTEXT-FORMAT.md` to start. A new agent client
added here should mirror that link into its own dotdir.

## Local overlay

Internal (non-public) skills and rules that must not be tracked live in
`.agents/local/skills/<name>/` and `.agents/local/rules/<name>.md`. The
top-level `.agents/local/` is excluded in `.gitignore`; individual linked names
are excluded by `.git/info/exclude` so `git status` stays clean. `mac` links
each overlay entry into `skills/` or `rules/` with a relative target and
registers the name in the per-clone exclude file. Links are idempotent; dangling
links (from a removed overlay entry) are pruned on the next run.

The canonical way to populate the overlay is `tablekit-config skills install`:

```sh
cd ~/Codespace/portal-frontend   # any project with @tablecheck/tablekit-*
npx tablekit-config skills install tablekit-css tablekit-react \
  --dir ~/Codespace/laptop/.agents/local/skills
sh ~/Codespace/laptop/mac
```

Refresh with `npx tablekit-config skills update --dir ...` and re-run `mac`.

`check-payload` identifies overlay links by their `readlink` target and skips
them in every linting loop — they never appear in CI, which runs without the
overlay. An overlay skill is global and pinned to the package version it was
last exported from. Projects that vendor their own copy (e.g.
`portal-frontend/.claude/skills/`) take precedence because the project scope
wins over the user scope in Claude Code's resolution order
([ADR 0023](adr/0023-local-overlay-for-internal-skills-and-rules.md)).

A worktree or fresh checkout has no overlay links; re-run `mac` (just the
linking block suffices) to restore them.
