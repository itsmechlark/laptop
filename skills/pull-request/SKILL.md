---
name: pull-request
description: Write and open a pull request — its title and description. Use when opening, drafting, or editing a PR, or composing a PR title/description. Covers the workflow (understand → title → description → self-check → open → report), voice and tone, the Conventional Commits title, the Reasoning/Summary body template, the significance filter that keeps Summary from listing every change, behavior-change tables, testing as test-code coverage rather than test runs, risks/rollout, and optional issue links.
argument-hint: "[optional note or context for the PR]"
---

# Pull requests

**Don't open or update a PR unless explicitly asked.** Drafting the title/description for review is fine; creating or editing a PR publishes to the remote, so wait for explicit instruction (as with commits and pushes).

PRs are for the **engineering team** — write in technical language: what changed and how, design decisions and trade-offs, testing performed, risks, and rollout. If the work is tracked in an issue tracker, link the issue for product context, but keep the engineering narrative in the PR.

Once you've been asked to open a PR, work through the steps below and report the result (Step 6). Any note the user passes is context to fold into the description, not the literal title.

**Convention:** if the repository has a PR template (`.github/pull_request_template.md`, `docs/PULL_REQUEST_TEMPLATE.md`, or similar) or a consistent PR-body convention in its recent merged PRs, follow that — fill its sections, complete its checklist — and use the template below only for what it leaves unspecified. A project's own convention outranks this default.

## Splitting a wide build into narrow PRs

When a feature was built wide — proven end to end on a throwaway branch — don't open one sprawling PR from that branch. Decide the set first: the smallest group of independently reviewable PRs, each safe to merge on its own. Small PRs flow; large ones sit.

- **Cut each PR fresh off the default branch, each in its own worktree** — if a `git-worktree` skill is available, follow it for creating and placing those worktrees. The scratch branch's history is throwaway, so it never becomes the PR; carry over only the slice that PR owns.
- **Stack only when a dependency is real.** A change that needs code another PR in the set introduces stacks on it; everything independent branches straight off the default branch. Stacking for convenience buys a rebase chain you'll regret once the bottom PR gets review feedback.
- **Cleanup ships last** — retiring the code a change replaces is its own final PR, opened after the new path is live, for the same reason it's a separate commit: a mixed diff makes the rollback ambiguous.
- **Show the proposed split before opening anything** — the PRs, what each carries, and which stack — so it can be corrected while it's still a plan.

Each PR in the split then goes through the workflow below.

## Step 1: Understand what's shipping

Describe the whole branch, not just the last commit. Run these together:

- `git log <base>..HEAD --oneline` — every commit the PR will contain
- `git diff <base>...HEAD` — the full diff since the branch diverged from its base (three dots)
- The base is the repository's default branch unless told otherwise.

Read the commits and diff for the *why*. A description explains a set of changes to a reviewer — you can't write it from the last commit alone. Check for a PR template while you're there, and read the linked issue if the branch or the user names one: the problem statement usually lives there, not in the code.

## Step 2: Write the title

Conventional Commits, same as a commit subject: `<type>[optional scope]: <description>`. When the project tracks work in an issue tracker, append the key in square brackets — `<type>[optional scope]: <description> [ISSUE-KEY]` (e.g. `fix(onboarding): validate overlap instead of auto-setting end date [ABC-1234]`). Aim for ≤50 and never exceed the 72-character cap, measuring the `<type>[optional scope]: <description>` portion (a trailing `[ISSUE-KEY]` is exempt) so a PR and its lead commit correlate at a glance.

## Step 3: Write the description

```markdown
## Reasoning

Why this change exists: the problem it solves, the risk/impact of the status quo, the chosen approach, and any rollout/gating considerations. Product context plus engineering rationale.

## Summary

- <Behavior change — why it matters>
- <Non-obvious decision — what it rules out>

## Testing

- <Test added or changed, and what it covers>

## Risks & rollout

Failure modes, feature-flag/gating, and migration or rollback steps.
```

**Testing and Risks & rollout are situational.** Include Testing whenever test code changed or something needed manual verification, and Risks & rollout for risky or behavior-changing PRs. Omit a section that would add nothing — an empty heading is worse than no heading.

**Link the issue if there is one.** When the project uses an issue tracker, add a link to the tracked issue the way the repo already does (typically a Markdown link at the end of the body). Omit it if the project doesn't track issues, and never invent one.

### Summary — the changes that matter, not all of them

Bullets, not prose. Each is `<what changed> — <why it matters>`, present tense: "Rejects…", "Moves…", "Drops…".

A change earns a bullet only when the diff alone would leave a reviewer guessing. Three kinds qualify:

- **Observable behavior** — what now works, fails, or responds differently for a user or a caller.
- **A contract** — API shape, serializer payload, DB schema, public interface, flag, or config that a consumer depends on.
- **A non-obvious decision** — why this approach and not the one a reviewer would expect. Name the alternative you rejected.

Everything else is carried by the diff and stays out: file-by-file narration, renames and mechanical refactors, test and fixture edits (those belong in Testing), formatting, generated files, dependency bumps made in service of the above, and process notes ("added a changeset", "addressed review feedback").

