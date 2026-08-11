# AGENTS.md

## Project overview

`itsmechlark/laptop` provisions a macOS machine for web and mobile development,
and it carries the maintainer's AI-agent configuration as a second payload.

Two things live here:

1. **`mac`** — a single POSIX `sh` script that installs Homebrew packages, asdf
   language runtimes, and databases. It is idempotent: it installs, upgrades, or
   skips based on what's already on the machine, and is safe to re-run.
2. **Agent configuration** — `.agents/`, `rules/`, `skills/`, `.claude/`,
   `.codex/`, `.cursor/`. The `mac` script symlinks these into `~/.agents`,
   `~/.claude`, `~/.codex`, and `~/.cursor`, so this repo is the single source of
   truth for how coding agents behave on every machine that has run it. Claude
   Code, Codex, and Cursor are three front-ends over one shared policy — see
   "Agent-client configuration parity".

There is no build step, no package manager, and no application code. The only
language is POSIX shell plus Markdown.

### Read this first: two different AGENTS.md files

| File | Scope | Symlinked to |
| --- | --- | --- |
| `AGENTS.md` (this file) | Instructions for working **on this repository** | nowhere |
| `.agents/AGENTS.md` | The maintainer's **global engineering standards**, shipped to every project | `~/.agents/AGENTS.md` → `~/.claude/CLAUDE.md` |

`.agents/AGENTS.md` is cargo, not configuration for this repo. Editing it
changes agent behavior in *every* repository on the machine — treat changes to
it as global blast radius and keep them deliberate.

## Setup commands

Nothing needs installing to work on this repo beyond the linter:

```sh
brew install shellcheck
```

To run the provisioner itself (this mutates the machine — installs packages,
runs `sudo chsh`, and rewrites `~/.zshrc`):

```sh
sh mac 2>&1 | tee ~/laptop.log
```

The run log is the primary debugging artifact; keep the lines where it failed.

## Repository layout

```
mac                     # the provisioner (POSIX sh, shellcheck-clean)
README.md               # human-facing docs — update alongside `mac`
skills-lock.json        # provenance + content hashes for vendored skills (tool-owned)
skills-provenance.json  # source lineage for first-party derived skills (hand-owned)
.agents/
  AGENTS.md             # global engineering standards (shipped to ~/.claude/CLAUDE.md)
  AGENTS.local.md       # machine-local overrides — git-ignored
  skills/               # skill bodies: vendored + project-only (project-only = not linked from skills/)
rules/                  # path-scoped language standards, auto-loaded by glob
skills/                 # published skills → ~/.agents/skills; first-party dirs + symlinks into .agents/skills
.claude/settings.json   # Claude Code settings (permissions, sandbox, hooks, plugins)
.codex/                 # Codex config — mirrors .claude/settings.json
  config.toml           # permissions, sandbox, env scrub, hooks
  rules/default.rules   # prefix rules — mirror of the Claude deny/ask lists
.cursor/                # Cursor CLI config — mirrors the same policy
  cli-config.json       # permissions.deny lists, approvalMode, attribution-off
  hooks.json            # beforeShellExecution: command log + destructive-command gate
.github/workflows/      # CI
```

### Symlink map

`mac` (see `symlink_path`, near the end of the script) creates:

| Link | Target |
| --- | --- |
| `~/.agents/AGENTS.md` | `.agents/AGENTS.md` |
| `~/.agents/rules` | `rules/` |
| `~/.agents/skills` | `skills/` |
| `~/.agents/.skills-lock.json` | `skills-lock.json` |
| `~/.claude/CLAUDE.md` | `~/.agents/AGENTS.md` |
| `~/.claude/rules` | `~/.agents/rules` |
| `~/.claude/skills` | `~/.agents/skills` |
| `~/.claude/settings.json` | `.claude/settings.json` |
| `~/.codex/AGENTS.md` | `~/.agents/AGENTS.md` |
| `~/.codex/rules` | `.codex/rules/` |
| `~/.codex/skills` | `~/.agents/skills` |
| `~/.codex/config.toml` | `.codex/config.toml` |
| `~/.cursor/cli-config.json` | `.cursor/cli-config.json` |
| `~/.cursor/hooks.json` | `.cursor/hooks.json` |

**Consequence:** because directories are linked (not copied), editing a rule or
skill in this repo takes effect immediately — no re-run of `mac` required. Only
adding a *new top-level* link needs `sh mac` again. `symlink_path` moves any
pre-existing real file to `<path>.backup` before linking; check for stray
`.backup` files if a link looks wrong.

## Agent-client configuration parity

