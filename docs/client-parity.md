# Agent-client configuration parity

Claude Code, Codex, and Cursor are three front-ends over **one** security and
behavior policy. `.claude/settings.json` is the canonical expression;
`.codex/config.toml.template` and `.codex/rules/default.rules` translate it into
Codex's schema; `.cursor/cli-config.json` and `.cursor/hooks.json` into
Cursor's. They are mirrors, not independent configs. Why mirrored by hand:
[ADR 0002](adr/0002-one-policy-three-clients.md).

Claude and Codex are allow-by-default with deny/ask exceptions; Cursor is
prompt-by-default (`approvalMode: "allowlist"`) with allow exceptions. Identical
UX is impossible — the shared target is **security** parity: the same
secret-path and destructive-command denials, attribution-off default, and
command log plus worktree-convention gate.

**The invariant: any change to one client's permission, sandbox, hook, env, or
network/filesystem policy must be mirrored into every other client's config in
the same commit.** A machine that has run `mac` runs all three clients off these
files. The same extends to any future agentic client added here. When a policy
has no equivalent in a client, note the gap in the commit message.

Model choice, reasoning effort, and `enabledPlugins` are per-client tuning, not
shared policy.

## Policy map

Use this map to find the counterpart for a change:

| Policy | Claude (`.claude/settings.json`) | Codex (`.codex/…`) | Cursor (`.cursor/…`) |
| --- | --- | --- | --- |
| Blocked commands | `permissions.deny` — `Bash(…)` | `rules/default.rules` — `"forbidden"` | `cli-config.json` `permissions.deny` — `Shell(…)` + `hooks.json` gate |
| Approval-gated commands | `permissions.ask` — `Bash(…)` | `rules/default.rules` — `"prompt"` | `approvalMode: "allowlist"` prompts on unlisted |
| Implicit-POST `gh api` (mutation via `-f`/`-F`/`--field`/`--raw-field`/`--input`) | `hooks.PreToolUse` denies the implicit form → canonical `gh api --method POST` (gated by `permissions.ask`) | `config.toml` PreToolUse guard denies the implicit form → canonical `--method POST` (gated by `rules` `"prompt"`) | — (prompt-by-default gates any unlisted `gh`) |
| Unreadable secret paths | `permissions.deny` — `Read(…)` | `config.toml` filesystem `"deny"` | `cli-config.json` `permissions.deny` — `Read(…)` |
| Writable / readable roots | `sandbox.filesystem.allowWrite` / `allowRead` | `config.toml` `[permissions.developer.filesystem]` | — (no sandbox roots; `permissions.deny` `Write(…)` guards policy files) |
| Allowed network hosts | `sandbox.network.allowedDomains` | `config.toml` `[…network.domains]` | — (no egress allowlist) |
| Unix sockets | `sandbox.network.allowUnixSockets` | `config.toml` `[…network.unix_sockets]` | — |
| Mach port lookups (TLS trust daemon) | `sandbox.network.allowMachLookup` | — (no knob; `network_proxy` + domains only) | — (unsandboxed) |
| Unsandboxed command escape | `sandbox.excludedCommands` | — (`approval_policy = "on-request"`) | — (commands run unsandboxed, prompt-gated) |
| Second-line sandbox for unsafe commands (`srt`) | `permissions.ask` `Bash(srt *)` / `npx … *` (prompts each use); run un-nested via `sandbox.excludedCommands` | `rules/default.rules` `["srt"]` = `"prompt"` (shim form only — argv-prefix can't match the `npx` form); `on-request` approval escalates it out of Seatbelt so it runs un-nested (srt can't nest on macOS) | `approvalMode` prompts (`srt` unlisted) + `hooks.json` bypass early-return |
| Unsandboxed vulnerability scanner (`trivy`) | `permissions.ask` `Bash(trivy *)` + `sandbox.excludedCommands` `trivy *` | `rules/default.rules` `["trivy"]` = `"prompt"`; `on-request` approval escalates it out of Seatbelt | `approvalMode` prompts (`trivy` unlisted); runs unsandboxed (no Cursor sandbox) |
| 1Password shell plugin for Pulumi (`op plugin run -- pulumi`), unsandboxed so `op` can reach the 1Password app; `op` secret reads denied everywhere | `sandbox.excludedCommands` `op plugin run -- pulumi *` (never `op *`); `permissions.deny` and `permissions.ask` repeat every `pulumi` rule behind the `op plugin run -- ` prefix; `permissions.deny` `op read`, `op inject`, `op run`, `op item get`, `op document get`; the spellings those prefixes miss (`op --account … read`, any other `op plugin run` form) aren't excluded, so they stay sandboxed, where `Read(~/.config/op/**)` stops `op` | `rules/default.rules` `"forbidden"`/`"prompt"` for the same prefixed `pulumi` verbs and the same `op` reads; the `hooks.PreToolUse` guard unwraps `op plugin run --` so the canonical-form `pulumi` checks still apply, denies any other spelling of a plugin run (`op --account … plugin run`, options before `--`) so the prefixed rules can't be sidestepped, and denies `op` reads behind global flags (`op --account … read`) | `cli-config.json` `permissions.deny` `Shell(op plugin run -- pulumi destroy *)`/`stack rm` and the `op` reads; `hooks.json` guard denies the reads behind global flags, by absolute path, inside `$(…)` or backticks, and inside `op plugin run --`; the rest prompts through `approvalMode`. Cursor runs unsandboxed, so the read denials are its only barrier |
| Atlassian CLI (`acli`), unsandboxed on the assumption it keeps its login in the macOS keychain (unverified; re-check after the first `acli jira auth login`) | `sandbox.excludedCommands` `acli *`; `permissions.deny` for `jira workitem delete`/`attachment-delete`/`comment-delete` and `jira project delete`; `permissions.ask` for every other `jira workitem`/`jira project` write and all of `acli admin`. Network reuses the Atlassian hosts already allowed for the MCP | `rules/default.rules` `"forbidden"` and `"prompt"` for the same verbs; `on-request` approval escalates it out of Seatbelt. No new domains | `cli-config.json` `permissions.deny` `Shell(acli … delete *)`; the rest is covered by `approvalMode` prompting on unlisted commands; runs unsandboxed |
| Unsandboxed dependency install (`pnpm`, `npm`) | `sandbox.excludedCommands` for the install family and its aliases. `permissions.ask` for `add`, `update`/`up`/`upgrade`, `dedupe`, `rebuild`/`rb`, and install-test. A `hooks.PreToolUse` install gate allows `install`/`i`/`ci`, `remove`, and `prune` outright, in every permission mode, and prompts only when they name packages, an install input is uncommitted, npm lacks `--ignore-scripts`, or `packageManager` pins pnpm below 10. It never allows the purge flag, so that deny rule still applies. `permissions.deny` `Bash(pnpm *confirmModulesPurge*)` | `rules/default.rules` `["pnpm", [...]]` and `["npm", [...]]` = `"prompt"` for every form, because approval is Codex's only escape from Seatbelt. No purge-flag deny: an argv prefix can't match a flag at any position | `approvalMode` prompts (`pnpm`, `npm` unlisted); runs unsandboxed, so a purge completes and needs no deny |
| Unsandboxed mobile tooling (Maestro, Expo, EAS) | `sandbox.excludedCommands` for `maestro *`, `pnpm exec expo *`, `eas *`; `permissions.ask` for `pnpm exec expo`, `eas`, `maestro cloud`/`upload`/`login`/`logout`, and `mcp__maestro__run_on_cloud`. A `hooks.PreToolUse` Maestro gate on `Bash` and `mcp__maestro__run` reads every flow a `maestro test` or MCP run would execute, `runFlow` sub-flows included. It allows device-only flows and prompts on `runScript`, `evalScript`, `openLink`, `addMedia`, JavaScript beyond a plain `${VAR}`, a flow it cannot read, continuous mode, report output outside the project, and every other `maestro` subcommand. The `npx expo`, `npx eas-cli`, and `pnpm dlx eas-cli` forms are neither asked nor excluded: they stay sandboxed like any other `npx`, with no egress to `expo.dev` | `rules/default.rules` `"prompt"` for each form; `on-request` approval escalates it out of Seatbelt, the npx forms included. No Maestro MCP is wired into Codex | `approvalMode` prompts (all unlisted); no Maestro MCP wired into Cursor |
| EAS publishing and secrets (`submit`, `update` and its publishing `update:` forms, `deploy`, `credentials`, `channel:edit`/`rollout`, `metadata:push`, `env:`/`secret:` writes, `build --auto-submit`, `--include-sensitive`) | `permissions.deny` for `eas …`; `npx *eas-cli* …` and `pnpm dlx eas-cli* …` for `submit`, `update`, `deploy`, `credentials` | `rules/default.rules` `"forbidden"` per form; the PreToolUse guard in `config.toml.template` denies version-pinned runners and the two flags | `cli-config.json` `permissions.deny` `Shell(eas …)`; `hooks.json` gate denies the npx/dlx forms and the two flags |
| `srt-settings.json` self-policy guard | `sandbox.filesystem.denyWrite` + `permissions.ask` `Edit(…srt-settings.json)` | `[…filesystem]` `~/.srt-settings.json = "read"` + `:workspace_roots` `srt-settings.json = "read"` | `permissions.deny` `Write(**/srt-settings.json)` |
| Env-var scrubbing | `env` + `sandbox.credentials.envVars` | `config.toml` `[shell_environment_policy.filters]` | — |
| Subagent read-only | `agents/*.md` `tools` | — (body only) | `agents/*.md` `readonly` |
| Lifecycle hooks | `hooks.PreToolUse` | `config.toml` `[[hooks.PreToolUse]]` | `hooks.json` `beforeShellExecution` |

