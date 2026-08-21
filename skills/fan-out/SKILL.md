---
name: fan-out
description: Decompose a task into 2+ independent sub-problems and dispatch one agent per problem in parallel. Use when you face multiple failures across different subsystems, several unrelated investigations, or any workload that splits into pieces with no shared state. Covers prompt crafting, worktree isolation, and result integration.
argument-hint: "[description of the work to decompose]"
---

# Fan-Out

Decompose a task into independent sub-problems and dispatch one agent per problem, concurrently. Craft each agent's prompt so it is fully self-contained — agents inherit nothing from your session.

**Core principle:** one agent per independent problem domain. Let them work concurrently; integrate when they return.

## When to use this skill

- 2+ failures across different test files, subsystems, or services with unrelated root causes
- Several investigations that don't need each other's findings
- Parallel research into alternative approaches
- Any workload that splits into pieces with no shared state between them

Not for: related failures where fixing one may fix others; exploratory debugging where you don't yet know what's broken; work that requires seeing the full system state; agents that would edit the same files without worktree isolation.

A feature isn't yet a set of independent problems. Run `slice` first to find the pieces, then fan out only over the ones waiting on nothing unshipped — slices are normally *sequenced*, and dispatching a dependent one concurrently breaks the partition rule below before the first agent starts.

## 1. Identify independent domains

Before dispatching anything, partition the work. Each domain must be:

- **Self-contained** — solvable without knowing what the other agents find
- **Non-overlapping** — agents won't edit the same files (or use worktree isolation — see §3)
- **Clearly scoped** — you can state the goal and constraints in a paragraph

If two problems share state, a dependency, or the same files, they belong to one agent, not two.

## 2. Craft self-contained prompts

Agents start with zero context. Everything an agent needs to succeed must be in the prompt you write. A prompt that says "fix the bug we were looking at" fails because the agent has never looked at anything.

Every prompt should cover:

| Section | Purpose |
| --- | --- |
| **Goal** | What the agent should accomplish — one clear sentence |
| **Context** | The relevant error messages, file paths, test names, or symptoms — paste them, don't reference them |
| **Constraints** | What NOT to change; scope boundaries |
| **Expected output** | What the agent should return: a summary, a diff description, a diagnosis |

### Template

```
[Goal — one sentence stating what to accomplish]

Context:
[Paste the error output, failing test names, relevant file paths, or symptoms.
Include anything the agent needs to locate and understand the problem.]

Constraints:
- Only modify files in [scope]
- Do not change [out-of-scope areas]
- [Any other boundaries]

When done, return:
- What you found (root cause)
- What you changed and why
- Any concerns or open questions
```

### Prompt quality checklist

- Could a colleague who just joined the team act on this prompt with no other context? If not, add what's missing.
- Does it include the actual error messages or test output, not just "the failing tests"?
- Does it state what's out of scope, not just what's in scope?
- Does it say what to return?

## 3. Dispatch in parallel

Issue all Agent calls in a single response — multiple calls in one response run concurrently. One call per response runs sequentially.

```
Agent("Fix the 3 timing failures in agent-tool-abort.test.ts: ...")
Agent("Fix batch-completion-behavior.test.ts — tools not executing: ...")
Agent("Fix tool-approval-race-conditions.test.ts — execution count is 0: ...")
# All three run concurrently because they're in one response.
```

### Choosing agent types

- `general-purpose` — the default; good for most fix-and-investigate tasks
- `code-reviewer` — when the sub-task is reviewing code, not changing it
- `fork` — when the agent benefits from your conversation context (rare for fan-out; usually you want a clean slate)

### Read-only agents need no isolation

When agents only read code and report findings — investigations, research, reviews — they can all share the checkout safely. No worktrees needed.

### File-editing agents need worktree isolation

When two or more agents will modify files — even different files — each must work in its own worktree. Without isolation, concurrent edits collide. Do **not** use `isolation: "worktree"` on the Agent tool — it bypasses the `git-worktree` skill's placement and hook conventions.

Follow the `git-worktree` skill for all worktree operations — creation, config linking, dependency installation, and cleanup. This section only covers what the `git-worktree` skill doesn't: the fan-out-specific workflow of creating multiple worktrees, dispatching agents into them, and merging the results back.

