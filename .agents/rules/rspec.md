---
paths:
  - "**/*_spec.rb"
  - "**/spec/**/*.rb"
---

# RSpec spec standards

When working in a Ruby codebase, all specs must follow the [RSpec Style Guide](https://rspec.rubystyle.guide). Specs are the executable documentation of production behavior — write them to read as a behavior specification.

- Use `describe` for the thing under test; use `.method` for class methods and `#method` for instance methods.
- Use `context` to organize branches; start descriptions with **when**, **with**, or **without**. Every positive context should generally have a negative counterpart.
- Example (`it`) descriptions use third person, present tense ("returns the total") — never begin with "should", never end with a conditional (use a `context` instead). Keep under 60 characters.
- Always use the `expect` syntax; never the legacy `should` syntax.
- Declaration order within a group: `subject` → `let!`/`let` → `before`/`after` hooks. `subject` must be first when present; prefer named subjects.
- Prefer one expectation per example, or use `aggregate_failures` — pick one style and apply it consistently.
- Prefer verifying doubles (`instance_double`, `class_double`) over plain doubles; avoid `allow_any_instance_of`/`expect_any_instance_of`.
- Use Factory Bot (not fixtures), stub external HTTP (WebMock/VCR), and use Timecop instead of stubbing `Time`/`Date`.
- Don't chase DRY prematurely — duplication in tests is acceptable when it aids understanding; use shared examples (`it_behaves_like`) for genuine repetition.
- Use built-in and predicate matchers (`be_published`, `include`, `change(Model, :count).by(1)`); avoid bare `be` and asserting incidental/absolute state.
