---
name: rspec
description: Decide which kind of RSpec spec a behavior belongs in and how to shape it — model, request, system, service, mailer, or job — with the weight on service objects and command objects. Use when asked what kind of spec something should be, whether a behavior is a model spec or a request spec, how to test a service object, PORO, or command object, how to lay out the describe/context blocks for a class, or where a behavior sits in the testing pyramid in RSpec terms. Ruby and Rails with RSpec. Not for the order specs are written in, and not for deciding what to build or where a seam goes.
argument-hint: "[the class, service, or behavior to spec]"
---

# Shaping RSpec specs

Decide which RSpec spec type a behavior belongs in, and how to structure it — with the weight on service and command objects, which the model-versus-request split leaves out.

Two neighbors own the parts this skill defers to. The always-on style — group and example naming, `expect` syntax, `let` versus instance variables, Factory Bot, spec file paths — is settled by `rules/rspec.md`, which auto-loads on every spec file. The order a spec is written in — a failing example before the code that satisfies it — belongs to `tdd`. This skill decides the *shape and level*; it overrides neither.

## When to use this skill

- Deciding what kind of spec a behavior needs — "should this be a model spec or a request spec?"
- Writing specs for a service object, command object, or plain Ruby object whose home isn't obvious
- Laying out the `describe`/`context` structure for a class you're about to spec
- Placing a behavior in the testing pyramid in RSpec's own vocabulary
- Ruby and Rails, using RSpec
- Not for the order you write specs in — a failing example first — that's `tdd`
- Not for which test *level* a behavior needs in a language-agnostic sense (`rules/testing-levels.md`) or the discipline every level shares (`rules/testing.md`); both auto-load on spec files
- Not for deciding what to build or where a seam should go — that's `codebase-design`

## Choosing a spec type

Each RSpec spec type realizes one of the levels in `rules/testing-levels.md`. Pick the type by the level the behavior belongs at, not by the file that happens to reach it.

| Spec type | Covers | Level |
| --- | --- | --- |
| Model spec | Validations, scopes, and the business logic on a record — its own methods | Unit |
| Service / command / PORO spec | A service object's public call: the result it returns and the side effects it commits | Unit while it stays pure; Integration once it persists, enqueues, or coordinates real collaborators |
| Request spec | An HTTP endpoint through the stack — status, JSON or redirect, auth, params, the persisted effect | Integration |
| System spec | A user journey through the browser, JavaScript-dependent behavior, a multi-step form | End to end |
| Mailer / job / helper spec | The one unit's contract — the mail built, the work enqueued, the value returned | Unit, or Integration once it touches the database or a queue |

- **Default to the lowest spec type that can see the behavior.** A calculation on a record is a model spec; reaching it through a request spec does not discharge its own coverage — a higher-level test never does (`rules/testing-levels.md`).
- **Which spec type an HTTP API needs — request or system — is `rules/rspec.md`'s call.** Read the condition there rather than re-deriving it here.

## The testing pyramid, in RSpec

The pyramid itself — many fast unit specs at the base, fewer integration specs, a few end-to-end at the top — is stated in `rules/testing-levels.md` and `tdd`. What is RSpec-specific is where each spec type lands on it:

- **Base:** model specs and service/PORO specs. Fast, isolated, the bulk of the suite.
- **Middle:** request specs, roughly one per endpoint.
- **Tip:** a few system specs, on the journeys worth proving through a real browser.

So when a behavior could be proven at more than one level, push it down. A suite that is mostly system specs is slow and flaky and hides which layer broke; the fix is to move each behavior to the lowest spec that can still see it and keep system specs for the handful of genuine cross-boundary journeys.

## Service and command objects

The gap the model/request/system split leaves. A service object — a `Create…`, a `…Calculator`, anything exposing a single `call` or `perform` — has a contract of its own, and it earns its own spec.

- **Spec it through its public entry point**, asserting the outcome it owns: the value or result object it returns, and the side effects it commits — a record created, a mail enqueued, an event published. Never its private methods.
- **Let the level follow what it touches.** Pure computation with its collaborators doubled is a unit spec; once the object persists, enqueues, or orchestrates real collaborators, it is an integration spec against a real datastore, never a mocked one (`rules/testing.md`).
- **Assert the failure result, not only the success.** The guard that refuses, the failure result, the raised error — a service spec that exercises only the happy path documents half the contract (`rules/testing.md`).
- **For a result-object service, assert `success?`/`failure?` and the payload or errors** through the result, rather than reaching past it into internal state.
- **A service you must mock half the app to spec is a design signal, not a mocking problem.** The coupling is too tight — take it to `codebase-design` rather than reaching for a bigger double.

## Core shape

- **Organize by scenario.** A `context` per branch or precondition, and one behavior per example, so each spec type above reads as the set of cases it owns.
- **Arrange around the public interface:** set up only the world the scenario needs, act through the entry point, assert the outcome.

`describe`/`context` wording, example naming, and where shared setup lives are `rules/rspec.md`'s to settle — it auto-loads on every spec file, so this section stays on shape and leaves the phrasing to the cops.

## Gotchas

- **A service object still needs its own spec when a request spec already drives it.** The request spec proves the endpoint; it does not discharge the service's unit coverage (`rules/testing-levels.md`). This is the mistake the model/request split invites, and the reason this skill leans on the service section above.
- **This skill decides shape and level only.** The order comes from `tdd`; the style — naming, `expect` syntax, factories, file paths — comes from `rules/rspec.md`. When they speak, they win.

## Attribution

- [el-feo/ai-context](https://github.com/el-feo/ai-context/tree/main/plugins/ruby-rails/skills/rspec) - rspec, MIT
