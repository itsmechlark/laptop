# Surveying the queue

Answering "what needs my attention?" — the survey entry point. Present the
buckets below, each oldest-first, with counts and a one-line summary per item,
then let the maintainer pick. The survey decides nothing on its own.

## The five buckets

1. **Untriaged** — no category or state role. Never evaluated.
2. **`needs-triage`** — evaluation started, not finished.
3. **`needs-info`, reporter has replied** — activity since the last triage note.
   Unblocked; needs another look.
4. **Stalled** — `needs-info` with no reporter activity since the triage note,
   past the staleness threshold.
5. **Aging `ready-for-agent`** — briefed but unclaimed past the same threshold.

Buckets 3 and 4 partition the same state, and bucket 4 is the one that only
exists because someone drew it. Without it, an item nobody ever answered leaves
the queue forever: it is not untriaged, not `needs-triage`, and has no activity,
so it appears in no bucket while still counting as open. That is how a
`needs-info` queue becomes a graveyard nobody notices.

Bucket 5 exists for the opposite reason: those items look *finished*. A brief
describes behavior rather than file paths precisely so it survives a moving
codebase ([AGENT-BRIEF.md](AGENT-BRIEF.md)), but survival has a limit — the
interfaces it names get renamed, the repro branch goes stale against `main`, and
the impact it claims may have been overtaken. Surfacing an aging one asks a
narrow question, not "re-triage this": **does the brief still describe work worth
doing, in words that still match the code?** If yes it keeps its state and the
clock resets. If no, it goes back to `needs-triage` with a note saying what
drifted — never silently, because a brief nobody can trust is worse than an
untriaged item that nobody has promised anything about.

## Stalling is a decision, never a default

**Never close a stalled item automatically.** Reaching the threshold makes an
item *visible*, not resolved — surface it and let the maintainer choose:

- **Ping** — a follow-up comment on the open questions. Resets the clock.
- **Close as stale** — a close like any other, so it needs explicit approval
  (the draft-show-then-ask rule in the skill body applies unchanged).
- **Decide without the reporter** — sometimes the open question is answerable
  from the codebase or the maintainer's own knowledge. Then it moves on to
  `ready-for-agent`, `ready-for-human`, `resolved-elsewhere`, or `wontfix` on
  its merits, and the
  triage notes record that the answer came from us rather than the reporter.

**Any reporter comment resets the clock**, including one that doesn't answer the
question. Someone still engaged is not stalled.

The threshold is a project convention, not a fact about the tracker. **14 days is
a reasonable default; confirm it once with the maintainer and reuse it.** Slow
open-source queues run longer, an internal team's runs shorter. If a project
records the number anywhere — a contributing guide, a stale-bot config — that
number wins over the default.

## PRs in the queue

When PRs are in scope, include them and tag each line `[PR]` or `[issue]`.

Discovery surfaces **external** PRs only — a colleague's in-flight PR is review
work, not triage work. The filter is discovery-only: an explicitly named PR is
always triaged, whoever wrote it.

## Ordering

Within a bucket, oldest-first. It is the one ordering that needs no judgment and
does not quietly bury anything.

"What's ready for agents?" is the exception — that list is ordered by impact,
read from the `Impact` line each agent brief carries as reach · frequency · cost
([AGENT-BRIEF.md](AGENT-BRIEF.md)). Compare the parts rather than the sentence,
and where two genuinely tie, say they tie instead of inventing a tiebreak. A
`ready-for-agent` item whose brief has no `Impact` line sorts last and is worth
flagging: the brief is incomplete.

Untriaged items have no impact assessment yet, by definition. Don't invent one to
sort them — that is the triage the bucket is asking for.

## Large queues

When the queue has many independent items, use `fan-out` to dispatch one agent
per item, then present the collected results as the buckets above.

Independent is the operative word. Items that are plausible duplicates of each
other belong in one agent's hands — separate agents each see one side of a
duplicate pair and neither can spot it.
