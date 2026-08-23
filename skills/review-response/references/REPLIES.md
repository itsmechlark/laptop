# Drafting and posting the reply

What the reply says, and where it goes once it's approved. Triage and
verification come first and are in the skill body; this is the part after you
know what you think.

**Draft every reply before posting any of them.** They go into the response
report as drafts, and only get posted once the user says so. Posting lands in
the reviewer's inbox and can't be unsent.

## What a reply has to carry

Either the fix or a reasoned position. A reply carrying neither is empty, no
matter how polite it is.

| Situation | Reply carries |
| --- | --- |
| Suggestion was right | what changed, and where |
| Suggestion was wrong | the evidence, and the alternative |
| Suggestion was unclear | the specific question, and what you understood |
| Can't verify here | the limitation, and a request for direction |
| Right but out of scope | agreement, the follow-up link, why not now |
| You pushed back and were wrong | the correction, in one line |

## Worked examples

### Acknowledging correct feedback

The fix is the reply. Courtesy riding along with it is fine; courtesy instead
of it is not.

```
Fixed — `end_date` is now validated against siblings of the same shop.

Good catch, off-by-one in the loop bound. Fixed in `Reservation#window`.

Thanks — dropped the callback entirely, the validator covers it.
```

Not this:

```
You're absolutely right!            (validation, no substance)
Great point!                        (performative)
Let me implement that now           (announced, not verified, not done)
Thanks for catching that!           (courtesy standing in for the fix)
```

Add the commit SHA only once the commit exists. A draft reply that cites a SHA
you haven't made yet is the same failure in a different costume.

### Pushing back

Lead with the position, then the evidence that produced it, then the way
forward. A question at the end keeps it a conversation rather than a refusal.

```
Checked this — the build target is 10.15 and that API needs 13+, so the legacy
path has to stay. The current implementation does have the wrong bundle id
though. Fix that, or drop pre-13 support?
```

```
This would 404 for existing links: the old slug format is still in the wild and
`spec/requests/legacy_links_spec.rb` pins it. I can add the new format
alongside and deprecate the old one over a release — worth it?
```

```
Grepped for callers and nothing hits this endpoint. Rather than build out the
filters and export, I'd delete it. Is there usage I'm missing?
```

### Asking about an unclear comment

Say what you did understand, so the reviewer only has to fill the gap.

```
I follow 1, 2, 3 and 6 and can start on those. On 4 — "make the webhook check
stricter" — do you mean constant-time comparison of the signature, or rejecting
requests with no timestamp? They're different changes and 5 depends on which.
```

Ask before implementing any of it. Items in one review are usually related, and
a partial reading gets the neighbors wrong too.

### Saying you can't verify it

```
I can't reproduce the race here — it needs concurrent workers against a
prod-like dataset. I can add the advisory lock on the assumption it's real, or
leave it and open an issue to reproduce properly. Which do you want?
```

### Naming a contradiction

Quote both, in one thread, and let them settle it. Mentioning someone notifies
them, which is the point here — but it's still a notification, so name only the
people who need to answer.

```
These two pull opposite ways — @alice wants the retry in the caller (thread on
`client.rb:40`), @bob wants it in the adapter (here). I'll take the adapter
unless one of you objects, since the caller can't see which failures are
retryable. Shout if that's wrong.
```

### Correcting your own pushback

One line. No apology paragraph, no defense of the original position.

```
You were right — checked and it does drop the last page when the count is an
exact multiple. Fixing.
```

```
Verified this; my reading of the index was wrong, it's on `shop_id` alone.
Adding the composite.
```

### Answering a nit

A nit wants an answer, not necessarily a change.

```
Left it as-is — `each_with_object` reads worse here because the accumulator is
the thing being tested. Happy to change it if you feel strongly.
```

## Evidence for visual changes

For a UI or styling comment, prose can't prove resolution. Capture the
before/after by driving the app with `agent-browser`, and attach the images
through the web UI — the host CLI has no upload, so a reply pointing at an
unattached image is a reply pointing at nothing.

## Posting, once approved

An inline review comment has its own thread. Replying there keeps the answer
next to the code it's about; replying at the top level strands it, and the
reviewer has to reconcile two lists by hand.

```sh
# Reply inside an inline comment's thread (needs the comment id).
gh api repos/{owner}/{repo}/pulls/<n>/comments/<comment-id>/replies \
  -f body='Fixed — the bound was inclusive. See 3f2a1c9.'

# Reply to the PR as a whole: the summary after working through a review.
gh pr comment <n> --body-file "$TMPDIR/summary.md"
```

Write anything longer than a sentence to a file under `$TMPDIR` and pass
`--body-file`. Shell quoting mangles backticks, code fences, and apostrophes,
and the macOS sandbox blocks `/tmp`. On a non-GitHub host, the equivalent is
`glab` or the platform's API — same threads, different command.

**Don't resolve the thread on the reviewer's behalf.** Resolving hides it, and
hiding a thread you argued in ends the conversation without agreement.

## The summary comment

Distinct from the response report: that one is for the user, deciding what to
publish. This one is for the PR, once they've said yes.

```markdown
Worked through all 14. Fixed 9 (see the individual threads), pushed back on 3:

- **Retry placement** — kept in the adapter; the caller can't classify failures.
- **Legacy slug removal** — still live traffic, deprecating over a release instead.
- **Metrics endpoint** — nothing calls it, deleted rather than built out.

Two are waiting on you: the webhook wording in `client.rb:40`, and whether
pre-13 support is still in scope.
```

No task log, no "addressed feedback" narration, and no restating in full what
each fix did when its own thread already has it.

<!-- cspell:words pushback glab -->

