# Worked examples

Four walkthroughs: an epic cut into a sequence, with the gaps and deferrals its
list records; a small feature sharpened into one job story; a build order caught
pretending to be a slice list; and two slices that are independent by value but
collide at the merge. The domains are stand-ins — what carries across is the
shape of the cut and the reasoning that produced it.

## The captured list's frontmatter

A slice list written to a file opens with the same three-key block a PRD, a
spec, a plan, and a lore note carry:

```yaml
---
name: teammate-invites
description: How the invite loop was cut into four slices, riskiest first.
metadata:
  status: accepted
  topic: teammate-invites
  tickets: []
  repo: billing-api     # only in ~/.agents/slices/; omit in a repo's own docs directory
---
```

`metadata.topic` comes from the PRD when there is one, and every spec and plan
written under these slices repeats it — that is what joins the chain. The
`description` is required and short: one line, under 120 characters, no
wrapping, saying when someone should open the list rather than what it is
titled.

`metadata.status` moves through the lifecycle every planning artifact shares:
`draft` (written, not yet agreed) → `accepted` (agreed; implementation may
start) → `done` (every slice has shipped), with `superseded` when a wholesale
re-cut replaces the list — named in the new list's `metadata.supersedes`, the
same one-directional link `lore` and ADRs use.

A list is filed only after the user has agreed the sequence, so it is born
`accepted`; it reaches `done` when the last slice ships. Re-cutting the
remainder in place is an edit, not a supersession — a new file is warranted
only when the whole sequence is re-thought.

**Acceptance criteria are live state, not a template.** Each criterion starts
as `- [ ]` (unverified). As behavior is confirmed, change it to `- [x]`. A
slice whose every criterion is checked is done. A spec reaching `status: done`
does not check the slice's criteria — the slice file is the record of what was
verified, and it's updated directly when the behavior is confirmed, not inferred
from a sibling document.

**No slice count.** This skill re-cuts a list whenever one slice ships or
overruns, and a number in the frontmatter would go stale on the first re-cut
with nothing to catch it. The list below is the count.

Two rules bound it. **The block belongs to the file, never to the delivered
text** — a list pasted into a tracker renders it as literal YAML, so strip it
there. And **the output directory's existing convention wins**: where the
documents already at that path carry a different shape or none, match them and
say so, rather than leaving one directory with two conventions in it.

## An epic, sliced

**The feature as it arrived:** "Admins should be able to invite teammates into
the account."

**What step 1 established.** The user is an account owner setting up a new
workspace, in the first ten minutes, alone, and blocked until colleagues can get
in. Done means they stop emailing screenshots around. The part they were least
sure about: whether invitees would accept at all, or ignore the email like every
other product's.

That last answer decides the sequence. The riskiest assumption is that the
invite loop closes, and slice one already tests it — so the skeleton and the
risk are the same slice, and nothing has to be reordered to de-risk early.

### Slice 1 — Invite one teammate by email

```markdown
## S1 — Invite by email

When I've just created an account and my colleagues can't see any of it,
I want to send one person an invitation by email
so they can sign in and start working in the same account today.

**Ships when:** an owner enters an email address, the recipient gets a message,
clicks it, signs up, and lands in the account with the default role.

### Acceptance criteria

- [ ] An owner invites an address that has no account, and the invitee lands in
      the right account after signing up
- [ ] Inviting an address that already belongs to this account is rejected with
      a message saying so
- [ ] An invite link that has already been used, or is older than the expiry,
      shows an explanation rather than an error page

**Depends on:** none.
**Risk / learning:** tests the whole invite loop, including whether anyone accepts.
**Spec:** invite-by-email
```

The `Spec:` line appears once the spec is written — here `invite-by-email` is the
spec's `name`, and that spec's frontmatter points back with
`part-of: slice/teammate-invites#S1`.

One thin path through every layer: form, record, email, accept, membership. No
roles, no list, no resend. It is unquestionably incomplete and it is
unquestionably shippable.

### Slice 2 — See and revoke what's pending

