---
name: pull-request
description: Write and open a pull request — its title and description. Use when opening, drafting, or editing a PR, or composing a PR title/description. Covers the workflow (understand → title → description → open → report), voice and tone, the Conventional Commits title, the Reasoning/Summary body template, behavior-change tables, testing/risks, and optional issue links.
argument-hint: "[optional note or context for the PR]"
---

# Pull requests

**Don't open or update a PR unless explicitly asked.** Drafting the title/description for review is fine; creating or editing a PR publishes to the remote, so wait for explicit instruction (as with commits and pushes).

PRs are for the **engineering team** — write in technical language: what changed and how, design decisions and trade-offs, testing performed, risks, and rollout. If the work is tracked in an issue tracker, link the issue for product context, but keep the engineering narrative in the PR.

Once you've been asked to open a PR, work through the steps below and report the result (Step 5). Any note the user passes is context to fold into the description, not the literal title.

## Step 1: Understand what's shipping

Describe the whole branch, not just the last commit. Run these together:

- `git log <base>..HEAD --oneline` — every commit the PR will contain
- `git diff <base>...HEAD` — the full diff since the branch diverged from its base (three dots)
- The base is the repository's default branch unless told otherwise.

Read the commits and diff for the *why*. A description explains a set of changes to a reviewer — you can't write it from the last commit alone.

## Step 2: Write the title

Conventional Commits, same as a commit subject: `<type>[optional scope]: <description>`. When the project tracks work in an issue tracker, append the key in square brackets — `<type>[optional scope]: <description> [ISSUE-KEY]` (e.g. `fix(onboarding): validate overlap instead of auto-setting end date [ABC-1234]`). Aim for ≤50 and never exceed the 72-character cap, measuring the `<type>[optional scope]: <description>` portion (a trailing `[ISSUE-KEY]` is exempt) so a PR and its lead commit correlate at a glance.

## Step 3: Write the description

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

- **Behavior changes go in a table.** If the PR changes runtime/product behavior, include a Markdown table summarizing it (e.g. input/condition → resulting behavior, or before → after).
- **Testing and Risks & rollout are situational.** Include Testing when there's something meaningful to verify, and Risks & rollout for risky or behavior-changing PRs; omit a section that would add nothing.
- **Link the issue if there is one.** When the project uses an issue tracker, add a link to the tracked issue (typically a Markdown link at the end of the body). Follow the repository's existing PR convention, and omit it if the project doesn't track issues.

## Voice and tone

Write like an engineer briefing a teammate, not a language model.

- **The Summary is not a code walkthrough.** The code is the source of truth — don't narrate it line by line or method by method, and don't list the changed files back. Describe *what* changed and *why* above the level of the diff: the user-facing outcome plus a concise account of the approach.
- No hype or filler adjectives ("comprehensive", "robust", "seamless", "significantly").
- No throat-clearing ("This PR aims to", "In order to", "It's worth noting that").
- Plain, direct sentences of varied length; drop the uniformly-hedged cadence. Call out anything surprising, and flag risks and dependencies plainly.

## Step 4: Open the PR

Only after you've been asked to. Then:

- Make sure you're on a feature branch, not the default branch, and push it (`git push -u origin <branch>`).
- Open against the repository's default branch unless told otherwise.
- Pass the body from a file to avoid shell-mangling — e.g. `gh pr create --title "…" --body-file <file> --base <base>` (use whatever host CLI/UI the project uses). Open as a **draft** (`--draft`) when the work isn't ready for review.
- Don't fabricate a linked issue, reviewers, or labels.

## Step 5: Report what you did

Share the PR URL, and if you made a judgment call worth knowing about ("opened as a draft — CI still running", "based on `develop`, not `main`"), say so in a sentence.
