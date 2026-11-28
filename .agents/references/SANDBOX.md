---
name: sandbox-gotchas
description: Workarounds for shell commands that fail under a macOS Seatbelt sandbox, whichever agent runs them — gh CLI auth (telling an expired token apart from a sandbox keychain failure), the pipe/redirect trap where a pipe, a leading cd, or git -C re-sandboxes an excluded command, git fetch or push over HTTPS failing with "could not read Username" when chained, git index- and ref-writing commands that fail in worktrees the session did not create, git worktree add and remove failing on .git/worktrees, 1Password shell plugins (op plugin run) failing in-sandbox or with "interactive IO not available", the pnpm purge prompt that destroys node_modules when silenced, pnpm and npm installs that fail in-sandbox, simulator, emulator, and Java-based tools (Maestro, Expo) that can't reach their system services, and process lookups (ps, pgrep) that fail quietly, so use lsof or kill -0. Read when a command fails with "operation not permitted", HTTP 401, "could not read Username", "interactive IO not available", or a keychain/credential error, or when a loop that waits on a process returns immediately. An agent that runs unsandboxed needs only the gh token triage.
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
- anything between the program and its subcommand, so `git -C <dir> commit`,
  `git --no-pager fetch`, and `git -c k=v push` all miss a `git commit *` /
  `git fetch *` / `git push *` pattern
- a **`VAR=value`** prefix (`GIT_SEQUENCE_EDITOR=true git rebase …`) — a
  harness may strip a few well-known ones before matching, but don't rely on
  which

```sh
gh pr view 123 --json title,state           # bare — runs unsandboxed
gh pr view 123 --json title,state | jq      # sandboxed (jq isn't excluded)
gh pr view 123 --json title,state > f.json  # sandboxed — a redirect re-sandboxes the call
```

**Never pipe, redirect, or wrap a command on the exclusion list.** It was
excluded because it needs something the sandbox blocks — credentials, the
network, a keychain, per-worktree git state. Wrapped, it runs sandboxed without
that and fails, often with an error that doesn't mention the sandbox. Run it as
a single bare call and shape its output with its own flags. The "Excluded
commands" row in [Harness mechanics](#harness-mechanics) lists what is on each
harness's list.

To run an excluded command in another directory, change directory in its own
call, confirm where you are (`git rev-parse --show-toplevel`), then run the
command bare. That only works where the harness keeps the working directory
between calls. Where it doesn't, no bare form reaches the other directory: leave
the write to a session that can, and say so.

So there is **no** "redirect to a file, then read it" trick — the redirect
itself sandboxes `gh`. Keep it a single bare command, let the output come back on
stdout, and shape the output with `gh`'s own flags rather than piping.

### git over HTTPS: the trap reads as an auth failure

`git fetch`, `pull`, `push`, and `ls-remote` against an HTTPS remote get their
credentials from a credential helper — commonly `gh auth git-credential`, which
needs `gh`'s config and keychain. Chain one with the commands that use its
result and the whole call stays sandboxed, so the helper can't answer and git
falls back to prompting with no terminal:

```
warning: failed to load config: open …/.config/gh/config.yml: operation not permitted
fatal: could not read Username for 'https://github.com': Device not configured
```

The error says nothing about the token. Fetch in one bare call, then run
`rev-parse`, `merge-base`, `log`, or `diff` in the next — those are local and
work sandboxed:

```sh
git fetch origin pull/123/head:refs/remotes/origin/pr-123 main
```

```sh
git merge-base origin/main origin/pr-123 && git diff --numstat origin/main...origin/pr-123
```

