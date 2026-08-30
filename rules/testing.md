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
  - "**/__tests__/**/*.js"
  - "**/__tests__/**/*.jsx"
  - "**/__tests__/**/*.ts"
  - "**/__tests__/**/*.tsx"
  - "**/e2e/**/*.js"
  - "**/e2e/**/*.jsx"
  - "**/e2e/**/*.ts"
  - "**/e2e/**/*.tsx"
  - "**/playwright.config.ts"
---

# Testing standards

Framework-agnostic test discipline — RSpec, ExUnit, Vitest/Jest, QUnit alike. Which level a behavior belongs at is in `testing-levels.md`, which loads on these same paths; framework mechanics are in `rspec.md` and the testing bullets of `elixir.md`, `react-typescript.md`, and `ember.md`.

- **Mock only at the boundary.** The only doubles are third-party APIs and external services — network, the system clock, the filesystem. Double what sits outside the boundary under test and nothing inside it, and seed only the data the scenario needs. A test that mocks its subject or its internal collaborators asserts the mock, not the behavior.
- **Never mock the datastore.** Databases, caches, and key-value stores get a real test-scoped instance, an in-memory database, or in-process bindings. A mocked query, transaction, or rollback asserts nothing about what it stands in for and hides exactly the bugs a persistence test exists to catch.
- **Cover the error paths, not just the happy one:** invalid input, the raised exception, the guard that refuses. A test that only exercises success documents half the behavior.
- **One test file per unit under test, mirroring the source path** — `src/foo/bar.ts` → `__tests__/foo/bar.test.ts`, `app/models/order.rb` → `spec/models/order_spec.rb`. At integration the unit is the entrypoint rather than the module, so it is one file per entrypoint. A reader looking for a behavior should have one obvious file to open.
- **Name examples as specifications** — what the code guarantees and under what conditions — so the suite is where a reader learns the module, including its edge cases and failure modes.
- **Assert behavior and contracts, not implementation details**, so a refactor that preserves behavior keeps the tests green.
- **Make tests deterministic.** Stub outbound HTTP and control time rather than depending on the wall clock or a live network, so an outcome never depends on when or where the suite runs.
- **No `sleep`.** For async work, wait on the condition — poll for the expected state, or use the framework's synchronization helpers — never a fixed delay. A fixed delay is either too short (flaky) or too slow (wasteful), and usually both.
- **Keep examples isolated.** No shared mutable state that leaks between tests; set up per-test so any test can run alone and in any order.
- **Flakiness is a defect, and retries hide it.** When a test is intermittent, look at the async boundary, the isolation, and the teardown — never at the retry count or the length of a wait.
- **Every test runs in CI.** Nothing "manual only", nothing gated behind a local-only condition, nothing pending unless it was explicitly asked for.
- **Test data is synthetic.** Never real user records — names, emails, photos, or anything copied out of production. Use a reserved domain (`@example.invalid`), and tag generated resources so they stay distinguishable from real data at a glance.
- **Never commit credentials or session state.** Cookies, tokens, passwords, saved storage state, and authenticated profiles are generated per run into a git-ignored directory — a committed one is a leaked credential that also rots.
- **Never bypass authentication, authorization, or validation for a test's convenience.** Set auth up through the interface a real client uses. A test build may change identifiers and suppress notifications; it may not skip a permission check or a domain constraint, because then the test stops covering the thing that matters.
- **A test never writes to production.** A config flag or a target name doesn't authorize it; that takes a deliberate, isolated path with its own approval. Read-only smoke checks against production are fine.
