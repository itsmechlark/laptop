# The two reports

Both are handovers, not status updates: each ends with a question and waits.
The verification report is produced at step 4, before any code is touched; the
response report at step 6, after the fixes are proven and before anything is
published. They share one numbering so the pair reads as a single thread of
work.

The worked examples below are one PR carried through both.

## Verification report

The table carries only the threads that need action. Every other thread is
accounted for underneath it, so the counts reconcile and nothing looks
forgotten.

```markdown
## Review verification — 10 threads on #412, 5 need action

| # | Item | State / class | Verification outcome | Proposed action |
| --- | --- | --- | --- | --- |
| 1 | `2071…` orders.rb:40 — retry belongs in the caller | change requested | Doesn't hold — the caller can't classify which failures are retryable | Push back |
| 2 | `2072…` client.rb:12 — drop the legacy branch | blocking | Confirmed — build target is 10.15, that API needs 13+ | Fix (keep legacy, correct the bundle id) |
| 3 | `2073…` sync.rb:88 — "make the webhook check stricter" | unclear | — | Ask: constant-time compare, or reject missing timestamps? |
| 4 | `2074…` metrics.rb:5 — implement filters and export | non-blocking (@bob approved) | No callers — `grep` finds none | Propose deletion (YAGNI) |
| 5 | `2075…` job.rb:22 — races under concurrent retries | reopened · change requested | Can't verify here — needs a prod-like dataset | Ask for direction |

**Held:** 3 gates 1 — the answer changes whether the retry moves at all.

**Awaiting reviewer (no action):** 6 `2076…` cache.rb:14, 7 `2077…` README:8 — you replied on both, nothing back since. Listed so they aren't forgotten.

**Settled by approval:** 8 `2078…`, 9 `2079…` — @bob approved after your replies. Eligible to resolve at step 6.

**Already resolved:** 10 `2080…`, closed by @alice. Skipped.

@bob's review was an approval with suggestions, so 4 is a suggestion rather than a gate.
```

Close with the question: post the questions and pushback now, and start on which
fixes?

**When nothing needs action, that is the report.** A review where every thread
is resolved, accepted, or awaiting the reviewer is a finished review. Say so,
list what's outstanding on their side, and stop — don't manufacture work to fill
the table.

## Response report

Same numbering as above. Only the items that were actually worked appear in the
table; the rest are accounted for in the lines below it.

```markdown
## Review response — 3 of the 5 actionable items

| # | Review item | Fix implemented | Draft reply |
| --- | --- | --- | --- |
| 1 | orders.rb:40 — retry belongs in the caller | None — pushed back | see below |
| 2 | client.rb:12 — drop the legacy branch | Kept the 10.15 path, corrected the bundle id to `com.acme.sync` | "Checked — build target is 10.15 and that API needs 13+, so the legacy path stays. You were right about the bundle id though, fixed." |
| 4 | metrics.rb:5 — implement filters and export | Endpoint and its route deleted | "Grepped for callers and nothing hits this. Deleted rather than built out — shout if there's usage I'm missing." |

**1, in full:** "Checked this — the caller can't tell which failures are retryable, so moving the retry there means retrying auth errors too. Keeping it in the adapter. Happy to expose a predicate if you want the caller to decide."

**Verified:** `rspec spec/models spec/requests` green, RuboCop clean. 5 unverified — no prod-like dataset here, and the reply says so.

**Not done:** 3 and 5 are questions waiting on the reviewer. 6 and 7 still awaiting a response to earlier replies.

**Eligible to resolve:** 8 and 9 — @bob approved after those replies landed. Nothing else is; the rest are unanswered or were pushed back on.
```

Keep the reply in the cell when it's a sentence or two; when it's longer, put
"see below" in the cell and the full text under the table. A table cell with a
paragraph in it is unreadable, and the reply is the part the user is actually
checking.

Close with the one question: commit, push, post these replies, and resolve the
eligible threads?

## What each report has to carry

If you write these from memory, these are the parts that matter — the exact
layout is less important than the reconciliation.

| Report | Must carry |
| --- | --- |
| Verification | every actionable item with its verification outcome and your proposed action; every non-actionable thread accounted for by state; anything held pending an answer; the closing question |
| Response | every item worked, the fix that landed, the draft reply; what was verified and what couldn't be; what's still outstanding and on whom; which threads are eligible to resolve; the closing question |

The reconciliation is the point. A report whose numbers don't add up to the
thread count is how an item gets dropped.

<!-- cspell:words pushback RuboCop -->

