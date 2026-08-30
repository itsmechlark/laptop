---
name: triage
description: Move issues and external PRs through a triage state machine — categorize, check for prior art, verify the claim, sharpen what's underspecified, and write agent-ready briefs. Works against GitHub (gh) or Jira (Atlassian MCP). Use when asked to triage an issue or PR, work through the backlog, decide what needs attention, or turn a report into something an agent can pick up.
argument-hint: "[item reference or request — e.g. '#42', 'HDR-1234', 'what needs my attention?']"
disable-model-invocation: true
---

# Triage

Move items that already exist on an issue tracker through a small state machine. Triage produces a **decision** — and, when the decision is "someone should build this", a brief precise enough to work from cold, days later.

What to work: `$ARGUMENTS`. A bare `#42` resolves against the repository's tracker; a `PROJ-1234`-shaped key resolves against Jira; plain language picks an entry point below. Nothing at all means survey the queue.

**An external PR is an issue with attached code** — same roles, same states, same machine. Deltas are marked *for a PR* throughout.

**Core principle:** the decision has to land somewhere the next reader finds it. A conclusion reached in conversation and never written to the tracker is not a triage.

## When to use this skill

- Working an issue or an external PR that already exists on a tracker
- Surveying the queue — what is untriaged, what is stalled, what an agent could take unattended
- Turning a vague report into an agent-ready brief with acceptance criteria that can fail
- Recording a rejected enhancement so the same idea isn't re-litigated in six months
- Not for filing a *fresh* bug from an error message or stack trace: that is a dedupe-and-create job against the tracker, and where the environment ships a plugin skill for it (an Atlassian bundle usually does), that skill owns the path
- Not for an enhancement that turns out to be an epic — `slice` cuts it, then triage the slices
- Not for putting a whole agreed slice list onto the tracker for the first time — creating a set is an outward-facing write the user authorizes with the count in front of them, and triage works the items afterwards
- Not for judging the code in an external PR beyond "does it do what it claims" — that's `code-review`
- Not for a specification too large to live in a tracker comment — that's `draft-spec`

## Prerequisites

**Confirm tracker access before reading anything into the queue.** Every step below asserts things about real items in a system other people depend on. On GitHub that means `gh auth status` succeeds and `gh` can see the repository; on Jira, that the Atlassian MCP tools are present *and* authorized — an unauthorized MCP server looks identical to an empty backlog. If access is missing, say so plainly and stop: **never describe tracker state from memory, and never infer it from the codebase**, because a fabricated queue is worse than no answer — it reads exactly like a real one.

Two things are optional, and their absence changes the work rather than blocking it: **browser automation**, needed only to reproduce a failure that shows up in a running UI ([VERIFY.md](references/VERIFY.md)); and the two **rejection knowledge bases** — the repo's committed `.out-of-scope/` and the machine-local cross-repo one at `~/.agents/out-of-scope/`. A missing directory means no prior rejections to check, never that the check was skipped ([OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md)).

## Writing to the tracker

Comments, label changes, and closes are outward-facing and land in a reporter's inbox. Treat them like a push:

- **Draft, show, then ask.** Show the exact text and the exact state change before it goes out. Approval for one comment is not standing permission for the next.
- **Never close an item or apply `wontfix` without explicit approval**, even when the analysis is obvious.
- Every comment posted during triage opens with:

  ```
  > *Written by an AI agent during triage.*
  ```

  This is transparency to a human reporter, not attribution — it belongs on tracker comments only. The house rule against AI attribution in commits and PR descriptions (`git-commit`, `pull-request`) holds without exception.

## Roles

Two **category** roles: `bug` (something is broken) and `enhancement` (new or improved behavior).

**Plenty of real items are neither** — a support question, a docs fix, a discussion, spam. Don't force one on: the categories drive the workflow below, so a question filed as a bug gets verified and briefed as though someone had reported a defect. Say the item is out of category, say what it actually is, and ask how the tracker handles that class. Answer a support question if you can, but answering it is not triage and it earns no state role.

Five **state** roles:

| State | Meaning |
| --- | --- |
| `needs-triage` | not yet evaluated |
| `needs-info` | waiting on the reporter |
| `ready-for-agent` | fully specified; an unattended agent can take it |
| `ready-for-human` | needs a human — judgment, access, or design calls |
| `resolved-elsewhere` | the request is already satisfied, or tracked on another item |
| `wontfix` | declined on the merits |

**`resolved-elsewhere` and `wontfix` are not the same close**, and conflating them tells a reporter the opposite of the truth: closing "add dark mode" as `wontfix` after dark mode shipped says you refused something you actually built. Already-built and duplicate are `resolved-elsewhere`; only a decision not to do the thing is `wontfix`. Real trackers encode this too — GitHub closes as `completed` versus `not planned`, Jira resolves as *Done* / *Duplicate* versus *Won't Do* — so pick the close reason to match, not just the label.

*For a PR*, states read against the diff: `ready-for-agent` means a brief is attached and the next step on the diff is delegable; `ready-for-human` means it's ready to review and merge.