If the bare fetch fails the same way, run the `gh` token triage below. A network
subcommand that isn't on the exclusion list — `git clone`, `git submodule
update` — fails like this however it's written; hand it to the user rather than
rephrasing it.

## git in a worktree: index, ref, and worktree writes are blocked

Git stores per-worktree state — the index, `ORIG_HEAD`, `MERGE_HEAD`,
`CHERRY_PICK_HEAD`, `REVERT_HEAD`, and rebase progress — inside the main
repository's `.git/worktrees/<name>/` directory, not under the worktree's own
working tree. Some sandboxes make this path read-only for worktrees the current
session did not create, so any git command that writes a lock file there fails:

```
fatal: Unable to create '…/.git/worktrees/<name>/index.lock': Operation not permitted
```

or, for ref-writing commands:

```
fatal: update_ref failed for ref 'ORIG_HEAD': cannot lock ref 'ORIG_HEAD':
Unable to create '…/.git/worktrees/<name>/ORIG_HEAD.lock': Operation not permitted
```

Anything that writes the index, a per-worktree ref, or the worktree's `HEAD`
is affected: `add`, `apply --cached`, `commit`, `rm`, `mv`, `restore`, `stash`,
`merge`, `rebase`, `cherry-pick`, `pull`, `fetch` (`FETCH_HEAD`), `reset`,
`revert`, `checkout`, `switch`, and `branch -m` on a checked-out branch, along
with rarer ones such as `am`, `bisect`, and `update-index`. Read-only commands —
`status`, `diff`, `log`, `show` — are unaffected, wrapped or not. The main
working tree is unaffected too, because its per-worktree files live under `.git/`
directly — which is why a wrapped write command that works in the main checkout
fails the first time it runs in a worktree.

Get the command out of the sandbox by the harness's escape route (above): on an
exclusion-list harness, the git subcommand must be on the list and the command
must be bare (no pipe — see the pipe trap). A subcommand that isn't on the list
fails however it's written; report it rather than rephrasing it. On an
escalation harness, approve the prompt.

Creating a worktree is the exception the exclusion list does not cover. `git
worktree add` writes a new `.git/worktrees/<name>/`, and a sandbox can keep that
read-only even for an excluded, bare command:

```
fatal: could not create directory of '.git/worktrees/<name>': Operation not permitted
```

Create it through the harness's own worktree mechanism, which grants the session
write access to the worktree it makes. When the branch needs a start-point
other than the mechanism's default, create the branch first with `git branch
<name> <start-point>` (it writes only a shared ref, not `.git/worktrees`, so it
works sandboxed), then let the mechanism check it out. Otherwise have the user
run the `git worktree add` themselves and enter the existing path. If the
mechanism bases new branches on a remote-tracking ref, fetch first — the local
ref is only as fresh as the last fetch.

`git worktree move` fails the same way. `remove` and `prune` are hook-assisted
in Claude Code: a `PreToolUse` hook intercepts bare `git worktree remove
<abs-path>` and `git worktree prune`, runs them from the hook context (outside
the sandbox where `.git/worktrees` is writable), and returns the result as a
deny reason. The command must be bare (no pipe, no `-C`, no prefix) and `remove`
requires an absolute path. `git worktree move` has no hook; hand the user the
command. Deleting the branch afterwards (`git branch -d`) writes only a shared
ref and works sandboxed.

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
| `echo '{"k":"v"}' \| gh api --method POST … --input -` | write body to `$TMPDIR/body.json` with `printf` or `jq`, then `gh api --method POST … --input "$TMPDIR/body.json"` (bare) |

On an escalation harness, approve the prompt. An expired token still needs
`gh auth login` — escalation won't rescue it.

## 1Password shell plugins: call `op plugin run` bare

A 1Password shell plugin works through an alias (`alias pulumi="op plugin run
-- pulumi"`) that the user's interactive shell sources. An agent's shell may not
load it, so `pulumi` resolves to the real binary and runs without the 1Password
credential — succeeding on any stale login it finds, or failing unauthenticated.
Call the plugin form explicitly, as one bare command:

```sh
op plugin run -- pulumi whoami
```

`op` itself can't run in-sandbox: it fails reading `~/.config/op/config` with
`operation not permitted`. Take the plugin form out by the harness's escape
route. On an exclusion-list harness, list `op plugin run -- <tool> *` for each
tool, never `op *` — that would let `op read op://…` print any vault secret
unsandboxed. Keep the form exact, with no `op` options before or after
`plugin run`: `op --account … plugin run -- pulumi …` misses the exclusion and
the wrapped tool's approval rules, so it stays sandboxed or is denied.