**Budget: 2–4 bullets, 7 at the absolute most.** When there are more candidates than budget, rank by blast radius — observable behavior, then contracts, then decisions — and cut from the bottom. Cut bullets don't move somewhere else; the diff already has them. If a PR can't fit under 7 bullets without hiding something a reviewer needs, that's the PR being too big rather than the budget being wrong — say so, and offer to split it.

**The Summary is not a code walkthrough.** The code is the source of truth. Don't narrate it method by method and don't list the changed files back.

Too verbose — narrating the diff:

> - Adds a `no_overlapping_periods` custom validator to `app/models/onboarding_period.rb`, invoked via `validate :no_overlapping_periods`, which loads siblings with `where(shop_id: shop_id).where.not(id: id)` and compares with `Range#overlaps?`.
> - Removes the `before_validation :set_end_date` callback that assigned `end_date = next_period.start_date - 1.day`.
> - Renames `OnboardingPeriod#range` to `#active_range` and updates the four call sites.
> - Adds model spec coverage for the validator and updates the factory to stop setting `end_date`.
> - Bumps RuboCop to 1.68 and fixes the resulting offenses.

Better:

> - Overlapping onboarding periods are now rejected with a validation error instead of being silently reconciled — the old callback rewrote `end_date` behind the user's back, which is how shops ended up with periods they never entered.
> - Overlap is checked against siblings of the same shop only, so multi-shop accounts can still hold identical date ranges.

The rename, the factory change, and the RuboCop bump don't appear. The diff carries them.

**Behavior changes go in a table.** When behavior changes across more than one condition, a table beats bullets — put it directly under them:

| Condition | Before | After |
| --- | --- | --- |
| New period overlaps an existing one | `end_date` silently rewritten | Rejected with a validation error |
| No overlap | Saved as entered | Unchanged |

**Show UI changes.** For visible UI change, attach a before/after screenshot or a short recording — one image settles what a paragraph argues about. Only include what you actually captured.

### Testing — test code, not test runs

What test code was added or changed, and what it pins down. Reviewers read this to judge coverage, not to learn that the suite is green.

Include:

- new tests or cases, and the behavior each one covers
- existing tests that changed, and why the assertion moved — an assertion changing *is* a behavior change, so justify it here
- verification CI can't reproduce, with its outcome: a UI flow exercised in the app, a migration run against a prod-like dataset, a manual repro of the original bug
- a required check you couldn't run in this environment, and why — that's the one fact about a test run worth writing down

Do not include:

- that the tests pass, or how many ran (CI reports this)
- the commands you ran
- a coverage claim you didn't verify

Running the suite, lint, and type-checks before opening is still required — see the Definition of Done in `CLAUDE.md`. This section covers what a reviewer can't get from CI, not the fact that you did your job.

### Risks & rollout

Failure modes, the flag gating the change and its default, migration and rollback steps. State cross-PR dependencies plainly here too — a PR that must land after another, or needs a config value set in production before it's enabled.

## Voice and tone

Write like an engineer briefing a teammate, not a language model.

- No hype or filler adjectives ("comprehensive", "robust", "seamless", "significantly").
- No throat-clearing ("This PR aims to", "In order to", "It's worth noting that").
- Plain, direct sentences of varied length; drop the uniformly-hedged cadence. Call out anything surprising, and flag risks and dependencies plainly.
- Write body prose as ordinary paragraphs. Don't hard-wrap lines or insert manual newlines mid-paragraph — the host soft-wraps Markdown, so hard breaks only waste width.

## Step 4: Self-check

Read your own body once before posting:

- Title is Conventional Commits, ≤50 characters (72 hard cap), with the issue key if the project uses one.
- Every Summary bullet passes the filter — behavior, contract, or non-obvious decision — and the rest are cut.
- Testing describes test code and verification CI can't show, not a green suite.
- No section reads as a task log ("then I also…", "addressed feedback").
- The repo's own template sections and checkboxes are filled.
- Nothing fabricated: no invented issue link, reviewer, label, or test you didn't write.
- The whole body reads in under a minute.

## Step 5: Open or update the PR

Only after you've been asked to. Then:

- Make sure you're on a feature branch, not the default branch, and push it (`git push -u origin <branch>`).
- Open against the repository's default branch unless told otherwise.
- Pass the body from a file to avoid shell-mangling — `gh pr create --title "…" --body-file <file> --base <base>` (or whatever host CLI the project uses). Write the file to `$TMPDIR`, not `/tmp`.
- Open as a **draft** (`--draft`) when the work isn't ready for review — CI unverified, a dependency unmerged, or the user called it a draft.

**Updating an existing PR:** `gh pr edit <number> --body-file <file>` (and `--title`), same rules and same file-based body. The description always describes the branch as it will land, not the journey it took: when review changes the work, rewrite the affected bullets in place. Never append "Update:" or "Addressed review feedback" paragraphs — a body that accumulates its own review changelog is exactly the bloat the Summary budget exists to prevent.

## Step 6: Report what you did

Share the PR URL, and if you made a judgment call worth knowing about ("opened as a draft — CI still running", "based on `develop`, not `main`", "dropped three Summary bullets the diff already covers"), say so in a sentence.

## Attribution

- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
