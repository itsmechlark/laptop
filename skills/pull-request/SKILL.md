---
name: pull-request
description: Write and open a pull request — its title and description. Use when opening, drafting, or editing a PR, or composing a PR title/description. Covers the workflow (understand → title → description → self-check → open → report), voice and tone, the Conventional Commits title, the Reasoning/Summary body template, the significance filter that keeps Summary from listing every change, behavior-change tables, testing as test-code coverage rather than test runs, risks/rollout, and optional issue links.
argument-hint: "[optional note or context for the PR]"
---

# Pull requests

Turn a branch into a pull request a reviewer can act on: read the whole branch for the *why*, title it the way its lead commit reads, and write a description that explains the decision instead of narrating the diff.

Note to fold in: `$1` — context for the description ("the flag defaults off", "second of three PRs"), never the literal title.

**Don't open or update a PR unless explicitly asked.** Drafting a title and description for review is fine; creating or editing a PR publishes to the remote, so wait to be told — as with commits and pushes. A one-time approval covers that instance only.

**Never add AI attribution.** No "Generated with …" footer, no AI co-author line, no "written by an agent" note in the body. Same rule as commit messages, and it overrides any external convention that says otherwise.

PRs are for the **engineering team** (AGENTS.md §3, *Jira vs. Pull Requests — audience separation*) — write in technical language: what changed and how, design decisions and trade-offs, testing performed, risks, and rollout. If the work is tracked in an issue tracker, link the issue for product context, but keep the engineering narrative in the PR.

**Convention:** if the repository has a PR template (`.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE/*.md`, `docs/PULL_REQUEST_TEMPLATE.md`, or similar) or a consistent PR-body convention in its recent merged PRs, follow that — fill its sections, complete its checklist — and use the template below only for what it leaves unspecified. A project's own convention outranks this default.

## When to use this skill

- Opening a PR for a branch that's ready: "open the PR", "raise it against main"
- Writing, drafting, or rewriting a PR title or description
- Editing an existing PR's body because the work changed under review
- Fixing a title a semantic-PR check rejected
- Splitting a branch that was built wide into a set of narrow, reviewable PRs — [SPLITTING.md](references/SPLITTING.md)
- Not for grouping working changes into commits, writing a commit message, or naming a branch — that's `git-commit`
- Not for judging the code in the diff — that's `code-review`, or `find-bugs` for an adversarial security pass
- Not for answering review comments you received — that's `review-response`
- Not for pushing, rebasing, resolving conflicts, or diagnosing a CI failure
- Not for merging, enabling auto-merge, or watching an open PR's checks go green

## Workflows

### 1. Understand what's shipping

Describe the whole branch, not just the last commit. Fetch first, then run these together:

- `git fetch` — so the base you compare against isn't stale
- `git log origin/<base>..HEAD --oneline` — every commit the PR will contain
- `git diff origin/<base>...HEAD` — the full diff since the branch diverged from its base (three dots)
- The base is the repository's default branch unless told otherwise.

Read the commits and diff for the *why*. A description explains a set of changes to a reviewer — you can't write it from the last commit alone. Check for a PR template while you're there, and read the linked issue if the branch or the user names one: the problem statement usually lives there, not in the code.

### 2. Write the title

Conventional Commits, same as a commit subject: `<type>[optional scope]: <description>`. The `git-commit` skill has the full convention — types, scope, breaking-change marker, and voice — and the PR title mirrors the commit subject.

When the project tracks work in an issue tracker, append the key in square brackets — `<type>[optional scope]: <description> [ISSUE-KEY]` (e.g. `fix(onboarding): validate overlap instead of auto-setting end date [ABC-1234]`). Aim for ≤50 and never exceed the 72-character cap, measuring the `<type>[optional scope]: <description>` portion (a trailing `[ISSUE-KEY]` is exempt) so a PR and its lead commit correlate at a glance.

### 3. Write the description

