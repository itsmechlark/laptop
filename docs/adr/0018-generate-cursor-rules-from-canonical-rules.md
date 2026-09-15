---
name: generate-cursor-rules
description: Cursor rule files (.mdc) are generated from the canonical rules/*.md, because a bare Cursor globs: string is invalid YAML for Claude and Cursor ignores .md.
metadata:
  status: accepted
  topic: agent-client-parity
---

# Generate Cursor rules from the canonical `rules/*.md`

**Context:** `rules/*.md` carries a `paths:` YAML list, and `mac` symlinked
`~/.cursor/rules` straight at `rules/`. Claude Code reads that directly. Cursor
never did: it loads only `.mdc` files and ignores `.md`, so every path-scoped
rule this repo ships was silently inert on Cursor. The symlink existed but
pointed at files Cursor cannot see.

The two hosts disagree on all three of the things that scope a rule:

| | Claude Code | Cursor |
| --- | --- | --- |
| Extension | `.md` | `.mdc` (ignores `.md`) |
| Key | `paths:` | `globs:` |
| Value | YAML sequence of quoted globs | bare comma-joined string, no quotes, no space after comma |

A single file cannot satisfy both. The tempting fix — add a `globs:` key
alongside `paths:` in each `rules/*.md` — is broken twice over. Cursor ignores
`.md` regardless of frontmatter, so the key would do nothing there. And a bare
`globs: **/*.ts` is **invalid YAML**: a leading `*` is a YAML alias reference,
so a strict parser (Ruby Psych, which Claude Code uses) throws and drops the
whole rule. Quoting it (`globs: "**/*.ts"`) parses, but Cursor reportedly
breaks on the quoted form. There is no value shape that both parsers accept.

**Decision:** Keep `rules/*.md` as the single source of truth and *generate*
the Cursor `.mdc` set from it, the same way `mac` renders `.codex/config.toml`
from `.codex/config.toml.template`. `scripts/gen-cursor-rules` reads each rule's
`paths:` list and writes `.cursor/rules/<name>.mdc` with a translated
frontmatter — `globs:` as the bare comma-joined string Cursor wants, plus
`alwaysApply: false` — followed by the rule body verbatim. `mac` runs the
generator and symlinks the output; the generated `.cursor/rules/` is
git-ignored, like `config.toml`.

One generator serves both the real output and its own verification.
`check-payload` runs it into a temp dir and re-derives the expected globs
independently from each rule's `paths:`, failing when the rendered `.mdc`
drifts from the source. `.github/workflows/tests.yml` shellchecks the script in
the `payload` job.

Scope is Cursor only. Codex reads `AGENTS.md` and `.codex/rules/default.rules`
and has no per-path rule dialect to translate into; Windsurf, Copilot, and Cline
are documented in the `agent-rules` skill but not shipped by this repo.

**Consequences:** Editing a `rules/*.md` now needs `sh mac` again to refresh the
Cursor copy — the fourth entry in the development workflow's short list of
changes that do, alongside a new top-level link, the Codex template, and a first
`.agents/CONTEXT.md`. The Claude copy is still live-on-edit through its symlink;
only the generated Cursor half needs the re-run.

A new rule needs nothing Cursor-specific: add the `rules/*.md` with its `paths:`
and the generator picks it up. A rule with no `paths:` entries fails the
generator loudly rather than emitting an `.mdc` with an empty `globs:`, which
Cursor would read as unscoped.

This extends "Agent-client configuration parity" to rules: one canonical policy,
translated per client, verified in sync. It matches the precedent set for the
security configs and for `config.toml` rather than inventing a new mechanism.

**Rejected:** A second `globs:` key in each `rules/*.md`. Broken on both hosts
as above — invalid YAML for Claude, ignored extension for Cursor — so it fails
the one thing it was meant to do.

Also rejected: hand-maintaining a parallel `.cursor/rules/*.mdc` set checked
into git. It doubles every rule edit and invites exactly the drift the parity
invariant exists to prevent; a reviewer would have to catch a stale `.mdc` by
eye. Generation makes the drift impossible and the check mechanical.

Also rejected: dropping the dead `~/.cursor/rules` symlink and shipping no rules
to Cursor. It is the least work and honest about today's behavior, but it
abandons path-scoped standards on one of the three first-party clients for no
reason beyond format friction the generator removes.

**Evidence:** `scripts/gen-cursor-rules`, `mac` (Cursor section),
`scripts/check-payload` (Cursor rule generation check), `.gitignore`
(`.cursor/rules`), `rules/*.md`.
