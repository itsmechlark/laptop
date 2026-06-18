---
name: pull-request
description: How to write a pull request title and description for TableCheck repos. Use when opening, drafting, or editing a GitHub pull request, writing a PR description, or composing a PR title. Covers the Reasoning/Summary template, behavior-change tables, the title format with appended Jira key, title length, and the Jira markdown link.
---

# Pull request title & description

PRs are for the **engineering team** — write in technical language: what changed and how, design decisions and trade-offs, testing performed, risks, and migration/rollout notes. Link the Jira ticket for product context, but keep the engineering narrative in the PR. (The Jira-vs-PR audience principle lives in CLAUDE.md §3.)

Model PR descriptions on Monolith [PR #7334](https://github.com/tablecheck/monolith/pull/7334).

## Title

The PR title follows the same Conventional Commits format as commits, with the **Jira ticket key appended in square brackets at the end** — `<type>(scope): <description> [TICKET-KEY]` (e.g. `fix(auto-allocation): validate overlap instead of auto-setting end_date [HDR-1097]`). If no ticket key is known, ask the user for it rather than omitting it. The title is bound by the same length limit as a commit subject — aim for ≤50 and never exceed the 72-character hard cap, measuring the `<type>(scope): <description>` portion (the trailing `[TICKET-KEY]` is exempt) so a PR and its commit stay easy to correlate at a glance.

## Body

```markdown
## Reasoning

Why this change exists: the problem it solves, the risk/impact of the
status quo, the chosen approach, and any rollout/gating considerations.
Product context plus engineering rationale.

## Summary

A product-like summary of what changed, with an engineering-level
overview of the approach.

More details [HDR-1089](https://tablecheck.atlassian.net/browse/HDR-1089)
```

Rules:
- **Summary is not a code walkthrough.** The code is the source of truth — do not narrate it line by line or method by method. Describe *what* changed and *why* at a level above the diff: product-facing outcome plus a concise engineering summary of the approach.
- **Behavior changes go in a table.** If the PR changes runtime/product behavior, include a Markdown table summarizing the behavior (e.g. input/condition → resulting behavior, or before → after).
- **Ticket link is a Markdown link** here (unlike commits, which use a plain URL): `[HDR-1089](https://tablecheck.atlassian.net/browse/HDR-1089)`. If no ticket key is known, ask the user for it.
