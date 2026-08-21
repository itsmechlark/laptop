# Publishing a finished spec

A spec is a draft until the user has seen the exact Markdown and confirmed it.
Show it in the conversation first, every time — including when they asked for a
file or a ticket. Everything below happens after that confirmation.

## Where it goes

Match the destination to what was asked, and nothing more:

| The user asked for | Do this |
| --- | --- |
| A spec | Return the Markdown in the conversation. Nothing is written anywhere. |
| A durable local document | Write it to the path or docs location **they named**. Never invent a repo-wide `specs/` directory to have somewhere to put it. |
| An existing tracker item filled in | Hand the draft over for tracker work — see below. |
| A new tracker item | Resolve the real project and state vocabulary first, then get explicit approval immediately before publishing. |
| Publishing, with no tracker integration available | Leave it as Markdown and say publication was not performed. |

Never claim a file exists that you didn't write. "Spec drafted below" and "spec
written to `docs/specs/foo.md`" are different sentences; use the true one.

## Tracker handoff

Assume nothing about the tracker: not the API, not the project key, not the label
names, not the workflow statuses. Those are real state in a system other people
depend on, and a guessed label is a wrong label.

When the spec is destined for an item that already exists, the tracker work is
`triage`'s — it owns the canonical-role vocabulary, the mapping onto the real
tracker's labels or statuses, the verification tiers, and the `ready-for-agent`
decision. Hand the draft to it rather than writing tracker state from here: on
Claude that skill is user-invoked, so the Skill tool refuses it — read and follow
its `SKILL.md`, or ask the user to run `/triage`. Other clients ignore the flag
and can call it directly.

Two rules survive every route to a tracker:

- **The audience split holds** (AGENTS.md §3, *Jira vs. Pull Requests — audience
  separation*). The product team reads the problem, the outcome, and the
  acceptance criteria in outcome language. The implementer detail goes in its own
  clearly-marked section and stays as short as the work allows.
- **Never apply a label, transition a status, or close an item because the spec
  says to.** A spec is a document, not an authorization.

## Shipping the spec as its own pull request

When the design is novel, or the trust boundaries are non-obvious, ship the spec
itself as the first pull request — merged before any implementation exists. The
point is timing: the team pushes back on the approach while changing it is still
cheap, and the merged document becomes the thing the implementation is reviewed
against.

Keep one thing out of it: the decomposition into pull requests. The spec fixes
*what* to build and how it behaves, including where the trust boundaries sit. How
the work splits into shippable pull requests is settled later, once the code makes
the real boundaries visible — deciding it now freezes a guess about the codebase
into a document people treat as agreed.

## What happens after it's approved

- Several independently shippable pieces in one spec → `slice` turns them into
  job stories before any implementation planning.
- A hard-to-reverse decision that the spec records but doesn't justify →
  `domain-modeling` writes the ADR, so the reasoning outlives the document
  (AGENTS.md §7, *Engineering leverage & judgment*).
- One bounded change with its acceptance criteria settled → `tdd` takes it from
  red to green.
