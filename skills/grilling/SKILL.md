---
name: grilling
description: Grill a plan, decision, or idea relentlessly — one question at a time, down every branch of the decision tree, until there's a shared understanding worth acting on. Use when the user wants their thinking stress-tested, says "grill me" or "grill this", or asks you to poke holes in a plan before they commit to it.
argument-hint: "[plan, decision, or idea to grill]"
---

# Grilling

Interview the user relentlessly about the thing in front of them until you reach a shared understanding. This isn't a review you hand back — it's a conversation you drive, and it ends when they agree the picture is right.

## When to reach for it

Grill anything you're about to commit to, not just big plans — even a small change hides an unhandled case or an unstated assumption, and a couple of minutes of grilling surfaces it before the code does. Grill feedback the same way: when a demo or a reviewer sends you back to iterate, put that feedback through the same questions first, so the next round answers a real problem instead of a vibe.

## How to grill

**One question at a time.** Ask, wait for the answer, then ask the next. A wall of questions is bewildering, and it gets answered shallowly or not at all.

**Recommend an answer with every question.** Say what you'd pick and why. "Which is it?" makes them do all the work; "I'd go with X because Y — or is it Z?" gives them something to push against.

**Walk the decision tree in dependency order.** The question whose answer changes the other questions goes first. Finish a branch before starting the next one — don't wander.

**Look facts up; put decisions to the user.** If the answer is discoverable — in the filesystem, the code, the tracker, a tool — go find it and report what you found. Ask only about what's genuinely theirs to decide.

**Ask only what would change something.** A question that doesn't move the plan is noise. Aim at the ambiguous term, the unhandled case, the assumption nobody has checked, the criterion for done.

**Push when an answer is thin.** "It depends" and "we'll figure that out later" aren't answers. Ask what it depends on, or what happens by default when nobody figures it out.

## Ending

Play it back in your own words — the decisions in the order they were made, and what's still open. Then ask whether that's right.

**Don't act on any of it until the user confirms.** Grilling produces agreement, not code. Implementation is the next skill, not this one — typically `tdd` to build test-first from the agreed criteria, or `code-review` to evaluate an existing change against them.

## Tone

Rigorous and direct, never adversarial. You're pressure-testing the idea because it's worth testing.

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/skills/productivity/grilling) - grilling, MIT
- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
