---
name: draft-spec
description: Turn the current conversation into a formal, agent-ready spec document for triage and implementation planning. Use when the user asks to spec something out, write a discussion up as an issue, or capture a feature before coding starts.
argument-hint: "[feature, decision, or conversation to specify]"
disable-model-invocation: true
---

# Draft Spec

Convert the current conversation into a spec that another person or agent can implement without guessing. Synthesize what is already known; do not restart the requirements interview.

## When to use

Use only when explicitly invoked, for example when the user asks to turn a discussion into a specification or issue. Do not invoke this automatically in the middle of implementation.

## Process

### 1. Ground the spec in the repository

Explore the repository enough to understand the current state before writing. Look for:

- The project's glossary or `CONTEXT.md`; use its vocabulary consistently.
- Relevant ADRs; respect settled decisions and call out conflicts rather than silently rewriting them.
- Existing behavior and similar features; do not describe something as new if the code already provides it.
- Existing test seams and prior art; prefer the highest existing seam over inventing a new one.

If no glossary, ADR, or prior art exists, say so internally and avoid inventing a project-specific vocabulary or convention.

### 2. Sketch the test seams, then confirm them

Before drafting the full spec, identify where the behavior should be verified. Prefer one high seam that exercises the user-visible contract, adding lower seams only where they expose an independent behavior or make a failure diagnosable. Name the seam in terms of observable behavior, not implementation files.

Briefly show the user the proposed seams and ask whether they match their expectations. This is the one confirmation gate in the workflow; do not turn it into a wall of requirements questions. If a missing answer genuinely prevents a defensible spec, ask one targeted question and explain what decision it changes.

### 3. Synthesize, do not interview

Use the conversation, repository evidence, glossary, ADRs, and confirmed seams as the source of truth. Preserve uncertainty honestly:

- Do not invent actors, outcomes, edge-case behavior, APIs, schema fields, or rollout plans.
- Put unresolved decisions in **Further Notes** or ask the one blocking question before drafting.
- Separate what the user wants from how the code will implement it.
- For Jira or another product-facing tracker, keep the main narrative in user and outcome language. Put concise implementer detail in **Implementation Decisions**.

### 4. Write the spec

Use the fixed template below and keep the section order unchanged. User stories should be extensive enough to cover the happy path, boundaries, permissions, failure states, and operational consequences that are supported by the conversation. Do not pad the list with speculative stories.

Do not include specific file paths, diffs, or code snippets. The only exception is a prototype-style type, state machine, reducer, or payload shape when the shape itself is the decision; include only the decision-rich part and say that it came from a prototype.

### 5. Check the draft

Before presenting it, check that:

- The problem and solution describe a user-visible outcome, not an implementation task.
- Every user story follows `As an <actor>, I want a <feature>, so that <benefit>`.
- Implementation decisions describe boundaries, contracts, data, interactions, and rollout constraints without becoming a code plan.
- Testing decisions describe external behavior and identify relevant prior art.
- Out-of-scope items protect the slice from silently becoming an epic.
- Assumptions and unresolved choices are visible rather than implied.

## Spec template

```markdown
## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A numbered list of user stories. Each user story uses this format:

1. As an <actor>, I want a <feature>, so that <benefit>

Cover the supported happy paths, edge cases, permissions, error states, and relevant operational behavior. Do not invent stories that the conversation or repository does not support.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules or boundaries that will be built or modified
- The interfaces or contracts that will change
- Technical clarifications from the developer
- Architectural decisions and relevant ADR constraints
- Schema or data changes and compatibility requirements
- API contracts and specific interactions
- Rollout, observability, security, or idempotency constraints where relevant

Do not include specific file paths or code snippets. A compact prototype-derived state machine, reducer, schema, or type shape is allowed when it expresses the decision more precisely than prose.

## Testing Decisions

A list of testing decisions that were made. Include:

- What makes a good test: verify external behavior through the highest useful seam, not implementation details.
- Which boundaries or modules will be tested and why.
- The happy path, edge cases, failure states, authorization boundaries, and compatibility cases that matter.
- Prior art for the tests: similar test types, helpers, fixtures, or conventions already used in the repository.

## Out of Scope

A description of the things that are explicitly out of scope for this spec, including adjacent slices that should not be pulled into the implementation.

## Further Notes

Assumptions, unresolved questions, dependencies, rollout notes, or other context that a future implementer should know.
```

## Publication and tracker handoff

The spec is a draft until the user has seen it and confirmed the seams and content. Show the exact Markdown before any outward-facing write.

Do not assume an issue tracker, tracker API, project key, label name, or workflow status. Do not publish directly with a hardcoded `ready-for-agent` label. Instead:

- If the user only asked for a spec, return the Markdown draft in the conversation.
- If they request a durable local artifact, write it to the path or documentation location they specify; do not invent a repository-wide specs directory.
- If an issue already exists, hand the draft to the repository's `triage` skill. Triage owns tracker-specific state mapping, verification, and the `ready-for-agent` decision.
- If a new tracker item is requested, use the configured tracker-specific issue-creation workflow, resolve the real project and state vocabulary first, and obtain explicit approval immediately before publishing.
- If no tracker integration is available, leave the spec as Markdown and say that publication was not performed.

The handoff must preserve the distinction between product-facing problem and outcome language and the short implementation brief an agent needs. Never apply a label or close an item merely because the spec says to do so.

## Tone

Precise, collaborative, and honest about uncertainty. The goal is a spec that survives handoff to a changing codebase, not paperwork that makes an underspecified request look complete.

Adapted from [mattpocock/skills](https://github.com/mattpocock/skills) (`skills/engineering/to-spec`, MIT).
