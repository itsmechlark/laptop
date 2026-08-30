---
paths:
  - "**/AGENTS.md"
  - "**/CLAUDE.md"
---

# Agent instruction file layout

How a repository arranges its instruction files, rules, and skills so every client reads the same source. Size budgets and truncation are in `agent-instructions.md`, which loads alongside this one and owns them.

- **`AGENTS.md` (uppercase) is the canonical file**, and must stay the real, git-tracked one. Codex and most agents only discover the uppercase name, and a mixed-case `Agents.md` does not resolve on case-sensitive filesystems.
- **`CLAUDE.md` beside it is a symlink to `AGENTS.md`**, never a copy — two copies drift silently and nothing reconciles them. Add the symlink beside every workspace `AGENTS.md`, not just the root one.
- **Shared rules live in `.agents/rules/`**, listed in a required-rules block in the nearest `AGENTS.md`. No client auto-discovers that directory: the listing is what makes it reachable, so keep every `AGENTS.md` self-explanatory rather than relying on `@`-import magic.
- **Path-scoped rules belong in the client's own rules directory**, not behind an import. Claude Code expands `@`-imports, but an import loads unconditionally at launch — putting a rule there trades its `paths:` glob for always-on cost, which is the opposite of why it was scoped.
- **Skills live in `.agents/skills/<name>/SKILL.md`** with a lowercase filename, and `.claude/skills` symlinks to `.agents/skills` so Claude Code discovers them. A session reload is needed after adding one.
- **The root `AGENTS.md` owns repo-wide** overview, setup, workflow, and PR conventions. Package names, filtered commands, generated artifacts, and workspace-specific validation belong in the nearest workspace `AGENTS.md` instead.
