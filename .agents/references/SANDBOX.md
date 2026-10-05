---
name: sandbox-gotchas
description: Workarounds for commands that fail under the macOS Seatbelt sandbox that Claude Code and Codex apply to each Bash command — gh CLI auth (telling an expired token apart from a sandbox keychain failure), Claude's pipe/redirect trap where a pipe, redirect, or substitution re-sandboxes an excluded command, and the pnpm purge prompt that destroys node_modules when silenced. Read when a command fails with "operation not permitted", HTTP 401, or a keychain/credential error. Cursor runs unsandboxed and is unaffected.
---

# Sandbox gotchas

Claude Code and Codex each run Bash commands inside a macOS Seatbelt sandbox
that blocks reads of credential paths, most of `~`, and system services reached
over Mach — including the macOS keychain. Cursor runs commands unsandboxed, so
nothing here applies to Cursor.

The two clients escape the sandbox differently, and the difference is the whole
reason the same command can work one way and fail another:

- **Claude Code** names specific commands in `sandbox.excludedCommands`
  (`.claude/settings.json`); a listed command runs outside the sandbox. The
  escape is matched **per command**, so a pipe defeats it — see the pipe trap
  below.
- **Codex** has no exclusion list. `approval_policy = "on-request"` means a
  command that needs more than the sandbox grants prompts for approval and, once
  approved, runs escalated out of Seatbelt. The fix on Codex is usually to
  approve the prompt, not to rewrite the command.

## The pipe/redirect trap (Claude Code)

`excludedCommands` is matched against the **whole call**, and every segment has
to match for the call to run unsandboxed. A pattern like `gh *` runs outside the
sandbox **only as a single bare command**. Add almost any shell construct and
the whole call — the excluded command included — is sandboxed again:

- a **pipe** to a non-excluded command (`jq`, `head`, `grep`, `tee`, `sort`, …)
- a **redirect** (`>`, `>>`)
- a **command substitution** (`$(...)`)
- a leading **`cd`**, or chaining a non-excluded command with `&&` / `;`

```sh
gh pr view 123 --json title,state           # bare — runs unsandboxed
gh pr view 123 --json title,state | jq      # sandboxed (jq isn't excluded)
gh pr view 123 --json title,state > f.json  # sandboxed — a redirect re-sandboxes the call
```

So there is **no** "redirect to a file, then Read it" trick — the redirect
itself sandboxes `gh`. Keep it a single bare command, let the output come back on
stdout (the harness captures it), and shape the output with `gh`'s own flags
rather than piping.

## gh CLI: triage the token before blaming the sandbox

A `gh` failure has two unrelated causes, and the fix for one does nothing for the
other. Triage first — run `gh` **bare** (no pipe, no redirect):

```sh
gh auth status
```

**The token is expired or revoked** when `gh auth status` reports "The token in
… is invalid", or a bare `gh api …` returns GitHub's own JSON
`{"message":"Requires authentication", … "status":"401"}`. This is **not** a
sandbox problem: a bare `gh` already runs outside the sandbox and reached the
keychain fine — GitHub rejected the token itself. No sandbox setting fixes it,
and neither does avoiding pipes. Re-authenticate outside the sandbox, then retry:

```sh
gh auth login -h github.com
```

A clean GitHub `401` from a bare command is this case, not the one below.

**The sandbox is the cause** when `gh auth status` is healthy yet a command still
fails with `failed to load config: … operation not permitted` on
`~/.config/gh/config.yml`, a TLS trust failure (`x509: OSStatus -26276`), or an
unexpectedly unauthenticated (rate-limited) response. `gh` keeps its token in the
macOS keychain (the `keyring` store), which is unreachable in-sandbox;
`allowMachLookup` does not change that. The fix is to keep `gh` a single bare
command so `excludedCommands` runs it unsandboxed — no pipe, redirect, or
substitution (see the pipe/redirect trap above). Shape output with `gh`'s own
flags instead of piping:

| Instead of | Use |
| --- | --- |
| `gh … \| jq '.field'` | `gh … --json field --jq '.field'` (gh embeds jq) |
| `gh … \| head -n N` | `gh … --limit N`, or `--json`/`--template` to shape output |
| `gh … \| grep X` | `gh … --json …` then filter with `--jq 'select(...)'` |
| `gh … \| tee file` | run `gh …` bare and read its stdout — don't redirect |

**On Codex**, approve the escalation prompt when `gh` asks for it; the escalated
command reaches the keychain. A pipe doesn't defeat this the way it does on
Claude, because Codex escalates the whole command rather than matching a listed
name. An expired token still needs `gh auth login` — escalation won't rescue it.

## pnpm: a purge prompt is not a flag to silence

The sandbox denies writes inside any `.idea/` directory, and a few common
packages (`iconv-lite@0.6.3`) ship one. A `node_modules` built outside the
sandbox contains those files, but pnpm cannot recreate them in-sandbox.

When pnpm reports that the modules directories "will be removed and reinstalled
from scratch", that prompt is the only thing between you and a full purge. It
appears even for `pnpm install --lockfile-only`. These all purge without asking,
then fail on the `.idea` write and leave `node_modules` empty:

- `--config.confirmModulesPurge=false` (it means "purge without asking")
- `CI=true`
- answering yes

Recovery is a plain `pnpm install --frozen-lockfile` run outside the sandbox.

For a dependency bump, edit the manifests or catalog, then ask the user to run
`! pnpm install` themselves (answering `n` to any purge prompt), and run the
gates in-sandbox afterwards. Do not regenerate the lockfile from the sandbox.

## When a bare command still fails: blocked Mach lookups

TLS verification through Claude's sandbox proxy needs a Mach lookup for the
system trust daemon; `sandbox.network.allowMachLookup` in `.claude/settings.json`
lists `com.apple.trustd*` for that. A new failure naming a different
`com.apple.*` service is the same class — a blocked Mach lookup — and widening
the allowlist is a Claude sandbox policy change: justify it in the commit.

This knob is **Claude-only**. Codex exposes no Mach-lookup allowlist (its sandbox
config is `network_proxy` plus `domains`/`unix_sockets`), and Cursor is
unsandboxed — so `allowMachLookup` has no counterpart to mirror in either, which
is the one deliberate break in the otherwise-mirrored sandbox network policy.
Never reach for `dangerouslyDisableSandbox`; report the restriction instead.
