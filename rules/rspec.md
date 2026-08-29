---
paths:
  - "**/*_spec.rb"
  - "**/spec/**/*.rb"
---

# RSpec spec standards

When working in a Ruby codebase, all specs must follow the [RSpec Style Guide](https://rspec.rubystyle.guide). This file covers RSpec-specific style — how a spec reads.

The general testing standards that hold in every framework — run the tests, cover the error paths, mock only at the boundary, no `sleep`, 100% pass, no skipped specs — live in `testing.md` and load alongside it.

Specs are the executable documentation of production behavior; for the order they get written in — a failing test before the code that satisfies it — follow the `tdd` skill.

- Use `describe` for the thing under test; use `.method` for class methods and `#method` for instance methods.
- Use `context` to organize branches; start descriptions with **when**, **with**, or **without**. Every positive context should generally have a negative counterpart.
- Example (`it`) descriptions use third person, present tense ("returns the total") — never begin with "should", never end with a conditional (use a `context` instead). Keep under 60 characters.
- Always use the `expect` syntax; never the legacy `should` syntax.
- Declaration order within a group: `subject` → `let!`/`let` → `before`/`after` hooks. `subject` must be first when present; prefer named subjects.
- Prefer one expectation per example, or use `aggregate_failures` — pick one style and apply it consistently.
- Prefer verifying doubles (`instance_double`, `class_double`) over plain doubles; avoid `allow_any_instance_of`/`expect_any_instance_of`. Stub at the boundary only (`testing.md`), never the subject itself.
- Use Factory Bot (not fixtures), and prefer `build_stubbed`/`build` over `create` unless the example genuinely needs persistence — it is far faster and keeps the test focused on behavior rather than the database. Declare date and time attributes in a block, so they are evaluated per example rather than frozen when the factory file loads.
- Realize `testing.md`'s determinism rule with Ruby tooling: stub external HTTP with WebMock, and control time with Rails' `ActiveSupport::Testing::TimeHelpers` (`travel_to`, `freeze_time`), falling back to Timecop only off Rails. Reach for VCR only when a response is too large to hand-write — a recorded cassette drifts from the real API silently.
- Keep example state isolated: avoid `before(:all)`/`before(:context)` for database or mutable state — it leaks across examples; set up per-example with `let`/`before`.
- Don't chase DRY prematurely — duplication in tests is acceptable when it aids understanding. For genuine repetition, reach for `it_behaves_like`, `shared_context` for setup repeated across files, or a custom matcher when the same multi-line expectation keeps recurring.
- Cover an HTTP API with **request specs**. Reach for a **system spec** only when the API's sole consumer is a JavaScript client living in the same codebase, where the behavior worth asserting spans both sides.
- Use built-in and predicate matchers (`be_published`, `include`, `change(Model, :count).by(1)`); avoid bare `be` and asserting incidental/absolute state.
- **Spec file paths must mirror the described constant** (`RSpec/SpecFilePathFormat`): `describe MyModule::MyClass` → `spec/**/my_module/my_class_spec.rb`. Non-class descriptions are exempt.
- **Spec files must end with `_spec.rb`** (`RSpec/SpecFilePathSuffix`): any file under `spec/` that contains examples but doesn't use the `_spec.rb` suffix is an offense.
