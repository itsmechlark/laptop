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

Which level a behavior belongs at, and what each level owes. The discipline that holds at every level — mocking, determinism, isolation, test data — is in `testing.md`, which loads on these same paths.

| Level | Covers | Drives it through |
| --- | --- | --- |
| Unit | Pure logic — transforms, predicates, sorting, pagination math, validation | The function itself |
| Integration | What only appears when parts meet — routes, middleware, persistence, jobs, service coordination | The entrypoint: a request, a message, a job, a command |
| End to end | A critical journey, a hop across processes, a runtime or browser difference | The real interface |

- **A higher-level test never discharges direct coverage.** Reaching a function transitively through a route or a component is not a unit test of that function. A change that adds both internal logic and a composed entrypoint ships both kinds, in the same change.
- **A module isn't done until it has its own test.** The only routine exemption is a file with no behavior of its own, such as a re-export barrel — and an exemption is stated with its reason, not assumed.
- **Move up a level when the behavior needs persistence branching, state transitions, or query filtering**, rather than simulating a datastore inside a unit test.
- **Drive an integration test through the boundary**, not by importing the internals behind it, and assert what the boundary exposes: status codes, payloads, persisted records, emitted events. Not internal call ordering, unless the ordering is itself the contract.
- **Don't spend an end-to-end test on** pure computation, one case out of a validation matrix, a single function or query, a repeat of an integration test that crosses no new boundary, or anything needing fragile sequencing to pass. Cover the matrix low and keep one representative journey high — these are slow and expensive to diagnose, so a few high-signal scenarios beat volume.
- **Prefer accessible locators end to end** — role, label, visible text — with a stable test id only where semantics can't identify the element. Generated class names and positional selectors break on changes that break nothing for a user.
- If a change looks like it wants an end-to-end test and you decide against it, say which lower-level coverage stands in and what boundary an end-to-end test wouldn't have added.
