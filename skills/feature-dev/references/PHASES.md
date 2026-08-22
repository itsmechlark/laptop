# The phases

Each phase has a goal and an exit condition. Read the phase you are entering; don't read ahead. The budget referenced from Phase 3 onward is in [LEANNESS.md](LEANNESS.md).

## Phase 0: Isolate and baseline

**Goal:** a place to work that can be thrown away, and a suite whose result means something.

When the work should stay off the main checkout — a long slice, a dirty tree, or parallel work already in flight — use `git-worktree` to set one up before Phase 1. It handles placement, branch naming, linking git-ignored local agent config, and installing the stack's dependencies.

Then **run the test suite once, before touching anything.** Note the result:

- **Green** — you have a baseline. Every red from here on is yours.
- **Red** — say so now and settle it before Phase 4. Fix it, quarantine it, or write down exactly which failures pre-date the slice. On an unknown baseline, TDD's "watch it fail" proves nothing and Phase 5 cannot distinguish a regression from the status quo.

Run the linter and type-checker too if they're fast. Knowing the repo was already clean is what lets you claim Definition of Done honestly at Phase 5.

**Exit:** an isolated branch or checkout, and a written baseline.

## Phase 1: Frame the work

**Goal:** understand what the user wants, and confirm it is a single slice before investing.

If the request is unclear, ask what they're building — the problem it solves, who it's for, what "done" looks like. Keep it short: `slice` interrogates scope properly in Phase 3, so here you only need enough to explore the codebase intelligently.

If the shape of the thing isn't settled — the approach is open, or the design needs working out before anyone slices it — that is `brainstorming`, which is user-invoke-only: read and follow its `SKILL.md` rather than invoking it, and come back here when its architectural path hands over an approved design. If the work arrived as an issue-tracker item rather than a conversation, `triage` is the entry point (also user-invoke-only — read and follow its `SKILL.md`).

Then make an explicit call on size: **is this one slice, or an epic hiding several?** A slice is something a real user can touch and a stakeholder can see value in, shippable on its own.

- **One slice** → confirm your understanding in a sentence or two and move on.
- **An epic** → say so plainly, help name the pieces briefly, then ask which single slice to build now. If they want the whole epic broken down first, that is `slice`'s large-feature path on its own — point them there and stop.

**Exit:** one named slice, confirmed by the user.

## Phase 2: Explore the codebase

**Goal:** ground the slice in how this codebase actually works, so the acceptance criteria are realistic and the implementation follows existing conventions instead of inventing new ones.

This matters most in a mature codebase: the right slice and the right tests both depend on where similar features live, what the testing conventions are, and which abstractions already exist. Skipping it produces slices that ignore reality and code that fights the grain.

Match the effort to the feature. For a small, well-understood change, a few targeted reads inline are enough. For unfamiliar territory or work spanning layers, dispatch parallel explorers — `fan-out` covers the partitioning, the self-contained prompts, and the integration, and its rules apply here: read-only explorers can share one checkout, and nothing they report is true until you've checked it. Three angles worth one agent each:

- Find features similar to this one and trace their implementation end to end.
- Map the architecture and conventions for the area this slice touches — wherever it lands: data, domain logic, endpoints, UI, background work.
- Identify the testing patterns relevant to this work: the framework, how tests are structured across layers (end-to-end, integration, unit), and what factories, fixtures, and helpers exist.

For a single unfamiliar file, class, or flow, `explain` builds the mental model faster than an explorer does — it reads for comprehension rather than searching.

Ask each explorer for the 5–10 files most worth reading, then **read those files yourself.** The explorers build the map; you need the detail in context to write code that matches it.

**Exit:** a short summary of the patterns that will shape the slice — where the code will live, what it should look like, what to reuse, and **what already exists.** That last part changes the slice: if the feature is half-built, or an adjacent one already covers part of it, Phase 3 needs to know before it starts asking questions. A slice shaped in ignorance of a half-finished implementation is a slice that will be re-cut in Phase 4.

## Phase 3: Shape the slice

**Goal:** turn the framed feature into one sharp slice with real acceptance criteria.

**Invoke `slice`** and let it lead the conversation. Phase 1 already established this is a single slice, so it should sharpen it into one job story — its small-feature path. Feed it what you learned in Phases 1–2 so the conversation starts warm, and let it ask its own questions rather than pre-answering them.

What you need out of this phase: a job story with a clear **"ships when"** and concrete **acceptance criteria** covering the happy path, the edge cases, and the error states. Those aren't paperwork — they become the failing tests in Phase 4. Push until each criterion is specific and verifiable ("a user can X and sees Y"); a vague criterion produces a vague test that proves nothing.

Two criteria are easy to forget here and expensive to retrofit once tests exist:

- **The rollout shape.** If the slice changes behavior an existing user already depends on, it ships behind a default-off flag, and the flag-off path must be behavior-preserving. Write that as a criterion — "with the flag off, X behaves exactly as before" — so Phase 4 tests both paths (AGENTS.md §5, *Safe rollout, feature flags & migrations*).
- **The migration shape.** A schema change is additive first: add and backfill, switch reads and writes, remove the old shape later. Say which step this slice is.

Close with a rough **size budget**: given what Phase 2 revealed, does this look buildable in under ~300 lines of production code? If it clearly can't, that is usually a signal the slice is still too big rather than that the budget is wrong — interrogate it now, while re-slicing is cheap. See [LEANNESS.md](LEANNESS.md).

**Exit:** one job story, a "ships when", verifiable criteria including rollout and migration shape, and a size call.

## Phase 4: Build it test-first

**Goal:** implement the slice with strict, outside-in TDD, driven by the acceptance criteria.

**Invoke `tdd`** and run its process without shortcuts. Hand it the acceptance criteria as the specification: each criterion is a behavior that needs a failing test before any production code exists.

The two skills fit together: `slice` produced the observable behaviors, and TDD drives them outside-in — start with a high-level test for the "ships when" behavior, let its failure push you down through the layers, write minimal code at each. Honor the Iron Law: no production code without a failing test first. The slice is done when every criterion is covered by a test you watched fail and then pass, and the suite is green with pristine output.

Keep the implementation lean while you build, and measure the diff against the budget before moving on — both are in [LEANNESS.md](LEANNESS.md).

**Exit:** every criterion covered by a test that was red before it was green, a green suite, and a diff measured against the budget.

## Phase 5: Review and fix the diff

**Goal:** catch the bugs, quality issues, and convention violations TDD won't surface; fix them; then satisfy the full Definition of Done.

TDD proves the slice does what the criteria demanded. It does not prove the code is simple, secure, or idiomatic. **Invoke `code-review`** over the slice's diff, scoped to the branch point — `git diff <base>...HEAD`, three dots, so the comparison is against the merge-base.

`code-review` returns findings and a per-axis verdict; **it does not edit code.** Applying the fixes is yours. Work its findings by axis:

- **Defects** are blocking. Fix them, or state plainly why a finding is a false positive.
- **Standards** findings are firm where the repo documents the convention and a judgement call where it doesn't.
- **Spec** findings mean the code and the acceptance criteria disagree — decide which one is wrong before touching either.

For a security-bearing slice — anything touching authentication, authorization, payments, untrusted input, or file paths — follow the review with `find-bugs`. It maps the attack surface and proves each finding reachable rather than returning a verdict, which is the pass a merge-focused review isn't trying to be.

Then close out **Definition of Done** (AGENTS.md §4), because the fixes were written outside the red-green-refactor loop and are the least-tested lines in the diff:

1. Re-run the full test suite.
2. Run the project's linter, formatter, and type-checker — RuboCop, Credo, ESLint/Prettier, `tsc`, Dialyzer, whichever apply. A green suite alone is not Done.
3. If a fix changed behavior no test covers, add that test — failing first, per Phase 4.
4. Self-review the diff for debug output, secrets, and out-of-scope churn.

Summarize what changed: what the review fixed, anything it flagged and you deliberately left (with the reason), and which checks you ran. If you could not run one here, say which and why rather than skipping it silently.

**Exit:** review findings resolved or explicitly deferred, and every check green and named.

## Phase 6: Commit the slice

**Goal:** land the finished, reviewed slice as a clean commit.

**Invoke `git-commit`.** Everything in the working tree is *one coherent slice*, so expect a single atomic commit rather than a split — the logic, its schema change, the handler, the UI, and the tests all tell one story. The exception is anything genuinely independent that snuck in: an unrelated cleanup, a drive-by fix from the review. Don't pre-split it yourself; `git-commit` makes that call.

Feed it the slice's "ships when" line so the message explains *why* the slice exists rather than only what changed, and pass along any risk or deliberate trade-off Phase 5 flagged so it lands in the body.

`git-commit` stops at creating commits. It does not push and does not open a PR.

**Exit:** the slice committed, working tree clean.

## Phase 7: Hand it back

**Goal:** close the loop and leave the user able to act.

Mark the todos complete and give a short summary:

- **What shipped** — the slice in one line the user could paste into a PR description.
- **Acceptance criteria** — confirm each is met and covered by a test.
- **Verification** — the checks you ran and their results; name anything you could not run here.
- **The commit** — subject line and SHA, and the branch it's on.
- **Key decisions** — anything notable from slicing, testing, or review, including findings deliberately left and the production-line count against the ~300 budget (restate the justification if it ran over).
- **Next steps** — the branch is unpushed with no PR open; say so. If this was one slice of a larger epic, name the slices still waiting. `pull-request` covers the title and description when the user is ready.