`[ERROR] interactive IO not available` is not the sandbox. `op` ran, found no
default credential for the current directory, and tried to open its credential
picker with no terminal to show it in. A default saved with "Use automatically
when in this directory or subdirectories" doesn't reach sibling worktree
directories (`<repo>.worktrees/<name>` sits beside `<repo>`, not inside it), so
the same command works in the main checkout and fails in a worktree. Ask the
user to run `op plugin init <tool>` in their own terminal and choose the global
default, or a directory that contains both the checkout and its worktrees. An
agent can't answer the picker.

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

So never run an install-family command (`install`, `i`, `add`, `remove`, `rm`,
`uninstall`, `un`, `update`, `up`, `upgrade`, `dedupe`, `rebuild`, `rb`,
`prune`, `install-test`, `it`) inside the sandbox. Take it out by the
harness's escape route (above). On an exclusion-list harness that means a single
bare call. A pipe, a leading `cd`, or a `CI=true` prefix sends it back into the
sandbox, and with it the purge. Where the harness has no escape route, ask the
user to run it in their own terminal, answering `n` to any purge prompt.

Put the subcommand straight after `pnpm` and any `--filter`, `-C`, or `-r`
after it: `pnpm add zod --filter web`, not `pnpm --filter web add zod`.
Exclusion lists and prefix rules match from the start of the command, so a flag
in front of the subcommand keeps it in the sandbox.

For a dependency bump, edit the manifests or catalog, run the install that way,
then run the gates in-sandbox. Recovery from a purged tree is the same bare
`pnpm install --frozen-lockfile`.

npm has no purge prompt, but it fails in-sandbox for the same `.idea` reason
and because its cache under `~/.npm` is not writable, so the same rule applies
to its install family (`install`, `i`, `ci`, `uninstall`, `update`, `dedupe`,
`rebuild`, `prune`, and their aliases). npm also runs every dependency's install
script, so pass `--ignore-scripts` where the project doesn't need them.

