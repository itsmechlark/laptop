---
name: file-tickets
description: Create the tracker items for a slice list that is already agreed — one issue per slice, in dependency order, carrying the tracker's real blocking relations and product-team wording. Use when asked to file tickets, create issues from a breakdown, put an approved epic into Jira or GitHub, or turn a settled slice list into a backlog. Publishes a decision that has already been made; it does not decide the slices, and it does not work items that already exist.
argument-hint: "[the agreed slice list, or the path to the file holding it]"
disable-model-invocation: true
---

# File tickets

Turn an agreed sequence of slices into real items on a real tracker, ordered so the dependencies are expressible and worded for the people who read the tracker.

What to file: `$ARGUMENTS` — a slice list in the conversation, or a path to the file `slice` wrote. Nothing at all means the conversation holds the list.

**This skill publishes; it does not decide.** Every ticket it files traces to a slice the user already agreed to. If you find yourself inventing a slice, merging two, or resolving a dependency the list left open, stop — that is `slice`'s work, and doing it here files a breakdown nobody approved.

**Creating N items is one publish action, not N.** Approval to file *a* ticket is not approval to file the set. Name the count when you ask.

## When to use this skill

- An agreed slice list needs to exist on GitHub or Jira so the team can pick work up
- An approved epic is going into the backlog for the first time
- A sequence captured in a Markdown file needs filing now that the team is ready to start
- Not for deciding what the slices are, re-cutting them, or sequencing them — that's `slice`, and this skill runs after it
- Not for items that already exist on the tracker — `triage` owns those, including moving a ticket to `ready-for-agent` once its blockers close
- Not for filing a single fresh bug from an error message: that is a dedupe-and-create job, and where the environment ships a plugin skill for it (an Atlassian bundle usually does), that skill owns the path
- Not for a specification too large to live in a ticket — `draft-spec` writes that, and the ticket links to it
- Not for splitting a finished branch into reviewable pull requests, which is a different decomposition made against real code — `pull-request` covers it

`triage` is user-invoke-only, so the Skill tool refuses it — route there by reading and following its `SKILL.md`, or by asking the user to run it.

## Prerequisites

**Confirm tracker access before drafting anything.** On GitHub that means `gh auth status` succeeds and `gh` can see the repository; on Jira, that the Atlassian MCP tools are present *and* authorized. An unauthorized MCP server looks exactly like an empty project. If access is missing, say so and stop at the drafted set — hand over the exact ticket bodies for the user to file by hand rather than describing a tracker you cannot reach.

**Resolve the tracker's real vocabulary, once, before the first create.** Not the API, not the project key, not the labels, not the statuses, and above all not the link types. A guessed label is a wrong label, and a guessed relation silently files a set with no dependency structure at all.

- **GitHub** — `gh label list` for labels; check whether the repository uses sub-issues, and whether anything native expresses "blocked by" (Projects fields often do; plain issues do not).
- **Jira** — read the available issue link types rather than assuming `Blocks` exists, the workflow statuses rather than assuming a status name, and the **issue types** the project actually offers. A set filed as the wrong type inherits the wrong workflow, and moving it afterwards is a per-ticket edit.

