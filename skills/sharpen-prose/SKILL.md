---
name: sharpen-prose
description: Edit a draft toward sharper, more direct prose while keeping the author's voice, or name the AI-slop patterns in it without rewriting. Use when asked to tighten, sharpen, or de-slop writing, to cut the filler from a draft, to make prose sound less AI-generated, or "does this read as AI?". Works on any prose — a blog post, an email, a README, a design doc, a talk abstract. Not for drafting from scratch, and never rewrites text the user only asked about.
argument-hint: "[the draft, or a path to it]"
disable-model-invocation: true
---

# Sharpen prose

Take a draft and make it land harder without making it sound like someone else wrote it. The failure mode this skill exists to prevent is not a bad edit — it's a *tidy* one, where the filler comes out and the writer's voice goes with it.

Draft to work on: `$ARGUMENTS`. If nothing came with the invocation, ask for the draft and nothing else.

## When to use this skill

- Someone brings a draft — a post, an email, a README, a design doc, a talk abstract — and wants it tightened, sharpened, or de-slopped
- Someone asks whether their writing reads as AI-generated, or what is wrong with it
- Filler, hedging, or a closing flourish needs to come out of prose that is otherwise fine
- Another skill is drafting its own artifact and needs a pattern it can't name — read [PATTERNS.md](references/PATTERNS.md) directly, without this workflow

Not for writing a draft from scratch. A PRD is `draft-prd`, an engineering spec is `draft-spec`, a commit message is `git-commit`, a PR description is `pull-request`, a status update is `standup`. Each produces its own artifact against its own template; this skill only edits prose that already exists.

## Two modes

Pick one from how the request is worded, and say which you're in before you start.

| Request | Mode | You produce |
| --- | --- | --- |
| "tighten this", "sharpen this", "cut the slop" | **Edit** | The full edited draft plus a short list of what changed |
| "does this sound like AI?", "what's wrong with this?" | **Detect** | Named patterns with the offending line quoted and a one-line fix each. No rewriting |

When the wording is ambiguous, ask. Rewriting a draft someone only wanted assessed destroys work they can't get back, and it's the reason this skill is user-invoked only.

**Never claim the text was AI-generated, and never score it.** Detectors guess; named patterns are evidence the author can check for themselves. Report "this opens with two sentences of throat-clearing," not "72% likely AI."

## Before you start

Three questions, only where the answer would change the edit:

- **Audience and venue.** A conference abstract and an internal design doc tolerate different registers.
- **What the reader should walk away thinking or doing.** Without this you can't tell setup from filler.
- **How much latitude.** Some drafts want a scalpel; some want the argument restructured.

Read the whole draft before touching a word. An opening that looks like throat-clearing is sometimes carrying a thread the fourth paragraph pays off.

## What you never touch

Before cutting anything, identify the traits that make this prose *this author's* and protect them:

- Their vocabulary and sentence rhythm, including the long sentences and the fragments.
- Bluntness, profanity, jokes, and asides. Edge is not slop.
- Admissions of uncertainty, and the digressions that carry character or context.
- Sentences that are already strong. Smoothing them for consistency is the single most common way this edit goes wrong.
- Their level of polish. A deliberately rough draft stays rough.

**Add nothing.** No new claims, examples, statistics, quotes, or opinions. If a sentence needs a fact the author didn't supply, flag the gap rather than filling it.

**The carve-out that matters here:** when the draft was generated rather than written — an agent's own output, a first pass from a model — there is no voice to protect and the constraint above is inert. Cut hard and lead with the point. Everything else in this skill still applies.

## How to edit

Name the core point first, in one sentence: what the reader should take away. Every judgment below is measured against it, and there is no useful order to the rest — work through the draft and apply whichever applies.

- **The draft leads with the point.** Cut setup that is dead weight; keep setup that supplies context, tension, or character.
- **Cutting is proportional to the slop actually present.** A draft with three filler phrases gets three edits, not a compression pass.
- **Every sentence earns its place** through a concrete fact, a protected detail, or a direct verb.
- **Apply the portability test.** A sentence that could be dropped into any other company's post about any other product is filler — cut it, or make it specific.
- **Show rather than label.** "This was a significant improvement" becomes the number.
- **Active voice with a human subject**, wherever the sentence allows it.
- **Untangle without flattening.** Fix genuinely confusing sentences; leave spoken cadence, fragments, and shifts of pace alone.

The words and the named patterns to cut are in [PATTERNS.md](references/PATTERNS.md). Read it before the first edit — the patterns are what you're looking for, and several are invisible until you have the name for them.

## The gate

Before handing anything back, run [CHECKLIST.md](references/CHECKLIST.md) against your own output and repair what fails. It is a pass/fail gate, not a suggestion: an edit that strips the author's voice fails it, and so does one that leaves the kicker in.

## Output

**Edit mode.** The complete edited draft, then a **What changed** section — three to six lines naming what you cut and why, in the author's terms. Not a diff, and not an inventory of every comma.

**Detect mode.** One entry per finding: the pattern name, the line quoted, and a one-line fix. Ordered by how much the fix would improve the draft. Nothing else — no edited version, no overall verdict, no count.

In both modes, say what you deliberately left alone when the author might expect otherwise. "I kept the tangent about the hiring process — it's doing the work of the section" is worth a line.

## Where this fits

AGENTS.md §8 (*Writing for a human reader*) is the always-on standard that governs every artifact the other skills produce, and it stays the thing they cite. This skill is two things §8 is not: the long-form taxonomy behind it, and the capability of editing prose somebody else wrote.

So there are two ways in, and only one of them runs this workflow. A person brings a draft and this skill edits it. Or one of the drafting skills listed above hits its own self-check step, suspects a pattern it can't name, and reads [PATTERNS.md](references/PATTERNS.md) for the full list. §8 is the contract; this is the reference behind it.

## Gotchas

- **The tidy edit is the dangerous one.** An edit that makes every sentence the same length and every paragraph the same shape has produced slop from prose. Robotic rhythm is on the cut list for the draft *and* for your output.
- **Don't edit quoted examples.** A draft demonstrating bad writing contains bad writing on purpose. The same goes for quoted source material, code comments in a snippet, and anything inside a fence.
- **Filler is contextual.** "Honestly" is empty in one sentence and carrying the author's whole register in another. Cut the ones that stall the point; leave the ones doing work.
- **Em dashes are a tell in aggregate, not individually.** The em-dash pattern is about density. Replacing every one with a colon is its own tell.
- **One pass, then stop.** Iterating on prose past the point the checklist passes reliably makes it blander.

## Attribution

- [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop/tree/main/skills/no-ai-slop) - no-ai-slop, MIT
