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

# Choosing a test level

Which level a behavior belongs at, and what each level owes. The discipline that holds at every level — run them, cover the error paths, mock only at the boundary, no `sleep` — is in `testing.md`. That one loads on test files themselves; this rule reaches further, into `__tests__/` and `e2e/` support code and the runner config, so on those paths read `testing.md` too rather than assuming it is already in context.

## Unit

- **A higher-level test never discharges direct coverage.** Reaching a function transitively through a route, a component, or an app layer is not a unit test of that function. A feature that adds both internal logic and a composed entrypoint ships both kinds, in the same change.
- **Pure logic is a unit target in isolation** — transforms, query and predicate builders, sorting and ranking, pagination math, validation helpers. Branches and error paths are cheapest to reach here, so reach them here rather than through a slower level.
- **A module isn't done until it has its own test.** The only routine exemption is a file with no behavior of its own, such as a re-export barrel — and an exemption is stated with its reason, not assumed.
- **When the behavior needs persistence branching, state transitions, or query filtering, move the test up a level** rather than simulating a datastore inside a unit test.

## Integration

- **Integration covers what only appears when the parts meet:** route composition, middleware wiring, request and response flow, persistence boundaries, background work being triggered, service-to-service coordination.
- **The unit here is the entrypoint, not the module** — so `testing.md`'s one-file-per-unit rule means one file per entrypoint or composed behavior. Drive it through the boundary — an HTTP request, a message handler, a job, a command — rather than importing the internals behind it.
- **Prefer realistic setup over mocking.** Double only what sits outside the boundary under test, and seed only the data the scenario needs.
- **Assert what the boundary exposes:** status codes, payloads, persisted records, emitted events. Not internal call ordering, unless the ordering is itself the contract.

## End to end

- **E2E earns its place at a real boundary and nowhere else:** a critical user journey, a hop across processes or services, a deployment or environment misconfiguration, parity across runtimes, browser- or device-specific behavior, or a failure that would block a release. Also where lower levels genuinely cannot reach the confidence needed.
- **Don't spend one on** pure computation, a single case out of a validation matrix, one function or query, a repeat of an integration test that crosses no new boundary, an implementation detail, or anything needing fragile sequencing to pass.
- **Cover the matrix low and keep one representative journey high.** These tests are slow and expensive to diagnose, so a few high-signal scenarios beat volume.
- **Prefer accessible locators** — role, label, visible text — with a stable test id only where semantics can't identify the element. Generated class names and positional selectors break on changes that break nothing for a user.
- If a change looks like it wants E2E and you decide against it, say which lower-level coverage stands in and what boundary an E2E wouldn't have added.
