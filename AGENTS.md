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

The vocabulary this document leans on — `payload`, `published payload`,
`first-party`, `flagged` — is defined in [`CONTEXT.md`](CONTEXT.md). Decisions
that would otherwise be re-argued live in [`docs/adr/`](docs/adr/).

### Read this first: two different AGENTS.md files

| File | Scope | Symlinked to |
| --- | --- | --- |
| `AGENTS.md` (this file) | Instructions for working **on this repository** | nowhere — but repo-root `CLAUDE.md` is a symlink *to* it |
| `.agents/AGENTS.md` | The maintainer's **global engineering standards**, shipped to every project | `~/.agents/AGENTS.md` → `~/.claude/CLAUDE.md` |

`.agents/AGENTS.md` is cargo, not configuration for this repo. Editing it
changes agent behavior in *every* repository on the machine — treat changes to
it as global blast radius and keep them deliberate.

Claude Code loads `CLAUDE.md`; Codex and Cursor load `AGENTS.md`. The root
`CLAUDE.md` symlink is the alias that gives all three the same repo
instructions — it is not a second file. Edit `AGENTS.md`; writing through
`CLAUDE.md` silently rewrites it.

## Setup commands

Nothing needs installing to work on this repo beyond the two linters:

```sh
brew install shellcheck cspell
```

`mac` installs `cspell` itself (the Development Tools group in the `brew bundle`
heredoc), so a provisioned machine already has it. `shellcheck` it does not
install — that one is always yours.

`scripts/check-payload` also needs `jq`, which supported macOS versions ship at
`/usr/bin/jq` and GitHub runners have preinstalled. `mac` does not install it.

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
CONTEXT.md              # this repo's glossary — what its own words mean
docs/verification.md    # what check-payload covers, fixtures, evals, spelling
docs/adr/               # architecture decision records, numbered sequentially
skills-lock.json        # provenance + content hashes for vendored skills (tool-owned)
skills-provenance.json  # source lineage for first-party derived skills (hand-owned)
rules-provenance.json   # source lineage for derived rules (hand-owned)
cspell.json             # spell check: dictionaries, project words, ignore paths
srt-settings.json       # srt (sandbox-runtime) config → ~/.srt-settings.json (global)
bin/srt                 # shim → ~/.bin/srt: npx --package=@anthropic-ai/sandbox-runtime srt
scripts/                # verification tooling; each relocates to the repo root itself
  check-payload         # static verification of the payload (POSIX sh + jq)
  run-trigger-evals     # runs spec/trigger-evals; needs a logged-in claude CLI
  lib/run_eval_local.py # trigger-eval engine: drives claude -p against installed skills