Claude Code, Codex, and Cursor are three front-ends over **one** security and
behavior policy. `.claude/settings.json` is the canonical expression of that
policy in Claude's schema; `.codex/config.toml` and `.codex/rules/default.rules`
translate the *same* policy into Codex's (their own comments call it "the
translated Claude policy"); `.cursor/cli-config.json` and `.cursor/hooks.json`
translate it into Cursor's. They are mirrors of each other, not independent
configs.

Claude and Codex are allow-by-default with deny/ask exceptions; Cursor is
prompt-by-default (`approvalMode: "allowlist"`) with allow exceptions. Identical
UX across the three is therefore impossible — the shared target is **security**
parity: the same secret-path and destructive-command denials, the same
attribution-off default, and the same command log plus worktree-convention gate.

**The invariant: any change to one client's permission, sandbox, hook, env, or
network/filesystem policy must be mirrored into every other client's config in
the same commit.** Tightening a deny in `.claude/settings.json` while leaving
`.codex/rules/default.rules` open defeats the point — a machine that has run
`mac` runs all three clients off these files. The same obligation extends to any
future AI tool or agentic client added here: give it a payload under its own
dotdir, wire it into `mac`'s symlink block, and hold it to this parity.

Use this map to find the counterpart for a change:

| Policy | Claude (`.claude/settings.json`) | Codex (`.codex/…`) | Cursor (`.cursor/…`) |
| --- | --- | --- | --- |
| Blocked commands | `permissions.deny` — `Bash(…)` | `rules/default.rules` — `decision = "forbidden"` | `cli-config.json` `permissions.deny` — `Shell(…)` (wholesale) + `hooks.json` gate (arg-nuanced) |
| Approval-gated commands | `permissions.ask` — `Bash(…)` | `rules/default.rules` — `decision = "prompt"` | `approvalMode: "allowlist"` — prompts on any unlisted command |
| Unreadable secret paths | `permissions.deny` — `Read(…)` | `config.toml` filesystem `"deny"` entries | `cli-config.json` `permissions.deny` — `Read(…)` |
| Writable / readable roots | `sandbox.filesystem.allowWrite` / `allowRead` | `config.toml` `[permissions.developer.filesystem]` | — (no sandbox roots; `permissions.deny` `Write(…)` guards the policy files only) |
| Allowed network hosts | `sandbox.network.allowedDomains` | `config.toml` `[permissions.developer.network.domains]` | — (no egress allowlist; `WebFetch(domain)` scopes only the agent's fetch tool) |
| Unix sockets | `sandbox.network.allowUnixSockets` | `config.toml` `[…network.unix_sockets]` (absolute path) | — |
| Env-var scrubbing | `env` (`CLAUDE_CODE_SUBPROCESS_ENV_SCRUB`) | `config.toml` `[shell_environment_policy.filters]` | — |
| Lifecycle hooks | `hooks.PreToolUse` | `config.toml` `[[hooks.PreToolUse]]` | `hooks.json` `beforeShellExecution` |

Not everything mirrors: model choice, reasoning effort, and Claude's
`enabledPlugins` are per-client tuning, not shared policy, and need no
counterpart. When a policy genuinely has no equivalent in a client, note the gap
in the commit message rather than silently dropping it. Cursor's gaps, recorded
here rather than dropped:

- **No sandboxed egress or filesystem roots.** Cursor has no counterpart to
  Claude's `sandbox.network.allowedDomains` / `filesystem` roots or Codex's
  `[permissions.developer]`; `WebFetch(domain)` governs only the agent's own
  fetch tool, not general subprocess egress. Deny-listing secret *paths* is the
  reachable half of that policy, and it is mirrored.
- **No env-var scrub.** No counterpart to `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` /
  Codex `[shell_environment_policy.filters]`.
- **The ask tier is implicit.** `approvalMode: "allowlist"` prompts on every
  command not explicitly allowed, so there is no per-command "ask" list to
  mirror — the empty `permissions.allow` is what realizes it.
- **Arg-nuanced blocks live in the hook.** Cursor `Shell()` keys on the command
  base, so wholesale-dangerous commands (`dd`, `sudo`, `mkfs`, …) are declarative
  `permissions.deny` entries, while forms distinguished by their arguments
  (`rm -rf`, `git push --force`, `git reset --hard`, `chmod 777`) are enforced by
  the `beforeShellExecution` gate. The gate is fail-open — a crash lets the
  command fall through to the normal approval prompt, matching the other clients'
  fail-open hooks — and the declarative `Shell()` denies are the always-on floor.
- **`~` home-glob reach is an assumption.** Cursor documents relative/absolute
  globs but not `~` expansion in `permissions` patterns; the `Read(~/…)` denials
  are best-effort, while in-workspace secrets are covered by reliable `**/` globs
  regardless.
- **No MCP drop-tool denies.** Claude's MongoDB `drop-*` MCP denials have no
  Cursor counterpart because that MCP is not wired into Cursor.
- **`sandbox.mode` / `networkAccess` omitted.** Their accepted enum values are
  undocumented; guessing risks breaking the whole config, so they are left unset.

## Testing instructions

There is no unit test suite. Verification is lint plus a real run.

```sh
shellcheck mac -e SC2039     # must be clean; SC2039 is excluded deliberately
```

CI (`.github/workflows/tests.yml`, on push to `main`, every PR, and
`workflow_dispatch`) runs a matrix of `macos-26` and `macos-15` with
`fail-fast: false`, and does:

1. `brew update`
2. `brew install shellcheck`
3. `shellcheck mac -e SC2039`
4. Unlink Homebrew's preinstalled `node` if present (runner-only workaround —
   the guard is `brew list node` so it never fails on runners without it)
