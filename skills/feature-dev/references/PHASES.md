# The phases

Each phase has a goal and an exit condition. Read the phase you are entering; don't read ahead. The budget referenced from Phase 3 onward is in [LEANNESS.md](LEANNESS.md).

## Phase 0: Isolate and baseline

**Goal:** a place to work that can be thrown away, and a suite whose result means something.

**Invoke `git-worktree` and take its pre-edit guard's ruling** — don't decide isolation by feel. The guard reads where you actually are; on the default branch in the main checkout it rules for a worktree, which is the ordinary outcome here rather than an exception earned by a long slice or a dirty tree. `git-worktree` then handles placement, branch naming, linking git-ignored local agent config, and installing the stack's dependencies.

**Building slice N of an epic is the case that catches people out.** Sitting in the previous slice's worktree, the guard does not rule "proceed" just because a worktree exists — a branch carrying finished-but-unmerged commits is the wrong place to start the next slice, and `git worktree add -b` would silently base it on that branch. Take the guard's second ruling and settle the start-point through `git-worktree`'s *Choosing the base*: merged predecessor or independent slice → a fresh worktree off the default branch; a slice that **depends** on the unmerged one → **its own new branch** stacked on the predecessor, cut here in this worktree (`git switch -c …`, or `gh stack add`). Either way you end Phase 0 on a branch that did not exist when you started. Reading "stacked, in the same worktree" as "keep committing on the predecessor's branch" is the failure this ruling exists to prevent — it puts two slices on one branch and Phase 6 can no longer commit them apart.

Then **run the test suite once, before touching anything.** Note the result:

- **Green** — you have a baseline. Every red from here on is yours.
- **Red** — say so now and settle it before Phase 4. Fix it, quarantine it, or write down exactly which failures pre-date the slice. On an unknown baseline, TDD's "watch it fail" proves nothing and Phase 5 cannot distinguish a regression from the status quo.

Run the linter and type-checker too if they're fast. Knowing the repo was already clean is what lets you claim Definition of Done honestly at Phase 5.

**On a stacked slice, the baseline is the parent branch's, not the default branch's.** You inherit whatever the layer below shipped, so measure against it — held against the default branch, the parent's own changes read as your regressions in Phase 5.

**Exit:** isolation resolved by the pre-edit guard, and a written baseline. State the branch by name and what it was cut from — if that branch already existed when Phase 0 began, and this is not a continuation of the work it already carries, Phase 0 is not done.

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

Give every explorer the same return contract, whatever angle it covers. `fan-out` requires one contract for the whole dispatch; this is what an exploration's should be:

- **Every claim anchored at `path:line`.** An unanchored report has to be re-searched before you can trust it, which costs more than the exploration saved.
- **A trace, not an inventory** — the entry point through the layers to wherever the work lands, naming the transformation at each hop rather than listing the files it passed through.
- **The 5–10 files most worth reading.**

Then **read those files yourself.** The explorers build the map; you need the detail in context to write code that matches it.

**Exit:** a short summary of the patterns that will shape the slice — where the code will live, what it should look like, what to reuse, and **what already exists.** That last part changes the slice: if the feature is half-built, or an adjacent one already covers part of it, Phase 3 needs to know before it starts asking questions. A slice shaped in ignorance of a half-finished implementation is a slice that will be re-cut in Phase 4.

## Phase 3: Shape the slice

**Goal:** turn the framed feature into one sharp slice with real acceptance criteria.

**Invoke `slice`** and let it lead the conversation. Phase 1 already established this is a single slice, so it should sharpen it into one job story — its small-feature path. Feed it what you learned in Phases 1–2 so the conversation starts warm, and let it ask its own questions rather than pre-answering them.

What you need out of this phase: a job story with a clear **"ships when"** and concrete **acceptance criteria** covering the happy path, the edge cases, and the error states. Those aren't paperwork — they become the failing tests in Phase 4. Push until each criterion is specific and verifiable ("a user can X and sees Y"); a vague criterion produces a vague test that proves nothing.

Two criteria are easy to forget here and expensive to retrofit once tests exist:

