---
paths:
  - "**/*.rb"
  - "**/Gemfile"
  - "**/*.rake"
  - "**/*.gemspec"
---

# Ruby standards

Ruby the language. Rails conventions are in `rails.md`, dependency declaration and pinning in `bundler.md`, gem authoring and release in `gem.md`, and specs in `rspec.md` — each loads on its own paths.

The `**/*.rb` glob reaches spec files too, and only the two style bullets below govern them. Everything from "Favor small Plain Old Ruby Objects" onward is about designing production objects — in a spec, follow `rspec.md` instead.

- **Style is a settled config, not a judgment call.** Adopt [`standard`](https://github.com/testdouble/standard) on a new project and the project's existing RuboCop configuration on an established one, then let the tool decide and keep it clean. Don't bikeshed the config or hand-tune a cop to accommodate a single file — the value is that nobody spends attention here.
- Limit conditional modifiers to short, simple lines (`do_later if async?`). Once the line runs long or the condition compounds (`if signed_in? && !current_user.active?`), use the multi-line form so the branch is visible while scanning, or extract a predicate that makes the modifier readable again.
- Favor small Plain Old Ruby Objects and composition over inheritance. Reach for a class rather than a module when behavior shared across models has state or an identity of its own.
- Model an immutable value object with `Data.define` (Ruby 3.2+) instead of a hash with three known keys, so the shape has a name and a wrong key fails at construction rather than as a `nil` three layers away.
- Avoid optional parameters. A method carrying several of them is usually doing more than one thing — split it.
- Prefer a descriptive method name over a bang (`!`) suffix. The `!` means "the dangerous one of the pair", so it says nothing when there is no safe twin beside it.
- Prefer `private`. Use `protected` only for comparison methods (`==`, `<`, `>`) that genuinely need a peer's internals.
- Prefer invoking the reader over touching the instance variable, and give a memoizing instance variable a leading underscore (`@_total`) so it reads as internal cache rather than as state.
- Rescue specific exceptions and raise domain-specific error classes with actionable messages. A broad `rescue StandardError` swallows the bugs you most wanted to hear about.
- Avoid monkey-patching, including within your own application. An override that lives away from the class it changes is invisible at every call site that depends on it.
- Use `def self.method` rather than `class << self`, and order class methods above instance methods.

Specs follow `rspec.md`, and they come first: new behavior and bug fixes are driven by a failing test before the code that satisfies it. The `tdd` skill covers that cycle.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/ruby) - ruby, MIT
