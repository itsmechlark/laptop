---
paths:
  - "**/*_spec.rb"
  - "**/spec/**/*.rb"
---

# RSpec spec standards

When working in a Ruby codebase, all specs must follow the [RSpec Style Guide](https://rspec.rubystyle.guide). Specs are the executable documentation of production behavior — write them to read as a behavior specification. This file covers how a spec should read; for the order it gets written in — a failing test before the code that satisfies it — follow the `tdd` skill.

- Cover the error paths, not just the happy one: invalid input, the raised exception, the guard that refuses. A spec that only exercises success documents half the behavior.

- Use `describe` for the thing under test; use `.method` for class methods and `#method` for instance methods.
- Use `context` to organize branches; start descriptions with **when**, **with**, or **without**. Every positive context should generally have a negative counterpart.
- Example (`it`) descriptions use third person, present tense ("returns the total") — never begin with "should", never end with a conditional (use a `context` instead). Keep under 60 characters.
- Always use the `expect` syntax; never the legacy `should` syntax.
- Declaration order within a group: `subject` → `let!`/`let` → `before`/`after` hooks. `subject` must be first when present; prefer named subjects.
- Prefer one expectation per example, or use `aggregate_failures` — pick one style and apply it consistently.
- Prefer verifying doubles (`instance_double`, `class_double`) over plain doubles; avoid `allow_any_instance_of`/`expect_any_instance_of`.
- Don't over-mock: stub at the boundary — HTTP, the clock, a third-party client — never the subject itself. A spec that mocks the object under test asserts the mock.
- Use Factory Bot (not fixtures), and prefer `build_stubbed`/`build` over `create` unless the example genuinely needs persistence — it is far faster and keeps the test focused on behavior rather than the database.
- Stub external HTTP (WebMock/VCR); control time with Rails' `ActiveSupport::Testing::TimeHelpers` (`travel_to`, `freeze_time`), falling back to Timecop only off Rails.
- Keep example state isolated: avoid `before(:all)`/`before(:context)` for database or mutable state — it leaks across examples; set up per-example with `let`/`before`.
- Don't chase DRY prematurely — duplication in tests is acceptable when it aids understanding. For genuine repetition, reach for `it_behaves_like`, `shared_context` for setup repeated across files, or a custom matcher when the same multi-line expectation keeps recurring.
- Use built-in and predicate matchers (`be_published`, `include`, `change(Model, :count).by(1)`); avoid bare `be` and asserting incidental/absolute state.
- **Spec file paths must mirror the described constant** (`RSpec/SpecFilePathFormat`): `describe MyModule::MyClass` → `spec/**/my_module/my_class_spec.rb`. Non-class descriptions are exempt.
- **Spec files must end with `_spec.rb`** (`RSpec/SpecFilePathSuffix`): any file under `spec/` that contains examples but doesn't use the `_spec.rb` suffix is an offense.
