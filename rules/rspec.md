---
paths:
  - "**/*_spec.rb"
  - "**/spec/**/*.rb"
---

# RSpec spec standards

How a spec reads. The discipline that holds in every framework — cover the error paths, mock only at the boundary, no fixed delays, no skipped examples — is in `testing.md`, and which level a behavior belongs at is in `testing-levels.md`; both load alongside this file.

For the order specs get written in — a failing example before the code that satisfies it — follow the `tdd` skill. For which spec type a behavior belongs in, and a worked layout for a service spec, follow the `rspec` skill.

## Style

Follow the [RSpec Style Guide](https://rspec.rubystyle.guide), enforced through `rubocop-rspec`, which also covers what this file leaves out, such as spec file paths and verifying doubles. The structural patterns below are the ones that drift when a spec is written without a linter in the loop, so they are stated here rather than left to the cops: a spec is not finished until `rubocop` is clean on it. The limits and word lists below are the cops' defaults; where the project's `.rubocop.yml` configures a cop differently, the project's config wins (`ruby.md`). Where a project doesn't run `rubocop-rspec`, these bullets hold as written.

### `describe` and `context`

- Open with `RSpec.describe ClassName` — the constant, never a string. Name a method with `describe '#instance_method'` or `describe '.class_method'`, `#` and `.` exactly.
- `describe` names *what* is under test (the class, then a method); `context` names *under what circumstances*. A `context` description starts with `when`, `with`, or `without`, and the nested descriptions read as one sentence: `describe '#cancel'` → `context 'when the reservation is seated'` → `it 'refuses the cancellation'`.
- A `context` almost always has its opposite. A lone `context 'when valid'` with no `when invalid` beside it is the smell — it is the missing error path `testing.md` asks for. The opposite can be the outer group's default world, and a branch with several cases (`with a nil name`, `with an empty name`) gets one context per case rather than an invented negation.
- Nest no deeper than three levels. A fourth means the group is doing too much; split the class under test or flatten the scenarios.
- No blank line after a group's opening line, one blank line between sibling groups, none after the last.

### `subject`

- `subject` is the first declaration in its group, above every `let` and hook.
- Name it — `subject(:cancellation) { … }` — whenever an example references it. Leave it anonymous only when nothing does, because the examples use `is_expected`.
- A nested group that redefines `subject` gives it a new name (`subject(:result) { cancellation.call }`) rather than shadowing the outer one.
- Never stub a method on the subject; that tests the stub. Extract the collaborator and stub that, at the boundary.

### `let`, `before`, and `after`

- Declare in this order: `subject`, then `let!`/`let`, then `before`/`after` hooks. Keep consecutive `let`s together with no blank line between them; leave one blank line after the `subject`, after the last `let`, and after each hook.
- `let`, never an instance variable. A context varies the scenario by overriding a `let` (`let(:status) { :seated }`), not by reassigning in a hook. Keep `let` for objects and meaningful values, not for a primitive used once.
- `before` carries setup every example in its group needs, and nothing else: no expectations inside a hook, and one `before` per group rather than several. An override of a `let` beats a conditional in `before`.
- Write hooks with no scope argument: `before { … }`, never `before(:each)` or `before(:example)` — per-example is already the default. Don't use `:all` or `:context` either: state set once for the group leaks between examples. Use `before` and a factory.
- `after` releases what an example acquired outside the transaction — a temp file, a global stub, a process-wide setting. Rows under transactional tests and RSpec doubles are already undone; an `after` that cleans them is dead weight. Time is not always undone: rspec-rails calls `travel_back` only inside its typed example groups (model, request, and the like), so a service or PORO spec that calls `freeze_time` or `travel_to` without a block needs `after { travel_back }` — or use the block form.

### `it`

- One behavior per example, described in the third person, present tense: `it 'cancels the reservation'`. Never begin with `should`, never end on a conditional (`… if the guest is VIP`) — that condition is a `context`. Keep the description under 60 characters; one that long is two examples.
- A single-line example uses `it { is_expected.to be_success }`. An example with no description at all is `specify`; one with a description is `it`.
- One expectation per example, by default. When several expectations assert one outcome — a response's status and body — tag the group or example `:aggregate_failures` instead of splitting them. Pick one style per file.
- `expect(…).to` syntax only, with `is_expected` for the implicit subject. No `should`.
- Never generate examples from an iterator (`%w[a b].each { |x| it … }`). Use `it_behaves_like`, or write the cases out.
- One blank line above and below every example.

## Fixtures, doubles, and time

- Use Factory Bot rather than fixtures, and prefer `build_stubbed`/`build` over `create` unless the example genuinely needs persistence — it is far faster and keeps the test about behavior rather than the database. Declare date and time attributes in a block, so they are evaluated per example rather than frozen when the factory file loads.
- Realize `testing.md`'s determinism rule with Ruby tooling: stub outbound HTTP with WebMock, and control time with `ActiveSupport::Testing::TimeHelpers` (`travel_to`, `freeze_time`), falling back to Timecop off Rails. Reach for VCR only when a response is too large to hand-write — a recorded cassette drifts from the real API silently, and a green suite is exactly what that drift looks like.
- Cover an HTTP API with **request specs**. Reach for a **system spec** only when the API's sole consumer is a JavaScript client living in the same codebase, where the behavior worth asserting spans both sides.
- Don't chase DRY prematurely — duplication in specs is acceptable when it aids understanding. For genuine repetition, reach for `it_behaves_like`, `shared_context` for setup repeated across files, or a custom matcher when the same multi-line expectation keeps recurring.

## Attribution

- [RSpec Style Guide](https://rspec.rubystyle.guide)
