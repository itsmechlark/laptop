# The out-of-scope knowledge base

Durable records of **rejected** requests. Two jobs:

- **Memory** — the reasoning survives the closed ticket.
- **Dedupe** — when the same idea returns in different words, triage surfaces the
  prior decision instead of re-litigating it.

## Two locations, one concept

| Where | Holds | Status |
| --- | --- | --- |
| `<repo>/.out-of-scope/` | Rejections grounded in *this* codebase or product | Committed to the repository |
| `~/.agents/out-of-scope/` | Rejections that belong to no single project | Machine-local, git-ignored |

**The routing test: would this reason still be true in another repository?**

"The rendering pipeline resolves a single palette at build time" is about one
codebase — project-local. "I don't add telemetry to my projects" is a standing
policy that would be argued again in every repo you own — cross-repo.

When a reason has both halves, write the project-local file and let it carry the
whole reason. The cross-repo KB is for policy that has no project to live in, not
a second copy of a decision that does.

### Why the project one is committed

Project rationale belongs to the project, not to a laptop. An uncommitted
`.out-of-scope/` dedupes for exactly one machine and one maintainer: everywhere
else the check finds nothing, and the request gets re-litigated — the failure
this knowledge base exists to prevent, in the one form nobody notices, because a
silent miss looks identical to a genuinely new idea.

It is also the answer to "why won't you add this?" for every future reporter, so
it wants to be readable by people who will never run this skill.

### Why the cross-repo one is not

`~/.agents/out-of-scope/` is created by `mac` and linked from this checkout,
which is a published repository — the ignore rule is what keeps your personal
policy out of its history. It is a symlink, so `find` needs `-L` or it matches
nothing and reports success.

**If the directory doesn't exist, `mac` hasn't run on this machine.** Say so in
one line and work with the project-local KB alone. Do **not** create it: a real
directory there is one `mac` run away from being moved aside to
`out-of-scope.backup`, taking the entries with it.

It sits beside `~/.agents/skills` and `~/.agents/standup` rather than under any
one skill, because `triage` writes it but `slice` and `draft-spec` read it too —
it is shared project memory, not one skill's private state.

## Layout

One file per **concept**, not per request — several tickets asking for the same
thing share a file. Same shape in both locations:

```
.out-of-scope/
├── dark-mode.md
├── plugin-system.md
└── graphql-api.md
```

Name it in kebab-case after the concept, recognizable without opening the file.

## Format

Write it as a short design note, not a database row — paragraphs, and a code
sample where it makes the constraint concrete.

```markdown
---
name: dark-mode
description: Theming was declined; the pipeline resolves one palette at build time.
metadata:
  scope: project
  constraint: build-time palette resolution
  prior-requests: ["#42", "#87"]
---

# Dark mode

This project does not support theming.

## Why this is out of scope

The rendering pipeline resolves a single palette at build time. Runtime
switching would need a theme context around the whole tree, theme-aware style
resolution per component, and somewhere to persist a user preference — a
structural change that pulls against the project's focus on authoring.
Theming is a downstream concern for consumers who redistribute the output.

## Prior requests

- #42 — "Add dark mode support"
- #87 — "Night theme for accessibility"
```

A cross-repo entry takes the same shape with `scope: cross-repo`, and its
`Prior requests` list spans repositories — so qualify each line (`acme/web#42`)
rather than leaving a bare number that means nothing outside the repo it came
from.

### The frontmatter

The same three-key block every artifact these skills author carries.
`description` is required and short — one line, under 120 characters, no
wrapping — and it is the field this knowledge base runs on: the dedupe check
below reads one line per entry instead of opening every file, which is what
makes checking both locations on every triage affordable.

`metadata.constraint` names the thing the rejection rests on in a few words, so
the staleness check has something to verify against the code. Add
`metadata.adr` only when a rejection also settled an architectural question —
omit the key otherwise rather than writing an empty one.