Whether such a call needs approval depends on the harness (see "Install-family
approval" below). Where a harness skips the prompt for committed install inputs,
a run right after you edit a `package.json`, a lockfile, `.npmrc`,
`pnpm-workspace.yaml`, `.pnpmfile.cjs`, or `patches/` still prompts. That is
expected; don't commit just to avoid it.

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

## Simulators, emulators, and Java-based tools

Mobile tooling reaches system services and home-directory state that the
sandbox blocks. Verified under Claude Code's sandbox:

| Symptom | Cause |
| --- | --- |
| `CoreSimulatorService connection became invalid` from the simulator CLI, `expo run:ios`, or Maestro on iOS | the simulator service is reached over XPC |
| `Unable to locate a Java Runtime` from `maestro` | the `/usr/bin/java` stub can't look up a JDK |
| `open: …/watchman/…-state: Operation not permitted` | watchman keeps its state under `~/.local/state` |
| reads of `~/.maestro`, `~/.expo`, or the Android SDK denied | those live under `~`, outside the readable roots |

None of this is fixed by an allowed path or domain. Run the tool outside the
sandbox by the harness's escape route (above), as one bare call. Prefer the
project's own binary (`pnpm exec expo`) over `npx expo`: `npx` fetches the newest
package from the registry when the binary isn't installed where it runs, and
that download shouldn't run unsandboxed.

Call the binary directly, not through a package script or pnpm's bin fallback.
`pnpm ios`, `pnpm run ios`, and `pnpm expo run:ios` don't match an exclusion
list, so they stay in the sandbox and fail with the errors above. Read the
script in `package.json` and run what it runs: `pnpm exec expo run:ios`.

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
| Excluded commands — never pipe, redirect, or wrap these | `acli *`; `gh *`; `git add *`, `git apply --cached *`, `git branch -M *`, `git branch -m *`, `git cherry-pick *`, `git checkout *`, `git commit *`, `git fetch *`, `git ls-remote *`, `git merge *`, `git mv *`, `git pull *`, `git push *`, `git rebase *`, `git reset *`, `git restore *`, `git revert *`, `git rm *`, `git stash *`, `git switch *`, `git worktree *`; `pulumi *`, `op plugin run -- pulumi *`; `srt *`, `npx @anthropic-ai/sandbox-runtime *`, `npx -y @anthropic-ai/sandbox-runtime *`; `trivy *`; `pnpm install *`, `pnpm i *`, `pnpm add *`, `pnpm remove *`, `pnpm rm *`, `pnpm uninstall *`, `pnpm un *`, `pnpm update *`, `pnpm up *`, `pnpm upgrade *`, `pnpm dedupe *`, `pnpm rebuild *`, `pnpm rb *`, `pnpm prune *`, `pnpm install-test *`, `pnpm it *`; `npm install *`, `npm i *`, `npm add *`, `npm ci *`, `npm clean-install *`, `npm uninstall *`, `npm remove *`, `npm rm *`, `npm r *`, `npm un *`, `npm unlink *`, `npm update *`, `npm up *`, `npm upgrade *`, `npm dedupe *`, `npm ddp *`, `npm rebuild *`, `npm rb *`, `npm prune *`, `npm install-test *`, `npm it *`, `npm install-ci-test *`, `npm cit *`; `maestro *`, `pnpm exec expo *`, `eas *` | none; escalation covers the whole command, so a pipe does not defeat it | none; nothing is sandboxed |
| Exclusion matching (verified) | a bare subcommand with no arguments matches (`git fetch` under `git fetch *`); `git -C`, `--no-pager`, `-c`, and most `VAR=` prefixes miss, though `GIT_TERMINAL_PROMPT=0` is stripped first. An excluded call skips the shell's own startup errors, a quick tell for which side it ran on | n/a | n/a |
| Working directory between calls | kept in the main session; reset for subagents, so a subagent can't `cd` then run a bare command | untested | untested |
| Install-family approval | a `PreToolUse` hook allows pnpm/npm `install` or `ci` with no package names, `remove`, and `prune` in every permission mode when every install input is committed (npm `install`/`ci` also need `--ignore-scripts`; a `packageManager` pin below pnpm 10 prompts); `add`, `update`, `dedupe`, `rebuild`, and install-test always prompt | every form prompts | every form prompts |
| Maestro approval | a `PreToolUse` hook allows `maestro test` (and the Maestro MCP `run` tool) when every flow it would run, sub-flows included, uses only device commands; scripts, `openLink`, `addMedia`, JavaScript, continuous mode, output outside the project, and other subcommands prompt | every form prompts | every form prompts |
| Background-job facility | `run_in_background` re-invokes the agent on exit | none | none |
| Mach lookup allowlist | `sandbox.network.allowMachLookup` (holds `com.apple.trustd*`) | none; config is `network_proxy` plus `domains`/`unix_sockets` | n/a |
| `.git/worktrees` writes (other session's worktrees) | read-only; escape via `excludedCommands` | untested; approval escalation is the escape route if affected | allowed |
| Creating a worktree | `git worktree add` stays sandboxed despite `excludedCommands`; use `EnterWorktree` with `name` — the `WorktreeCreate` hook in `.claude/settings.json` places it at `$HOME/Codespace/<repo>.worktrees/<name>`, cutting new branches from `origin/HEAD` without fetching. A second `name` is refused until `ExitWorktree` leaves the first | untested; approval escalation is the escape route if affected | `git worktree add` (unsandboxed) |
| Removing a worktree | Hook-assisted: `PreToolUse` intercepts bare `git worktree remove <abs-path>` and `git worktree prune`, runs them outside the sandbox, and returns the result as a deny reason. `remove` requires an absolute path; `move` has no hook. `ExitWorktree` with `remove` is the alternative for the worktree the session is still in | untested; approval escalation is the escape route if affected | `git worktree remove` (unsandboxed) |
| `.idea/` writes in the workspace | denied (built-in protected path) | untested; the profile grants workspace writes | allowed |
| `pnpm` shell lookup | unaffected | needs `NPM_CONFIG_SCRIPT_SHELL=/bin/sh`, set in `.codex/config.toml.template` | unaffected |
| Lifting the sandbox | `dangerouslyDisableSandbox` is disabled here | the escalation prompt is the route | n/a |

`allowMachLookup` has no counterpart to mirror in Codex or Cursor, which is the
one deliberate break in the otherwise-mirrored sandbox network policy.
