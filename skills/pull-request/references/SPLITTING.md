# Splitting a wide build into narrow PRs

When a feature was built wide — proven end to end on a throwaway branch — don't open one sprawling PR from that branch. Small PRs flow; large ones sit.

## Decide the set first

The target is the smallest group of independently reviewable PRs, each safe to merge on its own. Work it out before opening anything, and name for each one what it carries, what it depends on, and whether it can land alone.

**Size is the cheap signal, not the decision.** Much past ~300 lines of production code in one PR — the budget `feature-dev` carries per slice — and a split is usually available. It's a prompt to look, not a rule: a mechanical rename across forty files is one reviewable change at any size, and 200 lines spanning two unrelated concerns is already two PRs.

**Show the proposed split before opening anything** — the PRs, what each carries, and which stack — so it can be corrected while it's still a plan.

## Cut each PR fresh off the default branch

Each in its own worktree; the `git-worktree` skill covers creating and placing them. The scratch branch's history is throwaway, so it never becomes the PR: carry over only the slice that PR owns, and let the rest stay behind.

That means each PR's diff is small by construction rather than by discipline — you are not trying to explain a subset of a wide branch, you are shipping a branch that only ever held one change.

## Stack only when a dependency is real

A change that depends on code another PR in the set introduces stacks on that PR; everything independent branches straight off the default branch. Stacking for convenience buys a rebase chain you'll regret once the bottom PR gets review feedback.

When a stack is genuinely necessary:

- **Point the child at its parent** — `gh pr create --base <parent-branch>`, so the diff shows only what that PR adds. A stacked PR opened against the default branch shows its parent's changes too, and reviewers will read them as yours.
- **Say where each PR sits in the set**, in Risks & rollout: which PR it depends on, and that it must not merge first.
- **Land bottom-up.** The parent merges, then the child.
- **Rebase after each merge.** GitHub retargets the child to the parent's base once the parent's branch is merged and deleted, but with a squash or rebase merge the child still carries its own copies of the parent's commits — so its diff stays wrong until you rebase it onto the updated base. Do that before asking for review again.
- **Keep the stack shallow.** Two deep is manageable; four is a queue where feedback on the bottom rewrites everything above it.

## Cleanup ships last

Retiring the code a change replaces is its own final PR, opened after the new path is live — the same reason it's a separate commit in `git-commit`: a mixed diff makes the rollback ambiguous and buries the removal.

If the old path is gated by a flag, the cleanup PR is also where the flag goes, and it can't open until the flag has been on in production long enough to trust (AGENTS.md §5, *Safe rollout, feature flags & migrations*).

## Then run each PR through the workflow

Each PR in the split gets its own pass through the main workflow — its own title, its own Reasoning, its own Summary filtered on its own diff. A split done well means no PR's body has to explain the others; a body that can't avoid it is a sign the seam is in the wrong place.
