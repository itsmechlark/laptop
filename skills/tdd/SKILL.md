---
name: tdd
description: Implement a feature, fix a bug, or change behavior test-first under strict red-green-refactor — a failing test before any production code, driven outside-in through the layers. Use for "test-first", "write a failing test first", "red-green-refactor", "drive this outside-in", "TDD this", "fix the bug with a failing spec first", or working acceptance criteria one test at a time. Agnostic to language, framework, and test runner. Not for backfilling tests onto code whose behavior is not changing, debugging a flaky or slow suite, migrating between test frameworks, or judging a change whose tests already pass.
argument-hint: "[feature, bug, or behavior to implement]"
---

# Test-driven development

Build a feature or fix a bug by writing a failing test first and then the minimum code that makes it pass, so every line of production code exists because a test demanded it.

Behavior to drive out: `$ARGUMENTS`. If nothing came with the invocation, ask what should change before touching anything — TDD on a guess produces a test that pins the wrong behavior.

**Core principle:** if you didn't watch the test fail, you don't know it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.** Every shortcut in [Gotchas](#gotchas) rationalizes itself the same way, and every one ends with a test you never saw catch anything.

## When to use this skill

- Implementing a new feature or behavior you intend to keep
- Fixing a bug — a test that reproduces it first, then the fix
- Changing existing behavior where a silent regression would be costly
- Working acceptance criteria from a slice, a spec, or a ticket, one test at a time
- Any language, framework, or test runner: the workflow is agnostic to all three
- Not for a throwaway spike you will delete, or a change with no behavior to pin down — a copy tweak, a bumped config value
- Not for backfilling tests onto code whose behavior isn't changing: that's coverage work, and it has no red to watch
- Not for debugging a flaky or slow suite, or migrating between test frameworks
- Not for judging a change whose tests already pass — that's `code-review`, or `find-bugs` for an adversarial security pass
- Not for deciding what to build or how to shape the interface — `slice` cuts the work, `codebase-design` places the seam, and both hand the result here

Once you're keeping the code, it comes in test-first. That is what AGENTS.md §1, *Engineering mindset (plan & code like a staff engineer)*, requires — this skill is how that requirement gets executed, not an optional house style.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it. Start over. No exceptions — don't keep it as "reference", don't "adapt" it while writing tests, don't even look at it. Delete means delete. Implement fresh from the tests.

**The law governs code you write, not code you found.** Pre-existing untested production code is not yours to delete. Pin the behavior you're about to change with a characterization test first, then drive the change through the cycle below — the characterization test passes on its first run by design, and it is not your red. Your red is still the test for the new behavior. [WALKTHROUGH.md](references/WALKTHROUGH.md) traces that case.

## Workflows

### 1. Establish the baseline

Two things before the first test. Both are cheap, and skipping either quietly disables the cycle that follows.

**Run the full suite once.** On an already-failing suite you cannot tell your red from the pre-existing one, so "watch it fail" degrades into "watch something fail" — and the run that should have caught your mistake reads as noise you learn to skip past. If the suite starts red, fix the failure, quarantine it, or write down exactly which failures pre-date your work.

**Learn how to run a single test.** Step 3 runs one test after every change, so the single-test invocation — not the suite command — is the one that matters. Read the project's test config and CI workflow rather than guessing: a wrong guess runs the whole suite every time, the loop gets slow, and you stop running it. Per-ecosystem commands, plus which `rules/` file carries that stack's conventions: [RUNNERS.md](references/RUNNERS.md).

### 2. Write the outermost failing test

Start high: one test describing the behavior from the user's perspective — a slice's "ships when", or the reproduction of the bug. One behavior, a clear name, exercised through the public interface.

This is the top of a **stack of failing tests**. The test you're currently reading a failure from is the *active* test; everything below happens to whichever test that is.

### 3. Run the cycle on the active test

| Phase | What you do | The test must |
| --- | --- | --- |
| **RED** | Write one minimal test for one behavior, through the public interface | — |
| **Verify RED** | Run it | Fail *because the behavior is missing* — see below |
| **GREEN** | Write the simplest code that satisfies it | — |
| **Verify GREEN** | Run it, then the affected neighbors | Pass, with pristine output — no errors, no warnings |
| **REFACTOR** | Remove duplication, improve names, extract helpers | Stay green; no behavior added |

**Verify RED is mandatory and never skipped.** What makes a red honest is its *cause*, not its shape. The run must fail because of the behavior you're driving out, and that arrives two ways — both legitimate:

- **An assertion failure** — the code ran and gave the wrong answer.
- **A "not there yet" exception** — the method, route, class, or module you are about to build does not exist. Driving outside-in, this is the ordinary red at every structural layer, and in a compiled language it is the *only* red available until the signature exists.

**Not a red:** an exception from anything else — a typo, a missing import, a bad fixture, a wrong path, a compile error in code you already wrote. The test is broken, not the behavior missing; fix the test and run again. The question that settles it: **does the message name the thing you're about to build?** [RUNNERS.md](references/RUNNERS.md) shows all three shapes per runner.

Passing already? Then it's testing behavior that exists. Sharpen it until it fails, or admit you're writing coverage rather than driving behavior — the one deliberate exception is a characterization test, which is *meant* to pass ([The Iron Law](#the-iron-law)).

**When a test fails, fix the code — not the test.** Loosening an assertion to reach green destroys the only thing that made the test worth writing. A test changes when the behavior it specifies has deliberately changed, and then you say so out loud.

**Take the smallest step that could work.** Write the obvious implementation when you can see it; the moment you notice you're guessing, fake it — return the constant the test wants, then write the second test the constant can't survive. **Two failed attempts at green means the step was too big**: go back to the last green and take a smaller one rather than pushing through. Step sizing, the reds and greens worth keeping, what refactoring is allowed to mean, and how to keep a green you can return to: [CYCLE.md](references/CYCLE.md).

**One change, one run.** After every change — writing the test, adding a route, creating a file, implementing a function — run the affected test immediately. The failure message is the instruction for what to do next. Two changes before a run and you no longer know which one the test is reacting to.

**Async work breaks this loop quietly.** A test that finishes before the work it started neither passed nor failed, and it will sit green over a deleted implementation. Wait for the work rather than the clock, and for a race, test the guard rather than the interleaving: [ASYNC.md](references/ASYNC.md).

### 4. Drop down, or pop up

A failure rarely means "write this exact line". It usually means the layer below isn't there yet.

- **The failure names a lower layer with behavior of its own** → write a failing test at that layer. It becomes the active test; go back to step 3.
- **The active test goes green** → pop it. Rerun the test one layer up. Its next failure drives the next move.

The ladder, top to bottom — use your stack's names for these:

| When the failure points to… | Write this failing test |
| --- | --- |
| End-to-end behavior from the user's perspective | End-to-end / system test |
| A handler or endpoint's response, status, or routing | Integration test |
| Logic in a unit — a function, method, calculation, validation | Unit test |

**Build directly only for inert glue.** A few things have no behavior of their own and get no test of their own — a route or binding line, an empty class that clears a "not defined" error, trivial markup an end-to-end content check already covers. You still add them only because a failing test one layer up demanded them. Everything with behavior gets its own failing test first; when in doubt, drop down and write the test.

### 5. Close out

The top-level test is green and the stack is empty. Three things before it's done:

1. **Run the full suite.** Every cycle so far ran one test and its neighbors, scoped for speed — which means a regression outside that scope has been invisible the whole way through. This is the run that catches it, and it's the only honest comparison against the step 1 baseline.
2. **Walk the [verification checklist](#verification-checklist)**, then finish the rest of the Definition of Done: linters, formatters, type-checks.
3. **Hand off.** `code-review` over the diff, for the defects, convention breaches, and spec gaps a passing suite can't see; on anything security-bearing, follow it with `find-bugs` for an adversarial pass. Committing is the user's call, not a step you take on reaching green — when they ask for it, `git-commit` owns the history, and if there are checkpoint commits to fold into one message, tell it so.

## Real collaborators, and where mocks belong

Integration and end-to-end tests use real collaborators — a real datastore, no mocks — except external services, which you stub or fake so the suite runs offline. Unit tests isolate the object under test and mock its collaborators, because the goal is to prove *this* unit, not its dependencies.

Difficulty testing two units in isolation is a design signal, not a mocking problem: the coupling is too tight. Take it to `codebase-design` rather than reaching for a bigger mock.

**The testing pyramid:** many fast, precise unit tests at the bottom; fewer integration tests in the middle; a few end-to-end tests at the top proving the system works as a whole.

## Gotchas

The tempting shortcuts share one property: they all skip watching a test fail, and every one of them is a lie the code tells you later.

- **Never write the test after the code.** A test written against code you already have passes on its first run, and a test that never failed proves nothing. Worse, tests-after answer "what does this do?" when the question that finds bugs is "what *should* this do?"
- **Never keep code you wrote before its test**, not even "as reference". It biases every test you then write toward the implementation you already have, so you pin the edge cases you remembered instead of the ones the behavior actually has.
- **"I already manually tested it" is not coverage.** Manual testing leaves no record, can't be re-run, and is the first thing to slip under pressure.
- **"Deleting hours of work is wasteful" is the sunk-cost trap.** The time is gone either way; keeping code you can't trust is the actual waste.
- **"Being pragmatic means skipping TDD" is backwards.** TDD catches bugs before commit, documents behavior, and makes refactoring safe. The shortcut just moves the debugging to production.
- **Don't assert on the mock.** Checking that a stubbed datastore received `where(name: "Widget")` proves the mock was called, not that the feature works — and it stays green through a rewrite that breaks the feature outright. Assert real behavior through the public interface.
- **Cover the error paths, not just the happy one** — the invalid input, the raised exception, the guard that refuses. A suite that only exercises success documents half the behavior and leaves the silent-failure paths AGENTS.md §6, *Error handling, observability & reliability*, prohibits.
- **A behavior-changing slice ships behind a default-off flag, so it has two behaviors to test** — flag on, and flag off preserving today's behavior exactly (AGENTS.md §5, *Safe rollout, feature flags & migrations*). Drive both test-first; the flag-off test is the one that catches a "behavior-preserving" default that isn't.
- **Green is the end of the cycle, not the end of the work.** A passing suite says the code does what the tests demanded. It says nothing about whether the code is safe, simple, or idiomatic — that's step 5's handoff.

**Red flags — every one means stop, delete the code, and start over with TDD:** code before test · a layer with behavior built without a failing test at that layer · several changes then a single run · test written after implementation · a test that passes on its first run and wasn't meant to · can't explain why the test failed · loosening an assertion to reach green · "I'll add tests later" · "just this once" · "it's spirit not ritual" · "keep it as reference" · "this is different because…"

## Troubleshooting

| Issue | Solution |
| --- | --- |
| Don't know how to test it | Write the assertion first, against the API you wish existed. If that API is hard to name, the design isn't settled — that's `codebase-design`, not a testing problem. |
| Can't find the test runner or its single-test form | [RUNNERS.md](references/RUNNERS.md) — discovery order is the project's test config, then CI, then the lockfile. Never guess. |
| The suite was already red before you started | Fix or quarantine it, or record exactly which failures pre-date your work. Skipping this makes every Verify RED unreadable. |
| The test errors, and you're unsure whether that's a red | Ask whether the message names the thing you're about to build. If it does, that's the red. If it names a typo, a missing import, or a bad fixture, the test is broken — fix it and run again. |
| The test passes on its first run | It's testing behavior that already exists. Sharpen it until it fails, or you're writing coverage, not TDD. A characterization test is the deliberate exception — it's supposed to pass. |
| Two attempts at green have both failed | The step is too big. Revert to the last green and fake it — [CYCLE.md](references/CYCLE.md). |
| Test too complicated | The design is too complicated. Simplify the interface before simplifying the test. |
| Must mock everything to test one unit | Too coupled. Inject the dependencies; take the seam to `codebase-design`. |
| Test setup is huge | Extract helpers first; if it's still large, the object under test needs too much world to exist. |
| Refactoring turned a test red | Revert the refactor, not the test. A refactor that changes behavior isn't one — re-do it in smaller moves, staying green between each. |
| The test involves async work, a timer, or a job | Wait for the work, never `sleep` — [ASYNC.md](references/ASYNC.md). Then break the implementation on purpose and confirm the test notices. |
| The bug is a race or a double-submit | Don't try to reproduce the interleaving. Run the operation twice in sequence and drive out the guard that refuses the second — [ASYNC.md](references/ASYNC.md). |
| A test only fails in CI or under load | Treat it as a suspected race, not flakiness to re-run away. |
| The behavior exists but is untested and you must change it | Characterize first, then change — [The Iron Law](#the-iron-law) and [WALKTHROUGH.md](references/WALKTHROUGH.md). |
| The change is a pure rename with no behavior change | There's no red available. Lean on the existing suite as the safety net; if the identifier has no coverage, characterize it first. |

## Verification checklist

Before marking work complete:

- [ ] Baseline suite was green (or its pre-existing failures were recorded) before the first red
- [ ] Every new function or method that carries behavior has a test — inert glue excepted
- [ ] Each layer with behavior got its own failing test first
- [ ] Watched each test fail before implementing, and the failure named the behavior being built
- [ ] Ran the affected test after every change — never batched two changes before a run
- [ ] Wrote the minimal code to pass each test
- [ ] No assertion was weakened to reach green
- [ ] All tests pass; output is pristine (no errors or warnings)
- [ ] Tests exercise real code (mocks only for collaborators and external services)
- [ ] Edge cases and error states covered

Can't check every box? You skipped TDD. Start over.

This is the testing half of AGENTS.md §4, *Definition of Done* — lint, formatters, and type-checks are still owed, and unverified code is never reported as complete.

## References

Read these as needed for the task in hand, not upfront.

- [RUNNERS.md](references/RUNNERS.md) — finding the project's test runner and its single-test invocation, per ecosystem, and telling a real red from a broken test in each
- [CYCLE.md](references/CYCLE.md) — inside one turn: how big a step to take, the reds and greens worth keeping, what refactoring may mean, and what a stalled loop is telling you
- [ASYNC.md](references/ASYNC.md) — driving out asynchronous work, faking the clock, and testing the guard instead of the race
- [WALKTHROUGH.md](references/WALKTHROUGH.md) — one feature driven outside-in end to end, the bug-fix variant, and changing behavior in untested legacy code

## Attribution

- [thoughtbot/rails-consultant](https://github.com/thoughtbot/rails-consultant/tree/main/skills/test-driven-development) - test-driven-development, MIT
- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) - tdd, MIT
- [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) - test-driven-development, MIT
- Kent Beck, *Test-Driven Development: By Example* — the red-green-refactor cycle, and the fake-it / triangulate / obvious-implementation strategies
- Michael Feathers, *Working Effectively with Legacy Code* — characterization tests
