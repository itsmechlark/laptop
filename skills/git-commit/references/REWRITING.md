# Rewriting an existing commit

Amending, rewording, squashing, splitting, dropping, or reordering commits that already exist. This is a different job from creating commits, with two hazards the main workflow doesn't have: a rewrite can destroy uncommitted or committed work outright, and a rewrite of a pushed commit breaks every clone that already has it.

**Only rewrite what you haven't pushed**, unless the user explicitly asks for a force-push and you've told them what it costs.

## 1. Establish the safe set

```sh
git status -sb                        # ahead/behind against the upstream
git log --oneline @{upstream}..HEAD   # the commits not yet pushed
```

- `@{upstream}` errors → no upstream is configured, so nothing is pushed and the whole branch is yours to rewrite.
- Commits listed by that log are safe. Anything older is on the remote: rewriting it needs `git push --force-with-lease`, which rewrites history for everyone who has pulled the branch. Ask first, and say plainly that collaborators will have to reset. Policy blocks force-pushes for the agent, so the push itself is the user's to run — hand them the exact command.
- **Never rewrite the default branch**, and never rewrite someone else's commits on a shared branch.

## 2. Take an undo point

```sh
git rev-parse HEAD
```

Note that sha and hand it to the user in the report. Every operation below is recoverable with `git reset --keep <sha>`, and `git reflog` recovers it if the sha is lost. Take it before running anything, not after the first surprise.

Undo with `--keep`, not `--hard`: on a clean tree the two do the same thing, but `--keep` refuses rather than overwrite a file with uncommitted changes. `git reset --hard` is also blocked by policy for the agent, so offering it means handing the user a command you can't run yourself.

Commit or stash uncommitted work first. A rebase refuses to start with a dirty tree, and `git reset --hard` discards it without asking.

## 3. Pick the narrowest operation

| Ask | Operation |
| --- | --- |
| Reword the tip commit | `git commit --amend -F <file>` |
| Fold staged work into the tip commit, message unchanged | `git commit --amend --no-edit` |
| Fold new work into an older commit | `git commit --fixup <sha>`, then the scripted rebase below from `<sha>~1` |
| Reword an older commit | An empty `amend!` commit written by hand — `git commit --allow-empty -F <file>`, where the file's first line is `amend! <target's exact subject>`, then a blank line, then the replacement message — followed by the scripted rebase. Or `reset --soft` when the commit is near the tip |
| Squash a run of commits into one | `git reset --soft <base>`, then a fresh `git commit -F <file>` |
| Split one commit into several | `git reset <sha>` (mixed, keeps the changes unstaged), then re-stage and re-commit per the main workflow's grouping and staging steps |
| Drop a commit | `git rebase --onto <sha>~1 <sha>` |
| Reorder commits | Rarely worth the risk. Prefer `reset --soft` to the common base and re-commit in the order you want. |

**Interactive rebase is not available here** — `git rebase -i` opens an editor this environment can't drive. Since git 2.44, `--autosquash` works without `-i`, so no editor is involved:

```sh
git rebase --autosquash <base>
```

That consumes `fixup!` and `amend!` commits without prompting. Avoid `git commit --squash`: a `squash!` step stops the rebase for an editor to merge the two messages. `--fixup=reword:` would avoid that but refuses `-m` and `-F`, which is why the reword row writes its `amend!` commit by hand.

Keep the rebase bare. The older `GIT_SEQUENCE_EDITOR=true git rebase -i …` form is not equivalent here: a variable prefix stops a sandbox recognizing the command, and in a worktree the rebase then fails on a ref lock under `.git/worktrees/`. On git older than 2.44, use the `reset --soft` route instead.

For everything else, `git reset --soft <base>` plus a fresh commit does the same work with no rebase machinery and a much simpler failure mode — prefer it whenever the commits are contiguous and end at the tip.

## 4. Write a real message, not a concatenation

A rewritten message follows exactly the same rules as a new one — Conventional Commits subject, a body that explains the *why*, no AI attribution. See the format and voice sections of the main `SKILL.md`.

Squashing four `wip` commits means writing one message that explains the finished change. Read the originals first: the reasoning worth keeping is usually spread across them, and squashing is the moment it gets lost.

## 5. Verify, then report

```sh
git log --oneline <base>..HEAD    # the new shape
git diff <undo-point> HEAD        # content delta
```

For a pure reword or squash, `git diff <undo-point> HEAD` must come back **empty**. Anything else means the rewrite changed content as well as history — stop and reconcile it rather than reporting success.

Report the new log, what you changed, and the undo sha.

## Gotchas

- **A conflicted rebase leaves the branch mid-rebase**, with a detached HEAD and a half-applied history. `git rebase --abort` returns to where you started. Don't improvise your way forward through conflicts you weren't asked to resolve — abort, and report what conflicted.

- **`--amend` creates a new commit rather than editing one.** The original stays in the reflog and the sha changes, which is exactly why a pushed `--amend` diverges from the remote.

- **`git reset --hard` discards uncommitted work with no prompt and no reflog entry for it.** The reflog recovers commits, not a dirty working tree. Commit or stash before any reset, and use `--keep` for the undo.

- **`git push --force` overwrites whatever the remote gained since you last fetched.** If a force-push is genuinely wanted, the user runs `git push --force-with-lease`, which refuses when someone else has pushed. Force-pushes are the user's to run. Don't reach for `+<ref>`, a mirror push, or a flag spelling the policy happens not to match — that is getting around the rule, not following it.

- **Every rewrite command runs bare, from inside the checkout** — `git commit --amend`, `git reset`, `git rebase`. A wrapped one (`git -C`, `cd … &&`, a variable prefix) fails in a worktree on a lock file under `.git/worktrees/`, for the reason in the main `SKILL.md`'s staging step.

- **Squashing across a merge commit rewrites more than it looks like.** If `<base>..HEAD` contains a merge, stop and confirm the intent before flattening it.
