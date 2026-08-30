---
paths:
  - "**/*_spec.rb"
  - "**/spec/**/*.rb"
---

# RSpec spec standards

How a spec reads. The discipline that holds in every framework — cover the error paths, mock only at the boundary, no fixed delays, no skipped examples — is in `testing.md`, and which level a behavior belongs at is in `testing-levels.md`; both load alongside this file.

For the order specs get written in — a failing example before the code that satisfies it — follow the `tdd` skill.

- **Spec style is settled by tooling.** Follow the [RSpec Style Guide](https://rspec.rubystyle.guide) through `rubocop-rspec` — group naming, `describe`/`context` wording, example descriptions, `expect` syntax, declaration order, expectation counts, verifying doubles, and spec file paths are all cops. The bullets below are what a cop can't decide.
- Use Factory Bot rather than fixtures, and prefer `build_stubbed`/`build` over `create` unless the example genuinely needs persistence — it is far faster and keeps the test about behavior rather than the database. Declare date and time attributes in a block, so they are evaluated per example rather than frozen when the factory file loads.
- Realize `testing.md`'s determinism rule with Ruby tooling: stub outbound HTTP with WebMock, and control time with `ActiveSupport::Testing::TimeHelpers` (`travel_to`, `freeze_time`), falling back to Timecop off Rails. Reach for VCR only when a response is too large to hand-write — a recorded cassette drifts from the real API silently, and a green suite is exactly what that drift looks like.
- Cover an HTTP API with **request specs**. Reach for a **system spec** only when the API's sole consumer is a JavaScript client living in the same codebase, where the behavior worth asserting spans both sides.
- Don't chase DRY prematurely — duplication in specs is acceptable when it aids understanding. For genuine repetition, reach for `it_behaves_like`, `shared_context` for setup repeated across files, or a custom matcher when the same multi-line expectation keeps recurring.
