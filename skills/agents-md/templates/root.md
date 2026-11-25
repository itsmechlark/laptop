# <repository name>

<One to three lines: what this repository is, its stack, and the runtimes it
ships. No mission statement.>

## Required rules

Open and follow each before editing the files it covers.

- `.agents/rules/<rule>.md`: `<glob it covers>`

## Commands

Run from the repository root.

| Task | Command |
| --- | --- |
| Install | `<package manager> install` |
| Dev | `<command>` |
| Test one file | `<command> <path>` |
| Lint one file | `<command> <path>` |
| Type-check | `<command>` |
| Affected tests | `<command>` |
| Full gate | `<command>` |

Scope any script to one workspace with `<scoping syntax>`.

## Layout

| Path | What | Own `AGENTS.md` |
| --- | --- | --- |
| `<path>` | <one line> | yes |
| `<path>` | <one line> | — |

## Conventions

- <One non-obvious rule per bullet, stated as an instruction.>
- Never hand-edit `<generated path>`; regenerate with `<command>`.

## Done

- `<gate command>` passes on the final tree. Detail: `<docs page>`.
- <Only what differs from the global Definition of Done.>

## References

| Need | File |
| --- | --- |
| Glossary | `CONTEXT.md` |
| Bounded contexts | `CONTEXT-MAP.md` |
| Decisions | `docs/adr/` |
| Product, users, platforms | `PRODUCT.md` |
| Voice and tone | `BRAND.md` |
| Visual system | `DESIGN.md` |
| <Setup, release, runbooks, commit scopes> | `<path>` |

## Gotchas

- <A trap that has bitten more than once, in two lines at most.>
