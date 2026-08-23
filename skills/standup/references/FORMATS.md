# Update formats

Three skeletons live in `assets/`, ready to copy and fill. This file is the
judgment around them: which one, what changes per audience, and what a filled-in
one looks like when the news is good and when it isn't.

If the reader already has a format they use, match that instead. An established
format is a habit they read on autopilot; a new one spends attention that should
be going to the content.

Take the date from the environment (`date +%Y-%m-%d`), never from memory.

## Who's reading it

| Reader | Needs | Register |
| --- | --- | --- |
| Team | Dependencies, decisions, handoffs, what you're picking up | Terse; jargon is fine, they know the stack |
| Manager or lead | Progress against the commitment, and where you need a decision or help | Light jargon |
| Client | Outcomes and confidence, framed as timeline | No jargon — "background processing", not the queue library's name |

## Which skeleton

| Situation | Skeleton |
| --- | --- |
| Client or manager, written and asynchronous | [`assets/update-block.md`](../assets/update-block.md) |
| Team channel, written | [`assets/update-terse.md`](../assets/update-terse.md) |
| Team, spoken in a call | [`assets/update-spoken.txt`](../assets/update-spoken.txt) |

## Written block — client or manager

[`assets/update-block.md`](../assets/update-block.md) is the default for anyone
reading asynchronously and deciding something off the back of it.

For a **manager**, make "Heads up" specifically about where you need a decision
or help, and name the thing you need: "I need the staging credentials by
Wednesday or the integration slips" lands where "blocked on credentials" does
not.

For a **client**, keep every line in their vocabulary and frame risk as timeline
and confidence rather than internal mechanics. "Background processing" beats the
name of the queue library, every time.

Delete "Heads up" outright when there's nothing in it. A section kept alive with
filler teaches the reader to skip the one place real news will appear.

## Terse standup — team, written

[`assets/update-terse.md`](../assets/update-terse.md). A team channel wants less
ceremony than the block: three lines, because the reader is scanning six of
these in a row.

Jargon is fine here — name the service, the queue, the class. Dependencies and
handoffs are the whole point, since a teammate reads this to find out whether
their own day just changed.

## Spoken standup — team, live

[`assets/update-spoken.txt`](../assets/update-spoken.txt). Thirty seconds of
speech, so no headers, no bullets, no bold — three sentences the user can say
out loud. Two rules apply only to this form:

- **Put the blocker last and name the person.** It's the only line that needs
  someone to act, and in a call an ask has to land on a name, not on the room.
- **Say one thing per slot.** A spoken list of four items is a list nobody
  retains. Pick the one that matters; the rest come up if anyone asks.

## End of week

Same skeleton as the written block, three differences:

- **Summarize across days.** Nobody remembers Tuesday. Group by outcome rather
  than by day, and drop whatever Thursday superseded.
- **Say where the commitment stands.** A week is the unit a client or a manager
  tracks the plan in, so the update has to answer "are we on track" whether or
  not it was asked. Only the user can answer it.
- **A slipping date gets said here, or it gets said late.** The next checkpoint
  is a week away. If the honest answer is "we won't make it", that's a
  conversation first and a line in this update second.

## Worked example — an ordinary week

Client, end of week. Note what's absent: no commit list, no framework names, no
"continued working on".

```
**Update: 2026-08-21**

**Done:**

- Customers can reset their own password without emailing support. Live since
  Wednesday; 14 people have used it.
- Failed payments now retry automatically for three days before the booking is
  released.

**In progress:**

- Refunds. The partial-refund case is the fiddly one — I want the rounding
  right rather than fast, so this lands early next week rather than Friday.

**Up next:**

- Refunds, then the monthly statement export.

**Heads up:**

- The retry window is three days because that's what your payment provider
  allows on the current plan. If you want longer, that's a plan change on their
  side, not a code change on mine.
```

## Worked example — a thin day

The hard case, and the one worth studying. Nothing shipped, and the update still
has to be worth reading. Written plainly rather than dressed up, and it doesn't
pretend the day produced progress it didn't.

```
**Update: 2026-08-19**

**Done:**

- Nothing shipped today. I spent it tracking down why the imports were dropping
  about one row in every thousand.

**In progress:**

- Found it: rows with a comma inside a quoted address were being split in two.
  The fix is small; I'm writing the test that reproduces it before I change
  anything.

**Up next:**

- Land the fix tomorrow morning, then re-run the three imports that were
  affected.

**Heads up:**

- Roughly 40 rows from last week's imports are wrong in your data. I can correct
  them once the fix is in — I'd rather do that than have you find them.
```

Two things make it work: the bad news is the first line rather than buried under
something softer, and the last section turns the problem into an action with a
name on it. A reader who learns about those 40 rows from this update stays a
reader who trusts the next one.