- **The rollout shape.** If the slice changes behavior an existing user already depends on, it ships behind a default-off flag, and the flag-off path must be behavior-preserving. Write that as a criterion — "with the flag off, X behaves exactly as before" — so Phase 4 tests both paths (AGENTS.md §5, *Safe rollout, feature flags & migrations*).
- **The migration shape.** A schema change is additive first: add and backfill, switch reads and writes, remove the old shape later. Say which step this slice is.

Close with a rough **size budget**: given what Phase 2 revealed, does this look buildable in under ~300 lines of production code? If it clearly can't, that is usually a signal the slice is still too big rather than that the budget is wrong — interrogate it now, while re-slicing is cheap. See [LEANNESS.md](LEANNESS.md).

**If `slice` surfaces more than one slice, don't force it back to one story.** It takes Phase 1's size call rather than re-opening it, but pushing on the acceptance criteria can still expose scope that call missed — and then it switches to its large-feature path. Let it finish the breakdown and capture the list, then carry only the first slice in its sequence into Phase 4. The rest are Phase 7's to hand back.

**If you're building from a spec, slice list, or plan still marked `draft`, flip its `metadata.status` to `accepted`.** Confirming the slice with the user is the agreement that state records; leaving it `draft` while code lands against it is the field lying.

**Exit:** one job story to build now — a "ships when", verifiable criteria including rollout and migration shape, and a size call — plus any wider breakdown captured and its other slices deferred.

## Phase 4: Build it test-first

**Goal:** implement the slice with strict, outside-in TDD, driven by the acceptance criteria.

**Invoke `tdd`** and run its process without shortcuts. Hand it the acceptance criteria as the specification: each criterion is a behavior that needs a failing test before any production code exists.

The two skills fit together: `slice` produced the observable behaviors, and TDD drives them outside-in — start with a high-level test for the "ships when" behavior, let its failure push you down through the layers, write minimal code at each. Honor the Iron Law: no production code without a failing test first. The slice is done when every criterion is covered by a test you watched fail and then pass, and the suite is green with pristine output.

Keep the implementation lean while you build, and measure the diff against the budget before moving on — both are in [LEANNESS.md](LEANNESS.md).

