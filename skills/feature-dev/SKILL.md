---
name: feature-dev
description: Take one feature slice from idea to reviewed, committed code in a single guided pass — scope it to the smallest shippable slice, build it test-first, review and fix the diff, then land it as one atomic commit. Use when asked to build, implement, or ship a feature end to end with the full discipline chain rather than by hand. Agnostic to language, framework, and repo. Not for reviewing a change that already exists, dependency upgrades, or open-ended design questions where the approach is still unsettled.
argument-hint: "[feature or slice to build]"
disable-model-invocation: true
---

# Feature development

Take one feature slice from a rough idea to reviewed, committed code, threading four disciplines in sequence: slicing defines the work, TDD builds it, review hardens it, a clean commit lands it.

Feature to build: `$ARGUMENTS`. If nothing came with the invocation, ask what they're building — the problem it solves, who it's for, what "done" looks like — before starting Phase 0.

**The sequence is the value.** Each phase earns the next: don't slice until you understand the feature, don't build until the slice is sharp, don't call it done until the diff is reviewed and the project's checks pass, don't commit until it's green. Watering a phase down to reach the code sooner is the exact failure this workflow exists to prevent.

**One slice per pass.** This refines and builds exactly one slice. An epic — several independently shippable pieces — gets named in Phase 1 and narrowed to the single slice to build now.

## When to use this skill

- Building a feature end to end: define it, implement it test-first, review it, commit it
- A slice already scoped but not started, that should be built with the full discipline chain rather than freehand
- A design that has been agreed and now needs building
- Not for reviewing a change that already exists — a PR, someone else's diff, a branch you didn't write — that's `code-review`
- Not for deciding *what* to build while the approach is still open — that's `brainstorming`, whose architectural path hands the approved design back here
- Not for breaking a whole epic down — that's `slice` on its own; come back with one slice
- Not for writing a plan someone *else* executes — that's `draft-plan`. This skill builds the slice itself, in this session, which is exactly the case where a plan document is ceremony
- Not for work already filed on an issue tracker — `triage` is the entry point for those
- Not for dependency upgrades, mechanical refactors, or a one-line fix: eight phases cost more than the work

`brainstorming` and `triage` are both user-invoke-only, so the Skill tool refuses them — route to either by reading and following the target's `SKILL.md`.

## Workflows

### The run

Track the phases with `TaskCreate` and `TaskUpdate`, so the user can see where they are and an interrupted run is resumable. Read each phase's detail when you reach it, not all upfront.