5. `sh mac`

For changes to `mac`, the real test is a run on a **fresh macOS install**. Use a
[UTM] VM: prepare one machine with macOS installed and first launch complete,
then duplicate it before each test run. CI covers the happy path on a runner,
which is not the same as a clean laptop.

State plainly when you have only linted and not executed the script — do not
claim a `mac` change works because shellcheck passed.

[UTM]: https://mac.getutm.app

## Code style

### `mac` (POSIX shell)

- Target `#!/bin/sh`, not bash. `local` is used and SC3043 is disabled
  file-wide; SC2039 is excluded at the call site.
- **Every operation must be idempotent.** Follow the existing
  install-or-update shape (`gem_install_or_update`, `add_or_update_asdf_plugin`,
  `symlink_path` returning early when the link already matches). Re-running the
  script must be a no-op.
- Announce each phase with `fancy_echo`, matching the `"Doing thing ..."` style.
- Two-space indent. `set -e` plus the `trap ... EXIT` at the top mean any
  unguarded non-zero exit aborts the run — guard optional steps explicitly.
- Homebrew packages go in the `brew bundle --file=- <<EOF` heredoc, grouped by
  the existing comment headings (`# Unix`, `# GitHub`, `# Databases`, …).
- Scope `# shellcheck disable=` directives as narrowly as possible and leave
  them adjacent to the line they excuse.
- Anything user-specific belongs in `~/.laptop.local`, which is sourced at the
  end of the run — not in `mac`.

### `skills/<name>/SKILL.md`

YAML frontmatter then Markdown:

```markdown
---
name: kebab-case-name          # must match the directory name
description: What it does, and the triggers that should invoke it.
argument-hint: "[what the argument means]"   # optional
disable-model-invocation: true               # optional; user-invoked only
---
```

The `description` is what an agent matches against, so lead with the capability
and spell out concrete trigger phrases. Long-form material goes in
`skills/<name>/references/*.md` rather than bloating `SKILL.md`.

### `rules/<lang>.md`

Frontmatter is a glob list controlling when the rule auto-loads:

```markdown
---
paths:
  - "**/*.rb"
  - "**/Gemfile"
---
```

### Vendored skills

Third-party skills live in `.agents/skills/<name>/`, are recorded in
`skills-lock.json` with their source and content hash, and are exposed through a
symlink at `skills/<name>` → `../.agents/skills/<name>`. Don't hand-edit vendored
content: it desynchronizes the recorded hash. Re-vendor from upstream and update
`skills-lock.json` instead.

### Derived skills

First-party skills we authored by adapting or drawing on outside material are
tracked in `skills-provenance.json` (hand-owned; the `npx skills` tool never
touches it). Vendored vs. derived is one record per skill, in the file whose
owner won't clobber it: verbatim copies → `skills-lock.json`; things we wrote
ourselves from a source → `skills-provenance.json`.

Each skill maps to a **list** of sources, because one skill can draw on several
(e.g. `agent-skills` adapts awesome-copilot, conforms to the agentskills.io
spec, and cites anthropics/skills for examples). Every source carries its own
`relationship`, which decides how it syncs:

- `adapted` — forked then diverged; pinned to a `ref`. Update = 3-way reconcile
  (`git diff <ref>..HEAD -- <path>`, port the non-conflicting upstream changes),
  then bump that source's `ref` + `reviewed`. Never overwrite.
- `spec` — conforms to an external spec; watch the spec URL/version.
- `inspired-by` — ideas/terminology only, no `ref`; attribution, not synced.

Keep the human-readable `## Attribution` section in each derived SKILL.md as
the reader-facing attribution; its flat-list format is defined by the
`agent-skills` skill, and `skills-provenance.json` is its machine-readable
mirror.

