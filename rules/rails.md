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

Application-wide Rails conventions, layered on the language standards in `ruby.md`. The globs are deliberately broad — a non-Rails Ruby project that happens to have an `app/` or `config/` directory should ignore this file.

Layer-specific conventions load with the file being edited: `rails-model.md`, `rails-controller.md`, `rails-view.md`, and `rails-migration.md`.

- Embrace convention over configuration; follow the [Rails Style Guide](https://rails.rubystyle.guide).
- Keep controllers skinny and prevent god-object models — extract service objects, query objects, form objects, and presenters/decorators; use concerns judiciously. Keep orchestration and cross-domain side effects out of ActiveRecord callbacks and put them in service objects.
- Put code that isn't app-specific — the kind that could plausibly be extracted into a gem later — in `lib` rather than `app`, and name an initializer after the gem it configures.
- Offload slow or external work to idempotent, retry-safe background jobs (ActiveJob/Sidekiq); apply caching (fragment / Russian-doll) where it measurably helps.
- Prefer a modular monolith with bounded domains — Rails **engines** or **packwerk** packages — and enforce the boundaries rather than letting domains bleed together.
- Always use strong parameters; never interpolate untrusted input into SQL (use parameterized queries or Arel); run `brakeman` for static security analysis.
- Read configuration with `ENV.fetch("KEY")`, never `ENV["KEY"]`, so a missing variable fails on deploy instead of silently becoming `nil`.
- Prefer `cookies.signed` over `cookies`, so a tampered value is rejected rather than trusted, and set `config.sandbox_by_default` in production-like environments so an unplanned console session can't write.
- Use `Time.current`, `Date.current`, and `Time.zone.parse` — never `Time.now`, `Date.today`, or `Time.parse`, which read the server's zone instead of the application's.
- Set the application up for multiple locales from the start, order translations alphabetically by key, and raise on a missing translation in development and test rather than shipping the key to a user.
- Design a JSON API against the practices in Heroku's [HTTP API Design Guide](https://github.com/interagent/http-api-design) before the first endpoint exists. The payload is a published contract once a consumer depends on it: change it additively, and version it when you must break it.

Specs follow `rspec.md`, which covers factories, time control, and the spec type that belongs on an API endpoint.

Adapted from thoughtbot's [Rails guide](https://github.com/thoughtbot/guides/tree/main/rails) (MIT).
