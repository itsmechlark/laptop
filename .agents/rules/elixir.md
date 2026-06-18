---
paths:
  - "**/*.ex"
  - "**/*.exs"
---

# Elixir standards

Operate at a staff-engineer level in this ecosystem: know the idioms, the canonical style guide, and the standard tooling, and prefer them over generic cross-language habits.

- Run `mix format`; follow the community Elixir Style Guide (`github.com/christopheradams/elixir_style_guide`); lint with Credo and add typespecs verified by Dialyzer.
- Think functionally: immutability, pattern matching, and pipelines (`|>`); use `with` for happy-path chaining; return and pattern-match tagged tuples (`{:ok, _}` / `{:error, _}`).
- Use OTP deliberately — GenServer/Supervisor/Task with supervision trees and a "let it crash" stance; don't spawn processes merely to organize code.
- Phoenix: bound domains behind **contexts**; reach for LiveView before custom JS where it fits.
- Ecto: validate through changesets, prevent N+1 with `preload`, and wrap multi-step writes in `Ecto.Multi`/transactions.
- Test with ExUnit (`async: true` when safe) plus property-based tests (StreamData); instrument with Telemetry.
- For *expected* errors use tagged tuples and `with`; reserve "let it crash" + supervision for the genuinely exceptional.
