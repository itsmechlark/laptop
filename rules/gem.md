---
paths:
  - "**/*.gemspec"
  - "**/Appraisals"
  - "**/lib/**/version.rb"
---

# Ruby gem authoring standards

For a project that *is* a gem. Pinning dependencies in an application is in `bundler.md`; the language itself in `ruby.md`.

- The `.gemspec` is the single source of dependency truth. Declare runtime and development dependencies there, and have the `Gemfile` say `gemspec` rather than restating them.
- Test against the versions the gem claims to support: [Appraisal](https://github.com/thoughtbot/appraisal) for a matrix of dependency versions, and CI across every supported Ruby. A support claim nobody exercises is a claim that breaks in someone else's build.
- A gem's public API is a published contract the moment it is released. Keep the surface narrow, follow semantic versioning, and pair any removal with a deprecation warning and a release that carries it.
- Never monkey-patch from a library. A gem that reopens its consumers' classes makes their bugs yours, and the breakage surfaces in their code, not the gem's.
- **Release in this order every time:** bump the version constant → `bundle install` so the lockfile follows → run the full suite → update `CHANGELOG`/`NEWS`/`README` if the change is user-facing → commit with the version as the message (`v2.1.0`) → `rake release`, which tags, pushes the tag, and pushes the gem. Getting `rake release` ahead of the lockfile or the changelog ships a version whose own repository disagrees with it.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/ruby) - ruby, MIT
- [thoughtbot/guides](https://github.com/thoughtbot/guides/blob/main/ruby/how-to/release_a_ruby_gem.md) - release a Ruby gem, MIT
