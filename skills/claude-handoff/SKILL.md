---
name: claude-handoff
description: Hand the current conversation off to a fresh background agent that picks up the remaining work. Use when asked to hand off, continue in the background, pass work to another session, or start a background agent to finish a task. Writes a handoff summary and launches it with claude --bg.
argument-hint: "[what the next session should focus on]"
disable-model-invocation: true
---

# Claude Handoff

Write a handoff summary of the current conversation and launch a fresh background agent seeded with it — so the work continues without the user restarting from scratch.

Focus: `$ARGUMENTS`. Empty means hand off whatever the conversation's current task is.

## When to use this skill

- The conversation has reached a natural breakpoint and remaining work can continue unattended
- Context is getting long and a fresh session would work more efficiently
- The user wants to move on to something else while this work finishes in the background
- Not for dispatching multiple agents in parallel — that's `fan-out`
- Not for continuing work yourself in the same session — just keep working
- Not when the remaining work needs the user's input at every step — a background agent can't ask questions

## Workflow

### 1. Take stock

Before writing anything, identify:

- What has been accomplished in this conversation (decisions made, files changed, tests passing)
- What remains to be done
- What the user said they want the next session to focus on (`$ARGUMENTS`)
- Which artifacts already capture the state — specs, plans, commits, open PRs, issue descriptions

### 2. Write the handoff summary

The summary is the background agent's entire starting context — it has never seen this conversation. Structure it as:

**Goal** — one sentence on what the agent should accomplish.

**Context** — what has already been done and what state the codebase is in. Reference artifacts by path or URL rather than restating them: "The spec is at `docs/specs/auth-redesign.md`", not a paragraph duplicating it.

**Remaining work** — concrete next steps, ordered by dependency. Each step should be actionable without further clarification.

**Constraints** — anything the agent needs to know to avoid going wrong: decisions already made, approaches already rejected, files not to touch, conventions to follow.

**Suggested skills** — which skills the agent should invoke for which steps. Name them: "Use `tdd` for the implementation, `git-commit` when done."

### 3. Launch the background agent

Write the summary to a scratch file, then pass its contents as the prompt — never inline the summary text directly:

```sh
summary_file=$(mktemp)
# write the summary into "$summary_file", then:
claude --bg --name "<descriptive name>" "$(cat "$summary_file")"
```

Always pass `--name` with a short, descriptive label — it appears in `claude agents`, the session picker, and the terminal title. Keep it under ~40 characters: the task, not the plan. Good: `--name "Add rate limiting to /api/auth"`. Bad: `--name "Continue working on the thing"`.

The agent starts in the current working directory and returns immediately. The user manages it with `claude agents`.

### 4. Report what you launched

Tell the user:

- The name you gave the background agent
- A one-sentence summary of what it will do
- That they can check on it with `claude agents`

## Gotchas

- **Pass the summary through a file, not inline.** The summary references artifacts in backticks (`` `docs/specs/auth.md` ``) and may contain `$`. Typed literally inside the double-quoted prompt argument, the shell runs the backticks as a command and expands the `$`, corrupting what the agent receives. `"$(cat "$summary_file")"` is safe because command-substitution output is not re-expanded — the file reaches the agent verbatim.

- **This is a Claude Code workflow.** `claude --bg` and `claude agents` are Claude Code commands. On Codex or Cursor the skill still loads — they ignore `disable-model-invocation` — and running it launches a *separate* Claude session seeded with the summary, rather than continuing the current conversation.

- **The background agent has zero conversation context.** It does not inherit your messages, your tool results, or your mental model — only the summary you write. If a fact matters, it goes in the summary or in a file the summary points at.

- **Don't duplicate artifacts.** A spec, a plan, a commit message, an issue description — these already exist as files or URLs. Reference them; don't paste their contents into the summary. The agent can read them.

- **Redact sensitive information.** The summary becomes the agent's prompt, which may be logged or cached. Never include API keys, passwords, tokens, or PII — reference the secure storage location instead.

- **A background agent can't ask the user questions.** If the remaining work has open decisions, make them before handing off, or document the default the agent should use.

- **Long summaries defeat the purpose.** A summary over ~1000 words is probably restating things the agent can read from the codebase. Point at files; let the agent read them.

- **The agent starts in the same directory but a different process.** It has its own git state, its own tool permissions, and its own context window. A file you changed but didn't save won't be visible to it — commit or write to disk before launching.

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/blob/main/skills/in-progress/claude-handoff/SKILL.md) - claude-handoff, MIT
