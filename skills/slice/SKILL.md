---
name: slice
description: Break a feature into independently shippable slices — split an epic into stories, sharpen a story into a job story, or scope work for incremental delivery. Use when asked to break down a feature, slice an epic, split work into stories, write job stories, decide what to ship first, or re-cut the remaining slices after one has shipped or overrun its scope. Not for building a slice once it is defined, not for writing the task-by-task implementation plan inside one already cut, and not for deciding what to build while the approach is still open.
argument-hint: "[feature description]"
---

# Feature slicing

Cut a feature into pieces that each ship on their own and each deliver something a user can see.

Feature to slice: `$ARGUMENTS`. If nothing came with the invocation, open with: **"What are you building? Describe the feature or capability — big or small."**

**This is a thinking tool, not a generator.** Lead the user to define the work through questions instead of filling it in for them. A slice list they didn't argue their way to is a list they won't follow.

**Be collaborative and rigorous at once.** Push back when a slice is too big, too vague, or not end-to-end. Agreeing with a bad slice is the failure mode, not conflict.

**It ends at the slice list.** No code, no tests, no tickets. The handoffs below take it from there.

If the user asks you to skip the questions and just produce the slices, draft them — then mark every assumption you had to invent, and hand it back for correction rather than presenting it as settled.

## When to use this skill

- Breaking a feature or epic into smaller pieces: "cut this into things we can ship weekly"
- Scoping or sharpening a story before anyone starts work
- Deciding what ships first, or in what order
- Writing job stories for a feature
- Naming the increments for something that has to ship incrementally behind a flag
- Re-cutting what's left of a sequence after a slice shipped, or after one overran its scope
- Not for building a slice once it's defined — that's `tdd`, or `feature-dev` for the whole chain
- Not for items already filed on an issue tracker — `triage` works those
- Not for writing the work up as a single spec document — that's `draft-spec`
- Not for cutting one slice into implementation tasks with file paths and steps — that's `draft-plan`, which runs after a spec and only when the implementer can't come back and ask. Tasks are review-sized steps inside a slice, so a task list is the build order this skill's [Gotchas](#gotchas) refuse to accept as a slice list
- Not for deciding *what* to build while the approach is still open — `brainstorming` comes first, and its architectural path hands the approved design here
- Not for stating the problem the feature exists to solve — `draft-prd` writes that for the product team, and a feature with no agreed problem behind it has nothing to slice toward
- Not for estimating, prioritizing a backlog, or splitting a large source file

`brainstorming`, `triage`, and `feature-dev` are all user-invoke-only, so the Skill tool refuses them. Route to any of the three by reading and following the target's `SKILL.md`, or by telling the user to invoke it themselves.

## Workflows

Run this as a conversation. Wait for the user's answers at each step before moving on.

### 1. Understand the work

Once the feature is known, ask conversationally — not as a form:

- **Who is this for, specifically?** Not "users" — which person, in which moment, with which need.
- **What does done look like?** When this ships, what can that person do that they can't today?
- **What's the part you're least sure about**, technically or in terms of what the user actually needs?

Listen for: vagueness about the user (the scope isn't understood yet), vagueness about done (it will expand), and whatever they flag as uncertain (that's where the risk lives). If an answer is vague, ask one follow-up before moving on. Don't slice work you don't understand.

