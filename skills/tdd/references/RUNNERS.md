# Finding the runner, and running one test

The cycle runs a single test after every change. That makes the *single-test*
invocation the command you need — not the suite command, which is only used once,
for the baseline. This file covers how to find both, and how to tell a genuine
red from a broken test in each ecosystem.

## Discover, don't guess

A wrong guess usually still works — it just runs the whole suite every time. The
loop gets slow, and a slow loop is one you stop running. Look, in this order:

1. **The project's test config.** `spec/spec_helper.rb`, `vitest.config.*`,
   `jest.config.*`, `pytest.ini` / `pyproject.toml`, `test/test_helper.exs`,
   `testem.js`.
2. **The CI workflow.** `.github/workflows/*.yml` runs the suite the way the
   project's maintainers actually run it, wrapper script and all
   (`bin/rails test`, `bundle exec`, `pnpm test`).
3. **The manifest.** `package.json` scripts, `Gemfile`, `mix.exs`,
   `Cargo.toml`, `go.mod`.
4. **The repo's own instructions.** `AGENTS.md` or `CLAUDE.md` at the root often
   names the command outright.

If the project wraps its runner (`bin/test`, `make test`, `just test`), use the
wrapper — it carries environment setup you would otherwise reproduce by hand.

## Single-test invocations

Substitute the project's own prefix (`bundle exec`, `npx`, `pnpm`, `bin/`).

<!-- cspell:ignore Itest Errorf Fatalf -- Ruby's closed-up -I load-path flag, and two Go testing.T methods -->

| Ecosystem | One file | One example |
| --- | --- | --- |
| RSpec | `rspec spec/models/order_spec.rb` | `rspec spec/models/order_spec.rb:42` |
| Rails / Minitest | `bin/rails test test/models/order_test.rb` | `bin/rails test test/models/order_test.rb:42` |
| Plain Minitest | `ruby -Itest test/order_test.rb` | `ruby -Itest test/order_test.rb -n /refunds/` |
| Vitest | `vitest run src/order.test.ts` | `vitest run src/order.test.ts -t "refunds a deposit"` |
| Jest | `jest src/order.test.ts` | `jest src/order.test.ts -t "refunds a deposit"` |
| Ember / QUnit | `ember test --module "Unit \| order"` | `ember test --filter "refunds a deposit"` |
| ExUnit | `mix test test/order_test.exs` | `mix test test/order_test.exs:42` |
| pytest | `pytest tests/test_order.py` | `pytest tests/test_order.py::TestOrder::test_refunds` |
| Go | `go test ./order` | `go test ./order -run '^TestRefundsDeposit$'` |
| Rust | `cargo test --test order` | `cargo test refunds_deposit -- --exact` |

Two flags worth knowing wherever they exist: **fail-fast** (`--fail-fast`,
`--bail`, `-x`, `-failfast`) keeps a long suite from burying the one failure you
care about, and **seed/order** flags matter when a test passes alone but fails in
the suite — see [Troubleshooting](#when-the-run-disagrees-with-itself).

## Is this a red, or a broken test?

A red is defined by its *cause*, not by whether an exception was involved. The
run has to fail because the behavior you're driving out is missing. That shows
up two ways, and both are legitimate:

- **Assertion failure** — the code ran and gave the wrong answer.
- **"Not there yet"** — the method, class, route, or module you are about to
  build doesn't exist yet, so the runner blows up naming it. Outside-in, this is
  the ordinary red at every structural layer.

Anything else that stops the test is a **broken test**: a typo, a missing
import, a bad fixture, a stale path, a compile error in code you already wrote.
It proves nothing — fix it and run again.

The one question that settles it: **does the message name the thing you're
about to build?**

| Ecosystem | Assertion failure | "Not there yet" | Broken test |
| --- | --- | --- | --- |
| RSpec | `expected … got …`, `ExpectationNotMetError` | `NoMethodError: undefined method 'search'`, `NameError: uninitialized constant Order`, `ActionController::RoutingError` | `LoadError` on a require, a misspelled matcher, a factory or fixture blowing up in `before` |
| Minitest | `F`, counted under `failures` | `E` naming the constant or method you're adding | `E` naming anything else |
| Vitest / Jest | The `expect(received)` diff block | `ReferenceError: search is not defined`, `TypeError: x.search is not a function` | Module resolution or transform failure, an error thrown in `beforeEach` |
| QUnit | `Expected: / Result:` on a named assertion | `Died on test #N` naming the missing import or helper | `Died on test #N` for anything else |
| ExUnit | `Assertion with == failed`, `left:` / `right:` | `UndefinedFunctionError`, or a compile error naming the function you're adding | Any other compile error, a failing `setup` |
| pytest | The `assert` introspection block under `FAILED` | `AttributeError` / `ImportError` naming the target | Collection and fixture errors — counted under `errors`, not `failed` |
| Go | `t.Errorf` / `t.Fatalf` output | `undefined: RefundsDeposit` in the build failure | Any other build failure, or a panic from unrelated code |
| Rust | ``assertion `left == right` failed`` | `E0425 cannot find function`, `E0433 failed to resolve` | Any other compile error, or an unrelated panic |

**Go and Rust get two reds, not one.** A test can't run until it compiles, so
the first red is the compile error naming the function that doesn't exist. Add
the minimal signature — enough to compile, returning a zero value or
`todo!()` — and the second red is the assertion failing properly. Both are real;
skipping straight to a working implementation skips the assertion red, which is
the one that proves the test can fail.

## When the run disagrees with itself

- **Passes alone, fails in the suite** — order-dependence or shared state, not
  your change. Re-run with the seed the suite reported to reproduce it, then fix
  the leak (a global, a class-level cache, an unrolled-back record). Don't build
  on a green you only get in isolation.
- **Fails alone, passes in the suite** — something earlier in the suite is
  setting up state your test depends on. Your test is under-specified; give it
  its own setup.
- **Green on the first run of a brand-new test** — the behavior already exists,
  or the test isn't reaching the code. Break the production code deliberately and
  confirm the test notices before you trust it.

## Conventions on top of the workflow

This payload ships path-scoped rules that auto-load for the files you're about
to write. They cover how a test should *read*; this skill covers the order it
gets written in.

| Writing | Auto-loads |
| --- | --- |
| `**/*_spec.rb`, `**/spec/**/*.rb` | `rules/rspec.md` — naming, structure, factories, matchers, mocking at the boundary |
| `**/*.rb`, `**/Gemfile`, `**/*.rake` | `rules/ruby.md` |
| `**/*.ts`, `**/*.tsx` | `rules/react-typescript.md` |
| `**/*.js`, `**/*.hbs` | `rules/ember.md` — deliberately broad; ignore it when the file isn't part of an Ember app |
| `**/*.ex`, `**/*.exs` | `rules/elixir.md` |

They load without being asked. Nothing here needs to be invoked — this table
exists so you know which conventions are already in force while you write the
test.