spec/                   # fixtures check-payload validates and reads
  rules-cases.txt       # path -> which rules/ load for it
  invocability-fixture/ # deliberate violations; proves the check still fires
  orphan-fixture/       # unreachable references + stale anchors; proves the checks fire
  srt-shim-fixture/     # a self-wrapping, unpinned bin/srt; proves the shim check fires
  trigger-evals/*.json  # query sets for skill triggering (run by hand, not CI)
.agents/
  AGENTS.md             # global engineering standards (shipped to ~/.claude/CLAUDE.md)
  CONTEXT.md            # root context map — machine-local, git-ignored (optional)
  references/
    CONTEXT-FORMAT.md   # template for .agents/CONTEXT.md
  skills/               # skill bodies: vendored + project-only (project-only = not linked from skills/)
rules/                  # path-scoped language standards, auto-loaded by glob
skills/                 # published skills → ~/.agents/skills; first-party dirs + symlinks into .agents/skills
.claude/settings.json   # Claude Code settings (permissions, sandbox, hooks, plugins)
.codex/                 # Codex config — mirrors .claude/settings.json
  config.toml.template  # permissions, sandbox, env scrub, hooks — mac renders git-ignored config.toml
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
| `~/.agents/CONTEXT.md` | `.agents/CONTEXT.md` (when present) |
| `~/.claude/CLAUDE.md` | `~/.agents/AGENTS.md` |
| `~/.claude/rules` | `~/.agents/rules` |
| `~/.claude/skills` | `~/.agents/skills` |
| `~/.claude/settings.json` | `.claude/settings.json` |
| `~/.claude/CONTEXT.md` | `~/.agents/CONTEXT.md` |
| `~/.codex/AGENTS.md` | `~/.agents/AGENTS.md` |
| `~/.codex/rules` | `.codex/rules/` |
| `~/.codex/skills` | `~/.agents/skills` |
| `~/.codex/config.toml` | `.codex/config.toml` (rendered by `mac` from `.codex/config.toml.template`) |
| `~/.codex/CONTEXT.md` | `~/.agents/CONTEXT.md` |
| `~/.cursor/cli-config.json` | `.cursor/cli-config.json` |
| `~/.cursor/hooks.json` | `.cursor/hooks.json` |
| `~/.cursor/CONTEXT.md` | `~/.agents/CONTEXT.md` |
| `~/.srt-settings.json` | `srt-settings.json` |
| `~/.bin/srt` | `bin/srt` |

`symlink_path` moves any pre-existing real file to `<path>.backup` before
linking; check for stray `.backup` files if a link looks wrong.

## Development workflow

No build step, no dev server, no watch mode. The loop is: edit in the repo, and
the change is already live for every client — directories are linked, not
copied. Why links rather than copies:
[ADR 0001](docs/adr/0001-symlink-the-payload-instead-of-copying.md).

Only three changes need `sh mac` again:

1. Adding a **new top-level link**.
2. Editing `.codex/config.toml.template` — see below.
3. Creating `.agents/CONTEXT.md` for the first time — see below.

**Always edit via the repo path, never the home symlink.** The sandbox allows
writes to this repository but restricts the home dotdirs (`~/.claude/`,
`~/.agents/`, `~/.codex/`, `~/.cursor/`). Editing `~/.claude/settings.json` or
`~/.agents/skills/foo/SKILL.md` will hit a permission wall even though the
symlink resolves here. Use the repo-relative path instead — e.g.
`.claude/settings.json`, `skills/foo/SKILL.md`, `rules/ruby.md`,
`.agents/AGENTS.md`. The same applies to `skills-lock.json` and
`skills-provenance.json` and `rules-provenance.json` (all at the repo root).

**`.codex/config.toml` is generated, not linked to a tracked file.** `mac`
renders it from `.codex/config.toml.template`, then links the result; the output
is git-ignored because Codex needs an absolute Unix-socket path and does not
expand `~`. Edit the template and re-run `sh mac` to regenerate and relink —
edits to the generated file are overwritten.

**`.agents/CONTEXT.md` is optional and machine-local.** `mac` creates the four
`CONTEXT.md` links only when it exists, so `sh mac` is required after you first
create one; copy `.agents/references/CONTEXT-FORMAT.md` to start. A new agent
client added here should mirror that link into its own dotdir.

## Agent-client configuration parity

Claude Code, Codex, and Cursor are three front-ends over **one** security and
behavior policy. `.claude/settings.json` is the canonical expression;
`.codex/config.toml.template` and `.codex/rules/default.rules` translate it into
Codex's schema; `.cursor/cli-config.json` and `.cursor/hooks.json` into
Cursor's. They are mirrors, not independent configs.

Claude and Codex are allow-by-default with deny/ask exceptions; Cursor is
prompt-by-default (`approvalMode: "allowlist"`) with allow exceptions. Identical
UX is impossible — the shared target is **security** parity: the same
secret-path and destructive-command denials, attribution-off default, and
command log plus worktree-convention gate.

**The invariant: any change to one client's permission, sandbox, hook, env, or
network/filesystem policy must be mirrored into every other client's config in
the same commit.** A machine that has run `mac` runs all three clients off these
files. The same extends to any future agentic client added here.

Use this map to find the counterpart for a change:

| Policy | Claude (`.claude/settings.json`) | Codex (`.codex/…`) | Cursor (`.cursor/…`) |
| --- | --- | --- | --- |
| Blocked commands | `permissions.deny` — `Bash(…)` | `rules/default.rules` — `"forbidden"` | `cli-config.json` `permissions.deny` — `Shell(…)` + `hooks.json` gate |
| Approval-gated commands | `permissions.ask` — `Bash(…)` | `rules/default.rules` — `"prompt"` | `approvalMode: "allowlist"` prompts on unlisted |
| Unreadable secret paths | `permissions.deny` — `Read(…)` | `config.toml` filesystem `"deny"` | `cli-config.json` `permissions.deny` — `Read(…)` |
| Writable / readable roots | `sandbox.filesystem.allowWrite` / `allowRead` | `config.toml` `[permissions.developer.filesystem]` | — (no sandbox roots; `permissions.deny` `Write(…)` guards policy files) |
| Allowed network hosts | `sandbox.network.allowedDomains` | `config.toml` `[…network.domains]` | — (no egress allowlist) |
| Unix sockets | `sandbox.network.allowUnixSockets` | `config.toml` `[…network.unix_sockets]` | — |
| Unsandboxed command escape | `sandbox.excludedCommands` | — (`approval_policy = "on-request"`) | — (commands run unsandboxed, prompt-gated) |
| Second-line sandbox for unsafe commands (`srt`) | `permissions.ask` `Bash(srt *)` / `npx … *` (prompts each use); run un-nested via `sandbox.excludedCommands` | `rules/default.rules` `["srt"]` = `"prompt"` (shim form only — argv-prefix can't match the `npx` form); `on-request` approval escalates it out of Seatbelt so it runs un-nested (srt can't nest on macOS) | `approvalMode` prompts (`srt` unlisted) + `hooks.json` bypass early-return |
| `srt-settings.json` self-policy guard | `sandbox.filesystem.denyWrite` + `permissions.ask` `Edit(…srt-settings.json)` | `[…filesystem]` `~/.srt-settings.json = "read"` + `:workspace_roots` `srt-settings.json = "read"` | `permissions.deny` `Write(**/srt-settings.json)` |
| Env-var scrubbing | `env` + `sandbox.credentials.envVars` | `config.toml` `[shell_environment_policy.filters]` | — |
| Lifecycle hooks | `hooks.PreToolUse` | `config.toml` `[[hooks.PreToolUse]]` | `hooks.json` `beforeShellExecution` |

Model choice, reasoning effort, and `enabledPlugins` are per-client tuning, not
shared policy. When a policy has no equivalent in a client, note the gap in the
commit message. Why mirrored by hand:
[ADR 0002](docs/adr/0002-one-policy-three-clients.md).

Cursor's gaps, recorded here rather than dropped:

| Gap | What follows from it |
| --- | --- |
| No sandboxed egress or filesystem roots | No counterpart to Claude/Codex sandbox roots. Secret-path denials are the reachable half, and they are mirrored |
| No env-var scrub | No counterpart to `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` / `sandbox.credentials.envVars` / Codex filters |
| The ask tier is implicit | `approvalMode: "allowlist"` prompts on every unlisted command. Its two `permissions.allow` entries mirror machine-local write roots the other two grant. Keep the list to that — a general allowlist dismantles prompt-by-default |
| Arg-nuanced blocks live in the hook | Wholesale-dangerous commands (`dd`, `sudo`, `mkfs`) are `permissions.deny`; arg-distinguished forms (`rm -rf`, `git push --force`) are enforced by `beforeShellExecution` (fail-open — crash falls through to normal prompt) |
| `~` home-glob reach is an assumption | `~` expansion in `permissions` patterns is undocumented; `Read(~/…)` denials are best-effort, `**/` globs cover in-workspace secrets |
| No MCP drop-tool denies | Claude's MongoDB `drop-*` denials have no counterpart — that MCP is not wired into Cursor |
| `sandbox.mode` / `networkAccess` omitted | Accepted enum values are undocumented; left unset to avoid breaking the config |
| srt bypasses substring gates | `beforeShellExecution` skips the destructive checks for an unchained `srt`/`npx-srt` command (top-level `;` `|` `>` or a newline still fall through), then defers to the approval prompt — `srt` is not allowlisted, so it is not auto-run. srt's own sandbox is the boundary |

## Testing instructions

There is no unit test suite. Verification is lint, a spell check, and a real run
— for the provisioner *and* for the payload it ships.

```sh
shellcheck mac -e SC2039     # must be clean; SC2039 is excluded deliberately
shellcheck scripts/check-payload     # must be clean; no exclusions
sh scripts/check-payload             # static verification of skills/, rules/, clients
sh scripts/check-payload --collisions  # report: which descriptions share vocabulary
cspell lint --no-progress --dot "**/*"  # spelling; must be clean, CI enforces it
```

### The two jobs

CI (`.github/workflows/tests.yml`, on push to `main`, every PR, and
`workflow_dispatch`) runs two independent jobs.

**`payload`** — `ubuntu-latest`, seconds, no Homebrew. Shellchecks
`check-payload` and runs it (on PRs with `--since origin/<base>` for the
vendored-edit check). Closes with the spell check — `cspell` comes from npm,
pinned to the major `mac` installs from Homebrew.

**`tests`** — the matrix of `macos-26` and `macos-15` with `fail-fast: false`:

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

What `check-payload` settles and what it leaves to a person, how the `spec/`
fixtures are kept honest, which skills earn a trigger eval, and how spelling is
enforced are in [`docs/verification.md`](docs/verification.md). Read it before
adding a check, a fixture, or an eval set. Warnings never fail the run; failures
always do.

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

### `scripts/` (POSIX shell)

Same shell conventions as `mac` — `#!/bin/sh`, two-space indent, `fancy_echo`.
Both wrappers `cd` to the repo root, so paths are repo-relative from any
working directory. `scripts/lib/run_eval_local.py` is the one non-shell piece —
Python parsing `claude -p` stream-json; keep it self-contained (stdlib only).

