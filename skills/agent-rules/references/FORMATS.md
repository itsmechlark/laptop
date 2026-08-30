# Rule formats, host by host

Every host below reads markdown with YAML frontmatter and scopes it by glob.
Nothing else is shared. Confirm against the host's own docs before shipping — this
layer moves, and a wrong key fails silently.

## Claude Code

**Location.** `.claude/rules/**/*.md` for the project, `~/.claude/rules/**/*.md`
for the machine. Discovered recursively, so subdirectories are free organization.
Symlinked directories and files are resolved and loaded, and circular symlinks are
handled — a shared rule set can be linked into many projects from one source.

**Frontmatter.** One key matters:

```markdown
---
paths:
  - "src/api/**/*.ts"
  - "src/**/*.{ts,tsx}"
---

# API rules

- All endpoints validate input at the boundary
```

`paths` is a YAML sequence of globs. Omit it and the rule is unconditional,
loaded at launch with the same priority as the project instruction file.

**Load order.** User rules load before project rules, so project rules are read
last and effectively win. Rules and instruction files are concatenated, never
merged or overridden.

**Activation.** A path-scoped rule triggers when Claude *reads* a matching file —
not on every tool use, and not because the file is merely mentioned. Matching
also works through a symlinked path into the project directory.

**Brace expansion.** `src/**/*.{ts,tsx}` expands to two patterns, and groups
multiply: `{a,b}/{c,d}/*.{ts,tsx}` is eight. A rule's whole `paths` list shares
one budget of 1,000 expanded patterns and 4 MiB. A pattern that would exceed the
budget is used unexpanded, and its literal braces then match nothing.

**Two things that bite.**

- Path-scoped rules are **not re-injected after compaction**. The project-root
  instruction file is re-read from disk; a rule with `paths:` returns only when a
  matching file is read again.
- Project rules are skipped when `project` is excluded from `--setting-sources`.

## Cline

**Location.** `.clinerules/**/*.md`.

**Frontmatter.** Same key as Claude Code, plus two of its own:

```markdown
---
description: Frontend component conventions
paths:
  - "src/components/**"
  - "src/hooks/**"
---
```

A file with no frontmatter is always a candidate. `paths` narrows it to matching
files; `alwaysApply: true` forces it back to unconditional.

**Failure mode is the friendly one.** On invalid YAML, Cline fails open — the
rule activates with its raw content visible, which makes the mistake obvious
rather than invisible. It also strips UTF-8 byte-order marks.

**Migration.** Cline additionally reads `.cursorrules`, `.windsurfrules`, and
`AGENTS.md`, so a move onto it can be incremental.

## Cursor

**Location.** `.cursor/rules/**/*.mdc`. Subdirectories are supported.

**The extension is load-bearing.** A `.md` file in `.cursor/rules/` is ignored
outright. This is the single most common reason a ported rule does nothing.

**Frontmatter.** Three fields, and their combination *is* the rule type:

| Type | Frontmatter |
| --- | --- |
| Always Apply | `alwaysApply: true` — other fields ignored |
| Apply Intelligently | `alwaysApply: false` + `description`, no `globs` |
| Apply to Specific Files | `alwaysApply: false` + `globs` |
| Apply Manually | `alwaysApply: false`, no `description`, no `globs` |

```markdown
---
alwaysApply: false
globs: src/components/**/*.tsx,src/components/**/*.ts
---
```

**`globs` is a bare comma-separated string.** Not a YAML list, not quoted, no
space after the comma. Quoting collapses the value into one malformed pattern;
the list form is not read at all; a trailing space is invisible in the editor and
breaks the pattern beside it. This is the field people get wrong.

**Precedence.** Team rules → project rules → user rules. User rules apply to
Agent chat only, not to inline edit or tab completion.

**Guidance.** Keep a rule under ~500 lines and split rather than grow.

## Windsurf

**Location.** `.devin/rules/*.md` is preferred and takes precedence;
`.windsurf/rules/*.md` remains as a fallback. `global_rules.md` and a root
`AGENTS.md` carry no frontmatter and are always on.

