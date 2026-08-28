# Splitting a wide build into narrow PRs

When a feature was built wide — proven end to end on a throwaway branch — don't open one sprawling PR from that branch. Small PRs flow; large ones sit.

**This is the recovery path**, and it salvages a branch that already holds too much. Work that is *several shippable things* was never one PR to recover — `slice` cuts that, and each slice becomes its own PR off the default branch. Stacking, below, is for something narrower: **one** shippable thing whose implementation is too large to read in a single diff, layered for the reviewer. When you know that up front, build it in layers from the start rather than splitting afterwards — `gh-stack`'s `references/stack-design.md` is blunt about why, and it comes down to there being no non-interactive way to reorder a stack once it exists.

## Decide the set first

The target is the smallest group of independently reviewable PRs, each safe to merge on its own. Work it out before opening anything, and name for each one what it carries, what it depends on, and whether it can land alone.

**Size is the cheap signal, not the decision.** Much past ~300 lines of production code in one PR — the budget `feature-dev` carries per slice — and a split is usually available. It's a prompt to look, not a rule: a mechanical rename across forty files is one reviewable change at any size, and 200 lines spanning two unrelated concerns is already two PRs.

**Show the proposed split before opening anything** — the PRs, what each carries, and which stack — so it can be corrected while it's still a plan.

## Cut each PR fresh off the default branch

Each in its own worktree; the `git-worktree` skill covers creating and placing them. The scratch branch's history is throwaway, so it never becomes the PR: carry over only the slice that PR owns, and let the rest stay behind.

That means each PR's diff is small by construction rather than by discipline — you are not trying to explain a subset of a wide branch, you are shipping a branch that only ever held one change.

**A worktree per PR is for the independent ones.** A stack is a chain in a single checkout — you move through it with `gh stack up`, `down`, and `checkout <target>`, and splitting its layers across worktrees fights the tool for no gain.

## Stack only when a dependency is real

A change that depends on code another PR in the set introduces stacks on that PR; everything independent branches straight off the default branch. Stacking for convenience buys a rebase chain you'll regret once the bottom PR gets review feedback.

The judgment is yours either way:

- **Say where each PR sits in the set**, in Risks & rollout: which PR it depends on, and that it must not merge first.
- **Keep the stack shallow.** Two deep is manageable; four is a queue where feedback on the bottom rewrites everything above it.
- **Land bottom-up.** The parent merges, then the child.

The mechanics belong to `gh-stack`: opening the set, keeping each child's diff honest as parents merge, and landing the chain in order. Invoke it. This skill's job is the text on each PR, and restating its commands here only forks them from the vendored source.

**Two things it does not do, and one of them will bite you:**

- **`gh stack submit --auto` generates every title and body.** That is exactly the output this skill exists to write — a generated body has no Reasoning, no filtered Summary, and no Conventional Commits title. Submit the stack, then run each PR through steps 1–4 of the main workflow against its own diff, and set the real text with `gh pr edit <number> --title "…" --body-file <file>`. Do this before marking anything ready for review.
- **`submit` is one publish action for N PRs.** Approval to open *a* PR is not approval to open the set. The count is the thing to name when you ask.

Without the extension, or on a repository where stacked PRs aren't enabled (`gh stack` exits `9`), do it by hand: `gh pr create --base <parent-branch>` per child, so each diff shows only what that PR adds — a stacked PR opened against the default branch shows its parent's changes too, and reviewers will read them as yours. Then rebase every child after its parent merges. GitHub retargets a child once the parent's branch is merged and deleted, but under a squash or rebase merge the child still carries its own copies of the parent's commits, so its diff stays wrong until you rebase it onto the updated base.

## Cleanup ships last

Retiring the code a change replaces is its own final PR, opened after the new path is live — the same reason it's a separate commit in `git-commit`: a mixed diff makes the rollback ambiguous and buries the removal.

If the old path is gated by a flag, the cleanup PR is also where the flag goes, and it can't open until the flag has been on in production long enough to trust (AGENTS.md §5, *Safe rollout, feature flags & migrations*).

## Then run each PR through the workflow

Each PR in the split gets its own pass through the main workflow — its own title, its own Reasoning, its own Summary filtered on its own diff. A split done well means no PR's body has to explain the others; a body that can't avoid it is a sign the seam is in the wrong place.

For a stack this pass is not optional and it is not first: the PRs already exist with generated text, and the workflow is what replaces it.