**Update the provenance whenever a first-party skill changes** — it is part of
the change, not a follow-up:

- Authored a new skill from outside material → add a `skills.<name>` entry with
  one source per influence.
- Drew on a new influence for an existing skill → append a source to its list.
- Reconciled an upstream change into an `adapted` or `spec` source → bump that
  source's `ref` (and, for `spec`, its version) and its `reviewed` date.
- Edited a skill with no upstream source, or made a purely local change → no
  `ref` change; `inspired-by` sources never carry one.

Run the `update-skills` project skill (see below) to detect upstream drift and
walk the reconcile per skill; it reads and writes `skills-provenance.json`. When
you edit provenance by hand, keep this file and the SKILL.md `## Attribution` section in sync.

### Project-only skills

Some skills exist only to maintain *this* repo and must not ship to every
machine. Their bodies live in `.agents/skills/<name>/` alongside the vendored
ones, but — unlike vendored and first-party skills — they are deliberately **not**
linked from `skills/`, so `mac`'s `skills/` → `~/.agents/skills` chain never
carries them off this repo. They are available only when working inside this
repository. `update-skills` is one: it keeps `skills-provenance.json` in sync
with its sources and is scoped to this repo's skill set, so it stays here.

### Markdown

Match the surrounding file. `README.md` uses setext underlined headings and
reference-style links; the `.agents/` and `skills/` Markdown uses ATX (`##`)
headings. Keep prose wrapped at roughly the width already in the file.

## Documentation

`README.md` is the human-facing counterpart to this file. When you change `mac`
— especially the `brew bundle` list or what gets symlinked — update the
corresponding README section in the same commit. The "What it sets up" list is
expected to stay in sync with the heredoc.

## Commit and pull request guidelines

- **Never commit or push unless explicitly asked.** A one-time approval covers
  that instance only.
- **Never add AI attribution** — no `Co-Authored-By` AI trailer, no "Generated
  with …" footer. `.claude/settings.json` sets `attribution.commit` to empty to
  enforce this.
- Conventional Commits, imperative mood. Scopes in use here: `mac`, `skills`,
  `agents`, `claude`, `codex`, `cursor`, `ci`, `docs` — e.g. `fix(mac): set up
  asdf via PATH instead of asdf.sh`, `feat(skills): add create-agentsmd skill`.
- Keep PRs single-purpose; separate refactors from behavior changes.
- Required before opening a PR: `shellcheck mac -e SC2039` clean, and a fresh-VM
  run for anything touching `mac`.
- `@itsmechlark` owns every path via `CODEOWNERS` and reviews all PRs.

The `git-commit` and `pull-request` skills in `skills/` define the full message
and description templates — use them.

## Security

- Report vulnerabilities privately via [GitHub Security Advisories][advisory],
  never a public issue. See `SECURITY.md`.
- No secrets, credentials, tokens, or personal paths in tracked files. Anything
  machine-specific belongs in `.agents/AGENTS.local.md` or `~/.laptop.local`,
  both of which are outside version control.
- `.claude/settings.json`, `.codex/config.toml`, `.codex/rules/default.rules`,
  `.cursor/cli-config.json`, and `.cursor/hooks.json` are a security boundary:
  the Claude `permissions.deny` list, the Codex `forbidden` rules, and the Cursor
  `permissions.deny` list plus `beforeShellExecution` gate block reads of `.env`
  files, SSH/GPG/cloud credentials, and destructive git commands, and the
  `sandbox` / `[permissions.developer]` blocks constrain filesystem writes and
  network egress. Widening any of them is a deliberate act — justify it in the
  commit message, and mirror it across every client (see "Agent-client
  configuration parity") rather than loosening one client's rule to make a task
  easier.

[advisory]: https://github.com/itsmechlark/laptop/security/advisories/new

## Gotchas

- `mac` will `sudo chsh` and append to `~/.zshrc`. It is not side-effect free;
  never run it casually to "check something."
- `.gitignore` excludes `artifacts`, `*.swp`, `.claude/.cc-writes`,
  `.agents/*.local.md`, `.agents/.skills-lock.json`, and any nested
  `.claude` directory under `.agents/` or `skills/`.
- `skills-lock.json` at the root is the tracked file — edit that one. The
  `.agents/.skills-lock.json` symlink pointing back at it is a leftover from when
  `~/.agents` was itself a link to this repo, and is git-ignored.
- asdf is put on `PATH` via `${ASDF_DATA_DIR:-$HOME/.asdf}/shims` rather than
  sourcing `asdf.sh` — that was a deliberate fix (commit `0f46cb9`); don't
  regress it.
- The script installs the *latest* Ruby and Node that asdf reports, not pinned
  versions. Output differs between runs on different days by design.