## Cursor's gaps

Recorded here rather than dropped:

| Gap | What follows from it |
| --- | --- |
| No sandboxed egress or filesystem roots | No counterpart to Claude/Codex sandbox roots. Secret-path denials are the reachable half, and they are mirrored |
| No env-var scrub | No counterpart to `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` / `sandbox.credentials.envVars` / Codex filters |
| The ask tier is implicit | `approvalMode: "allowlist"` prompts on every unlisted command. Its two `permissions.allow` entries mirror machine-local write roots the other two grant. Keep the list to that — a general allowlist dismantles prompt-by-default |
| Arg-nuanced blocks live in the hook | Wholesale-dangerous commands (`dd`, `sudo`, `mkfs`) are `permissions.deny`; arg-distinguished forms (`rm -rf`, `git push --force`) are enforced by `beforeShellExecution` (fail-open — crash falls through to normal prompt) |
| `~` home-glob reach is an assumption | `~` expansion in `permissions` patterns is undocumented; `Read(~/…)` denials are best-effort, `**/` globs cover in-workspace secrets |
| No MCP drop-tool denies | Claude's MongoDB `drop-*` denials have no counterpart — that MCP is not wired into Cursor |
| `sandbox.mode` / `networkAccess` omitted | Accepted enum values are undocumented; left unset to avoid breaking the config |
| srt bypasses substring gates | `beforeShellExecution` skips the destructive checks for an unchained `srt`/`npx-srt` command (top-level `;` `\|` `>` or a newline still fall through), then defers to the approval prompt — `srt` is not allowlisted, so it is not auto-run. srt's own sandbox is the boundary |
| Subagent `tools` ignored | Read-only rests on `readonly`, which `check-payload` requires |
