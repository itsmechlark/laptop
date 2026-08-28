# Working a review across a stack

The main workflow assumes one PR with nothing built on top of it. When the PR under review has branches above it — or sits above another — feedback stops being local: a fix on a lower layer rewrites every branch above it, and those PRs belong to reviewers who never asked for anything.

This covers what changes. Moving through a stack and replaying it belongs to `gh-stack` — invoke it for the commands rather than working from a copy here.

## Find out you're in one, before step 5

`gh stack view --json` reports the chain: which branch you're on, which PR each branch carries, and `needsRebase` per branch. Run it once at step 1 if the PR looks stacked — its body says so, its base isn't the default branch, or the user said it's part of a set.

Outside a stack the command exits `2`, and without the extension installed it fails outright. Neither is a problem to solve; both mean the main workflow applies unchanged.

## Collect the set, work it bottom-up

Collect the threads on every open PR in the stack before acting on any of them, for the same reason step 1 collects threads rather than comments: the set has state that individual items don't show.

- **Feedback on a lower layer can moot comments above it.** A reviewer asking layer 1 to rename an interface makes half the comments on layer 3 stale before you touch them.
- **Work bottom-up**, the same order the stack lands in. Fixing layer 3 first means redoing it after layer 1's fix rebases it out from under you.
- **A comment marked outdated on an upper PR is weaker evidence here than the gotcha assumes.** Every parent merge and every upstack rebase moves lines on the branches above, so "the line moved" is routine rather than a signal. Judge whether the concern survived; don't read staleness into it.

## Decide which layer owns each fix

A comment lands on the PR where the reviewer saw the code, which is not always the PR that should carry the fix. Before implementing, establish the owner — `gh stack view --json` for the layout, `git log --all -- <path>` when a file's owning layer isn't obvious.

Then check out that layer and fix it there. Committing a lower layer's concern on the branch you happen to be standing on is the failure `gh-stack` warns about, and it is worse after review than before: the fix lands in a PR someone has already approved, and the layer that should have carried it still reads as unaddressed.

If the owner is a **merged** layer, the fix has nowhere to go in the stack — it becomes a change on the lowest open layer, or a follow-up PR. Say which in the report.

## Rebasing upstack has a cost, and someone else pays it

This is the one place the main workflow's advice cannot be followed as written.

> **Don't amend or force-push while a review is open.** Rewriting the branch detaches every inline comment from its line and clears the reviewer's per-file "viewed" state.

That is right for a standalone PR and unachievable in a stack. Rewriting a lower layer *requires* replaying every branch above it, and replaying them force-pushes them. There is no version of fixing layer 1 that leaves layer 2's inline comments attached.

So the rule becomes: **the cost is unavoidable, which makes it something to account for rather than something to avoid.**

- **Don't skip the replay to protect reviewer state.** A stack left un-replayed is worse than one with detached comments: the upper PRs sit on a parent that no longer exists, so their diffs show changes that aren't theirs. `needsRebase` in `gh stack view --json` is how you confirm it's done, and a fix isn't proven until that reads false for every branch above.
- **Batch it.** Fix everything the lower layers need, then replay once. Replaying per comment multiplies the churn by the number of comments.
- **Replaying is a publish action.** It force-pushes branches carrying other people's review state, so it sits behind the same gate as posting replies and committing — it goes in the step 6 question, named for what it is, not folded into "push".
- **A conflict during the replay is ordinary.** Resolve it in the layer it surfaced in; `gh-stack` covers continuing and aborting. Enabling `rerere` before you start means a conflict resolved once isn't resolved again on the next replay.

## Tell the reviewers above

Reviewers on the upper PRs get their comments detached and their "viewed" state cleared by a fix they didn't request. Say so, in the affected PR's thread, once: which lower layer changed, why, and that the diff has been replayed on top of it. One note per affected PR — not one per detached comment.

This is the same reasoning as the main workflow's rule that a PR body edit raises no notification. A force-push raises no explanation either, and the reviewer's own reading of it is that you rewrote history under them.

## Reporting and resolving across the set

Both reports cover the whole stack, not the PR you were pointed at:

- Number items by PR, so a reader can tell which layer each belongs to.
- Say which layer each fix landed in when it isn't the layer the comment was on. A reviewer looking for their fix in their own PR and not finding it will assume it was dropped.
- Name every PR that was replayed and every reviewer whose state that cleared.
- **Resolution stays per-thread and per-PR.** A rebase settles nothing; approval on layer 1 says nothing about the threads on layer 2. The resolution rules in the main workflow apply per PR, unchanged.
