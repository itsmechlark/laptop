---
paths:
  - "**/*.rb"
  - "**/Gemfile"
  - "**/*.rake"
  - "**/*.gemspec"
---

# Ruby & Rails standards

Operate at a principal-engineer level in this ecosystem: know the idioms, the canonical style guide, and the standard tooling, and prefer them over generic cross-language habits.

## Ruby
- Follow the [Ruby Style Guide](https://rubystyle.guide); enforce with RuboCop, and keep files `# frozen_string_literal: true`.
- Write expressive, idiomatic Ruby: prefer `Enumerable` methods (`map`, `each_with_object`, `filter_map`, `reduce`) over manual loops; use blocks and `&:sym`.
- Favor small Plain Old Ruby Objects (POROs) and composition over inheritance; use duck typing and modules/mixins deliberately.
- Model immutable value objects with `Data.define` (Ruby 3.2+) or `Struct`; use keyword arguments for clarity, freeze constants, and reach for pattern matching (`case/in`) on structured data.
- Rescue specific exceptions — never a bare `rescue` or broad `rescue StandardError`; raise domain-specific error classes and fail fast with clear, actionable messages.
- Audit dependencies with `bundler-audit`; keep `Gemfile.lock` committed and gem versions current and CVE-free.

## Ruby on Rails
- Embrace convention over configuration; follow the [Rails Style Guide](https://rails.rubystyle.guide).
- Keep controllers skinny and prevent god-object models — extract service objects, query objects, form objects, and presenters/decorators; use concerns judiciously. Keep orchestration and cross-domain side effects out of ActiveRecord callbacks and put them in service objects.
- ActiveRecord: use named scopes; prevent N+1 with `includes`/`preload`/`eager_load` (catch regressions with the `bullet` gem); batch large reads with `find_each`/`in_batches`; wrap multi-step writes in a transaction. Push integrity to the database (NOT NULL, foreign-key + unique constraints, indexes on FKs and lookup columns), and keep migrations reversible and backward-compatible (expand/contract).
- Always use strong parameters; never interpolate untrusted input into SQL (use parameterized queries / Arel); run `brakeman` for static security analysis.
- Offload slow or external work to idempotent, retry-safe background jobs (ActiveJob/Sidekiq); apply caching (fragment / Russian-doll) where it measurably helps.
- Prefer a modular monolith with bounded domains — Rails **engines** or **packwerk** packages — and enforce the boundaries rather than letting domains bleed together.

Specs follow the RSpec standards (see `rspec.md`), and they come first: new behavior and bug fixes are driven by a failing test before the code that satisfies it. The `tdd` skill covers that cycle.