`scripts/check-payload` differs from `mac` in two deliberate ways:

- **No `set -e`.** A linter reports every problem in one pass; failures
  accumulate in a counter and set the exit status at the end. Don't "fix" this.
- **`jq` is a dependency.** Already required by the `PreToolUse` hooks in
  `.claude/settings.json`, and preinstalled on GitHub runners, so it adds no new
  install burden.

`scripts/run-trigger-evals` does the opposite and exits on the first problem,
because everything it checks is a precondition for spending tokens.

New checks belong in `check-payload` only when they're deterministic and
file-local. Anything needing a model, a network call, or a judgment about prose
quality goes in `spec/trigger-evals/` and stays out of CI — see
[`docs/verification.md`](docs/verification.md).

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

Two subdirectories, split by whether the agent has to *read* the file:

| Directory | Holds | Enters context |
| --- | --- | --- |
| `skills/<name>/references/*.md` | Prose the agent reads to decide | Yes, when linked |
| `skills/<name>/assets/*` | Files used as-is in output — templates, boilerplate | No |

A file the agent copies and fills in rather than reasons about belongs in
`assets/`: it stays out of context, so an HTML mockup skeleton or a config
template costs nothing to keep complete. Reference it by relative path from the
`references/*.md` that uses it (`../assets/<file>`).
`skills/brainstorming/assets/mockup-template.html` is the worked example.