Every triaged item carries **exactly one category and one state**, which makes applying a state a **replacement**, not an addition. `gh issue edit --add-label` leaves the old one in place and the item then trips the two-role stop on its next pass, so remove and add in the same edit. A Jira transition already replaces the status; a Jira *label* does not.

These are canonical names, not literal labels. Resolve them against the real tracker before writing:

- **GitHub** — read the actual labels (`gh label list`), map each canonical role to one of them, and confirm the mapping once.
- **Jira** — states are usually workflow **statuses**, not labels; category is usually **issue type**. Read the available transitions (`getTransitionsForJiraIssue`) rather than assuming a status exists.

Normal transitions: unlabeled → `needs-triage` → one of `needs-info` / `ready-for-agent` / `ready-for-human` / `resolved-elsewhere` / `wontfix`. `needs-info` returns to `needs-triage` when the reporter replies. The maintainer can override anything — flag transitions that look wrong and ask before applying.

## Entry points

The maintainer invokes `/triage` and says what they want in plain language — interpret and act:

| What they say | What you do |
| --- | --- |
| "What needs my attention?" | Survey the queue — the five buckets below |
| "Let's look at #42" / "HDR-1234" | Run the workflow on one item |
| "Move #42 to ready-for-agent" | Quick override |
| "What's ready for agents?" | List `ready-for-agent`, ordered by each brief's `Impact` line |

### Survey the queue

Five buckets, each oldest-first, with counts and a one-line summary per item: **untriaged**; **`needs-triage`**; **`needs-info`, reporter has replied**; **stalled** — `needs-info` with no reply past the staleness threshold; and **aging `ready-for-agent`** — briefed but unclaimed past the same threshold. The last two exist because their items are otherwise invisible: one has no activity to surface it, the other looks finished.

What belongs in each, what an aging brief is re-checked against, why a stalled item is never closed automatically, how PRs are filtered, and how to fan out a large queue: [QUEUE.md](references/QUEUE.md). Then let the maintainer pick.

### Quick override

"Move #42 to ready-for-agent" is a decision, not a question — trust it. Confirm what you're about to do (role changes, comment, close), then do it, skipping verification and sharpening. If it's moving to `ready-for-agent` and no brief exists, ask whether to write one; a brief-less `ready-for-agent` is how an unattended agent ends up guessing. Same for a bug with no repro artifact — offer to produce one, don't block on it.

## Workflows

### 1. Gather context and check for prior art

Read the whole item — body, comments, labels, author, dates; *for a PR*, the diff too. Where prior triage notes exist this is a resumption, not a fresh start: read them, check whether the reporter answered the open questions, present the updated picture before continuing, and never re-ask what is already settled.

**If the item describes a security weakness, stop the public workflow here.** A vulnerability filed as a public issue is already a disclosure problem, and normal triage compounds it by posting a working reproduction underneath. Tell the maintainer, keep any artifact out of the tracker, and let them route it to a private advisory — `SECURITY.md` names the channel — before anything else happens. This overrides step 3: an exploit is never a public comment, whatever tier it would have been.

Leave the item alone in the meantime — **no state role, no comment, no close.** Each of those is a public signal on a disclosure the maintainer hasn't decided how to handle yet, and closing one quietly is its own kind of announcement. Hand them the options — delete the issue, convert it to an advisory, or leave it visible and patch fast — and let them pick.

Then run three checks against reality:

- **Already built** — search the codebase for the requested behavior by domain concept, not by the reporter's wording. If it exists, the item is `resolved-elsewhere`, not declined.
- **Already rejected** — read **both** knowledge bases, the repo's `.out-of-scope/` and `~/.agents/out-of-scope/`, and surface anything resembling this request. Say which one matched: a cross-repo hit is standing policy, not one project's call ([OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md)).
- **Already reported** — search the tracker for the same underlying problem, **including closed items** (`gh search issues`, or JQL across all statuses).

**Write the searches into whatever you post** — the queries themselves and what they returned, not just "checked for duplicates". Reported to the conversation only, they evaporate, and the next person to open the item runs all three again.

### 2. Recommend, then wait

State the category, the reasoning, and what the codebase says about the request. Wait for direction before writing anything **to the tracker** — a scratch branch or a local repro in step 3 is not a tracker write and needs no approval of its own. For an enhancement the recommended state is a conclusion; for a bug or a PR it is a **forecast**, because the state follows a verification tier you have not produced yet. Say which state you expect, what would change it, and roughly what verifying will cost — this is the cheapest moment for the maintainer to say "don't bother, just move it".

### 3. Verify the claim, and keep the artifact

Bugs and PRs only — an enhancement has nothing to reproduce, so skip to step 4. Produce the strongest tier available: **(a)** a failing test on a `triage/<ref>-repro` branch, **(b)** a copy-pasteable command and its verbatim output, or **(c)** "couldn't reproduce", plus exactly what you tried. An external PR has a fourth outcome — **not run**, a safety hold, when executing the diff isn't safe here. Which fits what, how to capture a UI reproduction, and what each permits as an outcome: [VERIFY.md](references/VERIFY.md).

### 4. Sharpen — only if underspecified

