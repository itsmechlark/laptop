---
paths:
  - "**/AGENTS.md"
  - "**/CLAUDE.md"
---

# Agent instruction file limits

`AGENTS.md` and `CLAUDE.md` load into the context of every session, and each client caps how much of one it will accept. Two of those caps fail silently: content past the budget is dropped with nothing in the transcript to say so. Treat the budget as a constraint on the file rather than as advice.

| Client | Budget | Counted in | Scope | Past the budget |
| --- | --- | --- | --- | --- |
| Codex | `project_doc_max_bytes`, 32 KiB by default | bytes | combined across every instruction file it selects | truncated mid-file; only a tracing warning |
| Claude Code | 40,000 | characters | per file | startup warning, content still loaded |
| Claude Code | 4 MiB | bytes | per file | file skipped entirely |
| Cursor | none published | — | — | — |

- **Budget against Codex's 32 KiB, in bytes, combined.** It is the smallest cap and the only default that discards content. The global instruction file and the project's own share one budget, so a project file sitting comfortably under Claude's 40,000 characters can still be cut once the global file is counted ahead of it.
- **Measure bytes, not characters.** `wc -c` gives Codex's unit and `wc -m` gives Claude's. Em-dashes, `§`, and curly quotes cost two to three bytes each, so a file safely under 40,000 characters can pass 40,000 bytes.
- **Truncation takes the tail.** Codex cuts at the byte, so the last sections disappear first. On a long file that usually means the testing, verification, and commit conventions that conventionally sit at the bottom. If a file is near its budget, don't assume anything near the end was read.
- **Recover space by moving material out, not by compressing prose.** Long-form detail belongs in a skill, a `references/*.md`, or a linked doc read on demand. Tightening sentences buys a few hundred bytes and costs clarity; relocating a section buys kilobytes.
- **Raising Codex's cap is per-client tuning.** `project_doc_max_bytes` in `~/.codex/config.toml` lifts it (`65536` for 64 KiB). Claude Code has no equivalent setting and Cursor publishes no limit, so this is not a policy to mirror across clients.
- **Re-measure after any edit that grows one of these files.** A file that crossed its budget reads exactly like a file that didn't, in every client.
