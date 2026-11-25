---
paths:
  - "**/AGENTS.md"
  - "**/CLAUDE.md"
---

# Agent instruction file limits

`AGENTS.md` and `CLAUDE.md` load into every session, and each client caps how much of one it accepts. Measure against those caps on every edit that grows a file, and flag any overrun to the developer with what would be dropped. Whether an overrun is acceptable is theirs to decide — it can be, where nobody runs Codex in the repository or its cap is raised — but it must never pass unnoticed.

| Client | Budget | Counted in | Scope | Past the budget |
| --- | --- | --- | --- | --- |
| Codex | `project_doc_max_bytes`, 32 KiB by default | bytes | combined across the project's `AGENTS.md` files, from the repository root down to the working directory; the global `~/.codex/AGENTS.md` is not counted | truncated mid-file, with a warning naming the file and the bytes kept |
| Claude Code | 40,000 | characters | per file | startup warning, content still loaded |
| Claude Code | 4 MiB | bytes | per file | file skipped entirely |
| Cursor | none published | — | — | — |

- **Measure Codex's cap against the project chain.** Every `AGENTS.md` from the repository root down to the directory Codex was launched in shares one `project_doc_max_bytes`, so a monorepo's workspace file adds to the root's rather than replacing it. The global instruction file loads separately and does not count; it still costs context in every session, which is reason enough to keep it lean. Read the configured cap from `~/.codex/config.toml` before assuming 32 KiB.
- **Measure bytes, not characters.** `wc -c` gives Codex's unit and `wc -m` gives Claude's. Em-dashes, `§`, and curly quotes cost two to three bytes each, so a file safely under 40,000 characters can pass 40,000 bytes.
- **Truncation takes the tail.** Codex cuts at the byte, so the last sections disappear first — usually the testing, verification, and commit conventions that conventionally sit at the bottom. If a file is near its budget, don't assume anything near the end was read.
- **Recover space by moving material out, not by compressing prose.** Long-form detail belongs in a skill, a `references/*.md`, or a linked doc read on demand. Tightening sentences buys a few hundred bytes and costs clarity; relocating a section buys kilobytes.
- **Raising Codex's cap is per-client tuning.** `project_doc_max_bytes` in `~/.codex/config.toml` lifts it (`65536` for 64 KiB). Claude Code has no equivalent setting and Cursor publishes no limit, so this is not a policy to mirror across clients.
- **Re-measure after any edit that grows one of these files** — every chain from the root to each workspace file, against the configured cap; the `agents-md` skill carries a script that does it. Nothing in the file itself shows that it crossed the budget.
