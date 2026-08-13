---
name: tdd
description: Strict red-green-refactor TDD workflow for implementing features, fixing bugs, or changing behavior in any codebase. Enforces writing a failing test before any production code. Agnostic to language, framework, and test runner. Use whenever you want to implement with TDD.
argument-hint: "[feature, bug, or behavior to implement]"
disable-model-invocation: true
---

# Test-Driven Development

Build a feature or fix a bug by writing a failing test first and then the minimum code that makes it pass, so every line of production code exists because a test demanded it.

**Core principle:** if you didn't watch the test fail, you don't know if it tests the right thing.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to use this skill

- Implementing a new feature or behavior you intend to keep
- Fixing a bug — start with a test that reproduces it, then make it pass
- Changing existing behavior where a silent regression would be costly
- Any language, framework, or test runner: the workflow is agnostic to all three

Not for a throwaway spike you will delete, or a change with no behavior to pin down (a copy tweak, a bumped config value). Once you're keeping the code, it comes in test-first.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote code before the test? Delete it. Start over. No exceptions — don't keep it as "reference", don't "adapt" it while writing tests, don't even look at it. Delete means delete. Implement fresh from the tests.

## Outside-in development

Start every feature with a high-level test that describes behavior from the user's perspective. Run it, read the failure, and let that failure dictate the next move. As failures push you down the stack, write a new failing test at each layer you drop into — never write code for a layer without a failing test at that layer demanding it.

### One change, one run

After every change — writing a test, adding a route/binding, creating a file, implementing a function — run the affected test immediately with the project's test runner. The failure message is your instruction for what to do next. Don't batch changes and don't guess ahead: one change, one run, read the failure, decide. Two changes before a run and you no longer know which one the test is reacting to.

### Drop down by writing the next failing test

A failure rarely means "write this exact line." It usually means "the layer below isn't there yet." When the active test's failure points to a layer that has behavior of its own, drop down and write a failing test at that layer before building it. Think of it as a stack of failing tests:

- The **active** test is the one whose failure you're reading now.
- Its failure points to a missing lower layer → write a new failing test there. It becomes the active test.
- Drive that test red-green-refactor. If it forces you down another level, push another failing test.
- When the active test goes green, pop it: rerun the test one layer up. Its next failure drives the next move.

