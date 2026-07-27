---
name: pull-request
description: How to write a pull request title and description. Use when opening, drafting, or editing a pull request, writing a PR description, or composing a PR title. Covers the Reasoning/Summary template, behavior-change tables, the Conventional Commits title format, title length, and optional issue links.
---

# Pull request title & description

**Don't open or update a PR unless explicitly asked.** Drafting the title/description for review is fine; creating or editing the PR publishes to the remote, so wait for explicit instruction (as with commits and pushes).

PRs are for the **engineering team** — write in technical language: what changed and how, design decisions and trade-offs, testing performed, risks, and migration/rollout notes. If the work is tracked in an issue tracker, link the issue for product context, but keep the engineering narrative in the PR.

## Title

The PR title follows the same Conventional Commits format as commits: `<type>[optional scope]: <description>`. When the project tracks work in an issue tracker, append the issue key in square brackets at the end — `<type>[optional scope]: <description> [ISSUE-KEY]` (e.g. `fix(onboarding): validate overlap instead of auto-setting end date [ABC-1234]`). The title is bound by the same length limit as a commit subject — aim for ≤50 and never exceed the 72-character hard cap, measuring the `<type>[optional scope]: <description>` portion (any trailing `[ISSUE-KEY]` is exempt) so a PR and its commit stay easy to correlate at a glance.

## Body

```markdown
## Reasoning

Why this change exists: the problem it solves, the risk/impact of the
status quo, the chosen approach, and any rollout/gating considerations.
Product context plus engineering rationale.

## Summary

A product-like summary of what changed, with an engineering-level
overview of the approach.

## Testing

How the change was verified — commands run, scenarios exercised, results.

## Risks & rollout

Failure modes, feature-flag/gating, and migration or rollback steps.
```

Rules:
- **Summary is not a code walkthrough.** The code is the source of truth — do not narrate it line by line or method by method. Describe *what* changed and *why* at a level above the diff: the user-facing outcome plus a concise engineering summary of the approach.
- **Behavior changes go in a table.** If the PR changes runtime/product behavior, include a Markdown table summarizing it (e.g. input/condition → resulting behavior, or before → after).
- **Testing and Risks & rollout are situational.** Include Testing when there's something meaningful to verify, and Risks & rollout for risky or behavior-changing PRs; omit a section that would add nothing.
- **Link the issue if there is one.** When the project uses an issue tracker, add a link to the tracked issue (typically a Markdown link at the end of the body). Follow the repository's existing PR convention, and omit it if the project doesn't track issues.
