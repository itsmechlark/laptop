---
name: sandbox-gotchas
description: Workarounds for shell commands that fail under a macOS Seatbelt sandbox, whichever agent runs them — gh CLI auth (telling an expired token apart from a sandbox keychain failure), the pipe/redirect trap where a pipe re-sandboxes an excluded command, the pnpm purge prompt that destroys node_modules when silenced, and process lookups (ps, pgrep) that fail quietly, so use lsof or kill -0. Read when a command fails with "operation not permitted", HTTP 401, or a keychain/credential error, or when a loop that waits on a process returns immediately. An agent that runs unsandboxed needs only the gh token triage.
---

# Sandbox gotchas

Some agent harnesses run each shell command inside a macOS Seatbelt sandbox that
blocks reads of credential paths, most of `~`, and system services reached over
Mach — including the macOS keychain. Whether yours does is a fact about the
harness, not about this doc: `operation not permitted` on a path or service the
task needs is the tell. An agent that runs unsandboxed needs only the `gh` token
triage below and the advice never to `pkill -f` a pattern.

Each section says what happens and what to run instead, in terms of the shell.
Where a fix depends on how the harness lets a command escape the sandbox, see
[Harness mechanics](#harness-mechanics) at the end.

## Escape routes differ, and that decides which fix applies

A command that must leave the sandbox gets out one of two ways:

- **A named exclusion list.** The harness runs listed commands unsandboxed. The
  match is against the whole call, so any shell construct around the command
  cancels it — see the pipe trap.
- **Approval-time escalation.** The command prompts for approval and, once
  approved, runs unsandboxed. The whole command escalates, so a pipe does not
  defeat it. The fix is usually to approve the prompt, not to rewrite the command.

## The pipe/redirect trap (exclusion-list harnesses)

Every segment of a call has to match the exclusion list for it to run
unsandboxed. A pattern like `gh *` runs outside the sandbox **only as a single
bare command**. Add almost any shell construct and the whole call — the excluded
command included — is sandboxed again:

- a **pipe** to a non-excluded command (`jq`, `head`, `grep`, `tee`, `sort`, …)
- a **redirect** (`>`, `>>`)
- a **command substitution** (`$(...)`)
- a leading **`cd`**, or chaining a non-excluded command with `&&` / `;`

```sh
gh pr view 123 --json title,state           # bare — runs unsandboxed
gh pr view 123 --json title,state | jq      # sandboxed (jq isn't excluded)
gh pr view 123 --json title,state > f.json  # sandboxed — a redirect re-sandboxes the call
```

So there is **no** "redirect to a file, then read it" trick — the redirect
itself sandboxes `gh`. Keep it a single bare command, let the output come back on
stdout, and shape the output with `gh`'s own flags rather than piping.

## gh CLI: triage the token before blaming the sandbox

A `gh` failure has two unrelated causes, and the fix for one does nothing for the
other. Triage first — run `gh` **bare** (no pipe, no redirect):

```sh
gh auth status
```

**The token is expired or revoked** when `gh auth status` reports "The token in
… is invalid", or a bare `gh api …` returns GitHub's own JSON
`{"message":"Requires authentication", … "status":"401"}`. This is **not** a
sandbox problem: `gh` reached its token — unsandboxed by exclusion, by approved
escalation, or because the agent has no sandbox — and GitHub rejected it. No
sandbox setting fixes it, and neither does avoiding pipes. Re-authenticate
outside the sandbox, then retry:

```sh
gh auth login -h github.com
```

**The sandbox is the cause** when `gh auth status` is healthy yet a command still
fails with `failed to load config: … operation not permitted` on
`~/.config/gh/config.yml`, a TLS trust failure (`x509: OSStatus -26276`), or an
unexpectedly unauthenticated (rate-limited) response. `gh` keeps its token in the
macOS keychain (the `keyring` store), which is unreachable in-sandbox. Get `gh`
out of the sandbox by the harness's route (above): on an exclusion-list harness
keep it a single bare command, and shape output with `gh`'s own flags instead of
piping:

| Instead of | Use |
| --- | --- |
| `gh … \| jq '.field'` | `gh … --json field --jq '.field'` (gh embeds jq) |
| `gh … \| head -n N` | `gh … --limit N`, or `--json`/`--template` to shape output |
| `gh … \| grep X` | `gh … --json …` then filter with `--jq 'select(...)'` |
| `gh … \| tee file` | run `gh …` bare and read its stdout — don't redirect |

On an escalation harness, approve the prompt. An expired token still needs
`gh auth login` — escalation won't rescue it.

## pnpm: shell lookup fails before a lifecycle script starts

A filesystem profile that denies the root by default can make Node return
`spawn EPERM` when pnpm searches `PATH` for `sh`: one inaccessible `PATH` entry
stops the lookup before `/bin/sh`, even though spawning `/bin/sh` by absolute
path works. System tool directories inherited from the host on macOS can trigger
this. Setting `NPM_CONFIG_SCRIPT_SHELL=/bin/sh` makes pnpm start its lifecycle
shell by absolute path. Other tools that search `PATH` can still hit denied
entries. The pnpm warning about reading `~/.npmrc` is a credential denial doing
its job, separate from this failure.

## pnpm: a purge prompt is not a flag to silence

Some sandboxes deny writes inside any `.idea/` directory in the workspace, and a
few common packages (`iconv-lite@0.6.3`) ship one. A `node_modules` built outside
the sandbox contains those files, but pnpm cannot recreate them in-sandbox.

When pnpm reports that the modules directories "will be removed and reinstalled
from scratch", that prompt is the only thing between you and a full purge. It
appears even for `pnpm install --lockfile-only`. These all purge without asking,
then fail on the `.idea` write and leave `node_modules` empty:

- `--config.confirmModulesPurge=false` (it means "purge without asking")
- `CI=true`
- answering yes

Recovery is a plain `pnpm install --frozen-lockfile` run outside the sandbox.

For a dependency bump, edit the manifests or catalog, then ask the user to run
`pnpm install` in their own terminal, answering `n` to any purge prompt, and run
the gates in-sandbox afterwards. Do not regenerate the lockfile from the sandbox.

## Process inspection: ps, pgrep, and friends

The sandbox refuses `ps` and `top` (setuid binaries: `operation not permitted`)
and blocks the `sysmond` Mach service that `pgrep` and `pkill` need (`Cannot get
process list`, exit 3). Verified under Claude Code's sandbox; the others are
untested.

The failure is quiet. A loop like `while pgrep -f job; do sleep 5; done` sees a
non-zero exit, decides the process is gone, and exits at once. When a wait loop
returns instantly, suspect this before suspecting the job.

| Need | Use |
| --- | --- |
| Wait for a command you start | `cmd & pid=$!; wait "$pid"` (`$?` is its exit status); or the harness's own background-job facility, if it re-invokes you on exit |
| Is a PID alive | `kill -0 "$pid" 2>/dev/null` |
| Find PIDs by name (`pgrep NAME`) | `lsof -t -c NAME` (matches the command-name prefix; no `-f`) |
| What listens on a port | `lsof -nP -iTCP:PORT -sTCP:LISTEN` |
| Stop it | `kill "$pid"`; never `pkill -f` |

Each shell call may be a fresh process, so `$!` can be gone by the next one. To
wait across calls, save the PID to a file under `$TMPDIR` at start. A PID that
has gone means "finished, inspect the output", not "succeeded".

A zsh background job under the sandbox can print `nice(5) failed: operation not
permitted`. That is zsh trying to lower the job's priority; the job still runs.
`setopt no_bg_nice` silences it.

Don't add `pgrep` to an exclusion list: `lsof` covers it, and a pipe
re-sandboxes it anyway.

## When a bare command still fails: blocked Mach lookups

TLS verification through a sandbox proxy needs a Mach lookup for the system trust
daemon, and `pgrep` needs one for `sysmond`. A new failure naming a `com.apple.*`
service is the same class: a blocked Mach lookup. Widening what a sandbox allows
is a policy change for whoever owns its configuration, to be justified in the
commit — not something to work around from inside it. Don't try to lift the
sandbox; report the restriction instead, or take the harness's approval route
where it has one.

## Harness mechanics

Where each harness this payload configures sets the behavior above. Any other
agent follows whichever row matches how it runs shell commands.

| | Claude Code | Codex | Cursor |
| --- | --- | --- | --- |
| Sandboxed | yes | yes | no |
| Escape route | `sandbox.excludedCommands` in `.claude/settings.json` (matched per whole call) | `approval_policy = "on-request"`: approve the prompt and the command runs escalated | none needed |
| Background-job facility | `run_in_background` re-invokes the agent on exit | none | none |
| Mach lookup allowlist | `sandbox.network.allowMachLookup` (holds `com.apple.trustd*`) | none; config is `network_proxy` plus `domains`/`unix_sockets` | n/a |
| `.idea/` writes in the workspace | denied (built-in protected path) | untested; the profile grants workspace writes | allowed |
| `pnpm` shell lookup | unaffected | needs `NPM_CONFIG_SCRIPT_SHELL=/bin/sh`, set in `.codex/config.toml.template` | unaffected |
| Lifting the sandbox | `dangerouslyDisableSandbox` is disabled here | the escalation prompt is the route | n/a |

`allowMachLookup` has no counterpart to mirror in Codex or Cursor, which is the
one deliberate break in the otherwise-mirrored sandbox network policy.
