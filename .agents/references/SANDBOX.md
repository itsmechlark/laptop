---
name: sandbox-gotchas
description: Workarounds for commands that fail under the macOS Seatbelt sandbox that Claude Code and Codex apply to each Bash command — gh CLI keychain auth, and Claude's pipe trap where piping an excluded command re-sandboxes it. Read when a command fails with "operation not permitted", HTTP 401, or a keychain/credential error that doesn't reproduce when the command runs on its own. Cursor runs unsandboxed and is unaffected.
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

## The pipe trap (Claude Code)

A command in `excludedCommands` (e.g. `gh *`) runs unsandboxed **only when it
runs on its own**. The moment it joins a pipeline, the whole pipeline inherits
the sandbox profile from the non-excluded member (`head`, `jq`, `grep`, `tee`,
`sort`, …), and the excluded command is sandboxed too.

```sh
gh pr view 123 --json title,state        # unsandboxed — reaches the keychain, works
gh pr view 123 --json title,state | jq   # sandboxed via jq — keychain blocked, fails
```

Redirection is **not** a pipe. `>` and `>>` are handled by the shell, so the
command stays a bare excluded command:

```sh
gh pr view 123 --json title,state > "$TMPDIR/pr.json"   # still bare gh — works
```

Then Read the file (the Read tool is permission-governed, not sandboxed).

## gh CLI: keychain is unreachable when sandboxed

`gh` stores its token in the macOS keychain (the `keyring` credential store).
Inside the sandbox the keychain is unreachable, so a sandboxed `gh` fails to
authenticate — typically HTTP 401, or `failed to load config: … operation not
permitted` on `~/.config/gh/config.yml`. Adding `allowMachLookup` does not fix
this; the keychain stays unreachable. The only path that works is running `gh`
outside the sandbox.

**On Claude Code, never pipe `gh`.** Use its built-in flags instead of piping to
another tool, so the command stays bare and unsandboxed:

| Instead of | Use |
| --- | --- |
| `gh … \| jq '.field'` | `gh … --json field --jq '.field'` (gh embeds jq) |
| `gh … \| head -n N` | `gh … --limit N`, or `--json`/`--template` to shape output |
| `gh … \| grep X` | `gh … --json …` then filter with `--jq 'select(...)'` |
| `gh … \| tee file` | `gh … > file` (shell redirect, not a pipe), then Read it |

When post-processing genuinely can't be expressed in `gh`'s own flags, redirect
to `$TMPDIR` and process the file in a separate step.

**On Codex**, approve the escalation prompt when `gh` asks for it; the escalated
command reaches the keychain. Piping does not defeat this the way it does on
Claude, because Codex escalates the whole command, not a listed name.

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
