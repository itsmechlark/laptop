---
name: agent-handoff
description: Hand the current work off to a fresh agent session — Claude Code, Codex, or Cursor — by writing a dated handoff file and launching an agent against it. Use when asked to hand off, continue in the background, pass work to another session or a different agent, start a background agent to finish a task, or write up where the work stands for whoever picks it up next.
argument-hint: "[what the next session should focus on] [for claude|codex|cursor|none]"
disable-model-invocation: true
---

# Agent handoff

Write the state of the work to a dated file, then launch a fresh agent against that file. **The file is the handoff; the launch is a pointer to it.** Anyone — the next agent, a different client, you in a week — starts from the same bytes.

Focus: `$ARGUMENTS`. Empty means hand off whatever the conversation's current task is, to the client you are running in.

## When to use this skill

- The conversation has reached a natural breakpoint and remaining work can continue unattended
- Context is getting long and a fresh session would work more efficiently
- The user wants to move on while this work finishes elsewhere
- The work should continue in a *different* agent than the one running it
- The user wants the state written down and nothing launched — the file is the deliverable
- Not for dispatching several agents at independent sub-problems in parallel — that's `fan-out`
- Not for continuing work yourself in the same session — just keep working
- Not when the remaining work needs the user's input at every step — a launched agent can't ask questions
- Not for what the work taught about the codebase — that outlives the handoff and is `lore`

## Workflow

### 1. Take stock

Before writing anything, identify:

- What has been accomplished (decisions made, files changed, gates run)
- What remains, ordered by dependency
- What the user said the next session should focus on (`$ARGUMENTS`)
- Which artifacts already hold the state — specs, plans, commits, open PRs, issue descriptions

### 2. Find where the file goes

```sh
root=$(git rev-parse --show-toplevel)
dir="$root/docs/handoffs"; [ -d "$dir" ] || dir=~/.agents/handoffs
echo "$dir"
```

Anchor to the repo root, not the working directory — run from a subdirectory, a relative `docs/handoffs` misses the one that exists and sends the file to the global root instead. Keep `$dir`; step 3 greps the same directory it resolved.

The repository's `docs/handoffs/` when it exists. **When it doesn't, the handoff goes to `~/.agents/handoffs/` and carries `metadata.repo`** — never create `docs/handoffs/` in a repository that doesn't have one, and don't substitute `docs/`. The directory existing is how the repository opts in. Say which of the two paths you wrote to.

### 3. Write it

`<YYYYMMDDHHMMSS>-<kebab-slug>.md`, the timestamp from `date +%Y%m%d%H%M%S` and never from memory — it is the sort order, so a wrong one files the handoff in the wrong place in the chain forever.

```yaml
---
name: retry-backoff-on-webhook-delivery
description: Retry policy is in place; the dead-letter path and its specs are what remain.
metadata:
  status: open
  topic: webhook-delivery
  agent: codex
  supersedes: []
  repo: billing-api     # only in ~/.agents/handoffs/ — omit in a repo's own docs/handoffs/
---
```

`status` is `open` while the work is unfinished, `done` once it lands, `superseded` when a later handoff takes over. `agent` is the one you launch in step 5, or `none` when nothing is launched. `topic` is the join key this shares with the spec, plan, and lore notes for the same work. Before writing, look for what this continues:

```sh
grep -l 'topic: <topic>' "$dir"/*.md 2>/dev/null
```

**Search whichever directory step 2 settled on**, which is what `$dir` holds. A handoff bound for `~/.agents/handoffs/` that greps only `docs/handoffs/` finds nothing and silently starts a second chain for work that already had one. In the global root, match `repo:` as well — it is flat and shared across projects, so a `topic` is only unique within one of them.

A match means that handoff gets `metadata.status: superseded` and this one names **its filename** in `metadata.supersedes`, which is a list. The link is one-directional, as in `lore` — never edit the predecessor's body to hold the new state.

Then copy [templates/handoff.md](templates/handoff.md) and fill it — Goal, Context, Remaining work, Constraints, Gates, Suggested skills. **Use the template rather than composing the sections yourself**, whichever client you are: a handoff is read by an agent that did not write it, and the shape being identical every time is what lets it be read without being parsed. The template carries its own filling instructions, including deleting them as you go.

Four rules decide the prose, because this file outlives the moment it describes:

- **Never describe work by its commit status.** "Uncommitted", "staged", "nothing staged", "the tree is clean" — each is false the moment the handoff is committed, and the reader has no way to tell whether it still holds. Identify the change by what it is: its task, its branch, its files.
- **Reconcile against git before writing.** `git status`, `git log`, and `git diff` are what say where the work actually stands. What you remember doing and what is on disk diverge.
- **Scope it to the latest task.** Earlier work is in git history and in the superseded handoffs. Don't carry a section, a decision, or a gate result forward because the previous handoff had one.
- **Don't edit a handoff once written, except to flip its `status`.** A dated record that gets rewritten is not a record. The correction is the next handoff.

