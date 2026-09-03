# What belongs in lore, and what belongs somewhere else

Lore is one lane among six artifacts that all describe the same work. The lane
is narrow on purpose: a note is worth reading only because it holds what none of
the others can.

## The one question

**What outlives the branch, is readable with no network, and is in nobody's
diff?**

That is lore. Each clause rules something out:

- *Outlives the branch* — a handoff summary dies with the session.
- *No network* — a PR description lives on GitHub; an agent working from a
  checkout cannot read it.
- *In nobody's diff* — the change itself is already recorded, in the diff.

## The overlap map

| Artifact | Owns | Written by | The failure when lore duplicates it |
| --- | --- | --- | --- |
| Commit message | Why this atomic change, at diff granularity | `git-commit` | The note becomes a changelog of commits already in `git log` |
| PR description | What changed, how, testing, risks, rollout | `pull-request` | The note becomes the PR body in a file — the most common failure by volume |
| ADR | A hard-to-reverse decision the codebase must live with | `domain-modeling` | The decision rots in a dated file nobody looks at, instead of a numbered trail |
| Path-scoped rule | A convention every future edit must follow | `agent-rules` | A lesson that should load automatically instead waits to be found |
| Handoff summary | The next session's starting context | `claude-handoff` | The note is full of "remaining work" that is done by the time anyone reads it |
| Status update | What a person needs to know this week | `standup` | The note reads as progress reporting, which expires in days |

## The four things that are only lore's

### 1. Mechanism in code nobody here wrote

A dependency or framework behaving in a way the docs do not lead you to. It
appears in no diff, because nothing about it was authored — it was discovered.
This is the highest-value thing a lore directory holds.

Three shapes it takes, each of the kind that costs an afternoon to establish and
five seconds to read:

- **A default that is persisted, not computed.** An ORM applies a field's code
  default when loading a record and marks it dirty, so the next save writes it
  down. Changing the default in code then never reaches records that already
  exist, and the rollout needs a data migration rather than the one-line change
  everyone expects.
- **A hook that runs on the wrong side of validation.** A library rebuilds a
  value in a before-save callback, after validation has already passed. The
  record persists in a shape its own format validation rejects, and no error is
  raised anywhere.
- **A knob that is silently inert on one platform.** An environment variable
  that selects an allocator is ignored outside Linux, so a memory benchmark run
  locally measured something other than what production runs — and the
  conclusion drawn from it nearly reversed a correct decision.

### 2. The alternative that was rejected

A diff shows what was built. It never shows the three approaches tried first, or
which constraint killed each one. Without the note, the next person re-litigates
a settled question — or worse, re-implements the approach that already failed.

Record the constraint, not the preference: "the batched-publisher approach lost
because the read path needs read-your-writes inside the same request" is
reusable by anyone who meets that constraint again. "We chose the synchronous
approach" is not.

### 3. Reviewed and deliberately not changed

The genuinely invisible category. Code that was examined, understood, and left
alone leaves no artifact whatsoever — no diff, no commit, no PR line. The next
reviewer finds the same smell and either re-investigates it from scratch or
"fixes" it and breaks something.

Harden passes produce more of this than of anything else, which makes their
notes worth writing even when no code changed.

### 4. The cross-PR arc

A four-PR migration has four PR descriptions and no document that says why PR 1
duplicated a constant it knew was duplicated, or that PR 4 is where the
duplication goes away. The arc is held together by the `topic` field and the
`supersedes` chain, and by nothing else.

## Two boundaries worth stating precisely

**Lore or ADR?** Apply all three ADR tests — hard to reverse, surprising without
context, the result of a real trade-off. All three hold, it is an ADR and gets a
permanent number. Any one missing, it is lore. A decision that is easy to
reverse does not deserve a number, and a number is spent permanently.

**Lore or PR description?** If a reviewer needs it to approve the change, it is
the PR's. If a stranger needs it six months later to avoid breaking something,
it is lore's. Testing evidence, behavior-change tables and rollout steps are
always the PR's — they are consumed at review time and never again.