The ladder, top to bottom (use your stack's equivalent names):

| When the failure points to…                                   | Write this failing test |
| ------------------------------------------------------------- | ----------------------- |
| End-to-end behavior from the user's perspective               | End-to-end / system test |
| A handler/endpoint's response, status, or routing             | Integration test         |
| Logic in a unit — a function, method, calculation, validation | Unit test                |

Integration and end-to-end tests use real collaborators (a real datastore, no mocks) — except external services, which you stub or fake so the suite runs offline. Unit tests isolate the object under test and mock its collaborators, because the goal is to prove *this* unit, not its dependencies. Difficulty testing two units in isolation signals too-tight coupling.

### Build directly only for inert glue

A few things have no behavior of their own, so they get no test of their own — but you still add them only because a failing test one layer up demanded them: a route/binding line, an empty class or module to clear a "not defined" error, trivial markup an end-to-end test's content check already covers. Everything with behavior gets its own failing test first. When in doubt, drop down and write the test.

**The testing pyramid:** many fast, precise unit tests at the bottom; fewer integration tests in the middle; a few end-to-end tests at the top that prove the system works as a whole.

## Red-Green-Refactor

The cycle every test follows, at every layer. A test going green is what lets you pop back up.

### RED — write a failing test

One minimal test showing what should happen: one behavior, a clear name, testing real behavior through the public interface.

- **Good:** a test that calls `search("Widget")` and asserts it returns only the matching record — real behavior, one thing, named for what it does.
- **Bad:** a test that stubs the datastore and asserts it received a `where(name: "Widget")` call. That tests the mock, not whether search returns the right items — it proves nothing.

### Verify RED — watch it fail

**Mandatory. Never skip.** Run the test and confirm it *fails* (not errors), for the *expected* reason (the behavior is missing, not a typo). Passes already? You're testing existing behavior — fix the test. Errors? Fix the error and re-run until it fails correctly.

### GREEN — minimal code

Write the simplest code that passes the test.

- **Good:** implement `search(term)` as the simplest filter that returns matching records — just enough to pass.
- **Bad:** `search(term, fuzzy:, limit:, scope:)` — a search framework the test never asked for. YAGNI.

Don't add features, refactor other code, or "improve" beyond the test.

### Verify GREEN — watch it pass

**Mandatory.** Confirm the test passes, other tests still pass, and the output is pristine (no errors or warnings). Test fails? Fix the code, not the test. Other tests fail? Fix them now.

### REFACTOR — clean up

After green only: remove duplication, improve names, extract helpers. Keep tests green; don't add behavior.

### Repeat

Pop the stack. Rerun the test one layer up, read its next failure, and let it drive the next move — build inert glue, or push a new failing test for the next layer down. Continue until the top-level test is green and the stack is empty.

## Example: outside-in, in the abstract

**Story:** a guest searches for items by name.

1. **Top of the stack — end-to-end test.** Visit the page, type "Widget", submit, expect "Widget" in the result. Run it; the failure points at the request/handler layer.
2. **Drop down — integration test for the handler.** Request the index with `search=Widget`, expect the response to include "Widget". Run it, one change at a time: no route → add the route (inert glue); handler not defined → create an empty handler; response missing "Widget" → the handler needs search logic, which is a unit concern. Drop down again.
3. **Drop down — unit test for the search.** `search("Widget")` returns only the matching record. Verify RED, implement the minimal filter, verify GREEN, pop it. Rerun the integration test; wire the handler and view until it's green, pop it. Rerun the end-to-end test and drive the remaining UI the same way until it's green and the stack is empty.

**Bug fix** is the same loop: write a failing test that reproduces the bug from the outside, drop to the layer the failure names, fix it under red-green-refactor. Never fix a bug without a test — the test proves the fix and prevents the regression.

## Gotchas

The tempting shortcuts share one property: they all skip watching a test fail, and every one of them is a lie the code tells you later.

- **Never write the test after the code.** A test written against code you already have passes on its first run, and a test that never failed proves nothing — you never saw it catch anything. Worse, tests-after answer "what does this do?" when the question that finds bugs is "what *should* this do?" Only test-first makes you watch it fail for the right reason.
- **Never keep code you wrote before its test**, not even "as reference." It biases every test you then write toward the implementation you already have, so you pin down the edge cases you remembered instead of the ones the behavior actually has. Delete it and implement fresh.
- **"I already manually tested it" is not coverage.** Manual testing leaves no record, can't be re-run, and is the first thing to slip under pressure. Only an automated test still defends the behavior next month.
- **"Deleting hours of work is wasteful" is the sunk-cost trap.** The time is gone either way; keeping code you can't trust is the actual waste.
- **"Being pragmatic means skipping TDD" is backwards.** TDD is the pragmatic path — it catches bugs before commit, documents behavior, and makes refactoring safe. The shortcut just moves the debugging to production.
- **Don't assert on the mock.** Checking that a stubbed datastore received `where(name: "Widget")` proves the mock was called, not that the feature works. Assert real behavior through the public interface; mock only collaborators and external services.

**Red flags — every one means stop, delete the code, and start over with TDD:** code before test · a layer with behavior built without a failing test at that layer · several changes then a single run · test written after implementation · test passes on its first run · can't explain why the test failed · "I'll add tests later" · "just this once" · "it's spirit not ritual" · "keep it as reference" · "this is different because…"

## Troubleshooting

| Problem                  | Solution                                                            |
| ------------------------ | ------------------------------------------------------------------ |
| Don't know how to test   | Write the wished-for API and the assertion first. Ask your partner.|
| Test too complicated     | The design is too complicated. Simplify the interface.             |
| Must mock everything     | The code is too coupled. Use dependency injection.                 |
| Test setup is huge       | Extract helpers; if still complex, simplify the design.            |

## Verification checklist

Before marking work complete:

- [ ] Every new function/method has a test
- [ ] Ran the affected test after every change — never batched two changes before running
- [ ] Each layer with behavior got its own failing test first
- [ ] Watched each test fail before implementing, for the expected reason
- [ ] Wrote the minimal code to pass each test
- [ ] All tests pass; output is pristine (no errors or warnings)
- [ ] Tests exercise real code (mocks only for collaborators/external services)
- [ ] Edge cases and error states covered

Can't check every box? You skipped TDD. Start over.

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/tdd) - tdd, MIT
- [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/test-driven-development) - test-driven-development, MIT