**Frontmatter.** An explicit mode, rather than an inferred one:

```markdown
---
trigger: glob
globs: **/*.test.ts
---
```

| `trigger` | Behavior |
| --- | --- |
| `always_on` | Always in context |
| `glob` | Applies when files matching `globs` are edited |
| `model_decision` | Cascade decides from the rule's `description` |
| `manual` | Only when @-mentioned by name |

**Hard caps.** 12,000 characters per workspace rule file, 6,000 for the global
one. These are enforced limits, not advice.

**Troubleshooting.** A rule behaving as always-on when it was scoped usually
means the frontmatter does not start at line 1 — a leading blank line or a
byte-order mark is enough.

## GitHub Copilot

**Location.** `.github/instructions/**/*.instructions.md`. The filename must end
in `.instructions.md`. The repository-wide counterpart is
`.github/copilot-instructions.md`, which takes no frontmatter.

**Frontmatter.**

```markdown
---
name: 'Python standards'
description: 'Coding conventions for Python files'
applyTo: '**/*.py'
---
```

`applyTo` is a glob string; multiple patterns are comma-separated inside the one
value — `applyTo: "**/*.ts,**/*.tsx"`. `applyTo: "**"` makes the file
unconditional. The whole frontmatter block is optional.

`excludeAgent: "code-review"` or `excludeAgent: "coding-agent"` hides the file
from one surface. Absent, every agent reads it.

**Scope caveat.** On github.com, path-specific instructions are honored by the
coding agent and code review. Do not assume every Copilot surface reads them, and
note that both a matching path-specific file and the repository-wide file apply
at once — conflicts between them resolve non-deterministically.

**No file references.** `@path` includes are not expanded inside
`*.instructions.md`.

## Amazon Q

**Location.** `.amazonq/rules/**/*.md`. No frontmatter, no scoping: every rule in
the directory is always in context. Budget the whole directory as though it were
one instruction file.

## Porting one rule across hosts

The body is portable; only the frontmatter is not. To carry one rule to another
host:

1. **Translate the scoping key**, including the value's shape — a YAML list for
   `paths`, a bare comma-separated string for Cursor's `globs`, a quoted
   comma-separated string for `applyTo`, `trigger: glob` plus `globs` for
   Windsurf.
2. **Translate the always-on form.** Omitting the key means unconditional on
   Claude Code and Cline; on Cursor it means Apply Manually — the opposite. This
   is where a port silently inverts.
3. **Re-check the extension and filename.** `.mdc` for Cursor,
   `*.instructions.md` for Copilot.
4. **Re-check the cap.** A 15,000-character rule that is fine on Claude Code is
   over Windsurf's limit.
5. **Verify it loaded**, on the host, before trusting it. Cursor lists loaded
   rules in Settings → Rules; Claude Code has `/context` and an
   `InstructionsLoaded` hook that logs which instruction files loaded and why.

Generators such as Rulesync exist to emit every dialect from one source. They
solve the transcription, not the semantic differences in step 2 — read what they
produce for at least one rule before trusting the rest.

## The standardization proposal

There is no ratified spec. The most concrete attempt is [agents.md issue
#179](https://github.com/agentsmd/agents.md/issues/179), which proposes a shared
`.agents/rules/` directory read *alongside* the existing per-host ones, with
markdown plus optional frontmatter:

| Field | Purpose |
| --- | --- |
| `name` | Kebab-case identifier, defaulting to the filename stem |
| `description` | What the rule covers |
| `trigger` | `always`, `auto`, or `manual`; defaults to `always` |
| `paths` | Globs for file-scoped activation |
| `keywords` | Prompt keywords for activation |
| `priority` | Integer; higher wins a conflict |
| `tags` | Grouping only, no semantic effect |

It is an open issue with no maintainer response and no adopting host. Treat it as
a signal about where the ecosystem is heading — `paths` and `trigger` are the
keys it picked, which is worth knowing when choosing between dialects — not as
something to write against today.
