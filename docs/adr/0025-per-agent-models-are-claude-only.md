---
name: per-agent-models-are-claude-only
description: Why four subagents run on a cheaper model on Claude Code only, why Cursor now reads a rendered copy of agents/, and how effort reaches Codex.
metadata:
  status: accepted
  supersedes: 24
  topic: agents
---

# Per-agent models are Claude-only

**Context:** [ADR 0024](0024-subagents-wrap-skills-for-fresh-context-work.md)
pinned every subagent to `model: inherit`. Claude Code and Cursor read the same
file, and they don't accept the same model names. As verified against their
documentation on 2026-11-22,
[Claude Code](https://code.claude.com/docs/en/sub-agents) accepts the aliases
`sonnet`, `opus`, `haiku`, and `fable`, a full model ID, or `inherit`.
[Cursor](https://cursor.com/docs/context/subagents) documents only `inherit` or
a full model ID, and says nothing about an unrecognized value. So every
subagent ran on the session's model, often the most expensive one, including
those doing bounded reading and writing.

**Decision:** `explainer`, `cold-reader`, `review-responder`, and `spec-writer`
run on `model: sonnet`. `explainer` runs at `effort: low`, because it mostly
searches. The other three run at `medium`. `reviewer`, `bug-hunter`, and
`implementer` stay on `inherit`, because a defect they miss ships.

`model` and `effort` are Claude Code's fields. The other clients get rendered
copies that carry only what they can read:

- **Cursor** now reads a copy rendered by `scripts/gen-cursor-agents` into
  `.cursor/generated-agents/`, linked to `~/.cursor/agents`. That replaces
  ADR 0024's direct link to `agents/`. The copy resets `model` to `inherit` and
  drops `effort`, which Cursor does not define. Everything else, including
  `readonly`, passes through unchanged. Cursor runs every agent on its
  parent's model.
- **Codex** gets `effort` as `model_reasoning_effort`, with Claude's `max`
  mapped to Codex's highest level, `xhigh`. It gets no model, because a Claude
  alias names no Codex model. So Codex saves only where an agent's effort is
  set below the parent's, which today means `explainer`, against the template's
  `medium`.

`check-payload` now accepts `model` as an alias or `inherit`. A full model ID
fails, because it would be pinned on Claude Code alone and age there
unnoticed. `effort` must be one of `low`, `medium`, `high`, `xhigh`, or `max`.
The check renders the Cursor copy and fails if `model` is not `inherit`, if
`effort` survives, or if `readonly` differs from the source. The fixture grows
to fourteen detections.

The rendered Cursor copy is what Cursor loads as instructions, so no agent may
write it. That follows ADR 0024's rule for the Codex copy. Claude Code denies
`Edit` and sandboxed writes to `.cursor/generated-agents/` and
`~/.cursor/agents/`, and Cursor adds `Write(~/.cursor/agents/**)` beside its
existing `Write(**/.cursor/**)`. Codex's `.cursor/** = "read"` already covers
the repository copy, and `~/.cursor` is not writable there.

**Consequences:** The savings are Claude Code's. Cursor saves nothing, and
Codex saves only on `explainer`. Neither gap can be closed without naming
models from each vendor's catalog in this repository, and those names change
faster than the agents do. Model choice is per-client tuning under
[ADR 0002](0002-one-policy-three-clients.md), not shared policy.

An agent edit now needs `sh mac` before Cursor sees it, as Codex already did.
Like Codex, a stale Cursor copy left by an edit without `sh mac` is not
detected.

On the Claude side, a nested subagent inherits its parent's model. An agent
this repository pins to Sonnet therefore runs anything it spawns on Sonnet as
well. None of the four can spawn today: each lists its `tools` without
`Agent`.

Making room for this decision took the combined AGENTS.md files past Codex's
64 KiB `project_doc_max_bytes`. The template now sets 96 KiB. Past that, the
fix is moving material out of AGENTS.md, not raising the cap again.

**Rejected:**

- **Aliases in the shared file, relying on Cursor's fallback.** Cursor
  documents a fallback only for blocked or unavailable models, not for an
  unrecognized name, so behavior on `sonnet` is unknown.
- **Cursor and Codex model IDs in the frontmatter** (`cursor-model:`,
  `codex-model:`). They would be the only vendor catalog names in the payload,
  and pinned names go stale without failing anything.
- **Haiku for `explainer`.** Mapping a flow with `file:line` evidence and
  judging placement calls for more reasoning than search alone. Sonnet at low
  effort is the cheaper setting that keeps the answers trustworthy.
- **`CLAUDE_CODE_SUBAGENT_MODEL`.** It applies to every subagent at once, and a
  definition's own `model` field, `inherit` included, already outranks it.

**Evidence:** `agents/explainer.md`, `agents/cold-reader.md`,
`agents/review-responder.md`, `agents/spec-writer.md`,
`scripts/gen-cursor-agents`, the `effort` mapping in `scripts/gen-codex-agents`,
and the model, effort, and Cursor-render checks in `scripts/check-payload`.
