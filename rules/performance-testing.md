---
paths:
  - "**/bench/**"
  - "**/benchmark/**"
  - "**/benchmarks/**"
  - "**/*.bench.js"
  - "**/*.bench.ts"
  - "**/*.benchmark.js"
  - "**/*.benchmark.ts"
  - "**/spec/performance/**"
  - "**/test/performance/**"
  - "**/tests/performance/**"
  - "**/__tests__/performance/**"
  - "**/k6/**"
  - "**/*.k6.js"
  - "**/*.k6.ts"
---

# Performance testing

Scale, load, and benchmark tests: where they live and what they owe. A performance test is any test whose assertion is about cost rather than correctness — elapsed time, throughput, memory or allocations, query count, or how behavior holds up as data volume grows. The discipline every test shares is in `testing.md`; which level a functional test belongs at is in `testing-levels.md`.

- **Performance tests belong in a dedicated suite that the default test run excludes.** Give it its own location — `spec/performance/`, `test/performance/`, `__tests__/performance/`, `bench/`, `*.bench.ts`, `k6/` — and run it through its own named command (`rspec --tag performance`, `mix test --only performance`, `vitest bench`, a `test:perf` script), so the default run stays fast.
- **Key the exclusion on location, not on remembering a tag.** An RSpec `define_derived_metadata(file_path: %r{/spec/performance/})` that sets `performance: true`, paired with `filter_run_excluding performance: true`; an ExUnit `@moduletag :performance` on every module in the suite, paired with `exclude: [:performance]` in `test_helper.exs`; Vitest's bench files, which `vitest run` already skips; a separate Jest config. A file dropped into the suite must never leak into the default run.
- **Unit and integration tests hold no performance tests.** No timing, throughput, memory, query-count, or volume assertion goes into a unit or integration file, tagged or not. When one turns up there, move it into the suite rather than duplicating it. Instrumentation that fails the default run on an N+1 — Bullet with `Bullet.raise` — is a linter over the whole suite, not a performance test, and stays.
- **Mirror the source path under the suite root** — `app/models/order.rb` → `spec/performance/models/order_spec.rb`. The one-file-per-unit rule in `testing.md` holds within each suite.
- **The suite still runs in CI**, in its own job — scheduled, or triggered for changes to the paths it guards — never manual-only. When a change touches a guarded path, run the suite's command before calling the work done; that is the relevant suite, even though the default run skips it.
- **Prefer a deterministic measure where one captures the cost.** Query count and allocation count don't drift between runs, so they take an exact or upper-bound assertion. Wall-clock time and throughput do drift: compare them against a recorded baseline with a stated tolerance, never a fixed absolute threshold, on consistent hardware — a laptop number and a shared-runner number are not comparable. The verdict, not the raw number, is what has to be repeatable.
- **Prove the cost doesn't grow with N.** Run the scenario at two sizes and assert the cost is flat, or grows as expected, between them. A single small dataset cannot expose an N+1 or an unbounded load.
- **Generate volume synthetically in setup**, sized to the claim the test makes. Don't commit large fixture dumps.
- **A regression flag is investigated, not retried.** Re-running until it passes, or widening a tolerance to make it pass, masks the failure. A tolerance changes only as a deliberate edit with its reason stated.
- **Load tests target an isolated environment.** Never production — read-only traffic still loads it — and never a shared environment without its owners' agreement.
- **A change that claims a performance improvement carries the measurement.** Report before-and-after numbers from the suite, on the same hardware, in the pull request.
- **Follow the repo's existing performance surface.** Where none exists, standing one up is a proposal, not a silent addition: name the hot path worth guarding and raise it separately.
