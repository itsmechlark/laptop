---
name: sandboxed-pruning-of-claude-auto-memory-is-impossible
description: Why Claude auto-memory cannot be rm-pruned in a sandboxed session, and tombstones are the in-session convention.
metadata:
  status: accepted
  topic: sandbox
---

# Sandboxed pruning of Claude auto-memory is impossible

**Context:** Claude Code's auto-memory stores one file per fact under
`~/.claude/projects/<project-slug>/memory/`, and its own instructions tell an
agent to delete memories that turn out to be wrong. Deletion needs `rm`, a
sandboxed Bash operation. Claude Code protects the whole `~/.claude/projects`
subtree against sandboxed Bash writes: an ordinary nested path like
`~/.claude/foo/bar` is writable under the `allowWrite` grant on `~/.claude`, but
anything under `~/.claude/projects/**` is denied. The Write tool reaches memory
files — it is governed by `permissions`, not the sandbox — so an agent asked to
prune can overwrite a file but never unlink it, and `MEMORY.md` pointers
accumulate stale entries.

We tried the obvious lever: a narrow, more specific
`sandbox.filesystem.allowWrite` entry, `~/.claude/projects/*/memory/**`, on the
theory that a deeper explicit grant would re-open just the memory subtree. After a
session reload it was verified **inert** — writing `probe.md` (a non-dot name,
matching real `*.md` memory files) into the memory dir still returned `operation
not permitted`. The protection over `~/.claude/projects/**` is applied after and
above `allowWrite`; no path grant, globbed or literal, overrides it. Two other
levers are closed too: `dangerouslyDisableSandbox` is disabled by policy, and
adding `rm` to `sandbox.excludedCommands` would un-sandbox every delete on the
machine, far past memory.

**Decision:** Do not add any memory path to `sandbox.filesystem.allowWrite` — a
verified no-op does not belong in a security-boundary file. In a sandboxed
session, "pruning" a memory means retiring it in place: overwrite the file with a
`SUPERSEDED` tombstone and remove its pointer from `MEMORY.md`, so nothing
recalls it. Actually deleting the files is an out-of-band step the user runs in a
normal (non-sandboxed) terminal.

**Consequences:** Retired memories stop influencing sessions immediately (no
pointer, tombstoned body), which is the behavior that mattered. The files remain
on disk until an out-of-band `rm`, so the memory dir grows slowly with
tombstones; that is cosmetic, not correctness. An agent that reports a memory as
"deleted" is wrong in this setup and should say "retired / tombstoned."

**Client parity:** No config changed, so nothing to mirror. The constraint is
Claude-specific — the `~/.claude/projects` protection is a Claude Code product
behavior; Codex and Cursor store memory elsewhere and are unaffected.

**Rejected:** Adding `~/.claude/projects/*/memory/**` (or a per-repo
`settings.local.json` with the literal slug) to `allowWrite` — verified inert,
and the literal form fails for the same reason the glob did, since the protection
is subtree-wide rather than pattern-specific. Un-sandboxing `rm` via
`excludedCommands` — opens destructive deletes machine-wide to buy one narrow
capability. Leaving the inert grant in place as documentation — a security-policy
file should not carry entries that do nothing.
