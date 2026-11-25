---
name: agents-md
description: Write, standardize, and trim AGENTS.md and CLAUDE.md instruction files, root and nested, so each one is a short index backed by real commands and paths rather than a handbook. Use when asked to create, update, audit, or standardize AGENTS.md or CLAUDE.md, when one has grown bloated or past a client's size budget, when a monorepo's workspace files repeat the root or each other, when deciding whether a passage belongs in AGENTS.md or in an ADR, runbook, rule, lore note, or the README, or when setting up the CLAUDE.md symlink. Not for writing the path-scoped rule or skill a passage moves into, and not for the README itself.
argument-hint: "[path to an AGENTS.md, a workspace, or the repo]"
---

# AGENTS.md

An `AGENTS.md` is an index that loads whole into every session under its
directory. It holds what an agent would get wrong and cannot cheaply look up —
the exact commands, the conventions no config enforces, the paths it must not
touch — and points at the documents that carry everything else. Anything longer
than a few lines lives at the far end of a pointer.

Target: `$ARGUMENTS`. Empty means the repository: every `AGENTS.md` and
`CLAUDE.md` in it.

Two rules own the neighboring subjects. Claude Code and Cursor load them when an
instruction file is open; on Codex, or before the first file exists, read them
from `~/.agents/rules/`. Apply them; do not restate them in the files you write:

- `agent-instructions.md` — each client's size cap, what counts toward it, and
  truncation from the tail.
- `agent-instructions-layout.md` — `AGENTS.md` canonical with a `CLAUDE.md`
  symlink, `.agents/rules/`, the root-versus-workspace split, and pointing at
  `CONTEXT.md` and `docs/adr/` once.

## When to use this skill

- Creating `AGENTS.md` for a repository or a workspace
- Updating one after commands, layout, or conventions changed
- Auditing or trimming files that have grown, or a chain that is past budget
- Standardizing a monorepo's root and workspace files to one shape
- Deciding where a passage belongs when it no longer fits
- Not for writing the path-scoped rule a passage becomes — that is
  `agent-rules`; this skill decides it should move, that one writes it
- Not for writing a skill — `agent-skills`
- Not for glossary terms or decision records — `domain-modeling`; for what an
  investigation or a feature's history taught — `lore`
- Not for `README.md` or `CONTRIBUTING.md`, which are for people;
  `AGENTS.md` links them

## The keep test

Every line passes all four, or it moves:

1. **Would an agent act wrongly without it?** Not "is it true" or "is it
   useful context" — would the next change come out wrong.
2. **Is it expensive to discover?** A script in `package.json`, a directory
   `ls` shows, a rule the linter enforces are each one lookup away, and a copy
   here is a second source that drifts. The exception is the command that is
   not obvious from its name: the filter syntax, the file-scoped test
   invocation, the wrapper that must not be swapped for the bare tool.
3. **Is it true everywhere this file governs?** A convention for one subtree
   moves down to that subtree's file or to a path-scoped rule.
4. **Is it said nowhere else that loads?** The global instruction file, an
   ancestor `AGENTS.md`, and any rule matching the same paths are already in
   context. Repeating them costs bytes twice and drifts.

Fail 1 or 2: cut it. Fail 3: push it down. Fail 4: cut the copy and keep the
source. A passage that passes all four but runs past three lines relocates,
leaving a one-line pointer.

## Budgets

