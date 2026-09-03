---
name: draft-prd
description: Write the product requirements for work that arrived without them — the problem, who has it, the outcome that counts as success, and what is explicitly out of scope. Use when asked for a PRD, a product brief, or a one-pager, when a feature request needs its problem stated before anyone designs a solution, or when a brainstorm or a stakeholder handoff produces something to build with no product framing behind it. Interviews for what is missing and stays deliberately approach-free; not the engineering specification, and not for choosing how to build it.
argument-hint: "[the feature, request, or problem to write requirements for]"
---

# Draft PRD

State the problem a piece of work exists to solve, who has it, and what would count as having solved it — before anyone argues about how. The audience is the product team (AGENTS.md §3, *Jira vs. Pull Requests — audience separation*), so every sentence is in outcome language: what a person can do afterwards that they cannot do now.

Subject: `$ARGUMENTS` — the feature, request, or problem to write up. Empty means the conversation is the subject.

**This skill may interview; its sibling may not.** `draft-spec` synthesizes a decision that is already made and is forbidden from reopening requirements. This one exists for the opposite case: the work arrived as a solution with no problem behind it, and the missing half has to be asked for. Ask, then write.

**Approach-free is the constraint that makes it useful.** A PRD that names a schema, an endpoint, a library, or a screen has decided the thing the design conversation was supposed to decide, and it decided it without the people who would have argued. Requirements bound the solution space; they do not pick a point in it.

## When to use this skill

- A feature request, a stakeholder ask, or a support escalation needs its problem stated before anyone designs against it
- A brainstorm or an upstream conversation produced something to build, but no framing a product team could review — no stated problem, no user, no measure
- A backlog item everyone has a different mental model of needs one shared statement of what it is for
- Work is about to be cut into slices, and nobody can say what the slices are in service of
- Not for choosing the approach — that's `brainstorming`, which runs after the problem is agreed and produces a design; route there by reading and following its `SKILL.md`
- Not for the engineering specification of an approach already chosen — that's `draft-spec`, which is the same handoff one layer down and writes for implementers rather than for the product team
- Not for cutting the work into independently shippable pieces (`slice`), which runs on an agreed PRD
- Not for pressure-testing a PRD that already exists — `grilling` interviews a document claim by claim
- Not for recording an architectural decision and its consequences, which is `domain-modeling`'s ADR

## Is there a problem here, or only a request?

Run this before writing anything. All three must hold:

1. **The problem survives without the solution.** Delete the proposed feature from the request and something is still wrong for somebody. If nothing is left, the request is a solution in search of a justification, and writing it up gives it one it hasn't earned.
2. **Someone specific has it.** A named segment, role, or situation — not "users". A problem everyone has equally is usually a problem nobody has acutely.
3. **You can state what would falsify success.** An outcome that no observation could contradict is a slogan.

When one fails, say which, and ask the question that closes it rather than drafting around the gap. The most valuable output this skill produces is sometimes the sentence *"this doesn't have a problem behind it yet"* — that costs one reply and saves a quarter.

## Workflow

### 1. Harvest before you ask

Every question you ask that the conversation already answered spends the user's patience on your reading. Before the first question, collect:

- **The conversation and any upstream design output** — a brainstorm, a thread, a stakeholder message. Take the framing that is already there.
- **The project's glossary or `CONTEXT.md`** — use its vocabulary exactly. A PRD that renames the domain teaches the wrong words to everyone downstream, and new terms belong to `domain-modeling` before they belong here.
- **The rejection knowledge bases** — the repo's `.out-of-scope/` and `~/.agents/out-of-scope/`. A problem already declined needs the earlier reasoning answered, not re-proposed. Surface the hit before drafting.
- **What the product already does.** A requirement the current behavior satisfies is not a requirement; it is a discoverability problem, which is a different PRD.

### 2. Ask only what changes the document

One question at a time, and only where a missing answer would change what gets built rather than how it reads. Say what each answer decides, so the user can tell you it doesn't matter.

