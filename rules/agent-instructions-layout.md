---
paths:
  - "**/AGENTS.md"
  - "**/CLAUDE.md"
---

# Agent instruction file layout

How a repository arranges its instruction files, rules, and skills so every agent reads the same source. The per-client size caps these files must stay under are in `agent-instructions.md`, which loads alongside this rule and owns everything about budget and truncation.

- **`AGENTS.md` (uppercase) is the canonical file**, and must stay the real, git-tracked one. Codex and most agents only discover the uppercase name, and a mixed-case `Agents.md` does not resolve on case-sensitive filesystems (Linux/CI).
- **`CLAUDE.md` beside it is a symlink to `AGENTS.md`**, never a copy — two copies drift silently and nothing reconciles them. Add the symlink beside every workspace `AGENTS.md`, not just the root one.
- **Shared rules live in `.agents/rules/`**, listed in a required-rules block in the nearest `AGENTS.md`. No client auto-discovers that directory: the listing is what makes it reachable, so keep every `AGENTS.md` self-explanatory rather than relying on `@`-import magic.
- **Path-scoped rules belong in the client's own rules directory**, not behind an import. Claude Code expands `@`-imports, but an import loads unconditionally at launch — putting a rule there trades its `paths:` glob for always-on cost, which is the opposite of why it was scoped.
- **Skills live in `.agents/skills/<name>/SKILL.md`** with a lowercase filename, and `.claude/skills` symlinks to `.agents/skills` so Claude Code discovers them. A session reload is needed after adding one.
- **The root `AGENTS.md` owns repo-wide** overview, setup, workflow, and PR conventions. Package names, filtered commands, generated artifacts, and workspace-specific validation belong in the nearest workspace `AGENTS.md` instead.
- **Measure the combined budget after any edit that grows one of these files.** The global file and the repo's own share Codex's allowance, so the root pair is the case to check first — a monorepo adds one workspace file on top of it, never instead of it:

  ```sh
  G=$(wc -c < ~/.agents/AGENTS.md 2>/dev/null || echo 0)
  R=$(wc -c < AGENTS.md)
  echo "root: $((G + R)) / 32768"
  for W in $(git ls-files '*/AGENTS.md'); do
    case "$W" in .agents/*) continue ;; esac
    echo "$W: $((G + R + $(wc -c < "$W"))) / 32768"
  done
  ```
