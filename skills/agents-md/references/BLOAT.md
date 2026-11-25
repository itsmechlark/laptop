# Relocation map and bloat catalogue

## Where content goes

| Content | Home | Written with |
| --- | --- | --- |
| Why a decision was made, alternatives rejected | ADR in `docs/adr/` | `domain-modeling` |
| What a project word means | `CONTEXT.md` | `domain-modeling` |
| Which bounded contexts exist, where each glossary lives, how they relate | `CONTEXT-MAP.md` at the root, only where there is more than one context | `domain-modeling` |
| Convention for some paths only | Path-scoped rule | `agent-rules` |
| Repeatable multi-step workflow | Skill | `agent-skills` |
| How a feature works, its history, an incident, why a pin is held back | Lore note, or the doc beside the code | `lore` |
| Procedure past five steps: release, device setup, credentials | Runbook (`docs/runbooks/`) or `README.md` | — |
| Why one odd-looking line is the way it is | Comment at that line | — |
| The full Definition of Done, gate matrix, runtime matrix | A `docs/` page, linked from `## Done` | — |
| What the product is for, who uses it, on which platforms | `PRODUCT.md`, or `README.md` where there is none | — |
| Voice, tone, positioning, naming, how copy should sound | `BRAND.md` | — |
| Visual system: color and type tokens, spacing, component look | `DESIGN.md` | — |
| Machine paths, personal preferences | `*.local.md` or `.agents/CONTEXT.md`, git-ignored | — |

`PRODUCT.md`, `BRAND.md`, `DESIGN.md`, and `CONTEXT-MAP.md` sit at the root,
where the tools that read them look; a root symlink to the copy a docs site
publishes counts. `AGENTS.md` names each one that exists once, as a row in
`## References`, and restates none of them.

The shapes an `AGENTS.md` grows into follow, in roughly the order they turn up
in an audit. Each has a tell, what it costs, and where the content goes. None of
them is wrong to *know*; each is wrong to load into every session.

## Mission and pitch

**Tell:** an opening paragraph on who the product serves and why it matters.

**Cost:** every session pays for a paragraph that changes no edit. Tone rules
hidden in it ("respectful, never X-style patterns") are the one part that does.

