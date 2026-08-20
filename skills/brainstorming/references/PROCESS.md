# Brainstorming process

Detailed guidance for each phase. The spike path stops at "present the probe,
get a nod" and needs nothing here.

Most of this file is the architectural path. On the bounded path, read only
"Understanding the idea" and "Working in existing codebases" — the rest
describes ceremony bounded work is meant to skip.

## Architectural checklist

Track progress (e.g. with tasks) and complete items in order.

1. Explore project context — check files, docs, recent commits
2. Ask clarifying questions — one at a time, understand purpose, constraints,
   success criteria
3. Propose 2–3 approaches — with trade-offs and your recommendation
4. Present design — in sections scaled to their complexity, get user approval
   after each section
5. Write spec — invoke `draft-spec` to formalize the validated design, or write
   to a user-specified location
6. Self-review the spec — run the [SPEC-REVIEW.md](SPEC-REVIEW.md) checklist
   before handing it to the user
7. User reviews written spec — ask the user to review before proceeding
8. Transition to implementation — invoke `slice` to decompose the work, or
   `feature-dev` for the full build workflow

The visual companion is not a step — it's a cross-cutting tool. At any point
during steps 2–4, if a question would be clearer shown than described, offer it.
See [VISUAL-COMPANION.md](VISUAL-COMPANION.md).

## Understanding the idea

- Check the current project state first (files, docs, recent commits).
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
- Be ready to go back and clarify if something doesn't make sense.

Section-by-section approval is architectural only. A bounded design is one short
message — approach, files touched, testing — presented once, then stop and wait
for a yes.

## Design for isolation and clarity

- Break the system into smaller units that each have one clear purpose,
  communicate through well-defined interfaces, and can be understood and tested
  independently.
- For each unit, you should be able to answer: what does it do, how do you use
  it, and what does it depend on?
- Can someone understand what a unit does without reading its internals? Can you
  change the internals without breaking consumers? If not, the boundaries need
  work.
- Smaller, well-bounded units are easier to reason about — edits are more
  reliable when files are focused. When a file grows large, that's often a
  signal it's doing too much.

## Working in existing codebases

- Explore the current structure before proposing changes. Follow existing
  patterns.
- Where existing code has problems that affect the work (e.g., a file that's
  grown too large, unclear boundaries, tangled responsibilities), include
  targeted improvements as part of the design.
- Don't propose unrelated refactoring. Stay focused on what serves the current
  goal.

## After the design (architectural path)

Once the user approves the design in conversation, continue with steps 5–8 of
the architectural checklist above:

- **Write the spec** — invoke `draft-spec` to formalize the validated design
  into a spec document, or write directly to a user-specified location. Don't
  invent a repository-wide specs directory without the user's input.
- **Self-review the spec** — run the [SPEC-REVIEW.md](SPEC-REVIEW.md)
  checklist: scan for placeholders, check internal consistency, verify scope is
  implementable as one unit, and resolve ambiguous requirements. Fix issues
  inline — no separate review cycle.
- **User reviews the written spec** — ask the user to review before proceeding:
  > "Spec written and self-reviewed. Please take a look and let me know if you
  > want any changes before we move to implementation planning."
- **Transition to implementation** — invoke `slice` to decompose the work into
  shippable slices, or `feature-dev` for the full build workflow. The
  brainstorming skill's job ends here.