### 4. Settle which agent

The user names it — "hand this to codex", "for cursor". **Their choice wins even when you are a different client.** With none named, use the client you are running in: it is the one whose auth, config, and permissions you know are working.

"None" is a valid answer. Where the user asked only for the state to be written down, record `agent: none`, skip step 5, and report the path — principle 6.

### 5. Launch it

Resolve the binary, confirm the flags, pass the *path*:

```sh
command -v <binary> >/dev/null \
  && <binary> <non-interactive-flag> "Continue the work described in <path/to/handoff.md>. Read it first." \
  || echo "<binary> not installed — handoff written, nothing launched"
```

| Agent | Binary | Non-interactive start | Session label |
| --- | --- | --- | --- |
| Claude Code | `claude` | `--bg` — returns immediately, managed with `claude agents` | `-n`/`--name` |
| Codex | `codex` | `codex exec` — foreground; background it with the shell | none |
| Cursor | `cursor-agent` | `-p`/`--print` — foreground; background it with the shell | none; `--resume <chatId>` reattaches |

**Only Claude Code backgrounds itself.** Codex and Cursor run in the foreground and return when the work is done, so a handoff meant to be unattended needs the shell to detach it — and the user should be told which they got, because one returns immediately and one does not.

All three rows were confirmed against the installed CLIs on 2026-09-12. Confirm them again anyway; that is principle 3, and it is why the table is a starting point rather than the instruction.

### 6. Report

Tell the user the path you wrote, which agent you launched, a one-sentence summary of what it will do, and how to check on it — `claude agents` for a Claude session started with `--bg`, and for the other two, whether you detached it or it is still running in front of you.

## Guiding principles for the launch

These decide the cases the table doesn't cover, including clients added later.

1. **The named agent wins.** Never substitute one for another because it is the one you are running in or the one you know best. If the user said Codex and Codex is missing, say so and stop — the handoff file still stands on its own, and a different agent is the user's call.
2. **Default to the client you are running in.** Unnamed, it is the only one whose auth and permissions you have evidence for.
3. **Confirm the flag from `--help`, never from memory.** These CLIs move. Three things to find each time: how to start non-interactively, how to label the session, and how the prompt is passed. A flag that was right last month is a launch that silently opens an interactive session nobody is watching.
4. **Pass the file path, never the file's contents.** The prompt stays short, the handoff the agent works from is the same bytes anyone else reads, and the shell never gets the chance to run the backticks or expand the `$` in a summary that references `` `docs/specs/20260911142205-webhook-retry.md` ``.
5. **Make the decisions before you hand off.** A launched agent cannot ask a question. Every open choice is either settled in `Constraints` or written down as the default it should take.
6. **The launch is optional; the file is not.** No binary, no auth, or the user only wanted the state captured — write the handoff and say where it is. A handoff nobody launched is still the next session's starting point.

## Gotchas

- **The launched agent has zero conversation context.** It does not inherit your messages, your tool results, or your mental model — only the file. If a fact matters, it goes in the handoff or in something the handoff points at.

- **Don't duplicate artifacts.** A spec, a plan, a commit message, an issue description — these already exist as files or URLs. Reference them; the agent can read them.

- **Redact sensitive information.** The handoff is a file that may be committed and a prompt that may be logged. Never include API keys, passwords, tokens, or PII — reference the secure storage location instead.

- **Long handoffs defeat the purpose.** Past ~1000 words it is restating what the agent can read from the codebase. Point at files.

- **Write to disk before launching.** The agent starts in the same directory but a different process, with its own git state, its own permissions, and its own context window. An unsaved edit is invisible to it.

- **`~/.agents/handoffs/` is flat and shared across projects**, which is why `metadata.repo` is required there — the repository's name, never a path.

- **A `done` handoff is closed out, not deleted.** Flip `metadata.status` when the work lands. Deleting it erases the chain, which is the part no PR description holds.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| The named agent's binary isn't installed | Say so and stop. The file is written; which agent to use instead is the user's call, not a substitution you make (principle 1). |
| The launch opened an interactive session and is sitting there | Wrong flag for that client. Re-read its `--help` — only `claude --bg` returns on its own; the other two need the shell to detach them. |
| `docs/handoffs/` doesn't exist and the repo looks like it wants one | Write to `~/.agents/handoffs/` anyway and say so. Creating the directory is the team's call; offer it, don't take it. |
| Two handoffs for the same work, hours apart | One supersedes the other. Flip the older one's `status`, name its filename in the newer one's `supersedes`. |
| The remaining work still has an open decision in it | Settle it before handing off, or write the default into `Constraints`. A launched agent cannot come back and ask. |
| The handoff is running past ~1000 words | It has started restating the codebase. Cut back to what points at files. |
| You are mid-task and the user asks for a handoff | Reconcile against git first. What you remember changing and what is on disk are not the same list. |

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/blob/main/skills/in-progress/claude-handoff/SKILL.md) - claude-handoff, MIT
