---
name: ship-sandbox-troubleshooting-as-a-referenced-doc
description: Why sandbox failure workarounds ship as a read-on-demand .agents/references/SANDBOX.md pointed to from AGENTS.md, rather than inline in AGENTS.md or as a skill.
metadata:
  status: accepted
  topic: agent-instructions
---

# Sandbox troubleshooting ships as a read-on-demand referenced doc

**Context:** The Seatbelt sandbox that Claude Code and Codex apply to each Bash
command breaks tools in ways an agent cannot reason out from the error alone —
most persistently `gh`, which loses keychain access when sandboxed and fails
with HTTP 401 or an "operation not permitted" on its own config. The subtlety
is the pipe trap: `gh` is in `excludedCommands` and works on its own, but a pipe
to `head` or `jq` re-sandboxes the whole pipeline. This recurs across sessions,
and each one re-derives the same workaround or disables the sandbox to escape
it. The knowledge needs to ship to every client and be in front of an agent at
the moment a command fails.

**Decision:** The workaround lives in `.agents/references/SANDBOX.md`, a
read-on-demand doc shipped by symlinking `.agents/references/` into
`~/.agents/references`. `.agents/AGENTS.md` — the always-loaded global file —
carries only a one-line pointer telling an agent to Read it when a command
fails under the sandbox. The body loads on demand, not every session.

**Consequences:** The fix is one Read away from any agent on Claude Code or
Codex, and future sandbox gotchas append to one file instead of scattering.
`references/` now ships (previously only `CONTEXT-FORMAT.md` lived there,
unshipped), so it is a new top-level link — `sh mac` is required after pulling
this, and the symlink-map tables, README, and repo layout name it. The pointer
is a breadcrumb, so it only helps an agent that Reads it when a command fails;
the wording ties the Read to the symptoms ("operation not permitted", HTTP 401,
a credential error that doesn't reproduce on its own) to make that likely.
Cursor runs unsandboxed and never needs the doc, but reaches it through the same
payload at no cost.

**Rejected:** Inlining the workaround in `.agents/AGENTS.md`. It is the only
always-loaded global file, and Codex counts it plus each project's own
`AGENTS.md` against a single 32 KiB budget, silently truncating the tail ([the
`agent-instructions` rule](../../rules/agent-instructions.md)). A harness gotcha
would spend every repo's shared byte budget; a one-line pointer costs almost
nothing.

**Rejected:** A skill. Skills are task workflows invoked by description match,
and this is reference prose an agent consults mid-failure, not a procedure it
runs. A skill also carries the invocability and trigger-eval machinery this repo
holds skills to, for no gain over a plain doc with a pointer.

**Evidence:** `.agents/references/SANDBOX.md`, `.agents/AGENTS.md`, `mac`
(`symlink_path "$AGENTS_DIR/references"`), `AGENTS.md` (symlink map + layout),
`README.md`