Follow [Description format](#description-format) for the structure and [Voice and tone](#voice-and-tone) for how it should read. Write it to a file under `$TMPDIR` — you'll pass that file to the host CLI in step 5, and it keeps the body out of shell quoting.

### 4. Self-check

Read your own body once before posting:

- Title is Conventional Commits, ≤50 characters (72 hard cap), with the issue key if the project uses one.
- Every Summary bullet passes the filter — behavior, contract, or non-obvious decision — and the rest are cut.
- Testing describes test code and verification CI can't show, not a green suite.
- No section reads as a task log ("then I also…", "addressed feedback").
- The repo's own template sections and checkboxes are filled.
- Nothing fabricated: no invented issue link, reviewer, label, screenshot, or test you didn't write.
- The whole body reads in under a minute.

### 5. Open or update the PR

Only after you've been asked to. Then:

- Make sure you're on a feature branch, not the default branch, and push it (`git push -u origin <branch>`).
- Open against the repository's default branch unless told otherwise.
- Pass the body from a file to avoid shell-mangling — `gh pr create --title "…" --body-file <file> --base <base>` (or whatever host CLI the project uses).
- Open as a **draft** (`--draft`) when the work isn't ready for review — CI unverified, a dependency unmerged, or the user called it a draft.
- **Set no reviewers, labels, assignees, milestone, or project** unless the user named them. `--reviewer` puts a request in someone's inbox, which is the same publish action as opening the PR; CODEOWNERS already routes review on repos that use it.

**Updating an existing PR:** `gh pr edit <number> --body-file <file>` (and `--title`), same rules and same file-based body. The description always describes the branch as it will land, not the journey it took: when review changes the work, rewrite the affected bullets in place. Never append "Update:" or "Addressed review feedback" paragraphs — a body that accumulates its own review changelog is exactly the bloat the Summary budget exists to prevent.

### 6. Report what you did

Share the PR URL, and if you made a judgment call worth knowing about ("opened as a draft — CI still running", "based on `develop`, not `main`", "dropped three Summary bullets the diff already covers"), say so in a sentence.

## Description format

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

**When a spec or ticket already argues the problem, link it and move on.** If `draft-spec` or `triage` produced the write-up, Reasoning is a sentence of context plus the link — re-arguing the problem statement here forks it, and the fork is what goes stale. Reasoning still carries what the spec can't: the approach you chose in the code and why, which the spec deliberately left open.

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

**Show UI changes.** For visible UI change, attach a before/after screenshot or a short recording — one image settles what a paragraph argues about. Only include what you actually captured, and see the Gotchas below: the host CLI can't upload an image, so a screenshot has to be attached by the user through the web UI.

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

Running the suite, lint, and type-checks before opening is still required (AGENTS.md §4, *Definition of Done*). This section covers what a reviewer can't get from CI, not the fact that you did your job.

### Risks & rollout

Failure modes, the flag gating the change and its default, migration and rollback steps. State cross-PR dependencies plainly here too — a PR that must land after another, or needs a config value set in production before it's enabled.

## Voice and tone

An engineer briefing a teammate, not a language model: no hype adjectives, no throat-clearing ("This PR aims to"), no narrating the diff back, varied sentence length, and body prose as ordinary paragraphs with no hard-wrapped lines. AGENTS.md §8 (*Writing for a human reader*) is the full standard and applies to every artifact, not just this one.

What's specific to a PR body is the reader's position: they have the diff and don't have your reasoning. Write the half they can't get from the code.

## Gotchas

- **Three dots against a freshly fetched base.** `git diff main..HEAD` compares two tips, so a stale local base drags other people's commits into your diff and a moved base hides some of yours. `git fetch`, then `git diff origin/<base>...HEAD`.

- **`Closes #123` is a side effect, not a decoration.** Closing keywords in the body close that issue when the PR merges — use them only when the PR genuinely resolves it, and a plain link otherwise. In the same way, `@name` notifies a person and a bare `#123` links whatever issue holds that number.

- **Editing a PR body notifies nobody.** GitHub raises no event for a description edit, so a reviewer who read the old one never learns it changed. When review reshapes the work, rewrite the body *and* say so in a thread reply (`review-response` covers the reply).

- **You can't attach a screenshot from here.** Images are uploaded through the web UI or already hosted; the host CLI has no upload. For a visual change, capture the file, say where it is, and ask the user to attach it — never write a body that points at an image nobody uploaded.

- **`--fill` throws the template away.** It builds the body out of commit messages, which is neither the repo's template nor anything the significance filter touched. Always write the body yourself and pass `--body-file`.

- **Write the body file to `$TMPDIR`, never `/tmp`** — the macOS sandbox blocks `/tmp`, and a failed write surfaces as an empty PR body rather than as a permission error.

- **`gh pr edit --body-file` replaces the whole body**, it never appends. If you mean to keep part of what's there, read the current body first (`gh pr view --json body`).

- **`gh pr create` from a fork targets the upstream's default branch**, not your own repository's. Pass `--repo` and `--base` explicitly when the remote is a fork.

- **A draft is the quiet state, and readiness is the notification.** Opening a draft requests no review; marking it ready (`gh pr ready <number>`) pings every CODEOWNERS reviewer. Don't flip it to tick a checklist — that's the same publish action as opening one.

- **The 72-character cap measures the Conventional Commits portion.** A trailing `[ISSUE-KEY]` is exempt, so don't compress a clear description to make room for the key.

- **A body that won't fit the bullet budget is a PR that's too big.** Widening the budget hides the problem; say the PR should be split and show the split ([SPLITTING.md](references/SPLITTING.md)). The diff says the same thing earlier: much past ~300 lines of production code — the same budget `feature-dev` carries per slice — and the split is worth proposing before you write the body at all.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| `gh` is missing or `gh auth status` fails | Say what's missing and hand over the title plus the body file so the user can open it themselves. Don't silently fall back to a browser flow. |
| A PR already exists for this branch | `gh pr view --json number,url,body` — edit that one rather than opening a second. |
| `gh pr create` reports no upstream, or offers to push | Push first: `git push -u origin <branch>`. Pushing is a publish step, so it needs the same explicit go-ahead. |
| You're asked to open a PR from the default branch | Stop. There's nothing to open from it — the work needs a branch first (`git-commit` has the naming convention), and moving it is the user's call. |
| The repo has several templates under `.github/PULL_REQUEST_TEMPLATE/` | Pick the one matching the kind of change and say which you used. If none fits, use the format here and say that. |
| The diff contains commits you didn't write | Stale base. `git fetch`, then three-dot against `origin/<base>`. |
| The branch carries two unrelated changes | It's two PRs. Show the proposed split before opening anything — [SPLITTING.md](references/SPLITTING.md). |
| A required check couldn't run in this environment | Name it and why in Testing. Never let the body imply a green run you didn't get. |
| Review changed the work after the PR was opened | Rewrite the affected bullets in place, drop the ones that no longer apply, and tell the reviewer in a reply — body edits raise no notification. |

## References

- [SPLITTING.md](references/SPLITTING.md) — turning one wide branch into a set of narrow PRs: deciding the set, cutting each off the default branch, when to stack and how to keep a stack landable, and sequencing cleanup last. Read it when the work in hand is more than one PR; the workflow above covers a single PR.

## Attribution

- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