The gaps worth an actual question are almost always these four: **who** exactly, **how you would know it worked**, **what is deliberately out**, and **why this is worth doing now rather than later**. Frequency, severity, and current workaround are worth one question between them when the problem's size is genuinely unknown.

Anything you end up supplying yourself is an assumption, not an answer — it goes in the document labeled as one. An invented user segment reads as research to everybody who wasn't here.

### 3. Write it

Use the template and keep its section order: [TEMPLATE.md](references/TEMPLATE.md), which carries what belongs in each section and the self-check to run before showing the draft.

Length is a feature. A PRD that a product manager, a designer, and an engineer will each read in full is worth more than a thorough one they skim, and the sections exist to be cut when they hold nothing (AGENTS.md §8, *Writing for a human reader*). Write `None` only where the absence is the news — no non-goals is never the news, and an empty **Out of scope** means the boundary hasn't been drawn yet.

### 4. Confirm, then hand off

Show the exact Markdown and get agreement before it goes anywhere. A PRD is the object other people's plans get built on; one that was "roughly agreed" gets re-argued at the point it is most expensive to reopen.

Where it goes next depends on what is still open:

- **The approach isn't chosen** — `brainstorming` takes the agreed problem and works out how to solve it. It is user-invoke-only, so read and follow its `SKILL.md` rather than invoking it.
- **The approach is settled and the work is large** — `slice` cuts it into independently shippable pieces.
- **A single agreed piece needs implementable detail** — `draft-spec` writes the engineering specification under this document, and cites it.
- **The user wants it attacked rather than accepted** — `grilling`, only when they ask.

Asked for it as a file, offer `docs/prds/<YYYYMMDDHHMMSS>-<kebab-slug>.md` **when that directory already exists** and `~/.agents/prds/<YYYYMMDDHHMMSS>-<kebab-slug>.md` when it doesn't — the second carries `metadata.repo`. Never create `docs/prds/` to make room for it: the directory existing is how a repository opts in, and a PRD is exactly the document a team should agree to host before it appears. Name the path you wrote to.

Publishing to a tracker or a wiki is an outward-facing write. Never do it without a separate yes, and never invent a project key, a space, or a label to make it fit.

## Gotchas

- **A solution in the Problem section is the failure mode.** "Users need a bulk-export button" is a solution; "operations staff re-key 200 bookings a week into a spreadsheet, and the errors surface as double-bookings" is a problem. Written the first way, the PRD forecloses every cheaper answer — and there is usually a cheaper answer.

- **A success measure nobody will look up is decoration.** Prefer a number someone already tracks, or a behavior an observer could count, over one that would need instrumentation nobody has agreed to build. If the measure needs new telemetry, that is itself a requirement — say so in the document.

- **Out of scope is the section that does the work.** It is what stops the feature growing between agreement and delivery, and it is the first thing cut when the writer is in a hurry. A PRD with no non-goals has agreed to everything anyone reads into it.

- **Don't smuggle in the estimate.** Effort, dates, and team assignment are planning, made against a design that does not exist yet. Naming a sprint here turns a requirement into a commitment nobody costed.

- **A PRD is not an ADR and does not replace one.** A hard-to-reverse decision with non-obvious context needs its own record that outlives this document (AGENTS.md §7, *Engineering leverage & judgment*).

- **Don't reopen a settled approach to write the requirements behind it.** Where a design is already agreed and only the product framing is missing, harvest the framing and write it — pulling the approach back open under cover of "just capturing requirements" costs the conversation twice.

- **Accessibility is a requirement, not a follow-up.** Where the work has an interface, keyboard operation, labeling, and error states that say what to do next belong in **Constraints** — AGENTS.md §2, *Quality attributes (always design for these)*, makes them part of the change rather than a later ticket. A PRD that leaves them out is how they become the ticket nobody prioritizes.

## Tone

Plain, specific, and honest about what is still unknown. Write for a product manager who will forward it to someone who was not in any of the conversations. Assumptions are labeled, open questions are listed rather than resolved by confident phrasing, and no adjective is doing work a number could do.

## References

- [TEMPLATE.md](references/TEMPLATE.md) — the PRD template, what each section holds, and the self-check before showing a draft
