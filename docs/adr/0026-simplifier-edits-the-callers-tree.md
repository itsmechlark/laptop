---
name: simplifier-edits-the-callers-tree
description: Why an eighth subagent, simplifier, joins the roster ADR 0024 set, and why it edits the caller's working tree in place instead of a worktree the caller prepares.
metadata:
  status: accepted
  topic: agents
---

# The simplifier edits the caller's tree

**Context:** The `simplify-code` skill replaced the `code-simplifier` plugin
for Claude Code, which shipped as a subagent rather than a skill. The plugin
could refactor a change from outside the context that wrote it: no attachment
to the shape the code was first written in, and none of the file contents
landing in the main thread. [ADR 0024](0024-subagents-wrap-skills-for-fresh-context-work.md)
admits a subagent that "earns its place by starting fresh", and simplifying
code it did not write is that case. A skill alone runs in whatever context
loads it.

The roster's only other writing agent, `implementer`, works in a worktree its
caller prepared. That fits a task built in parallel and merged later. A
cleanup pass applies to work that is usually uncommitted in the caller's own
tree, and a worktree branches from a commit, so it would not contain that work.

**Decision:** Add `simplifier`, wrapping `simplify-code`, as the eighth agent.
It edits the caller's working tree in place, with these limits written into
its body:

- It never stages, commits, stashes, resets, restores, checks out, or pushes,
  and never discards a change. The tree may hold work it did not make.
- The caller waits for it and does not edit the same tree meanwhile. The
  description says so, because nothing else enforces it.
- Everything `simplify-code` leaves to the user comes back as a returned
  finding, per ADR 0024's rule that questions stay in the main thread.

It keeps `model: inherit` ([ADR 0025](0025-per-agent-models-are-claude-only.md)):
it writes production code, which is not the place to save on the model.

**Consequences:** On Claude Code it is denied only the `Agent` tool, like
`implementer`. On Cursor and Codex nothing stops it running git commands
beyond its body's instructions and the parent's sandbox and approval policy,
the same gap ADR 0024 records for the read-only agents.

No skill dispatches it yet. The main session delegates to it by description,
or `simplify-code` names it for a fresh-context run.

Rejected: a worktree the caller prepares, as for `implementer`. Uncommitted
work would have to be committed or copied over first, and the result merged
back. That is a heavy round trip for a cleanup pass.
