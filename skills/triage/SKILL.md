---
name: triage
description: Move issues and external PRs through a triage state machine — categorize, check for prior art, verify the claim, sharpen what's underspecified, and write agent-ready briefs. Works against GitHub (gh) or Jira (Atlassian MCP). Use when asked to triage an issue or PR, work through the backlog, decide what needs attention, or turn a report into something an agent can pick up.
argument-hint: "[item reference or request — e.g. '#42', 'HDR-1234', 'what needs my attention?']"
disable-model-invocation: true
---

# Triage

Move items on the issue tracker through a small state machine. Triage produces a **decision**, plus — when the decision is "someone should build this" — a brief precise enough to work from cold, days later.

**An external PR is an issue with attached code**: same roles, same states, same machine. Deltas are marked *for a PR* below. Resolve a bare `#42` against the repo's tracker; resolve a `PROJ-1234`-shaped key against Jira.

## Reference docs

- [AGENT-BRIEF.md](references/AGENT-BRIEF.md) — writing briefs that survive a changing codebase
- [OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md) — the `.out-of-scope/` rejection knowledge base

Step 3 can run on `agent-browser` when the bug or PR lives in a web UI: drive the app to the failure and keep the screenshot as the artifact. Step 4 runs on two other skills: `grilling` (one question at a time until the shape is agreed) and `domain-modeling` (sharpen the terms, then capture them in `CONTEXT.md` or an ADR).

## Scope boundary

This skill works items that **already exist** in a tracker. Adjacent work belongs elsewhere:

- Filing a *fresh* bug from an error message or stack trace → `atlassian:triage-issue` (Jira dedupe + create).
- An enhancement that turns out to be an epic → hand off to `slice`, then triage the slices.
- Judging the code in an external PR beyond "does it do what it claims" → `code-review`.

## Writing to the tracker

Comments, label changes, and closes are outward-facing and land in a reporter's inbox. Treat them like a push:

- **Draft, show, then ask.** Show the exact text and the exact state change before it goes out. Approval for one comment is not standing permission for the next.
- **Never close an item or apply `wontfix` without explicit approval**, even when the analysis is obvious.
- Every comment posted during triage opens with:

  ```
  > *Written by an AI agent during triage.*
  ```

  This is transparency to a human reporter, not attribution — it belongs on tracker comments only. The house rule against AI attribution in commits and PR descriptions (`git-commit`, `pull-request`) still holds without exception.

## Roles

Two **category** roles: `bug` (something is broken) and `enhancement` (new or improved behavior).

Five **state** roles:

| State | Meaning |
| --- | --- |
| `needs-triage` | not yet evaluated |
| `needs-info` | waiting on the reporter |
| `ready-for-agent` | fully specified; an unattended agent can take it |
| `ready-for-human` | needs a human — judgment, access, or design calls |
| `wontfix` | will not be actioned |

*For a PR*, states read against the diff: `ready-for-agent` means a brief is attached and the next step on the diff is delegable; `ready-for-human` means it's ready to review and merge.

Every triaged item carries **exactly one category and one state**. If two state roles are present, stop and ask before anything else.

These are canonical names, not literal labels. Resolve them against the real tracker before writing:

- **GitHub** — read the actual labels (`gh label list`), map each canonical role to one of them, and confirm the mapping once. Missing labels: ask before creating any.
- **Jira** — states are usually workflow **statuses**, not labels; category is usually **issue type**. Read the available transitions (`getTransitionsForJiraIssue`) rather than assuming a status exists.

Normal transitions: unlabeled → `needs-triage` → one of `needs-info` / `ready-for-agent` / `ready-for-human` / `wontfix`. `needs-info` returns to `needs-triage` when the reporter replies. The maintainer can override anything — flag transitions that look wrong and ask before applying.

## Invocation

The maintainer invokes `/triage` and says what they want in plain language. Interpret and act:

- "What needs my attention?" → the three buckets below
- "Let's look at #42" / "HDR-1234" → triage one item
- "Move #42 to ready-for-agent" → quick override
- "What's ready for agents?" → list `ready-for-agent`, most impactful first

## Show what needs attention

Present three buckets, each oldest-first, with counts and a one-line summary per item:

1. **Untriaged** — no category or state role.
2. **`needs-triage`** — evaluation started, not finished.
3. **`needs-info` with reporter activity since the last triage note** — unblocked, needs another look.

When PRs are in scope, include them and tag each line `[PR]` or `[issue]`. Discovery surfaces **external** PRs only — a colleague's in-flight PR is review work, not triage work. The filter is discovery-only: an explicitly named PR is always triaged, whoever wrote it. Then let the maintainer pick.

## Triage one item