Invoke `grilling` and `domain-modeling` together, and **actually invoke them**: an interview improvised inside this step is the failure the handoff exists to prevent. Grill the gaps one question at a time — never a wall of questions — while sharpening the domain's terms and writing decisions to `CONTEXT.md` or an ADR inline as they land, rather than burying them in a tracker comment.

Aim each question at what would change the implementation: the ambiguous term, the unhandled edge case, the unstated expected behavior, the success criterion. If the request keeps growing, it's an epic — stop and hand it to `slice`. If it isn't an epic but needs a fuller specification than a tracker brief can hold, hand off to `draft-spec`.

### 5. Apply the outcome

Draft it, show it, then write:

- `ready-for-agent` → post an agent brief ([AGENT-BRIEF.md](references/AGENT-BRIEF.md)). A **bug** gets here only on a tier (a) or (b) artifact from step 3.
- `ready-for-human` → same structure, plus why it can't be delegated (judgment call, external access, design decision, manual verification, or a diff nobody could safely run here).
- `needs-info` → post triage notes (template below).
- `needs-triage` → apply the role; comment only if there's partial progress worth keeping.
- `resolved-elsewhere` → close as completed/duplicate, never as declined:
  - *Already built* — point to where the behavior lives, precisely enough that the reporter can go use it.
  - *Duplicate* — link the two together, move any new detail onto the survivor, close the other. **The survivor is the better item, not the older one**: prefer the one with a reproduction, an active reporter, or the clearer statement of the problem, and say why you kept it.
- `wontfix` → close as declined, with the comment depending on **why**:
  - *Rejected bug* — plain explanation, then close.
  - *Rejected enhancement* — record the reasoning, link it from the comment where the reader can reach it, then close. Which knowledge base it lands in, and why a project-local write gets the same draft-show-then-ask as a tracker comment: [OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md).

**On Jira, mind the audience** (AGENTS.md §3, *Jira vs. Pull Requests — audience separation*). The ticket is read by the product team: keep the problem, the outcome, and the acceptance criteria in outcome language. Interface-level detail goes inside the clearly-marked agent brief block — its reader is an implementer, not the product team — and stays as short as the work allows.

## Needs-info template

```markdown
## Triage notes

**Established so far:**

- point 1
- point 2

**Prior art checked:** the searches run, and what they returned

**Still needed from you (@reporter):**

- question 1
- question 2
```

Everything settled during verification and sharpening goes under "established" — that's the record the next session resumes from. A tier (c) verification belongs there in full: the commands you ran, the versions, what you saw instead. Questions must be specific and answerable; "please provide more information" is not a question.

## Gotchas

- **Two state roles on one item is a stop, not a judgment call.** Ask before anything else — you cannot tell which one is stale, and picking wrong silently rewrites someone's decision.
- **An external PR's diff is code you are about to execute.** Read it for execution surface before any checkout, run it somewhere disposable, or don't run it — but never report a diff as verified when nothing was run ([VERIFY.md](references/VERIFY.md)).
- **A stalled item is surfaced, never auto-closed.** Reaching the staleness threshold makes it visible; closing it is a maintainer's call and a close like any other ([QUEUE.md](references/QUEUE.md)).
- **A missing label is a question for the maintainer.** Never create a tracker label to make a canonical role fit; ask first.
- **Never soften an unverified claim into a verified one.** A confident read of the code is not a reproduction, and tier (c) is `needs-info` however obvious the diagnosis looks. A diff deliberately left unrun is the one exception, and it isn't a tier (c) — it's a safety hold, and it goes to `ready-for-human`.
- **A closed-and-fixed duplicate means regression, not resolution.** It is a different and more urgent bug than the one reported — say so instead of closing as a duplicate.
- **`resolved-elsewhere` never goes in `.out-of-scope/`.** That knowledge base is for requests you declined; a shipped feature or a duplicate filed there poisons every future dedupe check. Point to where the behavior lives instead.
- **A rejection grounded in a codebase belongs to that repo, not your machine.** The cross-repo KB is for policy with no project to live in — filing a project's reasoning there hides it from every co-maintainer and from the next reporter.
- **The `triage/<ref>-repro` branch is scratch, and scratch with no owner is litter.** The fix PR absorbs the test or the branch gets deleted.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| Jira has no status matching a canonical state | Read `getTransitionsForJiraIssue` and map to what exists; don't invent a status |
| `gh` returns an empty list on a repo that visibly has issues | Issues may be disabled, or you're on a fork — confirm the repo before reporting an empty queue |
| Read access but no write access to the tracker | Do the whole analysis and hand over the exact text and state changes for the maintainer to apply |

## References

Read these as needed for the item in hand, not all upfront.

- [QUEUE.md](references/QUEUE.md) — the five buckets, staleness, aging briefs, PR filtering, and ordering
- [VERIFY.md](references/VERIFY.md) — the verification tiers, running an untrusted diff safely, UI reproduction, and what each tier permits
- [AGENT-BRIEF.md](references/AGENT-BRIEF.md) — writing briefs that survive a changing codebase
- [OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md) — the `.out-of-scope/` rejection knowledge base

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/triage) - triage, MIT
