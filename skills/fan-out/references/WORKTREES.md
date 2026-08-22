# Isolating and merging fan-out agents

## When isolation is required

**Two or more agents that write files each need their own worktree, even when
the files they touch differ.** Concurrent edits in one checkout interleave: one
agent's uncommitted change becomes another's mystery diff, and a test run sees a
tree neither agent produced.

Agents that only **read** files can share a checkout. But "read-only" describes
the source, not the tree: an agent that *runs* the test suite, a build, a
formatter, or a generator writes to `tmp/`, `log/`, and coverage output, binds
ports, and touches the dev database. Two of those collide with no source edit
between them, and the symptoms look like real failures. Give them worktrees too,
or let only one of them run anything.

`git-worktree` owns every worktree operation — placement, branch naming, linking
git-ignored local config, installing dependencies, and cleanup. Follow it. What
follows is only the part it doesn't cover: running several worktrees at once for
one fan-out, and merging the results back.

**Don't reach for the Agent tool's `isolation: "worktree"` option.** It creates
its own worktree outside those conventions, so the layout, linked local config,
and hooks are all absent.

## Before dispatch: one prepared worktree per agent

Create each one per `git-worktree`. The single fan-out-specific rule: **base the
agent branches on your current branch**, not the default branch. If you're
already on `feat-xyz`, an agent branching from the default branch will bring
unrelated divergence back with its merge.

```sh
base_branch="$(git branch --show-current)"

git worktree add <repo>.worktrees/fan-out-agent-1 -b fan-out/agent-1 "$base_branch"
git worktree add <repo>.worktrees/fan-out-agent-2 -b fan-out/agent-2 "$base_branch"
```

**Then finish the setup — link the git-ignored local config and install the
dependencies — in every worktree, before any agent is dispatched.** A fresh
worktree holds only tracked files, so an agent sent into one hits a missing
`node_modules`, an absent `.env`, or unlinked local agent config, and burns its
turns diagnosing your setup instead of its task. Never put the setup in the
prompt: agents installing dependencies concurrently is another collision, and
each one pays for a step you could do once per worktree.

That setup is also the honest price of an editing fan-out: N worktrees means N
dependency installs. When it dominates the work itself, the fan-out isn't
earning its keep — do the domains serially in one worktree.

**Leave the base commit alone while the agents are out.** Rebasing, amending, or
force-pushing the branch they forked from leaves their branches pointing at a
commit that no longer exists, and every merge below turns into a conflict you
can't attribute.

## In the prompt: enter the worktree, then commit

An editing agent needs two instructions beyond its task. Give the **absolute**
path — an agent has no idea where you created its worktree, and a relative path
resolves against a directory it isn't in.

```
Your first step: enter the worktree at <absolute-worktree-path>
(use the host's worktree tool if it has one, with that absolute path).
Its dependencies and local config are already installed — don't reinstall them.

Then: [task description with full context]

Run the tests covering your change, then commit on this branch before you
finish. Do not push, open a pull request, merge, or switch branches.
When done, return: [expected output]
```

The full set of constraints every fan-out prompt carries is in
[PROMPTS.md](PROMPTS.md). An agent that finishes without committing leaves its
work in a worktree nobody merges — recoverable with `git -C <worktree-path>`,
but only if you notice.

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

Expect conflicts in the files no domain owns, even when the source files were
cleanly split: `Gemfile.lock` and other lockfiles, `db/schema.rb`, migration
timestamps, locale files, generated clients, barrel exports. Two agents each
adding a dependency conflict every time. Prevent it in the constraints — one
designated owner per shared file, or nobody, and you make the change yourself
after merging. Regenerate rather than hand-merge whatever is generated: run
`bundle install`, the migration, or the codegen once on the merged tree.

Then verify the combined tree: full suite, linter, type-checks, and
`code-review` over the whole diff. Individually green slices say nothing about
their union.

## Cleanup

Remove worktrees and branches per `git-worktree`. One caveat it can't state for
you: **a worktree can't be removed while your shell is inside it** — run cleanup
with `git -C <main-checkout>`, or leave first.