Size is a finding to flag, never a limit to enforce. Measure with the budget
script in [references/CHECKS.md](references/CHECKS.md#budget): it sums each
chain of project `AGENTS.md` files from the root down, against Codex's
configured cap, and each file's characters against Claude Code's. For every
chain over, tell the developer by how much and which sections Codex drops, and
let them decide. An overrun can be acceptable: nobody runs Codex in the
repository, or its cap is raised. Never cut a line that passes the keep test
only to fit a budget.

Line counts are a quicker signal of the same weight. A file past its mark gets
the same treatment, flagged with the passages that would move:

| File | Aim | Flag past |
| --- | --- | --- |
| Root, single package | 60 lines | 100 |
| Root, monorepo | 80 lines | 120 |
| Workspace | 30 lines | 60 |
| Leaf package | no file (see [Nested files](#nested-files)) | 30 |

## Sections

Fixed names in a fixed order, so a reader learns the shape once and a diff
between two repositories' files is meaningful. Every section is optional: leave
one out when it has nothing that passes the keep test, never fill it. The order
puts first what an agent needs first, and last what costs least when Codex cuts
the tail.

| Section | Holds |
| --- | --- |
| `# <repository name>` or `# <workspace path>` | One to three lines: what it is, the stack, the runtimes it ships. No mission statement |
| `## Required rules` | Plain-path list of the shared rules governing this tree, each with the paths it covers |
| `## Commands` | `Task \| Command` table: install, dev, the narrowest test, lint and type-check runs, the full gate |
| `## Layout` | Monorepo root: `Path \| What \| Own AGENTS.md` table. Elsewhere only for non-obvious ownership |
| `## Conventions` | One instruction per bullet: what no config enforces, generated files, paths never to edit |
| `## Done` | Only what differs from the global Definition of Done: the gate command, the runtimes, the gates this tree lacks |
| `## References` | `Need \| File` table: glossary, decisions, runbooks, setup, release, commit scopes |
| `## Gotchas` | Traps that have bitten more than once, two lines each at most |

Copy [templates/root.md](templates/root.md) or
[templates/workspace.md](templates/workspace.md) and delete what does not apply.
Which sections a given kind of repository needs — a Rails app, a gem, a pnpm
monorepo, a Pulumi stack, an Expo app, a docs site — and the file-scoped
commands for each test runner are in
[references/SHAPES.md](references/SHAPES.md).

Writing rules for every section:

- Bullets and tables, not paragraphs. One rule per bullet, phrased as an
  instruction.
- A command appears in backticks, exactly runnable from the repository root.
  A workspace file states its scoping prefix once
  (`pnpm --filter @scope/api`) and lists script names under it.
- Backticked paths are repo-root-relative. Markdown links are file-relative,
  so they resolve on GitHub: `[ADR 0012](../../docs/adr/0012-slug.md)`.
- Name the file, never "see the docs".
- Rationale only where the rule looks wrong without it, in a clause, not a
  paragraph. The full why is an ADR, linked.
- No dates, sprint numbers, or "currently" — they rot silently.

**Required rules are plain paths, never `@`-imports.** Where a rule is also
wired into a client's rules directory (`.claude/rules/`, Cursor's generated
`.mdc` files), that client loads it by its glob. The list is what reaches every
other client, Codex included, which has no rules directory. An `@` in front of
a path-scoped rule makes Claude Code load it at launch whatever its `paths:`
say, which is the per-session cost the glob was there to avoid.

**Never add an AI co-author or attribution section.** Upstream templates
include one; the standing policy here is the opposite, and it already lives in
the global file.

## Nested files

Write one only where the subtree's commands, runtimes, rules, or conventions
differ from the root's, and never restate an ancestor: Claude Code and Codex
load a nested file's ancestors along with it. Codex launched at the root never
reads a nested file, so the root's `## Layout` table must name each one. The
full set of rules for monorepos, pins included, is in
[references/SHAPES.md](references/SHAPES.md#nested-files).

## Where things go instead

A passage that fails the keep test, or passes but is too long, still holds
information. Land it in its home before deleting it here: an ADR, `CONTEXT.md`
or `CONTEXT-MAP.md`, `PRODUCT.md`, `BRAND.md`, `DESIGN.md`, a path-scoped rule,
a lore note, a runbook, a `docs/` page, or a comment at the code. Write into a repository directory only where the repository already has
one; the owning skill knows the global fallback.
[references/BLOAT.md](references/BLOAT.md) maps each kind of content to its home
and the skill that writes it, then catalogues the recurring shapes of bloat with
their tells. Read it before an audit.

## Workflow

### 1. Inventory

Run the budget script. Read the global instruction file in effect, so you know
what not to restate. For an update, read each existing file whole.

### 2. Read the sources

What the files should say comes from the repository, not from the old file:

- Package manager: the lockfile, the `packageManager` field, `.tool-versions`
- Commands: `package.json` scripts, `Makefile`, `justfile`, `Rakefile`,
  `bin/`, `mix.exs` aliases, `turbo.json` or `nx.json`
- The real gate: what `.github/workflows/` runs is what a change must pass
- Docs to point at: `README.md`, `CONTRIBUTING.md`, `docs/`, `SECURITY.md`,
  `CONTEXT.md`, `docs/adr/`, runbooks
- Rules: `.agents/rules/`, `.claude/rules/`, `.cursor/rules/`, and their globs
- Generated and vendored paths: lint and format ignore files,
  `.gitattributes` `linguist-generated`, codegen scripts

### 3. Classify

For an existing file, put every passage in one of five bins: **keep**, **push
down** (to which file), **relocate** (to which home), **cut as duplicate** (of
which source), or **cut as discoverable or stale**. A command or path that no
longer exists is stale; check before calling it so.

### 4. Show the plan, then get a yes

Somebody maintains the existing files, and a monorepo's worth is a large diff.
Show the classification, the homes each relocation lands in, and the sizes
before and after, then wait for a yes. Across a monorepo, make it one plan for
every file. Writing a first file where none exists needs no gate.

### 5. Relocate, then rewrite

Relocations land first, each through its owning skill, so nothing is deleted
before it has a home. Then rewrite each file against its template, root first,
so the workspace files can drop everything the root now says.

### 6. Verify

Run the path, command, and `CLAUDE.md` checks in
[references/CHECKS.md](references/CHECKS.md), then the budget script again.
Every check reads; none invokes a build tool to prove a target exists.

### 7. Report

A table per file — bytes before and after, chain total against the cap, lines
— then each relocation and where it landed. List every chain still over a
budget as a question for the developer, not as a failure. Say plainly which
checks ran and which did not.

## Gotchas

- **Vendored skill bundles ship their own `AGENTS.md`**, sometimes tens of
  kilobytes, often reachable through a `skills/<name>` or `.claude/skills`
  symlink. They are not the repository's instructions; never edit them. The
  checks list files with `git ls-files`, which does not follow those links.
- **"Discoverable" is not "obvious".** A `check:type` that runs through a
  wrapper raising the heap passes test 2: the next agent will replace it with
  bare `tsc`. Keep it, as one line.
- **A narrative with a decision inside it is two relocations.** The decision
  goes to an ADR, the mechanism to lore or the doc beside the code. What stays
  is the one instruction the narrative was protecting.

## Attribution

- [getsentry/skills](https://github.com/getsentry/skills/tree/main/skills/agents-md) - agents-md, Apache-2.0
- [AGENTS.md](https://agents.md/)
- [github/awesome-copilot](https://github.com/github/awesome-copilot) - create-agentsmd
