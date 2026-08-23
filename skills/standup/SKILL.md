---
name: standup
description: Write a standup or status update for a team, manager, or client — turn a stretch of work into what's done, what's next, and the risks worth flagging before they become surprises. Use when asked to write a standup, a daily or weekly update, an end-of-day or end-of-week summary, a progress report for a client or a manager, or "what do I say about this at standup?". Drafts the text for the user to send; not for posting it anywhere, and not for a PR description, a commit message, or a ticket comment.
argument-hint: "[audience and cadence — e.g. 'client, end of week']"
disable-model-invocation: true
---

# Standup updates

Turn a day's or a week's work into a short update the reader can act on, with the uncomfortable parts said plainly rather than softened.

Audience and cadence: `$ARGUMENTS`. If nothing came with the invocation, [Step 1](#1-fix-the-audience-and-the-cadence) settles both before anything else.

**This is a conversation, not a generator.** Git shows what was committed. The update turns on what the user knows and hasn't said yet — so ask, wait for the answer, then write.

**You draft; they send.** This produces text a human reviews and sends under their own name. Never post it to a channel, message it, email it, or attach it to a ticket ([Gotchas](#gotchas)). The one write this skill does make is [the private journal](#6-file-it-for-tomorrow), which goes nowhere near the reader.

**It goes out in their voice, not yours.** Build the update out of the words they used in the conversation. A client who can tell their contractor's update was generated has learned something you didn't mean to tell them.

## When to use this skill

- Writing the daily standup, spoken in a call or posted in a channel
- An end-of-day, start-of-day, or end-of-week update for a client, manager, or team
- "What do I say about this at standup?" when part of the stretch went badly
- A progress report after a week where the plan changed
- Not for the artifacts with their own audience and format: a commit message, a PR description, a tracker comment
- Not for deciding what to do next, or for re-planning work that slipped — this reports, it doesn't replan
- Not for a retro, a performance review, or a client proposal

Two skills take over when the sharpening in Step 3 turns up something bigger than an update: invoke `slice` to re-cut a plan whose remaining scope no longer fits, or `grilling` to pressure-test a plan the user has stopped believing in.

For the tracker items an update mentions, `triage` works them — and `feature-dev` runs the build the next update will report on. Both are user-invoke-only, so the Skill tool refuses them: route there by reading and following the target's `SKILL.md`, or by telling the user to invoke it themselves.

## Workflows

Run this as a conversation, and wait for each answer before moving on.

### 1. Fix the audience and the cadence

These two decide the format, the bluntness, and the jargon. Take them from the invocation or from the user's own words.

Read the audience off the words they used: "standup" on its own means the team, "the client" or "our weekly update" means external, "my manager" or "my lead" means upward. Ask only when the words genuinely don't say: **"Who's reading this — your team, your manager, or the client?"** Don't guess silently — what each reader needs, and how much jargon they'll tolerate, is in [FORMATS.md](references/FORMATS.md).

Then the cadence, which is two questions: how long a stretch, and spoken or written.

- **End of day** reports one day. **Start of day** is the same material aimed forward — what you're picking up, not what you finished.
- **End of week** summarizes across days, drops the detail nobody remembers by Friday, and is where a slipping date has to be said out loud: the next checkpoint is a week away.
- **Spoken** standups are thirty seconds of speech. Deliver three sentences the user can say, not a formatted block with headers.

Templates for each combination, including the spoken form: [FORMATS.md](references/FORMATS.md).

### 2. Gather what actually happened

Gather everything **before saying anything** — the whole point is to open with one informed message rather than interviewing the user for facts a command would have answered.

First the last update to this same reader, which is what makes this a continuity check rather than a blank page. Entries are named `YYYY-MM-DD-<audience>.md`, so the newest prior one sorts last:

```sh
today=$(date +%Y-%m-%d)
ls ~/.agents/standup/*-client.md 2>/dev/null | grep -v "/$today-" | tail -1
```

Substitute the audience from Step 1, and note both filters: **the same audience**, because a promise made to a client isn't the one made to the team, and **not today**, or a second run in one day compares the update to itself and reports nothing. Nothing found is normal on the first run — [GATHER.md](references/GATHER.md) has the dwell-time fallback for judging staleness without history, plus which sections to compare in the terse and spoken formats.

Then the repository:

```sh
git log --since="3 days ago" --author="$(git config user.email)" --oneline
git status --short
gh pr list --author "@me" --state all --limit 10
```

That covers one checkout, and the work that spread across repositories is the work people forget to report. For the multi-repo loop, the reviews and tickets a log never shows, and what to do when the tooling isn't reachable: [GATHER.md](references/GATHER.md). **Gathering is read-only throughout** — never comment on or transition anything while reading it.

Now open, in one message: what git shows, anything carried over from last time, and the question.

**"Here's what I can see from git, and what was still in flight when you last updated them. Before I help you write this — what did you actually spend your time on? Git doesn't always tell the full story."**

Wait. Commits miss investigation, debugging, reviews, meetings, decisions, and the four hours that produced no diff. Their answer is the update; everything you gathered is only what jogs it.

Two carry-overs are worth raising by name, and both are questions rather than conclusions:

- **Still in flight from last time** — say how long. "Billing has been in progress for three days" is the most useful sentence this skill produces, and the reader will notice the stall whether or not the update mentions it.
- **Promised last time and not done** — ask what happened to it before writing a word. An unremarked promise is what makes the next update untrustworthy.
- **Asked of the reader last time and still unanswered** — a decision requested, an access request, a question. Nobody chases these, and the work stays blocked while both sides wait. Raising it again is the cheapest thing in this whole skill.

Then, one at a time:

- **"What's the most important thing the reader should know — if they read one sentence and nothing else?"** Most updates bury the lead.
- **"Is there anything the reader needs to decide, unblock, or be aware of before your next working session?"** Blockers are cheap here and expensive later.

**Move on when** you can state the one-sentence headline and the reader's next action, if they have one. Short of that, ask again.

### 3. Sharpen the parts people soften

Pick two or three questions aimed at what they actually said, not the whole bank. Grouped by what each group surfaces: [QUESTIONS.md](references/QUESTIONS.md).

Three of them are worth asking almost every time:

- **The loose end.** "Done" in conversation routinely means "done except for". Ask which.
- **The risk they've decided to absorb.** Nobody volunteers a risk they believe they can handle alone. Those are exactly the ones a reader wants early.
- **The date.** If there is any doubt about the next deadline, this update is where it gets said — not the day before it lands.

Reframe every risk for the reader you fixed in Step 1: a client hears timeline and confidence, a manager hears the commitment and where you need help, a teammate hears the dependency or the decision that changes their own work.

**When the honest answer is "we're going to miss it", stop and say so before writing anything.** A broadcast update is the wrong place for a date to slip for the first time; the reader learns it in a paragraph, with nobody to ask. Put it to the user directly: **"This needs a conversation before it needs a paragraph. Who should hear it from you first?"** The update then records a decision they already discussed, which is a different document entirely.

Push once on internal alignment too — a decision, a direction change, or a new dependency that a teammate needs and this update won't reach. Internal alignment breaks quietly when people assume teammates will infer it from the code.

### 4. Write it

Produce something ready to send, in the shape [FORMATS.md](references/FORMATS.md) gives for this audience and cadence. Short beats thorough; a long update goes unread, which makes the risk buried in it undelivered.

The principles that decide the wording:

- **Outcomes over tasks.** "Users can now reset their own password" beats "implemented the password reset controller". The reader cares what changed for them.
- **Honest over optimistic.** A small concern raised early builds trust. The same concern arriving as a surprise spends it.
- **No filler.** "Continued working on the billing integration" is not an update. Name what changed, or say the day produced no visible progress and why.
- **Their words.** Match the register the user wrote in during the conversation — including how formal they are, and what they call things. AGENTS.md §8 (*Writing for a human reader*) is the standard: no hype adjectives, no throat-clearing, no uniformly-hedged sentences of identical length.

### 5. Read it back, then hand it over

Close with: **"Read it back — does it honestly reflect where things stand? Is there anything you softened that should be said more directly?"**

Wait for the answer. If they name something, reword it with them. This is the last point at which a softened risk can be caught, and the read-back catches more of them than any question in Step 3.

Then hand the text over and stop. Sending it is theirs.

### 6. File it for tomorrow

Once the text is final — after the read-back, never before — write it to `~/.agents/standup/YYYY-MM-DD-<audience>.md`, dated from `date +%Y-%m-%d`, in the same skeleton it was written in so tomorrow's sections line up with today's. The audience belongs in the name: a client update and a team standup on one day are two different promises to two different readers, and one filename would silently overwrite the other.

That file is the whole of Step 2's continuity check, and the only reason this skill can tell the user something they didn't already know.

Then prune to 14 days — enough for a sprint and any "last week" a reader refers to, past which it is a growing archive of client status nobody reads. **Never prune a reader's most recent entry, whatever its age:** a monthly report would otherwise lose all its history before the next one, and continuity for an infrequent reader is worth more than the two weeks. The command, which handles both rules: [GATHER.md](references/GATHER.md).

**Whatever you run, `-L` is not optional.** `~/.agents/standup` is a symlink, and BSD `find` does not follow one given as its starting point — without `-L` the command matches nothing, deletes nothing, and reports success while the journal grows forever (AGENTS.md §4, *Definition of Done*).

If the directory doesn't exist, `mac` hasn't run on this machine. Say so in one line and skip the journal — do **not** create it, since a real directory here is one `mac` run away from being moved aside to `standup.backup`, taking the history with it. Details: [GATHER.md](references/GATHER.md).

## Gotchas

- **Never deliver the update — no channel, no message, no email, no ticket.** It is outward-facing text going out under the user's name, to a client or a manager. Hand over the draft even when a Slack, Jira, or email tool is right there and the user seems to expect it: approval to *write* an update is not approval to *publish* it. Writing the journal in Step 6 is not delivery — it is a local file the reader never sees, and it is the only write in scope.

- **Never write a line the user didn't say.** A thin day tempts you to smooth it into plausible progress, and that is the one failure that costs the user their credibility rather than yours. Empty section, or no section.

- **The journal is written after the read-back, not before.** Filing the draft you produced in Step 4 records something the user then edited or rejected, so tomorrow's continuity check runs against words nobody sent. Final text only.

- **Never commit the journal, and never move it into a repository's tree.** `~/.agents/standup/` resolves into a git repository, and the entries are client status held in plaintext. The ignore rule that keeps them out of history is load-bearing, so don't stage them past it and don't write a copy anywhere a `git add -A` will find it.

- **A stall is the user's to explain, not yours to diagnose.** "Billing has been in progress three days" is an observation worth raising; deciding *why* and writing that into the update is inventing content. Ask, then use their answer.

- **"On track" is a claim only the user can make.** Don't add a confidence line, an estimate, or a reassurance they didn't state — a client reads it as a commitment.

- **Don't manufacture a risk to fill the "Heads up" section.** Omit the section entirely when there's nothing in it. Invented concern teaches the reader to skip the one section that will matter later.

- **An empty `git log` is a fact to check, not a quiet day.** `--author="$(git config user.email)"` silently matches nothing when the repository overrides the email, or when a rebase rewrote the author. Re-run it unfiltered before believing it.

- **Monday's "yesterday" is Friday.** `--since="yesterday"` on a Monday covers a weekend and reports nothing. Reach back three days by default and trim what doesn't belong.

- **A day's work often spans repositories.** Git in one checkout sees one. Ask which repos and which tracker items the stretch touched before deciding what got done.

- **Take the date from the environment** — `date +%Y-%m-%d` — never from memory. An update headed with the wrong date is the first thing the reader notices and the last thing they trust.

- **The update is not a changelog.** Never paste the commit list, however tidy it looks. Commit subjects are written for engineers reading a diff; the reader here wants what changed for them.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| "Nothing worth reporting happened" | Almost never true, and the reader needs to hear it if it is. Ask what they learned, what they ruled out, and what they're now blocked on. A day spent proving an approach doesn't work is a real result — write it as one. |
| The day was meetings and code review | Say that. Reviewing a teammate's branch and unblocking someone is work the reader benefits from; naming it also explains the absent commits before they're noticed. |
| Git shows nothing, but they worked all day | Believe the user, not the log. Check [Gotchas](#gotchas) for the two reasons the log lies, then write the update from their account. |
| They want the update with no questions | Draft it from git plus one question, then mark every assumption you had to invent and hand it back for correction rather than presenting it as settled. |
| They ask you to soften a risk you think matters | It's their update and their relationship. Record it as they want it, say once what a reader will conclude when it surfaces later, and move on. |
| They ask you to post or send it | Not yours to send ([Gotchas](#gotchas)). Hand over the text formatted for wherever it's going, and let them paste it. |
| The update covers a teammate's work too | Attribute it by name. An update that reads as though one person did all of it is a small dishonesty the teammate will notice. |
| The reader has an established format | Theirs wins over anything in [FORMATS.md](references/FORMATS.md). Ask for a recent example and match it. |
| There's no journal, or the write is refused | Proceed without it and say so once. Judge staleness from dwell time instead — [GATHER.md](references/GATHER.md). Never create the directory or write the entry elsewhere. |
| The journal contradicts what the user just said | The journal records what was *sent*, not what was true. Ask rather than correct them: "last time this went out as landing Tuesday — did that change?" The answer belongs in the update; the discrepancy doesn't. |
| Two updates to different readers on the same day | Expected, and why the filename carries the audience. Run the skill once per reader; each compares against its own history, because the promises differ. |
| The work slipped because the scope was too large | The update reports the slip; `slice` re-cuts what's left. Do them in that order, so the update doesn't promise a plan nobody has made yet. |
| It's a sprint review, a retro, or a written self-assessment | Out of scope. Those argue a case over weeks of work; this reports a stretch of it. |

## References

Read these when the step points at them, not upfront.

- [GATHER.md](references/GATHER.md) — gathering across several repos, the time window, reviews and tickets, and the read-only rule
- [FORMATS.md](references/FORMATS.md) — which skeleton in `assets/` to fill, what changes per audience, the end-of-week variant, and two worked updates including a thin day
- [QUESTIONS.md](references/QUESTIONS.md) — the sharpening bank, grouped by what each group surfaces, with the rule for choosing

## Attribution

- [thoughtbot/rails-consultant](https://github.com/thoughtbot/rails-consultant/tree/main/skills/standup) - standup, MIT
