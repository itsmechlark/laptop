---
paths:
  - "**/*.rb"
  - "**/Gemfile"
  - "**/*.rake"
  - "**/*.gemspec"
---

# Ruby standards

Operate at a principal-engineer level in this ecosystem: know the idioms, the canonical style guide, and the standard tooling, and prefer them over generic cross-language habits.

This file is Ruby the language. Rails conventions are in `rails.md`, dependency declaration and pinning in `bundler.md`, gem authoring and release in `gem.md`, and specs in `rspec.md` — each loads on its own paths, so a Rails model gets this file and `rails.md` together.

## Style

- Follow the [Ruby Style Guide](https://rubystyle.guide), and keep files `# frozen_string_literal: true`.
- Enforce style with an opinionated set of rules already decided: [`standard`](https://github.com/testdouble/standard) on a new project, the project's existing RuboCop configuration on an established one. Consistency is the whole point — don't bikeshed the config or hand-tune cops to accommodate a single file.
- Write expressive, idiomatic Ruby: prefer `Enumerable` methods (`map`, `each_with_object`, `filter_map`, `reduce`) over manual loops, and `&:sym` over a block that only calls one method.
- Limit conditional modifiers to short, simple lines (`do_later if async?`). Once the line runs long or the condition compounds (`if signed_in? && !current_user.active?`), use the multi-line form so the branch is visible while scanning — or extract a predicate that makes the modifier readable again.
- Avoid ternaries and multiple assignment on one line (`one, two = 1, 2`); the multi-line `if` puts the emphasis on the branches, which is usually where it belongs.
- Use `%()` for a single-line string that interpolates and contains double quotes, and a heredoc for anything multi-line.
- Avoid monkey-patching. Avoid organizational comments (`# Validations`) — a comment that labels a region is a sign the file wants splitting.

## Objects, methods, and names

- Favor small Plain Old Ruby Objects (POROs) and composition over inheritance; use duck typing and modules/mixins deliberately. Reach for a class rather than a module when behavior shared across models has state or an identity of its own.
- Model immutable value objects with `Data.define` (Ruby 3.2+) or `Struct`; use keyword arguments for clarity, freeze constants, and reach for pattern matching (`case/in`) on structured data.
- Suffix predicates with `?`. Prefer a descriptive name over a bang (`!`) suffix, and prefix an unused variable or parameter with `_`.
- Use `def self.method`, not `class << self`, and order class methods above instance methods.
- Avoid optional parameters. A method carrying several of them is usually doing more than one thing — split it.
- Prefer `private`. Use `protected` only for comparison methods (`==`, `<`, `>`) that genuinely need a peer's internals.
- Prefer invoking the reader over touching the instance variable, and give a memoizing instance variable a leading underscore (`@_total`) so it reads as internal cache rather than as state.
- Rescue specific exceptions — never a bare `rescue` or broad `rescue StandardError`; raise domain-specific error classes and fail fast with clear, actionable messages.

Specs follow the RSpec standards (`rspec.md`), and they come first: new behavior and bug fixes are driven by a failing test before the code that satisfies it. The `tdd` skill covers that cycle.

Style guidance here draws on thoughtbot's [Ruby guide](https://github.com/thoughtbot/guides/tree/main/ruby) (MIT).
