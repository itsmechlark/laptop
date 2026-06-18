---
paths:
  - "**/*.rb"
  - "**/Gemfile"
  - "**/*.rake"
  - "**/*.gemspec"
---

# Ruby & Rails standards

Operate at a staff-engineer level in this ecosystem: know the idioms, the canonical style guide, and the standard tooling, and prefer them over generic cross-language habits.

## Ruby
- Follow the [Ruby Style Guide](https://rubystyle.guide); enforce with RuboCop.
- Write expressive, idiomatic Ruby: prefer `Enumerable` methods (`map`, `each_with_object`, `reduce`) over manual loops; use blocks and `&:sym`.
- Favor small Plain Old Ruby Objects (POROs) and composition over inheritance; use duck typing and modules/mixins deliberately.
- Use keyword arguments for clarity; freeze constants; prefer immutable data where practical.
- Rescue specific exceptions — never a bare `rescue` or broad `rescue StandardError`; fail fast with clear, typed errors.
- Audit dependencies with `bundler-audit`; keep `Gemfile.lock` committed and gem versions current and CVE-free.

## Ruby on Rails
- Embrace convention over configuration; follow the [Rails Style Guide](https://rails.rubystyle.guide).
- Keep controllers skinny and prevent god-object models — extract service objects, query objects, form objects, and presenters/decorators; use concerns judiciously.
- ActiveRecord: use named scopes; prevent N+1 with `includes`/`preload`/`eager_load` (catch regressions with the `bullet` gem); push integrity to the database (NOT NULL, foreign-key + unique constraints, indexes on FKs and lookup columns); keep migrations reversible.
- Always use strong parameters; never interpolate untrusted input into SQL (use parameterized queries / Arel); run `brakeman` for static security analysis.
- Offload slow or external work to background jobs (ActiveJob/Sidekiq); apply caching (fragment / Russian-doll) where it measurably helps.
- Prefer a modular monolith built from Rails **engines** (the `engines/` folder) to keep domains bounded.

Specs follow the RSpec standards (see `rspec.md`).
