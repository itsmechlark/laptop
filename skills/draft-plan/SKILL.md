---
name: draft-plan
description: Write a task-by-task implementation plan an implementer can execute cold, from one slice or spec already agreed — exact file paths, the interface each task consumes and produces, and ordered steps carrying real code instead of placeholders. Use when handing work to a subagent, a parallel dispatch, a contractor, or a future session that cannot come back and ask, or when asked to write an implementation plan or plan the tasks for something already specified. Not for deciding what to build, not for cutting work into shippable slices, and never for executing the plan it writes.
argument-hint: "[slice or spec to plan]"
---

# Draft plan

Write the task-by-task brief for one slice, aimed at an implementer who cannot ask you anything.

Subject: `$ARGUMENTS` — the slice or spec to plan. Empty means whatever the conversation has already settled on.

**The plan exists because the implementer has no judgment available.** Someone with the repository open reads the spec and decides where the code goes, and that judgment beats anything written here — which is why `draft-spec` withholds file paths deliberately, so it survives contact with a codebase that keeps changing. This skill supplies exactly what the spec refuses. The staleness is only worth paying for when the implementer is cold: a fresh subagent, one arm of a parallel dispatch, a contractor, your own next session after the context is gone.

**It ends at the saved plan.** Writing a plan and executing it are two turns, always — see [The handoff](#the-handoff).

## When to use this skill

- One slice is agreed, and whoever builds it will not be you, in this session, with this conversation in front of them
- Several tasks will run in parallel, and each implementer has to know the names and types its neighbors define
- Work is going to an unattended agent, a contractor, or a session that will start after a context reset
- A spec is agreed but nobody can start from it cold, because it settles what to build and deliberately not where anything goes
- Not when you are about to build it yourself — read the spec and build. `feature-dev` runs that chain end to end, and a plan written to be executed immediately by its own author is ceremony that is stale by the first commit
- Not for cutting a feature into independently shippable pieces — that's `slice`, which runs first and produces the one slice this plans
- Not for the engineering specification itself — that's `draft-spec`. A plan argues from a spec, and a plan with no spec behind it is a guess wearing file paths
- Not for stating the problem the work exists to solve, which is `draft-prd`'s, two layers up
- Not for choosing the approach while it is still open, which is `brainstorming`'s
- Not for dispatching the agents — `fan-out` partitions and dispatches; this writes the task briefs it sends
- Not for placing a seam or naming a boundary — `codebase-design` decides where code should go; this only records the decision
- Not for executing anything: `tdd` drives one task, `feature-dev` the whole chain

## Does this need a plan?

Run this before writing anything. All three must hold:

1. **The implementer cannot ask.** Name them — the subagent, the contractor, the session that will have forgotten this one. If the honest answer is "me, next," the spec is already enough and the plan is dead weight that rots from the first commit.
2. **The approach is settled.** Every rival option has a resolution you can point at. A plan freezes a guess into exact file paths, and file paths get read as decided.
3. **It is one slice.** If the tasks span several independently shippable things, you are planning an epic. Go back to `slice`, take one, plan that.

When one fails, say which. The most useful thing this skill produces is sometimes the sentence *"the spec already covers this — build from it."*

## Workflows

### 1. Ground the plan in the repository

Every path in a plan is a claim about a codebase, so verify before writing:

- The spec, in full — it is the argument the plan executes, and it travels with the plan
- The files the work lands in, so `Modify:` names something real at a line range that exists
- How this repository tests: the runner, where specs live, what a test file is named
- The project's `CONTEXT.md` and any relevant ADRs — use the settled vocabulary rather than coining a synonym

A guessed path sends a cold implementer to a file that isn't there, and they cannot ask which one you meant.

### 2. Map the file structure before cutting tasks

Decide what each file is responsible for before deciding what each task does. This is where decomposition actually gets settled; doing it inside the task list produces tasks shaped by writing order instead of by responsibility.

Files that change together belong together — split by responsibility, not by technical layer. In an existing codebase, follow the patterns already there. A plan is not the place to unilaterally restructure, though splitting a file the work already makes unwieldy is fair.

Where a seam belongs is `codebase-design`'s question. Route there when the answer isn't obvious from existing patterns, and come back with it.

### 3. Cut the tasks

**A task is the smallest unit that carries its own test cycle and is worth a fresh reviewer's gate.**

Fold setup, configuration, scaffolding, and documentation into the task whose deliverable needs them. Split only where a reviewer could reasonably reject one task while approving its neighbor. Every task ends with something independently testable.

That is a different cut from `slice`'s. A slice is vertical and ships; a task is a review-sized step inside one slice and usually ships nothing on its own.

### 4. Write the interfaces

**Each task's implementer sees only their own task.** They cannot read Task 2 to learn what Task 5 will call. So every task states both sides:

- **Consumes** — what it uses from earlier tasks, as exact signatures
- **Produces** — what later tasks rely on: exact names, parameter and return types

This block is the whole reason a plan survives parallel execution. Dropping it is what makes a plan fail three tasks in, when two implementers pick different names for the same function and neither is wrong.

### 5. Write the steps

Steps are single actions, small enough to be unambiguous. Test-first is the house requirement (AGENTS.md §1, *Engineering mindset (plan & code like a staff engineer)*), so the shape is: write the failing test, run it and watch it fail, write the minimal code, run it green, commit. `tdd` owns that cycle and its rules — cite it rather than re-teaching it in every task.

Include the actual test code, the actual command, and the expected result. The header and task templates are in [TEMPLATE.md](references/TEMPLATE.md).

### 6. Self-review against the spec

Run this yourself before showing anything, and fix inline — there is no second pass.

1. **Spec coverage** — walk each requirement and point at the task implementing it. A requirement with no task is a gap; add the task.
2. **Placeholder scan** — search for the patterns in [No placeholders](#no-placeholders). Every hit is a defect.
3. **Name consistency** — do the types, signatures, and property names in later tasks match what earlier tasks defined? `clearLayers()` in Task 3 and `clearFullLayers()` in Task 7 is a bug that surfaces only at execution time.
4. **Global constraints** — version floors, naming rules, rollout flags, platform requirements, copied from the spec verbatim into their own section. Every task inherits them.

## No placeholders

These are plan failures, not style preferences. Each one costs a round trip the implementer cannot make.

| Never write | Why |
| --- | --- |
| "TBD", "TODO", "fill in details" | The decision is still yours; deferring it means nobody makes it |
| "Add appropriate error handling", "handle edge cases" | Appropriate to what? This is the sentence a plan exists to replace |
| "Write tests for the above", with no test code | The test is the task's definition of done. Without it the task has none |
| "Similar to Task 4" | Tasks are read out of order and in isolation. Repeat the code |
| A step saying what to do with no command or code | If you can't write it, you haven't decided it |
| A type, function, or method no task defines | The implementer invents one, and it won't match |

## The handoff

Show the plan, save it where the user asks, and stop there. With no convention to follow, offer `docs/plans/<YYYYMMDDHHMMSS>-<kebab-slug>.md` **when that directory already exists** and `~/.agents/plans/<YYYYMMDDHHMMSS>-<kebab-slug>.md` when it doesn't — the plan then carries `metadata.repo`, the repository's name. Never create `docs/plans/` to make room for the file: the directory existing is how a repository opts in, and most repositories belong to other people. Name the path you actually wrote to.

Then name the execution route instead of taking it:

- **Parallel** — `fan-out` partitions and dispatches. One task brief per agent prompt, pasted whole; worktree isolation is that skill's rule
- **Sequential, unattended** — one agent per task, reviewed between tasks
- **Sequential, yourself** — `tdd` per task, `code-review` over the result, `git-commit` to land it. When the slice is still loose, `feature-dev` runs that chain; read and follow its `SKILL.md`

**Writing the plan and executing it are two turns.** A plan executed in the same breath was never read by the person who asked for it, and the tasks were never the point — building it directly would have been faster. Ask which route, or wait to be told.

## Gotchas

- **A plan is disposable; the spec is durable.** File paths go stale, which is exactly why `draft-spec` refuses them. Write the plan immediately before execution rather than filing it beside the spec — a plan found six weeks later describes a repository that no longer exists, and reads as authoritative anyway.

- **Don't plan the epic.** A plan spanning several shippable pieces is a waterfall document wearing task headers. `slice` cuts first; this plans one of the results.

- **The plan cannot settle what the spec left open.** You will feel the ambiguity as a task whose steps you can't write. Say what's open and stop — inventing the answer buries a decision nobody made inside a document the implementer can't argue with.

- **Exact line ranges rot fastest.** `Modify: path/to/file.rb:123-145` is precise the day you write it and wrong after any edit above line 123. Name the method or class too, so a stale number stays recoverable.

- **An interface you never checked against the spec is fiction.** Producing a `Reservation#deposit_status` the spec never mentions means the plan invented a design decision. Trace every name back to the spec or to code that already exists.

- **Test-first is a requirement, not a template flourish.** The step shape is what makes an unattended implementer follow a cycle nobody can talk them into mid-run. Steps that write code before the test produce exactly the run `tdd`'s Iron Law exists to prevent.

- **Global constraints are inherited silently.** An implementer working one task reads their task, not the header. Anything that must hold everywhere goes in Global Constraints *and* in the tasks where a violation is plausible — a default-off rollout flag (AGENTS.md §5, *Safe rollout, feature flags & migrations*) is the usual one.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| The user asks for a plan and will obviously build it themselves | Say so and offer the spec instead. If they still want it, write it — as scratch, not as an artifact to keep |
| The spec has no acceptance criteria to write tests against | The gap is in the spec. `draft-spec` fills it; a plan that invents criteria pins behavior nobody agreed to |
| A task keeps growing past one reviewable change | It's two tasks. The tell is a step list whose middle third could be reviewed and rejected on its own |
| Nothing can be ordered — every task depends on every other | The file structure is wrong, not the ordering. Go back to [step 2](#2-map-the-file-structure-before-cutting-tasks), or route to `codebase-design` |
| The plan runs to fifteen tasks for one slice | Either the tasks are steps in costume, or the slice was an epic. Check the second first |
| There is no spec, only a conversation | Write the spec first with `draft-spec`, or this plan silently becomes one — without the review a spec gets |
| The user wants it executed straight away | Confirm the route, then start a new turn. Never both in one |
| The work is a mechanical sweep over many files | A task per file is noise. One task carrying the pattern, the file list, and the verification is the whole plan |

## References

Read this when you reach step 5, not upfront.

- [TEMPLATE.md](references/TEMPLATE.md) — the plan header, the Global Constraints block, the task template with its Interfaces section, and a worked task

## Attribution

- [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/writing-plans) - writing-plans, MIT