**Quote every entry in `prior-requests`.** They carry a `#`, and a cross-repo
entry qualifies them further (`"acme/web#42"`). Unquoted, a reference with a
space before the `#` silently becomes a YAML comment and the rest of the list
disappears — a dedupe failure that looks exactly like a file nobody has hit yet.

There is no `topic`. The join key threads a piece of work through its spec,
plan, and lore notes; a rejection has none of those by definition, which is what
makes it a rejection.

**The directory's existing convention wins.** Read what is already in
`.out-of-scope/` before writing the first entry; where those files carry a
different shape or none, match them and say so. And the block does not travel:
a rejection quoted into a close comment is prose for the reporter, never YAML.

**The reason has to be substantive.** Point at project scope, a technical
constraint, or a deliberate strategic choice. "We don't want this" isn't a
reason, and "we're too busy right now" isn't a rejection — that's a deferral, and
it doesn't belong here.

## This is not an ADR

Both record decisions, and they are not interchangeable. An **ADR** records a
decision you *made* and is never erased — a reversal is written as a new record
superseding the old one, because the trail is the value. An **out-of-scope entry**
records a request you *declined*, and reversing it means deleting the file: the
KB's job is to answer "has this been rejected?" today, and a tombstone answering
"yes, but not any more" gives the wrong answer to the only question asked of it.

So: an architectural choice with consequences the codebase has to live with is an
ADR (`domain-modeling` writes those). A request that isn't being built is an
out-of-scope entry. When a rejection also settles an architectural question,
write both — the ADR for the choice, the entry for the request — and link the
entry to the ADR.

## When to check

During step 1 of triage, both locations, every time. Match on concept, not
keywords — "night theme" matches `dark-mode.md`. Read the descriptions first;
opening files is for the entry that looks like a hit.

```sh
grep -h 'description:' .out-of-scope/*.md ~/.agents/out-of-scope/*.md
```

**Check the reason before you repeat it.** An entry cites something — a pipeline
that resolves one palette at build time, a dependency the project won't take, a
product boundary. Constraints get removed. Two refactors later the entry still
reads as authoritative while the thing it rests on is gone, and surfacing it
unchecked re-rejects a request on grounds that expired. So confirm the cited
constraint still holds in the code, and when it doesn't, say that first: the
entry is stale, and the request deserves fresh triage rather than an inherited
no. Date-check nothing — age alone says little, and a five-year-old entry resting
on a constraint that is still true is still right.

On a hit that survives that check, surface it: *"This looks like
`.out-of-scope/dark-mode.md`, rejected because X — which still holds in the code.
Still your position?"* A cross-repo hit is the stronger signal — standing policy
rather than one project's call — so say which location matched. The maintainer
can:

- **Confirm** — append this request to Prior requests, then close it.
- **Reconsider** — delete or amend the file; the request proceeds through normal
  triage.
- **Distinguish** — related but genuinely different; proceed through normal
  triage.

## When to write

Only when an **enhancement** is *rejected*. This covers rejected enhancement PRs
too — recording one keeps the same request from returning as fresh code.

Do **not** write here for anything that closes as `resolved-elsewhere` — a
shipped feature or a duplicate is not a rejected request, and filing one poisons
later dedupe checks. Point to where the behavior lives instead.

The flow: check both locations → append to Prior requests, or create the file →
comment linking to it → apply `wontfix` and close as declined.

**A project-local write is a repository change, not a scratch file.** It gets the
same draft-show-then-ask as a tracker comment, and on a repo you don't own it
goes through whatever contribution route that repo has. If neither is available,
skip the file and put the full reasoning in the close comment — an unrecorded
rejection is a loss, but a surprise commit to someone's repository is worse.

**A cross-repo entry cannot be linked from a public comment**, because the
reader can't reach your machine. Put the reasoning inline in the comment and keep
the file as your own memory.

## Reversing a decision

Delete the file. Old tickets stay closed — they're history. The request that
prompted the change of mind goes through normal triage.
