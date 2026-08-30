---
paths:
  - "**/app/**/*.rb"
  - "**/app/**/*.erb"
  - "**/config/**/*.rb"
  - "**/config/locales/**/*.yml"
  - "**/db/**/*.rb"
  - "**/config.ru"
---

# Ruby on Rails standards

Application-wide Rails conventions, layered on the language standards in `ruby.md`. The globs are deliberately broad — a non-Rails Ruby project that happens to have an `app/` or `config/` directory should ignore this file. Layer-specific conventions load with the file being edited: `rails-model.md`, `rails-controller.md`, `rails-view.md`, and `rails-migration.md`.

- Embrace convention over configuration, and follow the [Rails Style Guide](https://rails.rubystyle.guide) through `rubocop-rails` rather than by hand.
- Keep controllers skinny and prevent god-object models — extract service objects, query objects, form objects, and presenters. Keep orchestration and cross-domain side effects out of ActiveRecord callbacks: a callback fires for every writer, including the ones that only wanted to touch a column.
- Put code that isn't app-specific — the kind that could plausibly be extracted into a gem later — in `lib` rather than `app`, and name an initializer after the gem it configures.
- Prefer a modular monolith with bounded domains — Rails **engines** or **packwerk** packages — and enforce the boundaries rather than letting domains bleed together.
- Read configuration with `ENV.fetch("KEY")`, never `ENV["KEY"]`, so a missing variable fails on deploy instead of silently becoming `nil` and reaching production as a subtly wrong default.
- Use `Time.current`, `Date.current`, and `Time.zone.parse` — never `Time.now`, `Date.today`, or `Time.parse`, which read the server's zone instead of the application's.
- Prefer `cookies.signed` over `cookies`, so a tampered value is rejected rather than trusted, and set `config.sandbox_by_default` in production-like environments so an unplanned console session can't write.
- Build queries with Arel or parameter binding, and run `brakeman` in CI — it catches the string-interpolated `where` that review misses.
- Offload slow or external work to background jobs, and make each one idempotent: Sidekiq redelivers, so a job that isn't safe to run twice will eventually run twice.
- Set the application up for multiple locales from the start, order translations alphabetically by key, and raise on a missing translation in development and test rather than shipping the key to a user.
- Design a JSON API against Heroku's [HTTP API Design Guide](https://github.com/interagent/http-api-design) before the first endpoint exists. The payload is a published contract once a consumer depends on it.

Specs follow `rspec.md`, which covers factories, time control, and the spec type that belongs on an API endpoint.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails) - rails, MIT
