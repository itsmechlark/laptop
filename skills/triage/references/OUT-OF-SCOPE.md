# The out-of-scope knowledge base

`.out-of-scope/` holds durable records of **rejected** requests. Two jobs:

- **Memory** — the reasoning survives the closed ticket.
- **Dedupe** — when the same idea returns in different words, triage surfaces the prior decision instead of re-litigating it.

## Layout

One file per **concept**, not per request — several tickets asking for the same thing share a file:

```
.out-of-scope/
├── dark-mode.md
├── plugin-system.md
└── graphql-api.md
```

Name it in kebab-case after the concept, recognizable without opening the file.

## Format

Write it as a short design note, not a database row — paragraphs, and a code sample where it makes the constraint concrete.

```markdown
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

**The reason has to be substantive.** Point at project scope, a technical constraint, or a deliberate strategic choice. "We don't want this" isn't a reason, and "we're too busy right now" isn't a rejection — that's a deferral, and it doesn't belong here.

## When to check

During step 1 of triage. Match on concept, not keywords — "night theme" matches `dark-mode.md`. On a hit, surface it: *"This looks like `.out-of-scope/dark-mode.md`, rejected because X. Still your position?"* The maintainer can:

- **Confirm** — append this request to Prior requests, then close it.
- **Reconsider** — delete or amend the file; the request proceeds through normal triage.
- **Distinguish** — related but genuinely different; proceed through normal triage.

## When to write

Only when an **enhancement** is *rejected*. This covers rejected enhancement PRs too — recording one keeps the same request from returning as fresh code.

Do **not** write here when something closes as `wontfix` because it's **already built**. That's a shipped feature, not a rejected request, and filing it would poison later dedupe checks. Point to where the behavior lives instead.

The flow: check for an existing file → append to Prior requests, or create the file → comment linking to it → apply `wontfix` and close.

## Reversing a decision

Delete the file. Old tickets stay closed — they're history. The request that prompted the change of mind goes through normal triage.