**In a localized app, the slice's strings ship in every locale.** User-facing text goes through the i18n layer the neighboring code uses, never as a literal. Once the slice's own tests are green, **invoke `translate-locales`** for the keys this slice added or reworded in the source locale — before the full suite, where a missing-translation spec would otherwise stay red. A key that exists only in `en` falls back, shows the raw key, or raises in every other locale, and that is a defect on a normal path, not a follow-up. Translated locale files are data and stay out of the budget ([LEANNESS.md](LEANNESS.md#the-budget)). When the repo deliberately routes translation through a TMS or a translation team instead, say so in Phase 7 rather than translating.

**Exit:** every criterion covered by a test that was red before it was green, a green suite, the slice's new strings present in every shipped locale (or handed off, with a named reason), and a diff measured against the budget.

## Phase 5: Review and fix the diff

**Goal:** catch the bugs, quality issues, and convention violations TDD won't surface; fix them; then satisfy the full Definition of Done.

TDD proves the slice does what the criteria demanded. It does not prove the code is simple, secure, or idiomatic. **Invoke `code-review` over the slice as uncommitted work.** Commits are deferred to Phase 6, so on a branch Phase 0 just cut the whole slice is in the working tree and `<base>...HEAD` is empty — an empty fixed-point diff is a stop in `code-review`, not a pass. Only when the branch already carries commits of this slice (a resumed or continued run) pass the branch point as its argument — the remote-tracking form of the ref Phase 0 cut from, or the parent branch on a stack — and tell it to pull the uncommitted work in alongside. Either way, untracked new files appear in no diff; make sure `git status --short` is part of the file set. Pass the acceptance criteria from Phase 3 as the spec.

**Loading the skill is not running it.** The Skill tool returns `code-review`'s instructions, not a review; the review is the work you do next, following them through to their Output block. Phase 5 has not reviewed anything until that block exists in the conversation: the header line naming what was read (`HEAD` plus the dirty tree) and the files covered, the Defects, Standards, and Spec sections, Coverage, and a Verdict. A `git diff` followed by moving on is the failure this paragraph exists to name.

**Run the Defects axis in a fresh agent, whatever the diff's size.** `code-review` fans out only for a large diff, but this one was written in the context now reviewing it, and that context reads its own intent into every hunk. Dispatch the `reviewer` agent this payload ships, scoped to the Defects axis, with the review scope as commands — `git status --short` and the diff — and the Phase 3 acceptance criteria; none of the reasoning that produced the code (`fan-out`'s *Hand over the evidence, never your conclusion*). Where the host has no `reviewer`, use any read-only fresh agent and paste `code-review`'s *Defects axis* section whole, so it works the same checklist rather than its own idea of one. Fold its findings into the Defects section yourself, verified like any agent's claim. Standards and Spec can stay in this context: both measure the code against documents, not against what you meant. When the slice also owes a `find-bugs` hunt (below), it is fresh-context work for the same reason — dispatch the `bug-hunter` agent over the same scope in the same response, so the two run in parallel; without one, add the hunt to the fresh agent's brief and have it report in `find-bugs`'s shape.

**`find-bugs` runs inside the review, not after it.** On your own change `code-review`'s Defects axis makes `find-bugs` the default wherever the change touches concurrency, retries, money, auth, or tenancy; this workflow adds untrusted input and file paths to that list. Run its hunt there — in the `bug-hunter` agent, or the fresh Defects agent, above — with the same scope — no argument for uncommitted work, the branch point when the review was given one — fold its findings into the Defects section and its "Could not verify" items into Coverage, and only then write the Verdict. Loading `find-bugs` does not end `code-review`'s workflow — return to it and finish the report. A slice on one of those surfaces whose report carries neither `find-bugs` findings nor its "No significant issues found." line skipped the pass.

`code-review` returns findings and a per-axis verdict; **it does not edit code.** Applying the fixes is yours, and the verdict is not the bar for them. The verdict is a merge gate: it asks whether a merge should wait, and Medium and Low Defects, judgment-call Standards findings, and nits don't hold one up. This phase asks a different question — what is worth fixing while the code is uncommitted, still in your context, and as cheap to change as it will ever be. Work every finding:

- **Blocking — fix it.** A Critical or High Defect, a firm Standards breach, a missing or wrong Spec requirement. Fix it, or state plainly why it is a false positive. A Spec finding means the code and the acceptance criteria disagree; decide which one is wrong before touching either, and changing a criterion is the user's call.
- **Medium and Low Defects — fix them.** Each is a real bug on a narrower path. That no acceptance criterion named its edge case is why the review had to find it, not a reason to leave it. Leave one only when it is a false positive or its fix reaches into code the slice merely sits beside. If the fixes push the diff past the budget, make [LEANNESS.md](LEANNESS.md#when-it-runs-over)'s three-way call; the budget is advisory, and it never outranks a known bug.
- **Everything else non-blocking — fix it when it is worth fixing, which is the default.** A judgment-call Standards finding (a divergence from a named sibling, a possible smell), a nit, scope creep nobody asked for or declined (deletion, unless the user adds it to the criteria). It is worth fixing when the fix stays inside code this slice wrote or changed and you can name what it buys: a sibling's convention matched, duplication removed, a name a reader would otherwise misread. Leave it only for a reason you can name: the fix reaches into code the slice merely sits beside; it adds a capability no criterion asked for, or pushes the diff past the budget; the sibling divergence is a deliberate improvement — say so, and why; the smell's cure would cost clarity (LEANNESS.md names that overshoot); or the finding is taste with nothing concrete behind it. "Non-blocking" describes the verdict; it is not a reason. `simplify-code` applies the readability, duplication, and convention ones against the green tests.
- **What no edit resolves — put it to the user before Phase 6.** A Long-term impact flag (a second reviewer, or an ADR), a "Missing standard" candidate, a Needs discussion verdict: each is the user's decision, not yours to absorb. Raise it, then carry it into the commit body and Phase 7's key decisions.

A finding left because its fix reaches past the slice is a follow-up: name it in Phase 7 rather than widening the diff, which is the out-of-scope churn the self-review in step 5 below removes.

Fix Defects test-first. A Defect fix changes behavior, so it starts the way Phase 4 does: a failing test that reproduces the finding — `code-review`'s probe, where it wrote one — then the fix. Then measure the diff against the budget again; a pass that fixes everything worth fixing can still grow it.

Then close out **Definition of Done** (AGENTS.md §4), because the fixes were written outside the red-green-refactor loop and are the least-tested lines in the diff:

1. Re-run the full test suite.
2. Run the project's linter, formatter, and type-checker — RuboCop, Credo, ESLint/Prettier, `tsc`, Dialyzer, whichever apply. A green suite alone is not Done.
3. **Offer a browser pass** when the slice touches a UI or user-visible behavior, and run it only if the user agrees — a round-trip through a running app is theirs to spend, so name the criteria you'd exercise and ask rather than opening a browser unasked. On a yes, drive it with whatever automation the machine has — a browser-driving CLI (such as `agent-browser`), or a browser over MCP (Chrome, Firefox, Safari) — through the happy path and the edge cases Phase 3 named, and keep a screenshot for Phase 7. On a no, or where the app can't be run here, name the criteria left resting on tests alone rather than letting a green suite imply them.
4. If a non-Defect fix turned out to change behavior — a Standards cleanup that was not a pure refactor — give it the same treatment: back it out, write the test, watch it fail, reapply.
5. Self-review the diff for debug output, secrets, and out-of-scope churn.

Summarize what changed: what the review fixed — blocking and non-blocking separately — anything it flagged and you deliberately left (with the named reason), and which checks you ran. If you could not run one here, say which and why rather than skipping it silently.

**Exit:** `code-review`'s full report on screen, with its Verdict and the tree it read; every finding — blocking or not — fixed, shown to be a false positive, or left with a named reason; every escalation put to the user; every check green and named; and — for a UI slice — the browser pass run, declined, or ruled out.

## Phase 6: Commit the slice

**Goal:** land the finished, reviewed slice as a clean commit.

**Invoke `git-commit`.** Everything in the working tree is *one coherent slice*, so expect a single atomic commit rather than a split — the logic, its schema change, the handler, the UI, and the tests all tell one story. The exception is anything genuinely independent that snuck in: an unrelated cleanup, a drive-by fix from the review. Don't pre-split it yourself; `git-commit` makes that call.

Feed it the slice's "ships when" line so the message explains *why* the slice exists rather than only what changed, and pass along any risk, deliberate trade-off, or escalation Phase 5 flagged so it lands in the body.

`git-commit` stops at creating commits. It does not push and does not open a PR.

**Exit:** the slice committed, working tree clean.

## Phase 7: Hand it back

**Goal:** close the loop and leave the user able to act.

Mark the todos complete and give a short summary:

- **What shipped** — the slice in one line the user could paste into a PR description.
- **Acceptance criteria** — confirm each is met and covered by a test.
- **Verification** — the checks you ran and their results; name anything you could not run here. For a UI slice, say where the browser pass landed: what you drove and what you saw, or that it was declined or unavailable and which criteria rest on tests alone.
- **The commit** — subject line and SHA, and the branch it's on.
- **Key decisions** — anything notable from slicing, testing, or review, including findings deliberately left and the production-line count against the ~300 budget (restate the justification if it ran over).
- **Status** — the spec, slice list, or plan this built from moves to `done` when the slice ships. This workflow stops before the merge, so flip it once the slice lands — for an epic's shared list or index spec, only when the *last* slice does — and name the pending flip here if the merge is still open. A planning artifact left at `accepted` after its work shipped is the rot `lore` guards against.
- **Next steps** — the branch is unpushed with no PR open; say so. If this was one slice of a larger epic, name the slices still waiting, and that the clean path is to merge this one before cutting the next off the default branch. Where the next slice **depends** on this unmerged one, that is a stack rather than a fresh worktree — `git-worktree`'s *Choosing the base* makes the call and `gh-stack` manages the layers. `pull-request` covers the title and description when the user is ready, and its SPLITTING.md covers the stack.
