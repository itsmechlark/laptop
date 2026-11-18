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

**Don't reach for the Agent tool's `isolation: "worktree"` option.** It branches
from the default branch rather than your current one, and links no local config
or dependencies.

## Before dispatch: one prepared worktree per agent

Create each one per `git-worktree`, whose *Choosing the base* section picks the
start-point. For a fan-out that answer is always **your current branch**, and
the reason is this skill's: if you're already on `feat-xyz`, an agent branching
from the default branch will bring unrelated divergence back with its merge.

Name each branch to `git-commit`'s convention with the fan-out's own type —
`feat-fan-out-agent-1` — so an agent's commit step doesn't stop on the name.

```sh
base_branch="$(git branch --show-current)"

git worktree add <repo>.worktrees/feat-fan-out-agent-1 -b feat-fan-out-agent-1 "$base_branch"
git worktree add <repo>.worktrees/feat-fan-out-agent-2 -b feat-fan-out-agent-2 "$base_branch"
```

Under a sandbox that keeps `.git/worktrees` read-only, `git worktree add` fails
even as a bare command. Create the branches first, then let the harness's own
worktree mechanism check each one out. In Claude Code that is `EnterWorktree`,
whose `WorktreeCreate` hook finds the existing branch:

```sh
git branch --show-current                       # note it: <base-branch>
git branch feat-fan-out-agent-1 <base-branch>
git branch feat-fan-out-agent-2 <base-branch>
# then, per agent: EnterWorktree with name = feat-fan-out-agent-N
#                  link config + install deps (git-worktree steps 3–4)
#                  ExitWorktree with action = "keep"
```

**Exit between worktrees.** Claude Code refuses `EnterWorktree` with `name`
while the session is already inside one, so each creation needs an
`ExitWorktree` with `keep` before the next — and the last one returns you to
your own branch, where the merge below happens. See "git in a worktree" in
`~/.agents/references/SANDBOX.md`.

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
finish. Run git as bare commands — `git add <paths>`, `git commit -F <abs-path>`
— never `git -C`, `cd … &&`, or a pipe: wrapped, they fail on a lock file under
.git/worktrees. Before your first commit, run `git rev-parse --show-toplevel`
on its own; if it doesn't print <absolute-worktree-path>, don't commit — leave
the changes uncommitted in the worktree and say so in your report.
Do not push, open a pull request, merge, or switch branches.
When done, return: [expected output]
```

The location check is there because a subagent's working directory can reset
between shell calls. In that case a bare `git commit` runs in your checkout and
lands the agent's work on your branch, while a wrapped one fails. The agent
can't fix that from inside, so it leaves the commit to you. The full set of
constraints every fan-out prompt carries is in [PROMPTS.md](PROMPTS.md).

**Commit what an agent left uncommitted before merging anything.** `git -C
<worktree-path> status` shows it; then `cd` into the worktree in its own call and
commit with bare commands per `git-commit`. An agent's uncommitted work is
otherwise left in a worktree nobody merges.

## After they return: merge and verify

Each agent committed on its own branch. Merge those into your current branch,
whichever it is.

```sh
git log ..feat-fan-out-agent-1 --oneline
git diff ...feat-fan-out-agent-1 --stat

git merge feat-fan-out-agent-1
git merge feat-fan-out-agent-2
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

Remove worktrees and branches per `git-worktree`, after the merge has landed.
**A worktree can't be removed while your shell is inside it**, so `cd` back to
the main checkout first. Try a bare `git worktree remove <abs-path>`; if a
sandbox refuses it with `Operation not permitted`, hand the user the commands.
In Claude Code, `ExitWorktree` can't remove them either, since each was exited
with `keep`. Delete the merged `feat-fan-out-agent-N` branches yourself with
`git branch -d`.
