# Driving out async and concurrent behavior

Async is where "watch it fail" quietly stops working. A test that finishes
before the work it started has neither passed nor failed — it just ended, and
the runner reports whichever answer the timing happened to produce that run.

Two different problems live here, and they have different answers:

- **Asynchrony** — the work completes later. Testable, once the test waits for
  the right thing.
- **Concurrency** — two things race. Not reliably testable by running them at
  once; test the guard instead.

## The failure that looks like a pass

```js
it("marks the booking confirmed", () => {
  confirmBooking(id)                        // returns a promise; nobody awaits it
  expect(store.get(id).status).toBe("confirmed")   // runs first
})
```

Red before the code exists, green after — the loop looks healthy. But it is
green because `status` was already `"confirmed"` from a previous test, or
because the assertion read a default. Delete the body of `confirmBooking` and
this test may well stay green. That is the whole problem: it never observed the
behavior.

**The check that catches it:** once green, break the production code on purpose
and confirm the test goes red. For async work, do this every time — the ordinary
red you watched proves the function is missing, not that the assertion is
reached.

## Wait for the work, never for the clock

`sleep(100)` is not a wait. It is a bet that the machine is fast today, and it
loses on CI. Every ecosystem gives you something better:

| Ecosystem | Wait for the work |
| --- | --- |
| Vitest / Jest | `await` the promise; `await vi.runAllTimersAsync()` / `jest.runAllTimers()` for scheduled work |
| Testing Library | `await screen.findBy…`, `await waitFor(() => …)` — never `getBy` straight after an action |
| RSpec + Capybara | The `have_content` / `have_selector` matchers already retry to `Capybara.default_max_wait_time`; `expect(page).to have_no_content` is the correct negative, not `expect(page).not_to have_content` |
| RSpec, background jobs | `perform_enqueued_jobs`, or assert the enqueue and test the job separately |
| ExUnit | `assert_receive` / `assert_received` with a timeout; `Task.await`; `async: false` for anything sharing state |
| pytest | `pytest-asyncio` and `await` the coroutine; `anyio` for the multi-backend case |
| Go | Block on the channel or `errgroup.Wait()`; give the test a `context.WithTimeout` so a hang fails instead of hanging |
| Rust | `#[tokio::test]` and `.await`; `tokio::time::timeout` to bound it |

**Fake the clock rather than passing it.** Behavior that depends on elapsed time
— an expiry, a retry backoff, a cutoff window — should take the clock as a
dependency or use the runner's time-travel helper (`vi.useFakeTimers`,
`ActiveSupport::Testing::TimeHelpers`, `freezegun`). A test that waits out a real
30-second window is a test nobody runs twice.

## Concurrency: test the guard, not the race

You cannot reliably drive out a race by starting two threads and hoping the
interleaving shows up. It passes ninety-nine runs in a hundred, and the hundredth
looks like flakiness rather than the bug it is.

Drive out the **invariant** instead. The race is prevented by something concrete
— a unique index, a row lock, an atomic update, a state-machine transition that
can only fire once — and that guard is ordinary, deterministic, testable
behavior:

1. **Red:** a test that performs the operation twice in sequence and asserts the
   second one is refused, or is a no-op. No threads.
2. **Green:** add the constraint. A database unique index, `SELECT … FOR UPDATE`,
   a conditional update that matches on the current state.
3. **Then** assert the failure path: the second attempt raises, or returns the
   already-created record, and the caller handles it. AGENTS.md §6, *Error
   handling, observability & reliability*, requires it be handled rather than
   swallowed.

Sequential double-execution is the honest test for these, because it is exactly
what a retried job or a double-submitted form does. That is the failure mode
behind overbooking, and it does not need a thread to reproduce.

**Idempotency has a test, and it is a boring one.** For any mutating endpoint or
background job: run it twice with the same input, assert one charge, one
booking, one email. It's the retry semantics of the whole system reduced to a
single deterministic case.

## Gotchas

- **A negative assertion after an async action is almost always wrong.**
  "Nothing appeared" is trivially true one millisecond in. Use the framework's
  waiting negative (`have_no_content`, `waitFor` on the positive of something
  else) or assert on a state that must settle first.
- **A test that only fails under load or in CI is telling you something real.**
  Quarantine it if you must, but record it as a suspected race rather than
  re-running until it goes green.
- **`async: true` on a test touching shared state is a race you added.** ExUnit
  and pytest-xdist both parallelize by default in places; opt out for anything
  sharing a database row, a global, or a fixture file.
- **Don't test the scheduler.** Asserting that a job was enqueued with the right
  arguments is one test; asserting what the job does is another, at the job's
  own layer. Combining them produces a slow test that proves neither.
