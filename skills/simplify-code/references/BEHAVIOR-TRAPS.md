# Rewrites that look equivalent and aren't

Each entry is a simplification that reads like a pure refactor and changes behavior on some input. Before making one, find the input that separates the two forms, and confirm it can't reach this code or that a test pins it. If you can't confirm either, leave the original alone.

## Any language

- **Reordering conditions.** `a && b` and `b && a` differ when either side has a side effect, raises, or is expensive. Guard clauses carry the same risk: moving an early return above a check that used to run first changes which error a caller sees.
- **Dropping a "redundant" guard.** A nil check, a bounds check, or a `rescue` that looks unreachable from the code in front of you may be reachable from a caller you didn't read. Grep the callers before deleting it.
- **Merging two branches that do "the same thing".** They often differ in one argument, one log line, or one side effect. Diff them character by character first.
- **Hoisting a computation out of a loop or branch.** It now runs when it didn't before, or once instead of every iteration. That matters when it is impure, slow, or can fail.
- **Replacing a hand-written loop with a library call.** Early exit, mutation of the accumulator, and iteration order may all differ.
- **Changing an error message or class.** Callers, tests, log alerts, and API clients match on them.
- **Eager versus lazy.** Turning a lazy enumeration, a generator, or a stream into a list (or the reverse) changes when work happens, how much memory it takes, and whether an infinite source terminates.

## Efficiency rewrites

- **Sequential to concurrent.** `Promise.all`, a thread pool, or `Task.async_stream` changes the order side effects happen in, and how a failure lands: `Promise.all` rejects on the first error while the other calls keep running. Concurrent writes can also exhaust a connection pool, trip a rate limit, or race on shared state the sequential version never contended for.
- **Caching or memoizing.** A cached value goes stale when its inputs change, and a cache with a wider scope than the old computation (process-wide instead of per-request) leaks one tenant's or user's data into another's.
- **Batching queries.** Eager-loading or collapsing a per-item query into one can change the records returned when the association has scopes, default ordering, or conditions, and loading everything at once can trade an N+1 for an out-of-memory error.
- **Moving work off startup.** Lazy initialization moves a configuration error from boot, where it fails the deploy, to the first request, where a user sees it.

## JavaScript and TypeScript

- **`||` versus `??`.** `x || fallback` replaces `0`, `''`, `false`, and `NaN`; `x ?? fallback` replaces only `null` and `undefined`. Either swap changes behavior for exactly those values.
- **`if (x)` versus `if (x != null)`.** The same split: the first rejects every falsy value, the second only null and undefined.
- **`==` versus `===`.** `x == null` deliberately matches both `null` and `undefined`. "Fixing" it to `=== null` drops `undefined`.
- **`function` versus arrow function.** Arrows have no own `this`, `arguments`, or `prototype`, and can't be used with `new`. A method passed as a callback or a function used as a constructor breaks.
- **`forEach` versus `for…of` versus `map`.** `forEach` ignores a returned promise, so `await` inside it doesn't wait. `map` allocates and returns an array. A `return` in `forEach` is a `continue`, not an exit.
- **Destructuring with defaults.** A default fires only on `undefined`, not `null`. `const { a = 1 } = obj` and `const a = obj.a ?? 1` differ when `a` is `null`.
- **Spreading versus mutating.** `{ ...obj, k }` creates a new object, and anything holding a reference to the old one no longer sees updates. Turning `Object.assign(target, …)` into a spread breaks callers that relied on `target` changing.
- **Optional chaining.** `a?.b.c` short-circuits the whole chain on a nullish `a`. Adding `?.` where the code used to throw turns a loud failure into a silent `undefined`.
- **Removing a type assertion or a non-null `!`.** The runtime is the same, but the narrowed type may have been hiding a real `undefined` the compiler will now flag. Treat a new type error as information, not friction.

## Ruby and Rails

- **`present?`/`blank?` versus truthiness.** `""`, `" "`, `[]`, and `{}` are truthy but blank. `if x` and `if x.present?` disagree on all of them.
- **`any?` versus `!empty?`.** On an Array, `any?` without a block is false for `[nil, false]` while `empty?` only checks size, so the two disagree on a collection of falsy values. On an ActiveRecord relation `any?` is `!empty?`, and both run the same `SELECT 1 … LIMIT 1` when unloaded. The costly swaps there are toward `present?`/`blank?`, which load every record, and `size`, which runs a `COUNT` unless the relation is loaded.
- **`each` versus `map`.** `each` returns the receiver, `map` returns a new array. Swapping them changes the return value of the method if it was the last expression.
- **`&.` versus `try`.** `nil&.foo` is `nil`, but `obj&.foo` still raises `NoMethodError` if `obj` doesn't respond to `foo`. `try(:foo)` swallows that. Replacing one with the other changes which errors escape.
- **`and`/`or` versus `&&`/`||`.** Their precedence is lower than `=`. `x = a or b` assigns `a`, then evaluates `b`.
- **`find_by` versus `find`.** `find_by` returns `nil`, `find` raises `RecordNotFound`. A controller that relied on the raise for a 404 starts rendering with `nil`.
- **`update` versus `update_column(s)`.** The column forms skip validations, callbacks, and `updated_at`. `save` versus `save!` is the same split for errors.
- **Memoization with `||=`.** `@x ||= compute` recomputes every call when the result is `false` or `nil`. Turning a `defined?(@x)` guard into `||=` changes how many times `compute` runs.
- **Implicit return.** Extracting the last line into a helper, or adding a log line after it, changes what the method returns.
- **Keyword versus positional arguments.** Changing a signature from one to the other breaks every caller, including ones built with `send` or `public_send` that grep won't find by method name alone.

## Elixir

- **`if`/`unless` versus `case`/pattern matching.** `if` treats only `nil` and `false` as falsy; a `case` on `{:ok, _}` raises `CaseClauseError` on anything unmatched. Collapsing a `case` into `if` swallows the shapes the clauses used to reject.
- **`with` and its `else`.** Removing an `else` clause makes the unmatched value fall through as the return value instead of being handled. Adding one that is not exhaustive raises `WithClauseError`.
- **`Enum` versus `Stream`.** `Stream` is lazy. Replacing one with the other changes when side effects in the pipeline run, and whether they run at all.
- **Pipelines and argument order.** Folding a nested call into `|>` pipes into the *first* argument. For a function whose subject is not the first parameter, the arguments land in the wrong slots: a runtime error at best, a wrong result at worst.
- **`=` versus `==`.** A `=` in a function body is a match that raises `MatchError` on mismatch. Turning it into an `==` check turns an assertion into a boolean nobody reads.
- **Bang functions.** `File.read!` raises; `File.read` returns `{:error, reason}`. Swapping them moves error handling from the supervisor to the caller, or the reverse.
