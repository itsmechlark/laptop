---
name: <stable kebab-case identity, not the timestamped filename>
description: <one line, under 120 characters — what the next agent is picking up>
metadata:
  status: open
  topic: <kebab-case-join-key, shared with the spec, plan, and lore notes>
  agent: claude|codex|cursor|none
  supersedes: []
  repo: <the repository's name — only in ~/.agents/handoffs/; delete this line in a repo's own docs/handoffs/>
---

# <Task or area> — where it stands

REQUIRED. Replace every line of guidance in this file with content, and delete
the REQUIRED/OPTIONAL markers as you go. A heading with guidance still under it
is an unfilled handoff, and the next agent cannot tell that from a section that
genuinely had nothing to say.

## Goal

REQUIRED. One sentence: what the next agent should accomplish. Not what was
done — what has to be true when they are finished.

## Context

REQUIRED. What is already done, and what state the code is in. Reference
artifacts by path or URL instead of restating them —
`docs/specs/20260911142205-webhook-retry.md`, PR #412, the ticket key. The next
agent can open them; a paragraph paraphrasing one only goes stale on its own
schedule.

Never describe the work by its commit status. "Uncommitted", "staged", "nothing
staged", "the tree is clean" are each false the moment this file is committed.
Name the branch, the task, and the files instead.

## Remaining work

REQUIRED. Ordered by dependency, each step actionable without asking anyone a
question. A step that needs a decision is not a step — settle it under
Constraints, or say which default to take.

1. <step>
2. <step>

## Constraints

REQUIRED. Decisions already made, approaches tried and rejected with the reason
each lost, files not to touch, conventions this repo enforces. The rejected
approach earns its place most: without it the next agent re-implements the thing
that already failed.

## Gates

REQUIRED. What was run, over what scope, and what came back — so the next agent
knows what it can trust and what it has to run again. Give the gate you could not
run its own row with the reason, rather than leaving it out.

| Gate | Scope | Result |
| --- | --- | --- |
| <command> | <what it covered> | <passed, or the failure, or not run and why> |

## Suggested skills

OPTIONAL. Which skill handles which step, named — "`tdd` for the implementation,
`git-commit` once it lands." Omit the heading entirely when the remaining work is
ordinary; never write "None".
