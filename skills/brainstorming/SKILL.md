---
name: brainstorming
description: Explore an idea and shape it into a design before any code is written. Use when brainstorming a feature, thinking through an approach, designing before building, or when asked "how should we approach this" or "let's think this through." Classifies work as a spike, bounded change, or architectural, then walks the matching path to an approved design.
argument-hint: "[idea, feature, or design to explore]"
disable-model-invocation: true
---

# Brainstorming Ideas Into Designs

Turn ideas into fully formed designs through collaborative dialogue. Classify
how much process the request needs, work through the matching path — understand
context, refine the idea, present a design — and get approval before any
implementation begins.

Initial request: `$ARGUMENTS`

If no idea came with the invocation, open with: **"What are you thinking about
building? Describe the idea — rough is fine."** Classify only once you have an
answer; there is nothing to classify before that.

## When to use this skill

- User has an idea and wants to think it through before coding
- User asks to brainstorm, design, or explore an approach
- Before starting a feature, component, or behavioral change where the shape
  isn't obvious
- Not for stress-testing an existing plan — use `grilling` for that
- Not for writing a standalone spec from an existing conversation — use
  `draft-spec`
- Not for breaking a feature into slices — use `slice` (though the architectural
  path may hand off to it)

## The hard gate

Do NOT invoke any implementation skill, write any code, scaffold any project, or
take any implementation action until you have told the user what you intend and
they have approved it. This applies to every task on every path — the ceremony
scales with the task; the approval gate never does.

## Three paths

Before your first question, classify the request and say the classification out
loud — "this looks bounded, so I'll present a short design here rather than
write a spec" — so the user can override it.

**Spike** — a feasibility question ("can we...", "is it possible...", "quick and
dirty is fine") whose output is an answer, not code you keep. Present the
question and what you'll try in 2–3 sentences, get a nod, then investigate as
cheaply as correctness allows. No design doc, no spec. Report findings as a
recommendation; anything you built stays labeled throwaway. Probe code lives in
a scratch worktree (`git-worktree`) or `$TMPDIR` — never on the user's branch,
and never committed.

**Bounded** — a well-scoped change to code that already exists in this repo: a
new flag, a small endpoint, a one-file fix. Understanding the kind of app is not
enough — bounded means the flow you are changing is already here to read. If
there is no existing flow to change, the task is not bounded. Ask the clarifying
questions that matter, present a short design in chat (a few sentences to a few
short paragraphs — approach, files touched, testing), and STOP. Implementation
starts only after the user says yes.

**Architectural** — new projects, new subsystems, changes that restructure how
components fit together or alter interfaces others depend on. Follow the full
process: questions, approaches, sectioned design, written spec, then
implementation planning.

When in doubt between two paths, take the heavier one. The ratchet is one-way:
hidden complexity discovered mid-task upgrades the path — stop, say so, and step
up. Nothing downgrades mid-task.

Terminal states are path-bound. Spike: reported recommendation. Bounded:
approved design, then handoff. Architectural: approved spec, then `slice` or
`feature-dev`.

`feature-dev` is user-invoke-only, so the Skill tool refuses it — **read and
follow its `SKILL.md` directly**. Every other handoff here (`draft-spec`,
`slice`, `tdd`, `domain-modeling`, `codebase-design`, `grilling`) invokes
normally through the Skill tool. Whatever the reason a handoff's skill can't be
invoked, follow its `SKILL.md` rather than skipping the handoff.

## Checklists

Track progress (e.g. with tasks) and complete items in order.

**Spike:**
1. Explore project context — enough to frame the probe
2. Present question + probe plan — 2–3 sentences
3. Get approval — a nod is enough
4. Investigate — as cheaply as correctness allows
5. Report findings — a recommendation; label anything built as throwaway

**Bounded:**
1. Explore project context — check files, docs, recent commits
2. Ask clarifying questions — one at a time, the ones that matter
3. Present short design in chat — approach, files touched, testing
4. Get approval — STOP and wait for an explicit yes; presenting the design and
   starting in the same breath is skipping the gate

After approval, hand off to the normal development workflow: `tdd` for the
change itself, or `feature-dev` when the work wants the full slice → build →
review → commit chain. Prefer `tdd` for genuinely bounded work — `feature-dev`
opens by re-framing and re-slicing the thing you just designed. Brainstorming's
job ends at the approved design — no spec file, no plan document.

**Architectural:** explore context, ask clarifying questions, propose 2–3
approaches with trade-offs and your recommendation, then present the design in
sections (getting approval after each), record the decisions that held still,
write and self-review the spec, and hand off to implementation. The full
checklist is in [PROCESS.md](references/PROCESS.md).

**Visual companion (architectural only):** at any point during questions or
design, if a question would genuinely be clearer shown than described — a layout
mockup, a diagram, a side-by-side comparison — offer the visual companion as its
own message. If no visual question arises, never offer it. See
[VISUAL-COMPANION.md](references/VISUAL-COMPANION.md).

## Process

The detailed process for each phase — understanding the idea, exploring
approaches, presenting the design, working in existing codebases — is in
[PROCESS.md](references/PROCESS.md). Read it in full on the architectural path.
The bounded path needs only its "Understanding the idea", "Design for isolation
and clarity", and "Working in existing codebases" sections; the rest is
architectural ceremony. It also links to:

- [SPEC-REVIEW.md](references/SPEC-REVIEW.md) — spec self-review checklist
- [VISUAL-COMPANION.md](references/VISUAL-COMPANION.md) — browser-based mockups

Read these as needed during the architectural path, not all upfront.

## Red flags

| Thought | Reality |
|---------|---------|
| "This is too simple to need a design" | Simple means a short design, not no design. Two sentences in chat, then approval. |
| "I'll call it bounded and skip the spec" | Reaching for a label to skip work IS the doubt — take the heavier path. |
| "It's bounded and the design is obvious — I'll start while they read it" | The gate is the approval, not the design's length. Present, then stop until you hear yes. |
| "I understand this kind of app, so it's bounded" | Bounded measures the repo, not your familiarity. A new project has no existing flow — it is architectural. |
| "The spike works, so I'll keep the code" | A spike's output is an answer. Keeping the code is a new request — classify it. |
| "It grew, but I'm almost done — no need to re-classify" | Hidden complexity upgrades the path mid-task. Stop and say so. |
| "They approved the spike, so the follow-up change is approved too" | Each task gets its own classification and its own approval. |

## Gotchas

- **One question per message.** A wall of questions gets answered shallowly or
  not at all. Prefer multiple choice when possible.
- **Scope decomposition comes before design.** If the request describes multiple
  independent subsystems, flag it immediately — don't spend questions refining
  details of a project that needs decomposition first.
- **A request to skip the questions is not a request to skip the gate.** If the
  user wants the design without the interview, draft it — then mark every
  assumption you had to invent and hand it back for correction rather than
  presenting it as settled. The approval gate still stands.
- **Some requests don't need a design at all.** A typo, a rename, a one-line
  config change: say so in a sentence, offer to just make the change, and wait
  for the go-ahead. Don't manufacture ceremony to justify the invocation.

## Attribution

- [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/brainstorming) - brainstorming, MIT
