# Isolating and merging file-editing agents

## When isolation is required

Agents that only read — investigations, research, reviews — share one checkout
safely. **Two or more agents that write files each need their own worktree, even
when the files they touch differ.** Concurrent edits in one checkout interleave:
one agent's uncommitted change becomes another's mystery diff, and a test run
sees a tree neither agent produced.

`git-worktree` owns every worktree operation — placement, branch naming, linking
git-ignored local config, installing dependencies, and cleanup. Follow it. What
follows is only the part it doesn't cover: running several worktrees at once for
one fan-out, and merging the results back.

**Don't reach for the Agent tool's `isolation: "worktree"` option.** It creates
its own worktree outside those conventions, so the layout, linked local config,
and hooks are all absent.

## Before dispatch: one worktree per editing agent

Create each one per `git-worktree`. The single fan-out-specific rule: **base the
agent branches on your current branch**, not the default branch. If you're
already on `feat-xyz`, an agent branching from the default branch will bring
unrelated divergence back with its merge.

```sh
base_branch="$(git branch --show-current)"

git worktree add <repo>.worktrees/fan-out-agent-1 -b fan-out/agent-1 "$base_branch"
git worktree add <repo>.worktrees/fan-out-agent-2 -b fan-out/agent-2 "$base_branch"
```

## In the prompt: enter the worktree, then commit

An editing agent needs two instructions beyond its task. Give the **absolute**
path — an agent has no idea where you created its worktree, and a relative path
resolves against a directory it isn't in.

```
Your first step: enter the worktree at <absolute-worktree-path>
(use the host's worktree tool if it has one, with that absolute path).

Then: [task description with full context]

Commit your changes on this branch before you finish.
When done, return: [expected output]
```

An agent that finishes without committing leaves its work in a worktree nobody
merges — recoverable with `git -C <worktree-path>`, but only if you notice.

## After they return: merge and verify

Each agent committed on its own branch. Merge those into your current branch,
whichever it is.

```sh
git log ..fan-out/agent-1 --oneline
git diff ...fan-out/agent-1 --stat

git merge fan-out/agent-1
git merge fan-out/agent-2
```

A clean merge is the evidence that the partition held. **A conflict means it
didn't** — resolve it by hand, understanding what each agent was trying to do,
rather than accepting either side wholesale.

Then verify the combined tree: full suite, linter, type-checks, and
`code-review` over the whole diff. Individually green slices say nothing about
their union.

## Cleanup

Remove worktrees and branches per `git-worktree`. One caveat it can't state for
you: **a worktree can't be removed while your shell is inside it** — run cleanup
with `git -C <main-checkout>`, or leave first.