**Instead:** the pitch goes in `PRODUCT.md`, or `README.md` where there is
none; voice and tone go in `BRAND.md`. Keep the orientation to the stack in one
line. A tone or content rule an agent would break while writing code ("no
engagement-bait copy in notifications") stays as its own `## Conventions`
bullet, pointing at `BRAND.md` for the rest.

## Brand, design, and context restated

**Tell:** hex colors, font stacks, a control height, voice adjectives, a
"brand chain" paragraph tracing which brand file derives from which, or a list
of every bounded context with its glossary path.

**Cost:** each is the whole job of a file that already exists, and the copy in
`AGENTS.md` goes stale the first time the source is edited.

**Instead:** one `## References` row per file: `BRAND.md` for voice, `DESIGN.md`
for the visual system, `CONTEXT-MAP.md` for the contexts. Where one file is
derived from another (a brand guide PDF into `BRAND.md`), the derivation is
recorded in the derived file's own header, not here.

## Feature inventory

**Tell:** "It serves auth, health, waitlist, profiles, discovery, …" — a list of
every domain or route group in the workspace.

**Cost:** wrong the day a feature lands, and `ls src/` answers it.

**Instead:** cut it. Where a domain list *is* needed for naming, it is
`CONTEXT.md`'s job.

## Mechanism essays

**Tell:** several paragraphs on how one flow works end to end: how a payment
is retried, how a device proves itself at sign-in, which header carries what.

**Cost:** the largest single source of bytes in most bloated files, and loaded
for sessions that never touch that flow.

**Instead:** the mechanism goes to a lore note or the doc beside the code, and
the decision inside it, if there is one, to an ADR. What stays is the
instruction the essay was protecting, as one bullet with a link:
"Charge cards through `chargeWithIdempotencyKey`; never call the gateway client
directly ([ADR 0031](docs/adr/0031-slug.md))."

## History and war stories

**Tell:** "X is pinned to 2.4.1 because 2.4.0's resolver …", "drop the
override once …", "this predates the helper and stays as it is".

**Cost:** true until the upstream fix ships, then silently false.

**Instead:** a comment at the pin (`pnpm-workspace.yaml`, `Gemfile`), or a lore
note. Keep a bullet only when an agent would otherwise "fix" it: "Don't
bump a package past its override in `pnpm-workspace.yaml`."

## Restated global standards

**Tell:** "Never commit unless asked", "no AI attribution", "run gitleaks at
closeout", "no comments in production code" — anything the global instruction
file already says.

**Cost:** paid twice per session, and the copy drifts from the source.

**Instead:** cut. Repository-*specific* refinements stay: commit scopes, release
components, which `docs/` page carries them.

## Definition of Done in triplicate

**Tell:** the same gate list in the global file, the root, every workspace, and
a `docs/` page.

**Cost:** four copies to keep in step, and a workspace list that drifts from the
root one reads as a deliberate exception.

**Instead:** the full detail lives in one `docs/` page. The root's `## Done`
names the gate command and links it. A workspace's `## Done` names only its
delta: "No browser suite", "Lint already fails on warnings", "Device-only
behavior is reported as run only when it was".

## Boilerplate preamble

**Tell:** "This file narrows the root `AGENTS.md` for … Use it together with the
root, not instead of it. Domain vocabulary is in …" at the top of every nested
file.

**Cost:** small per file, large across fifteen, and it says nothing the loader
does not already do.

**Instead:** cut. The glossary pointer lives once, in the root.

## Script mirrors

**Tell:** a bullet per `package.json` script, each with the full
`pnpm --filter @scope/pkg` prefix.

**Cost:** duplicates the manifest, and the full prefix repeats on every line.

**Instead:** the root says how to scope a command to a workspace, and the
workspace file states its own prefix once. Under it, list only the scripts whose
names don't say what they do, or that carry a trap ("never in parallel with the
unit suite").

## One convention, many copies

**Tell:** the same paragraph — test placement by directory, coverage flags, the
build-before-type-check order — in several sibling packages.

**Cost:** n copies, and the one that gets updated is never all of them.

**Instead:** up one level, to the root's `## Conventions` or to a rule whose glob
covers every package it applies to.

## Imported path-scoped rules

**Tell:** a `Required rules` block of `@path/to/rule.md` lines where those rules
also sit in a rules directory with `paths:` globs.

**Cost:** Claude Code loads every `@`-import at launch, so a rule scoped to
`apps/api/**` costs every session in the repository.

**Instead:** plain paths, no `@`. Where the rule is also wired into a client's
rules directory, that client loads it by its glob; the list is what reaches
every other client, Codex included.

## Explaining pins

**Tell:** a `Rule specifics` section where each pin carries a paragraph:
the helper, its arguments, the exception, the reason for the exception.

**Cost:** pins are what a repo-agnostic rule defers to. A paragraph per pin
makes the instruction file the rule's long form.

**Instead:** one line per pin — concept, symbol, path. The reasoning goes to a
comment at the symbol or to the ADR. A workspace with more than about fifteen
pins should check whether some are discoverable from the code they name.

## Directory trees

**Tell:** an ASCII tree of the workspace.

**Cost:** `ls` and `tree` answer it, and it is out of date the next time a
directory is added.

**Instead:** cut the tree. Keep the ownership rules that aren't obvious from
names: "`support/` holds helpers specs share; specs never define factories."

## Restated tool config

**Tell:** "Use two-space indent", "single quotes", "max line length 100".

**Cost:** the formatter enforces it already, and the copy disagrees with the
config the day the config changes.

**Instead:** cut. Keep the command that applies it (`pnpm fix`), not the rules
it applies.

## Skill and plugin lists

**Tell:** a list of installed skills, plugins, or MCP servers.

**Cost:** the client already lists them, more accurately.

**Instead:** cut. Name a skill only where a step must use it ("follow the
design system's skill for component APIs, not the template's source").

## Prerequisites for occasional tasks

**Tell:** a toolchain list (Maestro CLI, Java 17, an emulator, `ANDROID_HOME`)
for a task most sessions never run.

**Cost:** loaded every session for the one that runs the device journey.

**Instead:** a runbook or the workspace `README.md`, linked from
`## References`.

## Dated claims

**Tell:** "as of Sprint 12", "currently", "for now", "will be added later",
roadmap status ("billing is schema-only, exports are default-off").

**Cost:** an agent cannot tell which sentences have expired.

**Instead:** cut, or move to the roadmap or product doc. Where an agent needs to
know a surface is flag-gated, say which flag, not when.

## Vague pointers

**Tell:** "see the docs", "refer to the wiki", "follow the usual process".

**Cost:** an agent searches for it, finds the wrong thing, and trusts it.

**Instead:** the exact repo-relative path, in `## References`.