```markdown
## S2 — Pending invites

When I've invited three people and can't remember which of them replied,
I want to see who's still outstanding and take an invite back
so I stop chasing people who already joined and can undo a typo'd address.

**Ships when:** the members screen lists pending invites with their sent date, and
revoking one makes its link stop working.

### Acceptance criteria

- [ ] Pending invites appear with the address and the date sent
- [ ] Revoking removes it from the list, and the link then shows "no longer
      valid" instead of granting access
- [ ] An invite that has been accepted moves out of pending and into members

**Depends on:** S1.
**Risk / learning:** low risk.
```

`Depends on:` names slice 1 because there is nothing to list until invites
exist. That's sequence. Slice 1 shipped and stayed useful without this one,
which is what makes them two slices rather than one.

### Slice 3 — Choose the role at invite time

```markdown
## S3 — Invite with a role

When I'm inviting a bookkeeper who should never touch settings,
I want to pick their role while I'm sending the invitation
so I don't have to remember to downgrade them after they accept.

**Ships when:** the invite form offers the account's roles, and the accepted member
arrives with the role that was chosen.

### Acceptance criteria

- [ ] An invite sent as a restricted role produces a member with that role
- [ ] The default is unchanged when no role is chosen
- [ ] A role removed from the account between sending and accepting falls back
      to the default rather than failing the acceptance

**Depends on:** S1.
**Risk / learning:** low risk — the permission model already exists.
```

Depends on slice 1, not on slice 2. Two independent branches off the skeleton,
so these two could go to different people, or to `fan-out`.

### Slice 4 — Auto-join by verified email domain

```markdown
## S4 — Domain auto-join

When someone from our company signs up with their work email and I never got
round to inviting them,
I want them to join our account automatically
so onboarding stops depending on me noticing.

**Ships when:** with the flag on for a pilot account, a signup at a verified domain
joins that account with the default role instead of creating a new one.

### Acceptance criteria

- [ ] A signup at the verified domain lands in the existing account
- [ ] A signup at a lookalike domain does not
- [ ] With the flag off, signup behaves exactly as it does today

**Depends on:** S1 — reuses the membership-creation path it shipped.
**Risk / learning:** highest-consequence slice — a wrong match puts a stranger
inside someone's account. Ships default-off and gets enabled per account.
```

The flag is not a fifth slice. It is what makes this one shippable while the
match rules are still being trusted, and "ships when" says so explicitly.

### Sequencing rationale

Invite-by-email goes first because it is the only slice that proves the loop
works end to end, and everything else is worthless if invitees ignore the email.
Pending-and-revoke follows: it costs little and removes the support burden of
mistyped addresses, which is the first thing that will happen in production.
Roles come third because the permission model already exists, so the slice is
mostly wiring. Domain auto-join is last despite being the most-requested item —
it is the one slice whose failure mode is a security incident, and it wants the
other three shipped and quiet first.

### Known Gaps and Deferred

Asked what the invite list knowingly ships without, the owner named two things,
and two sections close the file. The shape:

```markdown
## Known Gaps

- **S1** — [what a user can still hit, and why it ships anyway]
  Addressed by: [spec/<name>, or slice/<list-name>#<id>]

## Deferred

- [what is wanted, and why not now]
  Addressed by: [same forms]
```

An entry about one slice opens with its ID in bold; one about the whole list
carries none. Filled in for the invite list:

```markdown
## Known Gaps

- **S1** — An invitee who signs up under a different address than the one
  invited lands in a new account, not the inviting one. Rare enough to ship
  with.
  Addressed by: spec/invite-address-mismatch

## Deferred

- Inviting a whole team from a CSV. Wanted for larger accounts, but whether
  one-at-a-time invites are a real obstacle won't be known until S1 is live.
  Addressed by: slice/bulk-invites#B1
```

The first entry is a gap because the behavior ships and the shortfall is known
and accepted. It carries `Addressed by:` because a spec of its own, filed under
no slice in this list, was written for it afterward, and nothing follows the
locator. The second is deferred because it is
wanted and not cut; once someone cut it into a list of its own, the entry
pointed there instead of being deleted.

