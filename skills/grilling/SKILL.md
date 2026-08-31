---
name: grilling
description: Stress-test a plan, decision, or idea by interviewing the user one question at a time, down every branch of the decision tree, until there's a shared understanding worth acting on. Use when asked to "grill me", "grill this", poke holes in a plan, pressure-test or challenge thinking, play devil's advocate, or find what a plan is missing before committing to it. Produces agreement, never code.
argument-hint: "[plan, decision, or idea to grill]"
---

# Grilling

Interview the user relentlessly about the thing in front of them until you reach a shared understanding. This isn't a review you hand back — it's a conversation you drive, and it ends when they agree the picture is right.

Subject to grill: `$ARGUMENTS`. If nothing came with the invocation, ask what they want grilled — and nothing else — before starting.

**Don't act on any of it until the user confirms.** Grilling produces agreement, not code. Running out of questions is not the end of the session; the user saying the understanding is shared is. This is the most common way the skill fails: a few questions, then an outline, then an implementation nobody approved.

## When to use this skill

- The user says "grill me", "grill this", "poke holes in this", "pressure-test this", "challenge my assumptions", or asks what a plan is missing
- Anything about to be committed to — a plan, an approach, a decision, a small change. A couple of minutes of grilling surfaces the unhandled case before the code does
- Feedback received from a demo or a reviewer, before iterating on it — so the next round answers a real problem instead of a vibe
- Another skill needs an interview, rather than improvising one of its own
- Not for choosing what to build while the approach is still open — that's `brainstorming`; read and follow its `SKILL.md`
- Not for writing an already-settled design up as a document — that's `draft-spec`, or `draft-plan` for the task-by-task version of one. "Plan" here means a proposed course of action to argue with, never an implementation plan to author
- Not for evaluating code that already exists — that's `code-review`

## How to grill

**One question at a time.** Ask, wait for the answer, then ask the next. A wall of questions is bewildering, and it gets answered shallowly or not at all. This is a deliberate house divergence from the upstream skill's round-based format; hold it.

**Recommend an answer with every question.** Say what you'd pick and why. "Which is it?" makes them do all the work; "I'd go with X because Y — or is it Z?" gives them something to push against. Phrase it so agreement is unambiguous — a recommendation that argues *against* the question as you worded it makes "yes" mean two things.

**Walk the decision tree in dependency order.** The question whose answer changes the other questions goes first. Finish a branch before starting the next one — don't wander.

**Look facts up; put decisions to the user.** If the answer is discoverable — in the filesystem, the code, the tracker, a tool — go find it and report what you found. Ask only about what's genuinely theirs to decide. When a lookup is expensive, use the `fan-out` skill to run it in the background and keep grilling the branches that don't depend on it; only the questions downstream of the lookup wait.

**Ask only what would change something.** A question that doesn't move the plan is noise. Aim at the ambiguous term, the unhandled case, the assumption nobody has checked, the criterion for done.

**Push when an answer is thin.** "It depends" and "we'll figure that out later" aren't answers. Ask what it depends on, or what happens by default when nobody figures it out.

**Keep a running ledger.** Track what's settled, what's still open, and what you looked up, and carry it forward as the conversation grows. A long grilling that has lost track of its own answers re-asks a settled question, which reads as not having listened.

**Rigorous and direct, never adversarial.** You're pressure-testing the idea because it's worth testing.

## Ending

Play it back in your own words — the decisions in the order they were made, and what's still open. Then ask whether that's right.

**Write decisions down as they land, once the session is long enough to lose them.** Past a handful of settled branches, the ledger is the only record that a decision was made and why, and it dies with the session. Capture each one where it belongs as it lands — a term in `CONTEXT.md`, a hard-to-reverse trade-off in an ADR (`domain-modeling` owns both formats) — rather than reconstructing the whole session from memory at the end. Short sessions don't need this; a two-question grilling that writes an ADR is ceremony.

Once they confirm, hand off rather than continuing here:

| What the agreement is | Where it goes |
| --- | --- |
| Behavior to build | `tdd` — a failing test from the agreed criteria first |
| A change that already exists, now with criteria to judge it against | `code-review` |
| More than one independently shippable piece | `slice` |
| Something that needs writing up before anyone builds it | `draft-spec` |
| Terms that had to be pinned down to get here | `domain-modeling` — capture them in `CONTEXT.md` or an ADR before they drift |

## Gotchas

- **Never answer a decision yourself.** Facts are yours to find; decisions are the user's to make, and a grilling that supplies both has produced your opinion rather than theirs. Bounded, reversible choices (a variable name, a test's shape) don't need a question — anything the user would want a say in does.

- **Running inside another workflow is where this breaks most.** When `triage`, `find-bugs`, or `draft-spec` routes here, the surrounding resolve-this-ticket frame reads as license to keep moving, and the interview collapses into two questions and a plan. The host workflow's momentum is not consent: the confirmation gate is still the user's.

- **There is no question cap, and a long session is a scoping signal, not a length problem.** Some plans need three questions and some need fifty. When a session won't converge, the subject is usually too big — say so and hand it to `slice` rather than grinding through.

- **Don't grill something that doesn't exist yet.** If the user has a problem but no plan, there's nothing to pressure-test; the questions come out as an interrogation about work they haven't done. Say what's missing and route to `brainstorming` (read and follow its `SKILL.md`).

- **A question the user can't answer without a fact is your failure, not theirs.** Go find the fact, then ask the decision it unblocks.

- **Silence isn't assent.** An unanswered or sidestepped question stays open — carry it in the ledger and put it back on the table before playing anything back.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| The user answers "you decide" | Decide, state what you decided and the consequence you're accepting, and note it as yours in the playback. Don't launder it as agreement. |
| An answer contradicts an earlier one | Name both and ask which holds. A contradiction resolved silently means the playback is wrong. |
| The user says to wrap up | Stop asking. Play back what's settled, list what's still open as open, and let them decide whether that's enough. |
| The plan collapses mid-grill | That's a successful grilling. Say what broke it, and route to `brainstorming` (read and follow its `SKILL.md`) rather than salvaging a plan the user has already lost faith in. |
| The subject keeps growing with every answer | It's an epic. Stop and hand it to `slice`, then grill one slice. |
| You've run out of questions | Play it back and ask for confirmation. Don't manufacture a question to look thorough, and don't start building. |

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling) - grilling, MIT
- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
