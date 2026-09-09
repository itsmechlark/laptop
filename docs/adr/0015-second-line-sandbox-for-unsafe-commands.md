---
name: srt-second-line-sandbox
description: Why unsafe commands run under srt, bypassing the agent gates, governed by ~/.srt-settings.json.
metadata:
  status: accepted
  topic: sandbox
---

# A second-line sandbox for running unsafe commands (srt)

**Context:** The three client configs are one granular sandbox over the agent's
own commands ([ADR 0002](0002-one-policy-three-clients.md)): secret reads denied,
egress allowlisted, destructive forms gated. That layer confines the agent. It
gives no sanctioned way to run a command the agent does not trust — a downloaded
installer, a `curl | sh`, an unaudited build script. The gate either blocks it
or the agent runs it with its own broad grants; there is no confined middle.

Anthropic's `sandbox-runtime` (`srt`, npm `@anthropic-ai/sandbox-runtime`) wraps
a single command in an OS-level sandbox — macOS Seatbelt via `sandbox-exec` plus
a proxy that enforces a network allowlist. It is the dual-isolation idea: an
untrusted command needs both filesystem and network confinement, because either
one alone leaks (read a key, or exfiltrate what you already read).

**Decision:** Adopt `srt` as a second line for unsafe commands, run as
`srt <cmd>` through a `bin/srt` shim that execs a pinned
`npx -y --package=@anthropic-ai/sandbox-runtime srt` (fetched on demand — no
npm-global install; `ripgrep`, its macOS runtime dependency, is added to `mac`).
The `--package` form is load-bearing: `npx <pkg> srt …` runs the package's `srt`
bin but passes the bin name through as a positional, so srt receives `srt <cmd>`
and wraps *itself* — a broken nested run whose inner sandbox can't initialize.
`--package` makes `srt` the command rather than an argument.

One shared `srt-settings.json`, tracked here and symlinked to
`~/.srt-settings.json`, governs every run in every project. It is global cargo
like `.agents/AGENTS.md`, not a per-client policy file mirrored three ways. It is
deliberately looser than the agent sandbox where that is safe: reads are
default-on minus an enumerated secret floor; writes span `~/Codespace` plus tmp
and caches; egress is the shared allowlist plus pip; the allowed unix sockets
are the 1Password SSH-agent, the local Postgres socket, and the Docker daemon
socket, so SSH-based git, commit signing, database, and container dev work under
a wrapped command. `allowUnixSockets` is connect-only — it cannot grant a
`bind()`, so socket-creating tools (Chrome's `ProcessSingleton`) still run
outside srt, not wrapped.

Every `srt` use is gated by an approval prompt — Claude `permissions.ask`, a
Codex `["srt"]` `prompt` rule, and Cursor's prompt-by-default with `Shell(srt)`
left unlisted — so the agent cannot run it silently; on approval it runs under
srt's confinement. It **bypasses** the per-command destructive gates: srt's own
confinement is the boundary, so `srt-settings.json` is the entire filesystem and
network boundary for a wrapped command, and the bypass is natural rather than
special-cased — Claude and Codex gate on the command prefix — `srt` (and, on
Claude, the `npx …` form) — never the inner command; Cursor's substring hook gets an explicit
early-return for an unchained `srt`/`npx-srt` command that then falls through to
the prompt. The settings file and the shim are guarded read-only in all four
configs, the same way the client policy files are.

srt must run **un-nested** on macOS. It binds an `AF_UNIX` control socket in
`TMPDIR`, and a parent Seatbelt sandbox refuses that `bind()` (the same block
that stops Chrome's `ProcessSingleton`), so a nested srt dies with
`listen EPERM … srt-mux-*.sock` before running anything. Each client therefore
runs the approved `srt` through the unsandboxed escape it already has: Claude
`excludedCommands`, Cursor unsandboxed execution, Codex an `on-request` approval
that escalates the command out of Seatbelt. `enableWeakerNestedSandbox` is a
Linux/Docker-only knob that does nothing on macOS Seatbelt, so it stays at its
`false` default. A manually typed `srt` inside an already-sandboxed shell hits
the same `EPERM` — run it from a normal terminal.

**Consequences:** There is now a confined place to run untrusted commands on
every client, gated by an approval prompt. Because the per-command gates are
replaced by that prompt plus srt's confinement, a mis-scoped `srt-settings.json`
is the whole boundary for what an approved command can touch — hence the
conservative secret and policy-file denials. The
writable set is the blast radius: `~/Codespace` wholesale means a wrapped
`rm -rf` can damage any project, though never secrets, home-config, PATH-shim
dirs (`~/.asdf`, `~/.rvm` are not writable), shell rc, git internals, or the
client policy files (srt's own mandatory-deny set plus `denyWrite` cover these).
srt governs files and egress but not environment variables, so token scrubbing
still rests on each client's env policy — verify it survives Claude's
`excludedCommands`. The allowed unix sockets are reachable by a wrapped command,
so an approved `srt` run can authenticate or sign as the user (1Password agent)
and — via the Docker daemon socket — reach host-root-equivalent access that
escapes the sandbox entirely; the per-use approval prompt is what gates that.
That prompt is narrowest on Codex: its argv-prefix rules gate the `srt` shim but
cannot match the versioned `npx … sandbox-runtime … srt` form, so that raw form
runs srt-confined yet unprompted — the shim is the sanctioned entrypoint there,
while Claude and Cursor gate both forms. Because Codex's approved srt also runs
outside Seatbelt (above), srt's own proxy governs its egress there — the two
hosts beyond the primary allowlist are reachable, not intersected away. It adds a
fourth policy surface to guard, and a parity-table row that records the plumbing
per client.

**Rejected:** An npm-global install step in `mac`. It adds a maintained global
dependency and a version to keep current; npx-on-demand through a pinned shim
gives the same entrypoint with no install surface, and `registry.npmjs.org` is
already allowlisted.

Wrapping the whole agent process instead of individual commands. Per-command is
what "run this unsafe thing" needs; the one settings file serves a whole-process
wrap later too, so this was not either/or.

Reusing the primary allowlist verbatim, or allowing all egress. The primary list
has no Python index, which real work needs; allow-all discards the bounded-egress
half of dual isolation that makes running untrusted code acceptable. A bounded,
slightly broadened list is the middle path.

Keeping the gates on the inner command — teaching each client's guard to unwrap
`srt` and re-check what it wraps. That re-gates exactly the commands `srt` exists
to run, making it pointless. srt's OS confinement replaces the gate for wrapped
commands instead.
