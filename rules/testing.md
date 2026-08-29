---
paths:
  - "**/*_spec.rb"
  - "**/*_test.rb"
  - "**/spec/**/*.rb"
  - "**/test/**/*.rb"
  - "**/*_test.exs"
  - "**/test/**/*.exs"
  - "**/*.test.js"
  - "**/*.test.jsx"
  - "**/*.test.ts"
  - "**/*.test.tsx"
  - "**/*.spec.js"
  - "**/*.spec.jsx"
  - "**/*.spec.ts"
  - "**/*.spec.tsx"
  - "**/tests/**/*-test.js"
---

# Testing standards

Framework-agnostic testing discipline. These apply to every test suite — RSpec, ExUnit, Vitest/Jest, QUnit — and load alongside the language-specific rules (`rspec.md` for RSpec mechanics; the testing bullets in `elixir.md`, `react-typescript.md`, and `ember.md`). Tests are the executable specification of production behavior: write them to read as one. Which level a given behavior belongs at — unit, integration, or end to end — is in `test-levels.md`.

- **New behavior and bug fixes come with tests.** A bug fix starts with a test that reproduces the bug, then the fix that makes it pass. Write the test first — the `tdd` skill covers the red-green-refactor cycle.
- **Cover the error paths, not just the happy one:** invalid input, the raised exception, the guard that refuses. A test that only exercises success documents half the behavior.
- **Always run the tests — never claim work done on unverified code.** Run the specific test file for what you changed first, then widen to the broader suite once it's green.
- **100% pass rate.** 95% is not acceptable. A failing or flaky test is a defect to diagnose and fix, not to tolerate. Retries don't fix flakiness, they hide it — when a test is intermittent, look at the async boundary, the isolation, and the teardown, rather than raising the retry count or lengthening a wait.
- **Never jury-rig, skip, suppress, or delete a test because it's difficult.** Diagnose the failure and try another approach. If a shortcut looks unavoidable, stop and ask first.
- **No pending or skipped tests unless explicitly asked.** Every test must run in CI — nothing "manual only," nothing gated behind a local-only condition.
- **One test file per unit under test, mirroring the source path** — `src/foo/bar.ts` → `__tests__/foo/bar.test.ts`, `app/models/order.rb` → `spec/models/order_spec.rb`. Don't collect unrelated sources into one broad suite: a reader looking for a module's behavior should have one obvious file to open.
- **Name examples as specifications.** `describe`/`context`/`it` should read as requirements — what the code guarantees and under what conditions — so the suite alone teaches how a module works and why it works that way, including the edge cases it handles and the failure modes it guards.
- **Mock only at the boundary.** The only doubles are third-party APIs and external services — network, the system clock, the filesystem. Never mock the code under test or its internal collaborators: a test that mocks its subject asserts the mock, not the behavior.
- **Never mock the datastore.** Databases, caches, and key-value stores get a real test-scoped instance, an in-memory database, or in-process bindings. A mocked query, transaction, or rollback asserts nothing about the behavior it stands in for and hides exactly the bugs a persistence test exists to catch.
- **Make tests deterministic.** Stub outbound HTTP and control time rather than depending on the wall clock or a live network, so a test's outcome never depends on when or where it runs.
- **No `sleep`.** For async work, wait on the condition — poll for the expected state or use the framework's waiting/synchronization helpers — never a fixed delay. A `sleep` is either too short (flaky) or too slow (wasteful), and usually both.
- **Keep examples isolated.** No shared mutable state that leaks between tests; set up per-test so any test can run alone and in any order.
- **Assert behavior and contracts, not implementation details** — so a refactor that preserves behavior keeps the tests green. Duplication in tests is acceptable when it aids reading; extract shared setup only for genuine repetition.
- **Test data is synthetic.** Never real user records — names, emails, photos, or anything copied out of production. Use a reserved domain (`@example.invalid`), tag generated resources with a run identifier, and keep them distinguishable from real data at a glance.
- **Never commit credentials or session state.** Cookies, tokens, passwords, saved storage state, and authenticated profiles are generated per run into a git-ignored directory — a committed one is a leaked credential that also rots.
- **Never bypass authentication, authorization, or validation for a test's convenience.** Set auth up through the interface a real client uses. A test build may change identifiers and suppress notifications; it may not skip a permission check or a domain constraint, because then the test stops covering the thing that matters.
- **A test never writes to production.** A config flag or a target name doesn't authorize it; that takes a deliberate, isolated path with its own approval. Read-only smoke checks against production are fine.
