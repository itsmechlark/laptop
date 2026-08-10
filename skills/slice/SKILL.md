---
name: slice
description: Turn a feature into well-defined, independently shippable slices — whether it's an epic that needs breaking apart or a single story that needs sharpening into a job story. Agnostic to language, framework, and repo.
argument-hint: "[feature description]"
disable-model-invocation: true
---

# Slice

Turn a feature into slices that can each ship on their own and deliver visible value. This is a thinking tool, run as a conversation — lead the user to define the work through questions, don't fill it in for them.

## Phase 1: Understand the work

If no feature is specified, open with:

**"What are you building? Describe the feature or capability — big or small."**

Wait for their answer before proceeding.

Once the feature is known, ask three things — conversationally, not as a form:

- **Who is this for — specifically?** Not "users", but which person, in which moment, with which need.
- **What does done look like?** When this ships, what can that person do that they can't today?
- **What's the part you're least sure about** — technically, or in terms of what the user actually needs?

Wait for their answers. Listen for: vagueness about the user (the scope isn't understood), vagueness about done (it will expand), and whatever they flag as uncertain (that's where the risk lives). If an answer is vague, ask one follow-up before moving on. Don't slice work you don't understand.

## Phase 2: Shape the slices — Socratically

Based on the size of the feature, take one of two paths. Don't announce which — just follow the one that fits.

### Path A: The feature is already small

Sharpen it into one well-defined job story (format in Phase 3). Guide them:

- "What's the specific situation the user is in when they need this? What moment triggers the need?"
- "What do they want to do in that moment — and why does it matter to them?"
- "How would you know this is done? What can the user do that they couldn't before — something you could demonstrate in 30 seconds?"

Push on scope:

- "Is this actually one thing, or are you sneaking two things in? Could any part ship on its own?"
- "Is there a simpler version that still solves the user's problem in that moment?"

Push on acceptance criteria:

- "How would you verify this works? The happy path, the edge cases, the error states?"
- "If you handed this to someone who's never seen the feature, what checklist would confirm it's done?"

If pushing reveals the feature is actually multiple slices, switch to Path B.

### Path B: The feature is large

Guide them to find the slices themselves, one question at a time. Start here:

**"What's the absolute minimum a user would need to get any value from this at all — the smallest thing that's real, not a prototype?"**

This is the walking skeleton (from XP). It's almost always smaller than they think. The principle: **cut vertically through the stack** — a thin path through every layer that delivers real behavior — not horizontally, which builds a whole layer with nothing usable on top. Push on it:

- "Could a user actually do something with that, or is it just plumbing?"
- "Is that one slice, or two things that could ship separately?"
- "If you shipped only that, what feedback could you get from a real user?"

Once the first slice is clear, work outward:

- "What's the next most valuable thing to the user — not the next most obvious thing to build?"
- "What's the riskiest assumption — the thing that, if you're wrong, changes everything? Should that be a slice?"
- "Is there anything here that only exists to support another feature, not the user? That's probably not a slice."
- "Which slices depend on each other, and which are actually independent?"

As each slice takes shape, push on acceptance criteria (happy path, edge cases, error states — the same checklist as Path A). Keep pushing until they've named the full set. Validate each slice against two tests:

1. **Can it ship independently** — could it go to production on its own without the others?
2. **Can a user or stakeholder see the value** — is this end-to-end, or is it just a layer?

If a slice fails either test, it's too big or it isn't a slice.

## Phase 3: Deliverable

Format every slice as a job story: **When** [situation], **I want** [what], **so** [outcome].

### For a single slice

```
[Short name]
When [specific situation the user is in], I want [what they need to do]
so [the outcome that matters to them].
Ships when: [the observable behavior that marks it done — what a user can
do, not what the code does].
Acceptance criteria:
- [ ] [specific, verifiable condition — the happy path]
- [ ] [edge case or boundary condition]
- [ ] [error state or failure handling, if applicable]
Risk / learning: [what this slice tests or de-risks, or "low risk"].
```

Close with: **"Is this actually the smallest thing that delivers real value — or did you sneak scope into it?"**

### For multiple slices

First guide the sequencing:

**"Now order them. What ships first, and why — not what's easiest to build, but what delivers the most learning or value earliest?"**

- "Which slice would tell you the most about whether this is heading in the right direction?"
- "Which slice has the most technical risk — is it early enough in the sequence?"
- "If you ran out of budget after two slices, which two would you want shipped?"

Then produce the list. Format each as a job story (as above), adding a **Depends on:** line (a prior slice it requires, or "none"). After the list, give a one-paragraph sequencing rationale: why this order, what it de-risks early, what it leaves for later.

Close with: **"Look at your first slice. Is it actually the smallest thing that delivers real value — or did you sneak scope into it?"** Wait for their answer, then reflect in one short paragraph what it reveals about how they scope work — whether they tend to start too big or too small.

## Tone

Collaborative but rigorous. Push back on slices that are too big, too vague, or not actually end-to-end. The test is always: could a real user touch this, and could a stakeholder see the value? If not, it's not a slice yet.
