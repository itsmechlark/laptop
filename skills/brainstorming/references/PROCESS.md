# Brainstorming process

Detailed guidance for each phase. The spike path stops at "present the probe,
get a nod" and needs nothing here.

Most of this file is the architectural path. On the bounded path, read only
"Understanding the idea", "Design for isolation and clarity", and "Working in
existing codebases" — the rest describes ceremony bounded work is meant to skip.

## Architectural checklist

Track progress (e.g. with tasks) and complete items in order.

1. Explore project context — check files, docs, recent commits, and the
   project's glossary/`CONTEXT.md` and ADRs
2. Ask clarifying questions — one at a time, understand purpose, constraints,
   success criteria
3. Propose 2–3 approaches — with trade-offs and your recommendation
4. Present design — in sections scaled to their complexity, get user approval
   after each section
5. Record the decisions that held still — hand cross-cutting, architectural, or
   vocabulary decisions to `domain-modeling` for `CONTEXT.md` or an ADR
6. Write spec — invoke `draft-spec` to formalize the validated design, or write
   to a user-specified location
7. Self-review the spec — run the [SPEC-REVIEW.md](SPEC-REVIEW.md) checklist
   before handing it to the user
8. User reviews written spec — ask the user to review before proceeding
9. Transition to implementation — `slice` to decompose the work, or
   `feature-dev` for the full build workflow

The visual companion is not a step — it's a cross-cutting tool. At any point
during steps 2–4, if a question would be clearer shown than described, offer it.
See [VISUAL-COMPANION.md](VISUAL-COMPANION.md).

`feature-dev` is user-invoke-only — read and follow its `SKILL.md` rather than
reaching for the Skill tool, which refuses it. `draft-spec`, `slice`,
`domain-modeling`, `codebase-design`, and `grilling` are invocable normally.

## Understanding the idea

- Check the current project state first (files, docs, recent commits).
- Read the project's own vocabulary and settled decisions before proposing
  anything: the glossary or `CONTEXT.md`, and any ADRs. Use the terms already in
  use rather than inventing parallel ones, and treat a settled decision as a
  constraint — surface the conflict instead of quietly designing around it.
  `draft-spec` will expect all of this downstream.
- Before asking detailed questions, assess scope: if the request describes
  multiple independent subsystems, flag this immediately. Don't spend questions
  refining details of a project that needs decomposition first.
- If the project is too large for a single spec, help the user decompose into
  sub-projects: what are the independent pieces, how do they relate, what order
  should they be built? Then brainstorm the first sub-project through the normal
  design flow. Each sub-project gets its own spec, plan, and implementation
  cycle.
- Ask questions one at a time to refine the idea.
- Prefer multiple choice questions when possible, but open-ended is fine too.
- Focus on understanding: purpose, constraints, success criteria.

## Exploring approaches (architectural path)

- If the shaky part is the request's premise rather than its details — the
  problem may not be the real problem, or the user's chosen approach may not
  serve it — say so before proposing approaches, and offer to invoke `grilling`
  to pressure-test it. Refining the details of the wrong idea is the expensive
  failure this path exists to avoid.
- Propose 2–3 different approaches with trade-offs.
- Present options conversationally with your recommendation and reasoning.
- Lead with your recommended option and explain why.
- YAGNI ruthlessly — remove unnecessary features from every approach and design.

## Presenting the design (architectural path)

- Once you understand what you're building, present the design.
- Scale each section to its complexity: a few sentences if straightforward, up to
  200–300 words if nuanced.
- Ask after each section whether it looks right so far.
- Cover: architecture, components, data flow, error handling, testing.
- Cover the operational shape too, because the spec has a section for it and an
  undiscussed section gets filled with guesses: rollout (does this need a
  default-off flag?), data migration and backward compatibility, security, and
  idempotency for anything retryable. Where one genuinely doesn't apply, say so
  explicitly rather than dropping it silently.
- Be ready to go back and clarify if something doesn't make sense.

Section-by-section approval is architectural only. A bounded design is one short
message — approach, files touched, testing — presented once, then stop and wait
for a yes.

## Design for isolation and clarity

When the design turns on where a module's interface goes, what it should hide,
or whether a seam is worth its indirection, use `codebase-design` — it owns the
vocabulary (module, secret, seam, depth, volatility) and the method for pricing
the change. Use its terms exactly and don't restate them here; a second,
weaker account of module design in this file is how the two drift apart.

## Working in existing codebases

- Explore the current structure before proposing changes. Follow existing
  patterns.
- Where existing code has problems that affect the work (e.g., a file that's
  grown too large, unclear boundaries, tangled responsibilities), include
  targeted improvements as part of the design.
- Don't propose unrelated refactoring. Stay focused on what serves the current
  goal.

## After the design (architectural path)

Once the user approves the design in conversation, continue with steps 5–9 of
the architectural checklist above:

- **Record the decisions that held still** — a cross-cutting or architectural
  choice, or a new domain term the design introduced, belongs somewhere more
  durable than the spec that consumes it. Hand those to `domain-modeling` to
  settle in `CONTEXT.md` or an ADR (context → decision → consequences,
  including the alternatives you rejected) before the spec is written. Don't
  duplicate that machinery here, and don't write an ADR for a decision that is
  local to this one change.
- **Write the spec** — invoke `draft-spec` to formalize the validated design
  into a spec document, or write directly to a user-specified location. Don't
  invent a repository-wide specs directory without the user's input.
- **Self-review the spec** — run the [SPEC-REVIEW.md](SPEC-REVIEW.md)
  checklist: scan for placeholders, check internal consistency, verify scope is
  implementable as one unit, and resolve ambiguous requirements. Fix issues
  inline — no separate review cycle.
- **User reviews the spec** — ask the user to review before proceeding:
  > "Spec drafted and self-reviewed. Please take a look and let me know if you
  > want any changes before we move to implementation planning."

  Say "written to `<path>`" only if you actually wrote a file there.
- **Transition to implementation** — invoke `slice` to decompose the work into
  shippable slices, or `feature-dev` for the full build workflow. `feature-dev`
  is user-invoke-only: read and follow its `SKILL.md`. The brainstorming skill's
  job ends here.