#### Before dispatch: create one worktree per agent

Use the `git-worktree` skill to create each worktree. The one thing it doesn't specify for fan-out: **base agent branches on your current branch** — not the default branch. When you're already in a worktree on `feat-xyz`, the agents must branch from `feat-xyz` so their changes merge cleanly into your working state.

```sh
base_branch="$(git branch --show-current)"

# Create each worktree per git-worktree skill, passing the current branch as start-point
git worktree add <repo>.worktrees/fan-out-agent-1 -b fan-out/agent-1 "$base_branch"
git worktree add <repo>.worktrees/fan-out-agent-2 -b fan-out/agent-2 "$base_branch"
```

#### In each agent's prompt: enter the worktree and commit

The agent needs two instructions beyond its task: enter the worktree first, commit before finishing. Include the absolute worktree path — agents have no context about where you created them.

```
Your first step: enter the worktree at <absolute-worktree-path>
using EnterWorktree with that absolute path.

Then: [task description with full context]

Commit your changes on this branch before you finish.
When done, return: [expected output]
```

## 4. Integrate results

### Read-only agents (no worktrees)

1. **Read each summary.** Understand what each agent found.
2. **Synthesize.** Combine findings, resolve contradictions, act on the aggregate.

### File-editing agents (worktrees)

Each agent committed on its own branch. Merge those branches into your current branch — whether that's the default branch in the main checkout or a feature branch in a worktree.

```sh
# Review what each agent changed
git log ..fan-out/agent-1 --oneline
git diff ...fan-out/agent-1 --stat

# Merge each branch
git merge fan-out/agent-1
git merge fan-out/agent-2
```

If domains were truly independent, these merge cleanly. A conflict means the partition wasn't clean — resolve it manually rather than trusting either agent's version.

After merging, run the full test suite, linter, and type-checks — not just each agent's slice. Then run the `code-review` skill over the combined diff to catch cross-agent issues the individual agents couldn't see; spot-check for systematic errors.

Clean up the worktrees and branches per the `git-worktree` skill. One caveat: you can't remove a worktree your shell is inside — if you're in a worktree yourself, run cleanup with `git -C <main-checkout>` or exit first.

If an agent failed or returned inconclusive results, investigate its domain yourself rather than re-dispatching blindly — you now know more about the problem than you did before.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| **Too broad** — "Fix all the tests" | One clear problem per agent — "Fix the 3 timing failures in `abort.test.ts`" |
| **No context** — "Fix the race condition" | Paste the error output, name the file, describe the symptom |
| **No constraints** — agent refactors everything | State what's in scope and what's off-limits |
| **No output spec** — "Fix it" | "Return: root cause, what you changed, open questions" |
| **Related problems split apart** — fix one might fix the other | Investigate together first; only fan out what's truly independent |
| **No worktree for editing agents** — concurrent file edits collide | Create worktrees per `git-worktree` skill; don't use `isolation: "worktree"` |
| **Forgetting to commit** — agent changes strand in an unmerged worktree | Agent prompt must say "commit your changes before finishing" |

## Gotchas

- **Fan-out is not a substitute for understanding.** If you don't understand the problem well enough to partition it, you're not ready to fan out. Investigate first, dispatch second.
- **Agents can be confidently wrong.** A returned summary that says "fixed" doesn't mean fixed. Run the verification yourself.
- **Diminishing returns past ~5 agents.** Each agent you dispatch is one more result to read, integrate, and verify. If the fan-out grows large, you're probably partitioning too finely.
- **Don't re-dispatch failures blindly.** If an agent couldn't solve its problem, re-dispatching the same prompt won't help. Adjust the prompt with what you learned, or handle it yourself.
- **Branch the agents from your current state.** When you're already in a worktree on `feat-xyz`, base agent branches on `feat-xyz` — not on the default branch. Otherwise merging brings in unrelated divergence.

## Attribution

- [obra/superpowers](https://github.com/obra/superpowers/tree/main/skills/dispatching-parallel-agents) - dispatching-parallel-agents, MIT