- [ ] **0. Isolate and baseline** — run `git-worktree`'s pre-edit guard, and a known-green suite to measure against — [PHASES.md](references/PHASES.md#phase-0-isolate-and-baseline)
- [ ] **1. Frame the work** — understand the feature, and rule on one slice vs. an epic — [PHASES.md](references/PHASES.md#phase-1-frame-the-work)
- [ ] **2. Explore the codebase** — where this lands, what to reuse, how this repo tests — [PHASES.md](references/PHASES.md#phase-2-explore-the-codebase)
- [ ] **3. Shape the slice** — one job story with a "ships when" and verifiable acceptance criteria — [PHASES.md](references/PHASES.md#phase-3-shape-the-slice)
- [ ] **4. Build it test-first** — strict red-green-refactor, driven by those criteria — [PHASES.md](references/PHASES.md#phase-4-build-it-test-first)
- [ ] **5. Review and fix the diff** — findings, then the fixes, then the full Definition of Done — [PHASES.md](references/PHASES.md#phase-5-review-and-fix-the-diff)
- [ ] **6. Commit the slice** — one atomic commit whose message carries the "ships when" — [PHASES.md](references/PHASES.md#phase-6-commit-the-slice)
- [ ] **7. Hand it back** — what shipped, what's covered, what's still waiting — [PHASES.md](references/PHASES.md#phase-7-hand-it-back)

Phases 3, 4, 5, and 6 each run a co-shipped skill — `slice`, `tdd`, `code-review`, `git-commit` — through the Skill tool. Run them in sequence and keep the handoffs clean; each is rigorous on its own and your job is not to water it down. If one can't be invoked, follow its `SKILL.md` rather than skipping the phase.

### Keeping the diff lean

A small slice does not guarantee a small diff. Slicing controls *what* ships; nothing in it stops the implementation bloating with speculative abstractions, options nothing uses yet, or defensive branches no test demanded. Carry a **production-code budget of ~300 lines** from Phase 3 onward as a design constraint, and measure against it before review: [LEANNESS.md](references/LEANNESS.md).

## Gotchas

- **A green suite is not Done.** TDD proves the criteria are met; it says nothing about lint, format, or type-checks. Run all of them before the commit and report what you ran (AGENTS.md §4, *Definition of Done*) — "tests pass" claimed as done, with RuboCop or `tsc` unrun, is the most common way this workflow ships a red branch.

- **A new feature that changes existing behavior ships default-off.** Gate it behind a flag and keep the flag-off path behavior-preserving; keep any migration backward-compatible, expanding before it contracts (AGENTS.md §5, *Safe rollout, feature flags & migrations*). This is a Phase 3 acceptance criterion, not a Phase 6 afterthought — retrofitting a flag after the tests are written rewrites both.

- **Never commit before the review's fixes are green.** Phase 5 edits code outside the red-green-refactor loop, so its fixes are the least-tested lines in the diff. Re-run everything after them, and if a fix changed behavior no test covers, add that test — failing first.

- **The budget is a design constraint, not a gate you discover at the end.** Noticing a 900-line diff at the Phase 4 checkpoint means the last two hours went into code you're now deleting. Carry it from Phase 3.

- **Establish the baseline before writing anything.** Phase 5 cannot tell a regression from the status quo on a suite that was already red, and neither can Phase 4 — `tdd` records why under *Establish a green baseline before the first red*.

- **Don't pre-answer `slice`'s questions.** It is Socratic by design: it leads the user to define the work. Arriving from Phase 2 makes this harder rather than easier — you now know things the user hasn't been told, and the pull is to skip the questions and present a finished slice. Use what you learned to make the questions *specific*, not to answer them; unexamined acceptance criteria become tests that assert your assumptions instead of the user's needs.

- **A subagent's map is not a substitute for reading the files.** Explorers return the 5–10 files worth reading; the detail has to land in *your* context before you can follow the conventions they found.

- **Don't skip Phase 2 because the change looks small.** In a mature codebase the right slice and the right tests both depend on where similar features live. Skipping it produces code that fights the grain and passes anyway.

- **One slice per pass, even when the next one is obvious.** Building two defeats the point: the diff stops being reviewable, and the commit stops telling one story.

- **This workflow stops at the commit.** It does not push and does not open a PR. Leave the branch ready and let the user decide — `pull-request` covers the title and description when they do.

## Troubleshooting

| Problem | Resolution |
| --- | --- |
| The suite is red before you start | Fix or quarantine the failure first, or state explicitly which failures pre-date the slice. Never build on an unknown baseline. |
| `slice` surfaces more than one slice in Phase 3 | Expected — interrogating the criteria exposed scope Phase 1's size call missed. Let it finish the breakdown, capture the list, build the first slice in its sequence, and defer the rest to Phase 7. Don't force it back to one story. |
| The slice keeps growing during Phase 4 | It was an epic. Stop, return to the Phase 1/3 decision, ship the smaller piece, and defer the rest — see [LEANNESS.md](references/LEANNESS.md). |
| No seam exists to write the first failing test against | The design, not the test, is the problem. `codebase-design` locates the seam; take the refactor as its own commit before resuming Phase 4. |
| The review finds a defect that invalidates an acceptance criterion | The slice was wrong, not just the code. Go back to Phase 3, re-sharpen the criterion, and drive the correction test-first. |
| Unrelated changes are in the working tree at Phase 6 | Don't pre-split them yourself. Hand `git-commit` the full tree and the "ships when"; it makes the atomic-commit call. |
| The run was interrupted | Resume from the phase checklist, re-reading only that phase's section. Re-establish the baseline first if the tree changed hands. |

## References

Read each when you reach it, not all upfront.

- [PHASES.md](references/PHASES.md) — every phase in full: its goal, the skill it hands off to, and the exit condition the next phase depends on
- [LEANNESS.md](references/LEANNESS.md) — the ~300-line production budget, how to measure the diff against it, the lean-implementation rules, and the three-way call when it runs over

## Attribution

- [thoughtbot/rails-consultant](https://github.com/thoughtbot/rails-consultant/tree/main/skills/feature-dev) - feature-dev, MIT
