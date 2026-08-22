---
name: fan-out
description: Decompose a task into 2+ independent sub-problems and dispatch one agent per problem in parallel. Use when you face multiple failures across different subsystems, several unrelated investigations, or any workload that splits into pieces with no shared state. Covers prompt crafting, worktree isolation, and result integration.
argument-hint: "[description of the work to decompose]"
---

# Fan-Out

Split a task into independent sub-problems, dispatch one agent per problem concurrently, then integrate what comes back and verify it yourself.

Work to decompose: `$ARGUMENTS`. Empty means whatever workload the conversation already has on the table.

**One agent per independent problem domain.** Agents inherit nothing from your session, so each prompt has to stand alone — and nothing an agent claims is verified until you verify it.

## When to use this skill

- 2+ failures across different test files, subsystems, or services with unrelated root causes
- Several investigations that need nothing from each other
- Parallel research into alternatives, kept independent so they don't converge on one answer
- Any workload that splits into pieces with no shared state
- Not for related failures where fixing one may fix the others — investigate together, then fan out only what stays independent
- Not for exploratory debugging: if you can't name the pieces, you can't partition them
- Not for work that needs the whole system state held in one head
- Not for small work: writing the prompt, integrating the result, and verifying it is a fixed cost per agent, so a handful of five-minute fixes lands sooner done serially
- Not for a feature that hasn't been broken down yet — `slice` finds the pieces, and slices are normally *sequenced*; fan out only over the ones waiting on nothing unshipped

## Workflows

### 1. Partition the work

Every domain must be:

- **Self-contained** — solvable without knowing what the other agents find
- **Non-overlapping** — no two agents touch the same files, or they run in separate worktrees
- **Statable in a paragraph** — goal and constraints, with no hand-waving left in them

Two problems sharing state, a dependency, or a file belong to one agent, not two.

**Write the partition down** — domain, agent, and what it owes you. That list is what you integrate against; results arrive at different times, so a domain nobody reported on is otherwise invisible.

### 2. Write self-contained prompts

An agent starts with zero context, so "fix the bug we were looking at" fails — it has never looked at anything. Each prompt carries a one-sentence goal, the context **pasted in** (error output, file paths, test names — pasted, never referenced), the scope boundaries — what not to touch, and what not to do at all — and what to return, in the same shape for every agent in the fan-out.

Template, the mandatory constraints, quality checklist, and the prompt failure modes worth recognizing: [PROMPTS.md](references/PROMPTS.md).

### 3. Dispatch concurrently

**Issue every agent call in a single response.** Calls made together run in parallel; one call per response runs them in series and buys nothing.

Choose each agent's type by role from whatever the host offers — a general-purpose agent for fix-and-investigate work, a read-only explorer for search and investigation, a review-oriented one for reading code rather than changing it. When the roster is unfamiliar, general-purpose is the safe default; an agent that inherits your conversation is almost never what fan-out wants, since a clean slate is the point.

Agents that only **read** files share one checkout safely. The moment an agent *runs* something — the test suite, a build, a formatter, a generator — it writes to the tree (`tmp/`, `log/`, coverage output), binds ports, and touches the dev database, so two of those collide with no source edit between them. Isolate them exactly like agents that **edit files**, which always need a worktree each even when the files differ: [WORKTREES.md](references/WORKTREES.md).

### 4. Integrate and verify

1. **Read every result**, against the partition list from step 1. Synthesize across them and resolve contradictions before acting on any single one.
2. **Merge the editing agents' branches** — see [WORKTREES.md](references/WORKTREES.md).
3. **Verify the combined state**, not each agent's slice: the full test suite, linter, and type-checks (AGENTS.md §4, *Definition of Done*).
4. **Run `code-review` over the combined diff.** Cross-agent problems — duplicated helpers, contradictory assumptions, a shared contract two agents changed differently — are invisible to each agent alone.

## Gotchas

- **Fan-out is not a substitute for understanding.** If you can't partition the problem, you don't yet understand it well enough to dispatch it. Investigate first, dispatch second — a bad partition costs more than working serially.

- **Agents can be confidently wrong.** A summary saying "fixed" is a claim, not a result. Require the command and its output in the report, then run the tests and read the diff yourself; never pass an agent's verdict on as your own.

- **Paste the evidence, don't point at it.** "The failing tests" and "the file we changed" resolve to nothing in a fresh session. Anything the agent needs to locate the problem goes in the prompt verbatim.

- **Independent domains still share the files nobody owns.** Lockfiles, `db/schema.rb`, migration timestamps, locale files, and barrel exports conflict on merge even when no source file overlaps. Name them in the constraints: one designated agent may touch them, or none may and you make the change yourself after merging.

- **Keep the base commit still.** Base agent branches on your current branch, not the default branch — from the default branch they drag unrelated divergence into the merge. And don't rebase, amend, or force-push that base while agents are out: their branches then point at a commit that no longer exists, and every merge becomes a conflict you can't attribute.

- **Don't use the Agent tool's own `isolation: "worktree"` option.** It bypasses the placement, config-linking, and hook conventions in `git-worktree`; create the worktrees with that skill instead.

- **An agent that doesn't commit strands its work.** Its changes sit in a worktree nobody merges. The prompt must say to commit on its branch before finishing.

- **Don't synthesize before every result is in.** A partial synthesis reads exactly like a complete one, to you as much as to the user. Wait for the last agent, or say explicitly which domain is still outstanding.

- **Diminishing returns past ~5 agents.** Every agent is one more result to read, integrate, and verify. A fan-out that keeps growing is usually partitioned too finely.

## Troubleshooting

- **Two branches conflict on merge** — the partition wasn't clean. Resolve by hand and understand both intents; taking either agent's version wholesale discards work whose absence nothing will fail on.

- **An agent failed or came back inconclusive** — investigate that domain yourself. Re-dispatching the same prompt repeats the same failure; you now know more about the problem than the prompt did.

- **An agent reports success but there's nothing to merge** — it never committed. Recover from its worktree with `git -C <worktree-path>` before removing anything.

- **A worktree won't remove** — you're inside it. Run cleanup with `git -C <main-checkout>` or leave the worktree first.

- **An agent went well outside its scope** — the prompt stated what was in scope but not what was off-limits. Revert, add the boundary, dispatch again.

## References

Read these when you reach that step, not upfront.

- [PROMPTS.md](references/PROMPTS.md) — prompt anatomy, a fill-in template, the constraints every prompt must carry, the quality checklist, and the mistake-to-fix table
- [WORKTREES.md](references/WORKTREES.md) — when isolation is required, preparing one worktree per agent, the extra prompt instructions, merging back, and cleanup

## Attribution

- [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents) - dispatching-parallel-agents, MIT
