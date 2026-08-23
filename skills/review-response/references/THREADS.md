# Assembling threads and reading their state

A review is a conversation, and most of what you fetch needs nothing from you.
This is how to collect it and work out which threads are actually live. Read it
at step 1; the decision table it feeds is in the skill body.

Three fetches, because no single endpoint carries all of it:

| You need | Where it lives |
| --- | --- |
| Comments and their replies | REST — `pulls/{n}/comments` |
| Review state and when it was submitted | REST — `pulls/{n}/reviews` |
| Whether a thread is resolved | **GraphQL only** — `reviewThreads.isResolved` |

## 1. Group the comments into threads

Replies come back from the same endpoint as their parents. Each reply carries
`in_reply_to_id` pointing at the thread's root comment, so grouping on
`in_reply_to_id // id` reassembles the conversation:

```sh
gh api repos/{owner}/{repo}/pulls/<n>/comments --paginate --jq '
  group_by(.in_reply_to_id // .id)[]
  | { thread:      (.[0].in_reply_to_id // .[0].id),
      path:        .[0].path,
      line:        .[0].line,
      last_author: (max_by(.created_at) | .user.login),
      last_at:     (max_by(.created_at) | .created_at),
      comments:    [.[] | {user: .user.login, at: .created_at, body}] }'
```

Without the grouping every reply looks like a fresh item, which is how the same
comment gets answered twice and how your own earlier reply gets read as
something to act on.

## 2. Fetch the review states

```sh
gh api repos/{owner}/{repo}/pulls/<n>/reviews --paginate \
  --jq '.[] | {user: .user.login, state, submitted_at}'
```

`state` is `APPROVED`, `CHANGES_REQUESTED`, `COMMENTED`, or `DISMISSED`. Keep
`submitted_at` — the timestamp is what decides whether an approval settles a
given thread. A reviewer can approve more than once; the latest per reviewer is
the one that counts.

## 3. Fetch resolution state

Not available over REST. `gh pr view` doesn't carry it either:

```sh
gh api graphql -f owner='<owner>' -f repo='<repo>' -F number=<n> -f query='
  query($owner:String!, $repo:String!, $number:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$number) {
        reviewThreads(first:100) {
          nodes {
            id
            isResolved
            isOutdated
            comments(first:1) { nodes { databaseId path } }
          }
        }
      }
    }
  }'
```

`id` is the thread's node id — needed to resolve it later, and not the same as
the REST comment id. `comments.nodes[0].databaseId` is the REST id of the root
comment, which is what joins this to the grouped set from step 1.

## 4. Decide each thread's state

With the three fetches joined, every thread falls into exactly one state:

| `isResolved` | Last comment by | Approving review after it? | State |
| --- | --- | --- | --- |
| true | — | — | **Resolved** — skip entirely |
| false | reviewer, no author reply in the thread | — | **New** |
| false | reviewer, following an author reply | — | **Reopened** or **Accepted** — read it |
| false | author | no | **Awaiting reviewer** |
| false | author | yes | **Settled by approval** |

The last-comment-by test can't separate **Reopened** from **Accepted** — only the
content can. A reviewer reply that disputes, asks, or raises something new is
Reopened and needs work; one that agrees or acknowledges ("makes sense", "ah,
right", a thumbs-up in prose) is Accepted and needs none. Read the body; don't
infer from the fact that they spoke.

"Approving review after it" means a review by that reviewer with
`state: APPROVED` whose `submitted_at` is later than the thread's `last_at`.
Compare the timestamps; don't assume an approval anywhere on the PR covers
every thread. An approval submitted before your reply settles nothing, and one
submitted before a thread even started certainly doesn't.

A reviewer who approves and then leaves new comments has opened live threads,
not settled ones — those comments postdate the approval.

## 5. Resolving, once the user says so

Only threads in **Settled by approval**, and only after the response report has
been cleared. The mutation takes the GraphQL thread `id` from step 3:

```sh
gh api graphql -f threadId='<thread-node-id>' -f query='
  mutation($threadId:ID!) {
    resolveReviewThread(input:{threadId:$threadId}) {
      thread { id isResolved }
    }
  }'
```

Check `isResolved: true` came back before reporting it done.

Never resolve anything in the other states. **Awaiting reviewer** in particular
looks resolvable — you replied, the work is done, nothing is outstanding on your
side — and resolving it is how a reviewer's open question disappears before they
have read the answer.

## Non-GitHub hosts

The states are the same; the plumbing differs. GitLab exposes threads directly
(`/merge_requests/{iid}/discussions`, each with `resolved` and its notes
already grouped) and approvals separately (`/approvals`), so steps 1–3 collapse
into two calls. Bitbucket exposes comment threads with a `resolution` object.
Map onto the same five states and the rest of the skill applies unchanged.