**Ask where the set hangs, and never invent it.** Most slice lists belong under something — an epic, a parent issue, a milestone. Ask which, rather than inferring one from the feature's name, and attach children with the tracker's own mechanism (GitHub sub-issues, Jira's parent field) so the parent's rollup is real rather than a sentence in a body. If no parent exists, say so and let the user decide: an epic is a planning object other people's reports are built on, and one invented to have somewhere to put six tickets outlives the six.

## Is the list ready to file?

Run this before touching the tracker. All three must hold:

1. **Every slice is a job story with acceptance criteria** that someone who has never seen the feature could verify.
2. **Every slice carries a `Depends on:`** — an earlier slice whose behavior must already be live, or `none`.
3. **The user has agreed to the list**, not merely seen it.

When one fails, say which, and route to `slice` rather than filing. A ticket set is a commitment the whole team then plans against; filing a list that was still being argued about makes the argument expensive to reopen.

**One more read before you draft.** If every slice depends on the one before it, the list is a build order wearing job-story clothes — `slice` says so itself. Filing it produces a queue of one, and the tickets after the first are unworkable until it lands. Say so and hand it back.

## Workflow

### 1. Draft the set

One ticket per slice, in dependency order — a slice with `Depends on: none` comes before anything that depends on it. Number them in that order while drafting so you can talk about them before they have real keys.

Write each ticket to the template below. Two things stay out of the body:

- **File paths and code snippets.** They are stale within a sprint, and a ticket that names `app/models/booking.rb` sends the implementer to a file that moved. Name the behavior; let them find the code. The exception is a decision that prose states less precisely than a shape does — a state machine, a schema, a type — where the shape *is* the decision. Inline only that part.
- **Implementer detail, unless the ticket is unblocked.** See step 3.

### 2. Show the whole set and ask once

Present the set as a numbered list: each ticket's title, what it delivers, and what blocks it. Then show the full body of at least the first one, and offer the rest.

Ask one question, and put the count in it: *"File these 6 tickets in PROJ?"* Name the project, the labels you will apply, and the link type you will use. Approval covers this set on this tracker — not a seventh ticket you notice later, and not a re-file into a different project.

### 3. Create in dependency order, then link

The order is forced by the tracker, not by taste: a blocking relation needs both keys to exist, so nothing can reference a ticket that has not been created. Create every ticket first, then apply the relations in a second pass.

**Record each key as it comes back, not at the end.** A create that fails partway has already filed real items, and without the mapping built so far you cannot tell a retry from a duplicate — which is the one mistake here that cleans up worse than it lands.

Apply state as the frontier dictates:

- **A ticket with no blockers** is ready to be worked. Append the agent brief — `triage` owns that format in its `references/AGENT-BRIEF.md` — and apply the tracker's equivalent of `ready-for-agent`.
- **A blocked ticket gets no brief and no ready state.** It is not workable yet, and a ticket labeled ready whose prerequisite is not live is how an unattended agent starts building against behavior that does not exist. Leave it at the tracker's untriaged or backlog state.

Moving a ticket to the frontier later, once its blockers close, is `triage`'s quick override — not a second pass by this skill.

**Never modify or close a parent epic** to record that its children now exist. Filing children says nothing about whether the parent is done.

### 4. Report

Give the user the real keys mapped back to your draft numbers, in dependency order, which of them are unblocked, and anything you could not express on this tracker — a missing link type recorded in prose is a real gap, and saying so is cheaper than the team discovering it when two people start the same ticket.

## Ticket template

The audience is the product team (AGENTS.md §3, *Jira vs. Pull Requests — audience separation*), so the body is the problem, the outcome, and criteria in outcome language.

```markdown
## Problem

[The situation the user is in today and why it matters — two or three sentences.]

## Outcome

When [situation], [who] can [what], so [outcome that matters to them].

**Done when:** [observable behavior — what a user can do, not what the code does.]

## Acceptance criteria

- [ ] [happy path]
- [ ] [boundary or edge case]
- [ ] [error state, if there is one]

## Blocked by

[The blocking ticket, named in prose — or "Nothing".]
```

The native relation is applied separately in step 3; this section is the human-readable copy of it, and the only copy on a tracker that has no such relation.

**The title is the slice's short name, in outcome language** — it is the only part most people read, and it carries into sprint reports and release notes. No Conventional Commits prefix: `feat(booking):` is commit and pull-request vocabulary by the audience split above, and in a tracker it reads as noise to everyone who isn't an engineer.

Carry the slice's wording rather than paraphrasing it. `Ships when:` becomes **Done when**, and the acceptance criteria transfer verbatim: they are what the user argued their way to, and a rewrite quietly changes what was agreed.

Where the work needs more specification than this holds, `draft-spec` writes the document and the ticket links to it. Don't grow the ticket into a spec.

## Gotchas

- **Filing has no undo.** A GitHub issue can be closed but not deleted without admin rights, and a Jira delete needs a permission most accounts don't have. The approval in step 2 is the only gate that exists — a wrong project, a duplicated set, or a premature file gets cleaned up by hand, in public, on a board other people are watching.
- **Filing is not planning.** A set of tickets on a board looks like progress and is not; nothing has shipped. The same trap the pull-request split has — *"splitting is not shipping"* — with a tracker in place of a branch.
- **A dependency the tracker cannot express is still a dependency.** When there is no blocking link type, the `## Blocked by` prose is load-bearing — say in the report that the structure lives in the body, so nobody trusts an empty relations panel.
- **Don't file a ticket per layer.** "Add the endpoint", "add the model", "add the UI" is the horizontal cut `slice` rejects, and it survives into the tracker unnoticed because each one looks like a real task.
- **Expand, backfill, and contract are steps inside a ticket, not three tickets.** A migration nobody can see delivers nothing to file; it ships with the behavior that uses it.
- **Never create a label or a status to make the set fit.** Ask the user — a tracker's vocabulary belongs to the team, and inventing one entry fragments every filter built on it.
- **A slice list that already exists on the tracker is a different job.** Check before filing: a re-file produces duplicates that outlive the mistake, and dedupe is `triage`'s.
- **Approval to file is not approval to assign, transition, or notify.** Assigning a ticket lands in someone's inbox with an implied commitment; ask separately.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| The tracker has no "blocked by" link type | Record the dependency in the `## Blocked by` section and say so in the report; don't substitute a semantically different link |
| The user wants every ticket marked ready | Explain what ready means here — an agent can take it unattended — and that a blocked ticket cannot be. If they still want it, do it and note the risk in one line |
| Half the set files, then a call fails | Report exactly which keys exist and which do not before retrying, so the retry does not duplicate the first half |
| Read access but no write access | Do the whole draft and hand over the bodies and the relation list for the user to apply |
| The list came from a spec rather than from `slice` | Check the three readiness tests anyway. A spec settles what to build; it does not guarantee the work is cut into shippable pieces |
| A slice is blocked on another team or a vendor | That is not a `Depends on:` edge in this set. File it with the external dependency named in the Problem section, and leave it unblocked or hold it back, as the user prefers |

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/to-tickets) - to-tickets, MIT
- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
