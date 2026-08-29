---
paths:
  - "**/Gemfile"
  - "**/Gemfile.lock"
  - "**/gems.rb"
  - "**/gems.locked"
  - "**/*.gemspec"
  - "**/gemfiles/*.gemfile"
  - "**/.ruby-version"
---

# Bundler and dependency standards

How a Ruby project declares, pins, and audits what it depends on. Authoring and releasing a gem is in `gem.md`; the language itself in `ruby.md`.

- Declare the Ruby version in the `Gemfile`, and keep it in step with `.ruby-version` and the versions CI runs.
- **Pin by how much a gem can hurt you**, not by habit:

  | Constraint | Use for |
  | --- | --- |
  | Exact — `gem "rails", "7.1.3"` | Fragile, deeply coupled gems where a patch release can break the app. Rails is the archetype |
  | Pessimistic — `gem "rspec", "~> 3.13"` | Gems that follow semantic versioning, so the major is the promise: `rspec`, `factory_bot`, `capybara` |
  | Versionless — `gem "pg"` | Gems that are safe to update often and whose breakage is immediate and obvious |

- Commit `Gemfile.lock`. It is the record of what actually ran, and the only thing that makes a build reproducible.
- Generate the project's binstubs (`bin/rake`, `bin/rspec`) and commit them, so a contributor or a CI step runs the locked version without remembering `bundle exec`.
- Audit dependencies with `bundler-audit` and keep versions current and CVE-free. A gem with a known advisory is a finding to surface, never something to introduce quietly.
- Group development and test dependencies so a production install pulls only what production runs.
- Adding a dependency is a decision, not a convenience: prefer the stdlib or a gem already in the bundle, and weigh maintenance, license, and CVE surface before adding another.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/ruby) - ruby, MIT
