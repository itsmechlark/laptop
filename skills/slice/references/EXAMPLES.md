# Worked examples

Three walkthroughs: an epic cut into a sequence, a small feature sharpened into
one job story, and a build order caught pretending to be a slice list. The
domains are stand-ins — what carries across is the shape of the cut and the
reasoning that produced it.

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

```
Invite by email
When I've just created an account and my colleagues can't see any of it,
I want to send one person an invitation by email
so they can sign in and start working in the same account today.
Ships when: an owner enters an email address, the recipient gets a message,
clicks it, signs up, and lands in the account with the default role.
Acceptance criteria:
- [ ] An owner invites an address that has no account, and the invitee lands in
      the right account after signing up
- [ ] Inviting an address that already belongs to this account is rejected with
      a message saying so
- [ ] An invite link that has already been used, or is older than the expiry,
      shows an explanation rather than an error page
Depends on: none.
Risk / learning: tests the whole invite loop, including whether anyone accepts.
```

One thin path through every layer: form, record, email, accept, membership. No
roles, no list, no resend. It is unquestionably incomplete and it is
unquestionably shippable.

### Slice 2 — See and revoke what's pending

```
Pending invites
When I've invited three people and can't remember which of them replied,
I want to see who's still outstanding and take an invite back
so I stop chasing people who already joined and can undo a typo'd address.
Ships when: the members screen lists pending invites with their sent date, and
revoking one makes its link stop working.
Acceptance criteria:
- [ ] Pending invites appear with the address and the date sent
- [ ] Revoking removes it from the list, and the link then shows "no longer
      valid" instead of granting access
- [ ] An invite that has been accepted moves out of pending and into members
Depends on: Invite by email.
Risk / learning: low risk.
```

`Depends on:` names slice 1 because there is nothing to list until invites
exist. That's sequence. Slice 1 shipped and stayed useful without this one,
which is what makes them two slices rather than one.

### Slice 3 — Choose the role at invite time

```
Invite with a role
When I'm inviting a bookkeeper who should never touch settings,
I want to pick their role while I'm sending the invitation
so I don't have to remember to downgrade them after they accept.
Ships when: the invite form offers the account's roles, and the accepted member
arrives with the role that was chosen.
Acceptance criteria:
- [ ] An invite sent as a restricted role produces a member with that role
- [ ] The default is unchanged when no role is chosen
- [ ] A role removed from the account between sending and accepting falls back
      to the default rather than failing the acceptance
Depends on: Invite by email.
Risk / learning: low risk — the permission model already exists.
```

Depends on slice 1, not on slice 2. Two independent branches off the skeleton,
so these two could go to different people, or to `fan-out`.

### Slice 4 — Auto-join by verified email domain

```
Domain auto-join
When someone from our company signs up with their work email and I never got
round to inviting them,
I want them to join our account automatically
so onboarding stops depending on me noticing.
Ships when: with the flag on for a pilot account, a signup at a verified domain
joins that account with the default role instead of creating a new one.
Acceptance criteria:
- [ ] A signup at the verified domain lands in the existing account
- [ ] A signup at a lookalike domain does not
- [ ] With the flag off, signup behaves exactly as it does today
Depends on: Invite by email — reuses the membership-creation path it shipped.
Risk / learning: highest-consequence slice — a wrong match puts a stranger
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

## A small feature, sharpened

**As it arrived:** "Users should be able to rename their saved reports."

Push: "Is this one thing, or two?" — it turned out renaming and duplicating had
been quietly bundled together. Duplicating became its own slice for later.

```
Rename a saved report
When I've built a report called "Copy of Copy of Q3" and can't find it in a
list of forty,
I want to rename it in place
so the list stays something I can scan.
Ships when: a user renames a report from the list and the new name persists
across a reload.
Acceptance criteria:
- [ ] A renamed report keeps its data, schedule, and share links
- [ ] An empty name is rejected, and the old name is kept
- [ ] A name that duplicates another report of the same owner is allowed, and
      both stay distinguishable by their dates
Depends on: none.
Risk / learning: low risk.
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