**These skills co-ship, so name each other freely.** `mac` symlinks `skills/`
as a whole — prefer "that's `code-review`" over describing the boundary
abstractly. Keep references one hop deep and useful: a handoff routes work this
skill shouldn't do, not lists neighbors. Vendored skills are the exception —
see [Vendored skills](#vendored-skills).

**Say "read its `SKILL.md`", not "invoke", when the sibling is user-invoked.**
`disable-model-invocation: true` makes the Skill tool refuse it, so "invoke
`feature-dev`" cannot execute — the handoff must say to read and follow the
`SKILL.md`. The key is Claude-only; Codex and Cursor ignore it.

**Use the flag wherever a wrong auto-invocation is expensive**: a gate
(`brainstorming`), a multi-phase workflow ending in a commit (`feature-dev`), a
tracker write (`triage`), outward-facing text (`standup`). The invocability
check makes flagging cheap by catching mis-worded handoffs at build time.

**Where the expense is a side effect, the body is the guard, not the flag.**
Codex and Cursor ignore the key, so the rule that holds on every client is
written into the skill: `triage`'s draft-show-then-ask, `standup`'s never-send
([ADR 0003](docs/adr/0003-model-invocation-flag-is-claude-only.md)).

Mid-chain skills that others call constantly — `draft-spec`, `draft-plan`,
`slice`, `tdd`, `explain`, `grilling`, `code-review` — are better left
invocable, because every caller pays the indirection. When one of those also
has an expensive next step, the body carries the stop instead: `draft-plan`
ends at the saved plan and never executes it.

### `rules/<lang>.md`

Frontmatter is a glob list controlling when the rule auto-loads:

```markdown
---
paths:
  - "**/*.rb"
  - "**/Gemfile"
---
```

A rule drawn from outside material ends with the same `## Attribution` section
a derived skill carries, mirroring `rules-provenance.json` — see "Derived
skills and rules". A rule loads on every matching path, so keep the body terse
and push long-form material into a skill rather than growing the rule.

### Vendored skills

Third-party skills live in `.agents/skills/<name>/`, are recorded in
`skills-lock.json` with their source and content hash, and are exposed through a
symlink at `skills/<name>` → `../.agents/skills/<name>`. Don't hand-edit vendored
content: it desynchronizes the recorded hash. Re-vendor from upstream and update
`skills-lock.json` instead.

That includes prose you'd otherwise be free to add — a cross-reference into a
vendored skill is still a hand-edit. Point at it from a first-party skill
instead, which costs nothing and keeps the hash honest. Genuinely need the
divergence? Reclassify the skill as `adapted` in `skills-provenance.json` first,
so the fork is recorded rather than silent.

### Derived skills and rules

First-party skills and rules authored from outside material are tracked in
`skills-provenance.json` and `rules-provenance.json` (both hand-owned; `npx
skills` never touches either). Verbatim copies → `skills-lock.json`; our own
work from a source → the matching provenance record. Rules have no vendored
tier, so every rule is first-party and every rule with outside lineage is
recorded. Each subject maps to a **list** of sources (one skill or rule can
draw on several). Every source carries a `relationship`:

- `adapted` — forked then diverged; pinned to a `ref`. Update = 3-way reconcile
  (`git diff <ref>..HEAD -- <path>`, port the non-conflicting upstream changes),
  then bump that source's `ref` + `reviewed`. Never overwrite.
- `spec` — conforms to an external spec; watch the spec URL/version.
- `inspired-by` — ideas/terminology only, no `ref`; attribution, not synced.

Keep the human-readable `## Attribution` section in each derived `SKILL.md` and
`rules/<name>.md` as the reader-facing attribution — the same flat-list format
in both, defined by the `agent-skills` skill, with the provenance record as its
machine-readable mirror.

**`check-payload` fails the run when the two disagree**, for skills and rules
alike: a recorded subject with no `## Attribution`, a bullet count that doesn't
match the source count, a section that isn't last in the file, an em dash where
the format is ` - `, a GitHub bullet that doesn't name its recorded `origin`,
an `## Attribution` with no record behind it, or a record naming a file that no
longer exists. The single exemption is a vendored skill, whose lineage lives in
`skills-lock.json` and whose body is not ours to annotate.

**Update both the provenance and the `## Attribution` whenever a first-party
skill or rule changes** — they are part of the change, not a follow-up:

- New skill or rule from outside material → add the `skills.<name>` or
  `rules.<name>` entry + `## Attribution`.
- New influence on an existing one → append source + add to `## Attribution`.
  A source in a provenance record without a matching `## Attribution` entry is
  the common miss.
- Reconciled upstream (`adapted`/`spec`) → bump `ref`/`version` + `reviewed`.
- Purely local change → no `ref` change; `inspired-by` sources never carry one.

Several subjects may pin the same upstream path — the five Rails rules all pin
`thoughtbot/guides` at `rails`. Each carries its own `ref`, so porting a change
into one never licenses bumping another.

Run the `update-provenance` project skill (see below) to detect upstream drift
and walk the reconcile per subject; it reads and writes both records. It never
edits a `SKILL.md` or a rule on its own authority, so the `## Attribution`
change is always yours to make: every source in a subject's provenance list
must have a matching entry in its `## Attribution`, and the reverse.

### Project-only skills

Some skills exist only to maintain *this* repo and must not ship. Their bodies
live in `.agents/skills/<name>/` but are deliberately **not** linked from
`skills/`, so `mac`'s chain never carries them off this repo. They are still
first-party — that word says who wrote a skill, not whether it ships.
`update-provenance` is one: scoped to this repo's own skills and rules.

### Markdown

Match the surrounding file. `README.md` uses setext underlined headings and
reference-style links; the `.agents/` and `skills/` Markdown uses ATX (`##`)
headings. Keep prose wrapped at roughly the width already in the file. Spelling
is `en-US`, checked by `cspell` — see
[Spelling](docs/verification.md#spelling).

## Documentation

`README.md` is the human-facing counterpart to this file. When you change `mac`
— especially the `brew bundle` list or what gets symlinked — update the
corresponding README section in the same commit. The "What it sets up" list is
expected to stay in sync with the heredoc.

The same applies to verification: if you add a check or a fixture that a
contributor has to run or satisfy, say so in README's "Testing your changes" and
in `docs/verification.md` in the same commit. A gate nobody knows about is
enforced by CI and discovered by surprise.

`CONTEXT.md` at the root is this repo's glossary. A term that leaves the repo
leaves the glossary in the same commit.

`docs/adr/` holds decisions numbered sequentially. Never rewrite an accepted
ADR — write the next number, reference the superseded one, and mark it so. Both
formats belong to the `domain-modeling` skill.

## Commit and pull request guidelines

- **Never commit or push unless explicitly asked.** A one-time approval covers
  that instance only.
- **Never add AI attribution** — no `Co-Authored-By` AI trailer, no "Generated
  with …" footer. `.claude/settings.json` sets `attribution.commit` to empty to
  enforce this.
- Conventional Commits, imperative mood. The agent payload and provisioner —
  `.agents/`, `.claude/`, `.codex/`, `.cursor/`, `rules/`, `skills/`, `mac`,
  `skills-lock.json`, `skills-provenance.json`, and `rules-provenance.json` —
  are **production code**,
  not documentation, even where they're written in Markdown. Changes to them
  take a code type (`feat`, `fix`, `refactor`, `chore`, …), never `docs`.
  Reserve `docs` for the human-facing docs that describe the repo rather than
  ship from it: `README.md`, this `AGENTS.md`, `SECURITY.md`, the root
  `CONTEXT.md`, and `docs/`. Scopes in use
  here: `mac`, `skills`, `agents`, `claude`, `codex`, `cursor`, `srt`, `ci` — e.g.
  `fix(mac): set up asdf via PATH instead of asdf.sh`, `feat(skills): add
  create-agentsmd skill`.
- `check-payload` and `spec/` are verification code, so they take a code type
  under the `ci` scope — `feat(ci): check attribution against provenance`. A new
  fixture is a new assertion; describe what it now catches, not that a file was
  added.
- Keep PRs single-purpose; separate refactors from behavior changes.
- Required before opening a PR, and enforced by the two CI jobs:
  - `shellcheck mac -e SC2039` and `shellcheck scripts/check-payload`, both clean.
  - `sh scripts/check-payload` exits zero. Warnings are allowed to stand; failures are
    not, and "it's only the payload" is not an exemption — `skills/`, `rules/`,
    and the client configs are production code.
  - `cspell lint --no-progress --dot "**/*"` exits zero. The `payload` job runs
    it too, so check before you push rather than after.
  - A fresh-VM run for anything touching `mac`.
  - For a changed skill `description`, the trigger eval for that skill if one
    exists in `spec/trigger-evals/` — it needs a terminal, so CI cannot do it
    for you. Say so plainly when you have skipped it.
- `@itsmechlark` owns every path via `CODEOWNERS` and reviews all PRs.

The `git-commit` and `pull-request` skills in `skills/` define the full message
and description templates — use them.

## Security

- Report vulnerabilities privately via [GitHub Security Advisories][advisory],
  never a public issue. See `SECURITY.md`.
- No secrets, credentials, tokens, or personal paths in tracked files. Anything
  machine-specific belongs in `.agents/CONTEXT.md` (the git-ignored root context
  map, seeded from `.agents/references/CONTEXT-FORMAT.md`) or `~/.laptop.local`,
  both of which are outside version control. `.agents/CONTEXT.md` holds names,
  paths, and URLs only — never secrets.
- The client configs (`.claude/settings.json`, `.codex/config.toml.template`,
  `.codex/rules/default.rules`, `.cursor/cli-config.json`, `.cursor/hooks.json`)
  are a security boundary: they block reads of `.env` files, SSH/GPG/cloud
  credentials, and destructive git commands, and constrain filesystem writes and
  network egress. Widening any is a deliberate act — justify in the commit
  message and mirror across every client ("Agent-client configuration parity").
- `~/.srt-settings.json` (tracked as `srt-settings.json`) is a sixth boundary:
  the machine-wide config for `srt`, the second-line sandbox for unsafe
  commands. Every `srt` use prompts for approval, and once approved it bypasses
  the per-command destructive gates, so this file — tight on secret reads,
  egress, and policy-file writes — is the whole boundary for a wrapped command.
  Guarded read-only in every client; see
  [ADR 0015](docs/adr/0015-second-line-sandbox-for-unsafe-commands.md).

[advisory]: https://github.com/itsmechlark/laptop/security/advisories/new

## Gotchas

- `mac` will `sudo chsh` and append to `~/.zshrc`. It is not side-effect free;
  never run it casually to "check something."
- `.gitignore` excludes `artifacts`, `*.swp`, `.claude/.cc-writes`,
  `.agents/*.local.md`, `.agents/CONTEXT.md`, `.agents/standup`,
  `.agents/out-of-scope`, `.agents/.skills-lock.json`, and any nested `.claude`
  directory under `.agents/` or `skills/`.
- `mac` provisions eight real directories under `~/.agents/` — `standup`,
  `out-of-scope`, `lore`, `specs`, `plans`, `prds`, `slices`, `adr` — not
  symlinks, because Codex's Seatbelt sandbox rejects symlinked writable roots
  ([ADR 0008](docs/adr/0008-provision-agent-state-as-real-directories.md),
  supersedes [ADR 0004](docs/adr/0004-machine-local-agent-state-in-repo.md)).
  All three clients grant each one write; `skills` and `rules` are pointedly
  excluded, since they resolve into this repo.
- **All but `standup` are fallbacks, not defaults**
  ([ADR 0014](docs/adr/0014-fall-back-to-a-global-home-when-the-repo-has-not-opted-in.md)).
  A skill writes into a repository only where the matching directory (`lore/`,
  `docs/specs/`, `docs/adr/`, …) already exists — the repo's opt-in — and never
  creates one unasked; otherwise it writes to the global root and records
  `metadata.repo`, the repository's *name*, never a path. `out-of-scope` is not
  namespaced under a skill: `triage` writes it, `slice` and `draft-spec` read
  it. The journal prunes to 14 days; rejections never do. **A codebase-specific
  rejection goes in that repo's own `.out-of-scope/`** when it has one, else the
  global root marked `scope: project`.
- **`CONTEXT.md` names two unrelated files.** The root is this repo's committed
  glossary. `.agents/CONTEXT.md` is the git-ignored machine map — what the four
  symlinks point at. Never write a domain term into the map, or a machine path
  into the glossary.
- `skills-lock.json` at the root is the tracked file — edit that one. The
  `.agents/.skills-lock.json` symlink pointing back at it is a leftover from when
  `~/.agents` was itself a link to this repo, and is git-ignored.
- asdf is put on `PATH` via `${ASDF_DATA_DIR:-$HOME/.asdf}/shims` rather than
  sourcing `asdf.sh` — that was a deliberate fix (commit `0f46cb9`); don't
  regress it.
- The script installs the *latest* Ruby and Node that asdf reports, not pinned
  versions. Output differs between runs on different days by design.