**When there's a repository in front of you, spend a few minutes in it first.** What already exists decides which slice is actually the smallest: half of a proposed skeleton is often already built, and an existing seam makes a different cut cheaper. Read the feature's neighbors and any glossary or `CONTEXT.md`, and use the project's own words. Check the rejection knowledge bases too — the repo's `.out-of-scope/` and `~/.agents/out-of-scope/` — because a slice of something already declined needs that reasoning answered before it is cut, not after. Skip it when you arrived from a workflow that already mapped the codebase. Either way this is grounding only — what you find makes the questions specific and never answers them (see [Gotchas](#gotchas)).

**Move on when** you can name the person, the moment they're in, and what they'll be able to do that they can't today. Short of that, ask again.

### 2. Shape the slices

Take one of two paths based on the feature's size, decided by putting the feature *as stated* through the two tests below: if the whole thing ships on its own and one person can see the value, it's a single slice. **When it's a close call, take the large-feature path.** Sharpening an epic into one job story fails quietly — twelve acceptance criteria and nobody notices — while asking the minimum-value question about something already small costs one exchange and collapses back to a single slice. Don't announce which path you took: "this is an epic, so we'll do the breakdown" invites the user to defend the size instead of exploring it. When a caller has already made the size call and handed you one slice, take it — the tie-break is for an undecided feature, not permission to re-open someone else's ruling.

**The small-feature path** — it's already one slice, so sharpen it into a job story:

- "What's the specific situation the user is in when they need this?"
- "What do they want to do in that moment, and why does it matter?"
- "How would you know this is done — something you could demonstrate in 30 seconds?"
- "Is this actually one thing, or are you sneaking two things in?"
- "Is there a simpler version that still solves the problem?"

Push on the acceptance criteria: happy path, edge cases, error states. If pushing reveals multiple slices, switch to the large-feature path.

**The large-feature path** — it holds several slices, so guide the user to find them.

Start with: **"What's the absolute minimum a user would need to get any value from this at all — the smallest thing that's real, not a prototype?"**

That's the walking skeleton. The principle: **cut vertically through the stack** — a thin path through every layer that delivers real behavior — never horizontally, which builds a whole layer with nothing usable on top.

Push on it:

- "Could a user actually do something with that, or is it just plumbing?"
- "If you shipped only that, what feedback could you get from a real user?"

Then work outward:

- "What's the next most valuable thing to the user — not the next most obvious thing to build?"
- "What's the riskiest assumption? Should that be a slice?"
- "Is there anything here that only exists to support another feature? That's probably not a slice."
- "Which slices depend on each other, and which are actually independent?"

Validate each slice against **the two tests**:

1. **Can it ship on its own** — could it go to production with nothing after it? Building on behavior an earlier slice already shipped is fine; needing a *later* slice is not.
2. **Can a user or stakeholder see the value** — is this end-to-end, or just a layer?

A slice that fails either test is too big or isn't a slice. Worked examples of both paths, including a build order caught masquerading as a slice list: [EXAMPLES.md](references/EXAMPLES.md).

### 3. Sequence and hand back

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

`Ships when:` is the demonstration — the one path you'd show someone to prove the slice is live. The criteria are everything that has to hold for that to be true, including the boundaries and failures nobody demos. Three placeholders is not a quota: write as many as the behavior has, and no speculative ones.

`Depends on:` records **sequence, not coupling** — an earlier slice whose shipped behavior this one builds on. If a slice only makes sense once a *later* slice ships too, they aren't two slices; merge them.

Filled-in examples of every field: [EXAMPLES.md](references/EXAMPLES.md).

**For multiple slices**, guide the sequencing:

- "What ships first — not what's easiest to build, but what delivers the most learning or value earliest?"
- "Which slice has the most technical risk, and is it early enough in the sequence?"
- "If you ran out of budget after two slices, which two would you want shipped?"

After the list, give a one-paragraph sequencing rationale.

**Always close with:** "Look at your first slice. Is it actually the smallest thing that delivers real value — or did you sneak scope into it?" Wait for the answer; it is the last chance to catch a skeleton with scope hidden in it. After a multi-slice session, add one sentence on what the answer reveals about how they scope work.

### 4. Capture the list before it evaporates

A sequence agreed in conversation dies with it, and it's the artifact the next two weeks run on. Past one slice, ask where the list should live and write it there — a Markdown file at a path the user names, job stories verbatim so the criteria survive. One slice sharpened in three questions needs no file: say what you'd write, and let them decide.

This step files nothing and specs nothing. Putting the list on a tracker is an outward-facing write and a separate yes: ask where it goes, keep the dependency order, and say the count before creating anything. `triage` works those items once they exist, and is user-invoked, so read and follow its `SKILL.md`. `draft-spec` writes slice one up properly when a contractor or an unattended agent has to work it cold.

## Handing a slice off

Once the sequence is settled, `tdd` turns one slice's acceptance criteria into a red-green-refactor cycle — one slice at a time, in the order you just justified.

`fan-out` can put a slice per agent, but only across slices that all read `Depends on: none` and touch disjoint files. Parallelizing a slice that builds on one still unshipped turns a sequencing decision into a merge conflict.

For the whole chain rather than the build alone — explore, sharpen, build test-first, review, commit — that's `feature-dev`, which calls this skill as its shaping phase. Read and follow its `SKILL.md`, or tell the user to invoke it themselves.

## Re-slicing after something shipped

The common case is not a blank page. A slice shipped, or a build ran over its scope, and the rest of the list is now in question. Work the remainder, not the whole thing again:

- **Don't re-ask the skeleton question.** It's answered — something is live. The question now is what the next most valuable thing is *given* what users are doing with it.
- **Start from what shipping taught.** "What did you learn that you didn't know when we cut these?" is the whole re-entry interview when the answer is substantive, and one question is often all it takes.
- **Re-run [the two tests](#2-shape-the-slices) on every remaining slice.** A shipped slice turns `Depends on:` entries into satisfied ones, which can free two slices to run in parallel — or expose one that was only shippable as part of the piece that already went out.
- **Delete slices the feedback killed.** A slice nobody wants any more is not a slice to reshape. Say it's gone and why, so it doesn't reappear next quarter as an obligation.
- **Scope discovered mid-build re-cuts the remainder.** When a build overran because the slice was really two, the fix is to ship the smaller piece and re-cut what's left — never to append the overflow to the end of the list, which quietly grows the sequence past the point anyone still believes it.

## Gotchas

- **Reject horizontal slices.** "Build the database layer" or "set up the API" delivers nothing a user can touch. A layer isn't a slice, however much work it is.

- **"It's just one thing" is almost always wrong.** Push back. Most features hide two or three independently shippable pieces.

- **Past about five slices, check whether you sliced by task rather than by value.** A build order — model, then endpoint, then UI — masquerades as a slice list; collapse that and cut vertically again. It's a prompt to re-read the list against [the two tests](#2-shape-the-slices), not a cap: a quarter-sized epic can hold more, and if every entry passes both, the count is fine.

- **Every slice depending on the one before it is the same tell.** Real slices fan out from the skeleton; a single chain is a plan of work wearing job-story clothes.

- **A stack's layers are horizontal slices, and that's fine — for a stack.** `gh-stack` teaches `models <- api <- frontend`, precisely the cut this skill rejects, because a stack orders *review* within one shippable thing and nothing mid-stack ships. So neither direction converts: a stack's layer names are not a slice list, and this sequence is not a stack — `Depends on:` means the earlier slice is already live, so the next one is a fresh PR off the default branch, not a branch layered on an open one.

- **Don't confuse technical risk with user value.** The riskiest assumption should often ship first even when it isn't the most valuable, because it de-risks everything that follows.

- **A default-off flag is what makes an unfinished feature shippable, but flipping it isn't a slice.** Behavior-changing work ships dark and is enabled incrementally (AGENTS.md §5, *Safe rollout, feature flags & migrations*), so an early slice's visible value is often visible-with-the-flag-on, to a pilot group. Say which in `Ships when:`, or nobody can verify it.

- **Expand, backfill, and contract are steps inside a slice, not slices.** A migration nobody can see is the horizontal slice above in a costume; the schema change ships with the behavior that uses it.

- **Acceptance criteria that say "it works" say nothing.** Every criterion must be verifiable by someone who's never seen the feature.

- **Don't race to the deliverable format.** The questions in [Shape the slices](#2-shape-the-slices) are where the work happens; a filled-in template with unexamined answers is worth nothing.

- **Never answer your own questions from what you read in the codebase.** Grounding tells you what exists; it tells you nothing about who needs this or what done looks like. Slices derived from the code describe the code, and the acceptance criteria then assert your assumptions instead of the user's needs.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| The user insists the whole feature is one slice | Ask what they'd ship if the deadline halved. If an answer exists, so does a smaller slice. |
| Everything genuinely depends on everything | Usually the skeleton is missing. Find the thinnest path through all the layers, make that slice one, and re-test the rest against it. |
| Nothing is shippable until a compliance, contract, or launch date clears | That gates the release, not the slices. Slice as normal, ship behind the flag, and record the gate as a rollout note on the last slice. |
| A slice is only visible to an internal user or an operator | Still a slice — they're a user. Say which one in the job story, so "ships when" stays verifiable. |
| A slice is blocked on another team, a vendor, or an API nobody has written yet | `Depends on:` covers your own sequence, not theirs. It isn't shippable on its own until that lands, so either cut a slice against a stub or fixture that ships real behavior to a narrower audience, or sequence it last and name the external dependency as the risk. |
| The user rejects a cut you've pushed twice | It's their call. Record the slice as they want it, note the risk you see in one line, and move on — a third round spends the session's goodwill and doesn't change the outcome. |
| The user wants estimates | Out of scope here. Sequencing answers "what first"; sizing is a separate conversation. |
| The feature is a pure refactor with no user-visible change | There are no value slices to cut. Sequence it by risk instead, and use `codebase-design` to place the seams. |
| The conversation keeps reopening what to build | The approach isn't settled, so there's nothing to slice yet. Route to `brainstorming` (read and follow its `SKILL.md`) and come back with a design. |
| The slices are agreed but nobody can pick one up cold | A captured list is a record, not a brief. `draft-spec` writes one slice up so an agent or a contractor can work from it, and `draft-plan` goes one further into tasks and file paths when the implementer won't be able to ask anything. |
| A shipped slice made the rest of the list wrong | Expected. Re-cut the remainder against what shipping taught — [Re-slicing after something shipped](#re-slicing-after-something-shipped) — rather than starting the epic over. |

## References

Read this when you need it, not upfront.

- [EXAMPLES.md](references/EXAMPLES.md) — one epic sliced end to end with its sequencing rationale, one small feature sharpened into a single job story, and a build order caught pretending to be a slice list

## Attribution

- [thoughtbot/rails-consultant](https://github.com/thoughtbot/rails-consultant/tree/main/skills/slice) - slice, MIT
- Alistair Cockburn, *Crystal Clear* — the walking skeleton
- Alan Klement, "Replacing the User Story with the Job Story" — job stories