Had the owner wanted CSV invites inside this list, it would be a fifth slice
with its own ID and the Deferred entry would be removed the moment that slice was
written, with no link: the list itself carries it now. The same goes for a gap
that S3 closed. Neither entry belongs under a slice's criteria, which say what
must be true for the slice to ship, not what is known to be missing.

The order does not matter. Suppose S1 had shipped and its address-mismatch gap
was already recorded when the owner decided to close it with a new slice, S5.
The entry leaves in the same edit that adds S5, even though S1 is done. Leaving
it with `Addressed by: slice/invites#S5` would point the list at itself and
leave it describing one shortfall twice, as a gap and as a slice.

## A small feature, sharpened

**As it arrived:** "Users should be able to rename their saved reports."

Push: "Is this one thing, or two?" — it turned out renaming and duplicating had
been quietly bundled together. Duplicating became its own slice for later.

```markdown
## S1 — Rename a saved report

When I've built a report called "Copy of Copy of Q3" and can't find it in a
list of forty,
I want to rename it in place
so the list stays something I can scan.

**Ships when:** a user renames a report from the list and the new name persists
across a reload.

### Acceptance criteria

- [ ] A renamed report keeps its data, schedule, and share links
- [ ] An empty name is rejected, and the old name is kept
- [ ] A name that duplicates another report of the same owner is allowed, and
      both stay distinguishable by their dates

**Depends on:** none.
**Risk / learning:** low risk.
```

"Keeps its share links" is the criterion worth having. It is the thing a
reviewer wouldn't think to check and the thing users would notice within a day.

## A build order pretending to be a slice list

What came back from a first attempt at the invite epic:

```
1. Add the invitations table and model
2. Build the invitation mailer
3. Add the POST /invitations endpoint
4. Build the invite form
5. Handle acceptance and create the membership
```

Every entry fails both tests. None ships on its own — stopping after three
leaves a table, a mailer, and an endpoint no interface calls. None is visible
to anyone: the first person who can see anything is the user in step 5, which
means there is exactly one slice here, cut horizontally into five pieces of
work.

The tell is the dependency chain. Each item depends on its predecessor and
nothing branches, because a build order is a line while slices fan out from the
skeleton.

The collapse: items 1 through 5 are slice 1 above. Then ask what *else* the
feature contains beyond the first path, which is where slices 2, 3, and 4 come
from.

## Independent by value, coupled at the merge

Two slices off the same skeleton, both `Depends on: none`, both shippable in
either order — and both editing the same runtime module and its config:

```markdown
## S1 — Capture dead-letter failures

When a deployed job exhausts its retries, I want the poison job preserved
so an operator can investigate it instead of losing it silently.

**Ships when:** a job failing past its retry budget lands in the dead-letter queue.

**Depends on:** none.
**Shares files with:** S2 — both edit the runtime jobs consumer, its environment
types, and the worker config. Serialize: land this first, rebase the other.
**Risk / learning:** fixes an active data-loss bug.
```

```markdown
## S2 — Serialize the scheduler

When a scheduled run fires while a prior one is still going, I want the scheduler
to run exclusively so the deployed schedule is safe to turn on.

**Ships when:** two overlapping scheduled runs serialize, and only one does the work.

**Depends on:** none.
**Shares files with:** S1 — same runtime consumer, environment types, and worker
config. Serialize behind it, or stack this PR on its branch.
**Risk / learning:** unblocks the deployed schedule.
```

Both pass the two tests and neither waits on the other's behavior, so
`Depends on:` is honestly `none` for both. `Shares files with:` is the field that
stops them from being opened as two PRs off the default branch that then refuse to
merge: the second serializes behind the first, or stacks on its branch.
Re-cutting so one slice owned all three files was the third option, rejected
here — the two features are genuinely separate, and folding them together would
bury a data-loss fix inside a scheduling change.
