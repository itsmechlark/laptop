---
paths:
  - "**/*.ex"
  - "**/*.exs"
---

# Elixir standards

Operate at a principal-engineer level in this ecosystem: prefer its idioms and standard tooling over generic cross-language habits.

- Format with `mix format`, lint with Credo, and add typespecs verified by Dialyzer. Where `mix format` is silent, the community [Elixir Style Guide](https://github.com/christopheradams/elixir_style_guide) settles it — don't hand-tune.
- **Use tagged tuples and `with` for *expected* errors**, and reserve "let it crash" plus supervision for the genuinely exceptional. A failure the caller is supposed to handle should not be reaching a supervisor.
- Use OTP deliberately — GenServer, Supervisor, and Task inside supervision trees. Don't spawn a process merely to organize code: a module boundary is free and a process is state, mailboxes, and a failure mode.
- Phoenix: bound domains behind **contexts**, and reach for LiveView before custom JavaScript where it fits.
- Ecto: validate through changesets, prevent N+1 with `preload`, and wrap multi-step writes in `Ecto.Multi` or a transaction.
- Run ExUnit with `async: true` wherever the test touches no shared global — it is the difference between a suite that scales across cores and one that doesn't. Reach for property-based tests (StreamData) where the input space is larger than the cases you can enumerate, and instrument with Telemetry.

Test discipline is in `testing.md` and `testing-levels.md`, which load on test files; new behavior and bug fixes come test-first, and the `tdd` skill covers that cycle.