1. **Gather context.** Read the whole item — body, comments, labels, author, dates; *for a PR*, the diff too. Parse any prior triage notes so resolved questions aren't re-asked. Then run three checks against reality and report where you looked:
   - **Already built** — search the codebase for the requested behavior by domain concept, not by the reporter's wording. If it exists, it's an already-implemented `wontfix` (step 5).
   - **Already rejected** — read `.out-of-scope/*.md` and surface anything resembling this request.
   - **Already reported** — search the tracker for the same underlying problem, including closed items (`gh search issues`, or JQL across all statuses). A closed-and-fixed match makes this a possible regression, which is a different and more urgent bug than the one reported.

2. **Recommend.** State the category, the state, and the reasoning, plus what the codebase says about the request. Wait for direction before writing anything.

3. **Verify the claim, and keep the artifact.** Before sharpening anything, check the claim holds — reproducing a bug from the reporter's steps, or running a PR's diff against what it promises. Verification has to leave behind something that outlives the conversation; the word "confirmed" in a comment doesn't. Produce the strongest tier available:

   - **(a) A failing test**, on a scratch branch named `triage/<ref>-repro`, written with `tdd`. This makes the handoff red → green, which is where AGENTS.md §1 already points — a bug fix starts from a test that reproduces the bug. The `triage/` prefix marks the branch as scratch rather than work, so it sits outside the house branch convention on purpose; the fix PR absorbs the test or deletes the branch, because a scratch branch with no owner is litter.
   - **(b) A copy-pasteable command and its verbatim output** — the exact invocation, and what it printed, unedited. This is a first-class outcome, not a consolation: tier (a) is disproportionate for UI, timing-dependent, or environment-specific bugs, and impossible on a repo you can't push to. When the failure only shows in a running UI, reproduce it with `agent-browser`: drive the app to the broken state and keep the screenshot and the click path that got there. The screenshot is the artifact.
   - **(c) "Couldn't reproduce," plus exactly what you tried** — commands, versions, environment, what you expected to see instead. This *is* the body of the `needs-info` comment, and it asks a far better question than "please provide more information."

   *For a PR*, tier (b) is usually the fit: check the diff out, run the relevant tests or commands, record what you ran and what came back. When the diff changes a UI, running it means driving the app with `agent-browser` and keeping the screenshot. A fresh enhancement has nothing to reproduce — skip to step 4. Never soften an unverified claim into a verified one, and never let a confident read of the code stand in for a reproduction.

4. **Sharpen (only if underspecified).** Run `grilling` and `domain-modeling` together: grill the gaps one question at a time — never a wall of questions — while sharpening the domain's terms and writing decisions to `CONTEXT.md` or an ADR inline as they land, rather than burying them in a tracker comment. Aim each question at what would change the implementation: the ambiguous term, the unhandled edge case, the unstated expected behavior, the success criterion. If the request keeps growing, it's an epic — stop and hand it to `slice`.

5. **Apply the outcome.** Draft it, show it, then write:
   - `ready-for-agent` → post an agent brief ([AGENT-BRIEF.md](references/AGENT-BRIEF.md)). A **bug** gets here only on a tier (a) or (b) artifact from step 3; tier (c) is `needs-info` by definition, because without a repro an unattended agent can't tell done from plausibly-done.
   - `ready-for-human` → same structure, plus why it can't be delegated (judgment call, external access, design decision, manual verification).
   - `needs-info` → post triage notes (template below).
   - `wontfix` → close, with the comment depending on **why**:
     - *Already built* — point to where the behavior lives. Do **not** write to `.out-of-scope/`; that KB is for rejected requests, and a false entry poisons future dedupe.
     - *Duplicate* — link the original, move any new detail there, close this one.
     - *Rejected bug* — plain explanation, then close.
     - *Rejected enhancement* — write the reasoning to `.out-of-scope/`, link it from the comment, then close ([OUT-OF-SCOPE.md](references/OUT-OF-SCOPE.md)).
   - `needs-triage` → apply the role; comment only if there's partial progress worth keeping.

**On Jira, mind the audience** (AGENTS.md §3). The ticket is read by the product team: keep the problem, the outcome, and the acceptance criteria in outcome language. Interface-level detail goes inside the clearly-marked agent brief block — its reader is an implementer, not the product team — and stays as short as the work allows.

## Quick override

"Move #42 to ready-for-agent" is a decision, not a question — trust it. Confirm what you're about to do (role changes, comment, close), then do it. Skip verification and sharpening. If it's moving to `ready-for-agent` and no brief exists, ask whether to write one; a brief-less `ready-for-agent` is how an unattended agent ends up guessing. Same for a bug with no repro artifact — offer to produce one, don't block on it.

## Needs-info template

```markdown
## Triage notes

**Established so far:**

- point 1
- point 2

**Still needed from you (@reporter):**

- question 1
- question 2
```

Everything settled during verification and sharpening goes under "established" — that's the record the next session resumes from. A tier (c) verification belongs there in full: the commands you ran, the versions, what you saw instead. Questions must be specific and answerable; "please provide more information" is not a question.

## Resuming

If triage notes already exist, read them, check whether the reporter answered the open questions, and present the updated picture before continuing. Don't re-ask what's already settled.

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/skills/engineering/triage) - triage, MIT
