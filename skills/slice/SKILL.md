---
name: slice
description: Break a feature into independently shippable slices — split an epic into stories, sharpen a story into a job story, or scope work for incremental delivery. Use when asked to break down a feature, slice an epic, split work into stories, write job stories, or decide what to ship first. Not for building a slice once it is defined, and not for deciding what to build while the approach is still open.
argument-hint: "[feature description]"
---

# Feature slicing

Turn a feature into slices that can each ship on their own and deliver visible value. This is a thinking tool: lead the user to define the work through questions rather than filling it in for them. Be collaborative but rigorous — push back when a slice is too big, too vague, or not end-to-end.

## When to use this skill

- User asks to break a feature or epic into smaller pieces
- User needs to scope or sharpen a story before starting work
- User wants to decide what to ship first or sequence delivery
- User asks to write job stories for a feature
- Not for building a slice once it's defined
- Not for items already filed on an issue tracker — use `triage` to work those
- Not for writing the work up as a single spec document — use `draft-spec` for that
- Not for deciding *what* to build when the approach is still open — use `brainstorming` first; its architectural path hands the approved design here

## Workflow

Run as a conversation. Wait for the user's answers at each step before moving on.

If they ask you to skip the questions and just produce the slices, draft them — then mark every assumption you had to invent, and hand it back for correction rather than presenting it as settled.

### 1. Understand the work

If no feature is specified, open with: **"What are you building? Describe the feature or capability — big or small."**

Once the feature is known, ask conversationally (not as a form):

- **Who is this for — specifically?** Not "users" — which person, in which moment, with which need.
- **What does done look like?** When this ships, what can that person do that they can't today?
- **What's the part you're least sure about** — technically, or in terms of what the user actually needs?

Listen for: vagueness about the user (scope isn't understood), vagueness about done (it will expand), and whatever they flag as uncertain (that's where the risk lives). If an answer is vague, ask one follow-up before moving on. Don't slice work you don't understand.

### 2. Shape the slices

Take one of two paths based on the feature's size. Don't announce which.

**The small-feature path** — it's already one slice, so sharpen it into a job story:

- "What's the specific situation the user is in when they need this?"
- "What do they want to do in that moment — and why does it matter?"
- "How would you know this is done — something you could demonstrate in 30 seconds?"
- "Is this actually one thing, or are you sneaking two things in?"
- "Is there a simpler version that still solves the problem?"

Push on acceptance criteria: happy path, edge cases, error states. If pushing reveals multiple slices, switch to the large-feature path.

**The large-feature path** — it holds several slices, so guide the user to find them:

Start with: **"What's the absolute minimum a user would need to get any value from this at all — the smallest thing that's real, not a prototype?"**

This is the walking skeleton. The principle: **cut vertically through the stack** — a thin path through every layer that delivers real behavior — not horizontally, which builds a whole layer with nothing usable on top.

Push on it:

- "Could a user actually do something with that, or is it just plumbing?"
- "If you shipped only that, what feedback could you get from a real user?"

Then work outward:

- "What's the next most valuable thing to the user — not the next most obvious thing to build?"
- "What's the riskiest assumption? Should that be a slice?"
- "Is there anything here that only exists to support another feature? That's probably not a slice."
- "Which slices depend on each other, and which are actually independent?"

Validate each slice against two tests:

1. **Can it ship on its own** — could it go to production with nothing after it? Building on behavior an earlier slice already shipped is fine; needing a *later* slice is not.
2. **Can a user or stakeholder see the value** — is this end-to-end, or just a layer?

A slice that fails either test is too big or isn't a slice.

### 3. Deliver the output

Format every slice as a job story: **When** [situation], **I want** [what], **so** [outcome].

```
[Short name]
When [specific situation], I want [what they need to do]
so [the outcome that matters to them].
Ships when: [observable behavior — what a user can do, not what the code does].
Acceptance criteria:
- [ ] [happy path]
- [ ] [edge case or boundary]
- [ ] [error state, if applicable]
Depends on: [an earlier slice whose behavior must already be live, or "none"].
Risk / learning: [what this slice tests or de-risks, or "low risk"].
```

`Depends on:` records **sequence, not coupling** — an earlier slice whose shipped behavior this one builds on. If a slice only makes sense once a *later* slice ships too, they aren't two slices; merge them.

**For multiple slices**, guide the sequencing:

- "What ships first — not what's easiest to build, but what delivers the most learning or value earliest?"
- "Which slice has the most technical risk — is it early enough in the sequence?"
- "If you ran out of budget after two slices, which two would you want shipped?"

After the list, give a one-paragraph sequencing rationale.

**Always close with:** "Look at your first slice. Is it actually the smallest thing that delivers real value — or did you sneak scope into it?" For multiple slices, wait for their answer, then reflect in one sentence what it reveals about how they scope work.

### Handing a slice off

Once the sequence is settled, `tdd` turns one slice's acceptance criteria into a red-green-refactor cycle — one slice at a time, in the order you just justified. `fan-out` can put a slice per agent, but only across slices that all read `Depends on: none` and touch disjoint files; parallelizing a slice that builds on one still unshipped turns a sequencing decision into a merge conflict.

## Gotchas

- **Reject horizontal slices.** "Build the database layer" or "set up the API" delivers nothing a user can touch — a layer isn't a slice, however much work it is.
- **"It's just one thing" is almost always wrong.** Push back — most features hide two or three independently shippable pieces.
- **More than about five slices means you sliced by task, not by value.** A build order ("model, then endpoint, then UI") masquerades as a slice list. Collapse it and cut vertically again.
- **Don't confuse technical risk with user value.** The riskiest assumption should often ship first, even if it isn't the most valuable — it de-risks everything that follows.
- **Acceptance criteria that say "it works" say nothing.** Every criterion must be verifiable by someone who's never seen the feature.
- **Don't race to the deliverable format.** The questions in *Shape the slices* are where the work happens; a filled-in template with unexamined answers is worth nothing.

## Attribution

- [thoughtbot/rails-consultant](https://github.com/thoughtbot/rails-consultant/tree/main/skills/slice) - slice, MIT
- Alistair Cockburn, *Crystal Clear* — the walking skeleton
- Alan Klement, "Replacing the User Story with the Job Story" — job stories
