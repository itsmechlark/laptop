---
name: subagents-wrap-skills-for-fresh-context-work
description: Why the payload ships seven role subagents that wrap existing skills, why interviews and approvals stay in the main thread, and how one Markdown source reaches Claude Code, Cursor, and Codex.
metadata:
  status: accepted
  topic: agents
---

# Subagents wrap skills for fresh-context work

Terms used here — *payload*, *flagged skill*, *parity*, *subagent* — are
defined in the [glossary](../../CONTEXT.md).

**Context:** The first-party skills already cover the path from idea to merged
change — `brainstorming` and `slice` decide the work, `draft-spec` and
`draft-plan` write it up, `tdd` builds it, `code-review` and `find-bugs` harden
it, `git-commit` and `pull-request` land it. Three of them already dispatch a
fresh agent and brief it in prose each time:

- `feature-dev`'s review phase
  ([`PHASES.md`, Phase 5](../../skills/feature-dev/references/PHASES.md#phase-5-review-and-fix-the-diff))
  sends `code-review`'s Defects axis — the security, correctness, performance,
  and reliability pass, as opposed to its Standards and Spec axes — to an agent
  that did not write the code.
- `cold-read` sends each document to one reader per lens.
- `fan-out` sends one agent per independent partition of a task.

Nothing made a "read-only" agent actually read-only, and each caller rebuilt
the brief. All three clients load subagent definitions, as verified against
their documentation on 2026-11-18:
[Claude Code](https://code.claude.com/docs/en/sub-agents) reads
`~/.claude/agents/*.md`;
[Cursor](https://cursor.com/docs/context/subagents) reads `~/.cursor/agents/`
and, for compatibility, `~/.claude/agents/` and `~/.codex/agents/` — plus the
same three directories at project scope, which outrank them, with `.cursor/`
winning any tie;
[Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents) reads
`~/.codex/agents/*.toml`.

**Decision:** Ship seven role subagents in a top-level `agents/` directory. Each
wraps existing skills rather than restating them — preloaded through `skills:`
on Claude Code, and named by its `~/.agents/skills/<name>/SKILL.md` path in the
body for the clients that do not preload.

| Agent | Wraps | Dispatched by |
| --- | --- | --- |
| `reviewer` | `code-review` | `feature-dev` Phase 5; any session before a commit or PR |
| `bug-hunter` | `find-bugs` | `feature-dev` Phase 5, beside `reviewer` |
| `cold-reader` | — (the prompt carries its lens) | `cold-read` step 2 |
| `implementer` | `tdd`, `git-commit` | `fan-out`, for one task of a `draft-plan` plan |
| `explainer` | `explain`, `codebase-design` | `fan-out`; any session before planning |
| `spec-writer` | `draft-spec`, `draft-plan`, `domain-modeling` | the main session, by description, once a design is agreed |
| `review-responder` | `review-response`, `gh-cli` | the main session, by description, when PR feedback arrives |

No skill dispatches the last two; the client delegates to them when a request
matches their description, or the user names them.

Four rules hold the roster in shape:

- **Questions and approvals stay in the main thread.** Subagents get no
  question tool and no plan mode, so anything that interviews (`brainstorming`,
  `grilling`, `draft-prd`, `triage`, agreeing a cut in `slice`) or seeks
  approval — push, opening a PR, posting a review reply — is the caller's. An
  agent that reaches such a point returns the question instead of guessing. The
  one approved action an agent may take is a commit the caller's brief
  authorizes: `implementer` commits on its own worktree branch only when told
  to, because `fan-out` merges those branches and an uncommitted worktree
  strands the work.
- **A subagent earns its place by starting fresh** — reviewing code it did not
  write, reading a document it did not draft — or by keeping file contents out
  of the main context.
- **The orchestrator stays a skill.** `feature-dev` keeps running in the main
  thread and dispatches the agents it needs. It is flagged, and Claude Code
  will not preload a flagged skill into an agent anyway.
- **Agents do not take `isolation: worktree`.** Claude Code's option branches
  from the default branch and skips `git-worktree`'s config linking (`fan-out`'s
  gotcha), so `implementer` works in a worktree its caller prepared and checks it
  is there before editing.

One Markdown file per agent is the source. `mac` links `agents/` to
`~/.agents/agents`, and that to `~/.claude/agents` and `~/.cursor/agents`.
Codex cannot read Markdown agents, so `scripts/gen-codex-agents` renders
`name`, `description`, and the body into git-ignored
`.codex/generated-agents/*.toml`, which `mac` links to `~/.codex/agents` — the
same generated-output pattern as the Cursor rules
([ADR 0018](0018-generate-cursor-rules-from-canonical-rules.md)).

Cursor reads all three user directories, so it sees every agent twice: as
Markdown, which carries `readonly`, and as Codex TOML, which cannot. The
`~/.cursor/agents` link makes the Markdown win, because `.cursor/` outranks the
other two. The render goes to `.codex/generated-agents/` rather than
`.codex/agents/` for the same reason: inside this repository `.codex/agents/` is
a project-scope directory, and project scope would put the TOML copies ahead of
every user-scope Markdown file.

**Consequences:** The frontmatter is a union that each client reads
differently, per the documentation linked above. The gaps are recorded rather
than closed:

| Field | Claude Code | Cursor | Codex |
| --- | --- | --- | --- |
| `tools` / `disallowedTools` | enforced | ignored — inherits the parent's tools | not rendered — no per-agent allowlist |
| `readonly: true` | ignored (unknown field) | enforced | not rendered |
| `skills:` preload | enforced; a missing or flagged skill is skipped with a debug-log warning | ignored | ignored; skills come from the parent |
| `model` | honored | honored, with different model IDs | not rendered — inherits |

Read-only is therefore partial everywhere. On Claude Code the read-only agents
are denied Edit and Write but keep Bash, which they need for `git diff` and
`gh`, so a write through the shell is stopped only by the body's instructions
and the session's sandbox and permission rules. Cursor enforces `readonly`.
Codex has no per-agent setting, so the body's instructions and the parent's
sandbox and approval policy are all there is. Codex documents that an agent file
cannot override the parent's sandbox or approval settings, so no agent can widen
them. No agent changes any client's permission, sandbox, or network policy. The one
policy change this decision makes, write-protecting the rendered TOML, is
mirrored across all three clients ([ADR 0002](0002-one-policy-three-clients.md)).

`check-payload` enforces the shared shape. It fails when:

- `agents/` holds a subdirectory or a non-`.md` entry — Claude Code scans
  recursively, while the generator and the check read only the top level;
- the name differs from the filename, or the description is missing;
- a name or description is quoted or a block scalar, which the generator would
  copy into TOML verbatim;
- `model` is anything but `inherit` — Claude's aliases mean nothing to Cursor;
- the file sets `hooks`, `mcpServers`, or `permissionMode`, which grant
  capability on Claude Code alone and would widen policy from a file no other
  client mirrors;
- a preloaded skill does not exist, is flagged, or is not named by its
  `SKILL.md` path in the body;
- the write tools Claude Code would grant — Edit, Write, NotebookEdit, after
  both `tools` and `disallowedTools`, in either list shape — disagree with
  `readonly`;
- the body contains `'''` and cannot be a Codex TOML literal string.

A fixture with at least one violation of each kind must yield exactly thirteen
detections ([ADR 0006](0006-fixtures-assert-with-deliberate-violations.md)).
The check also renders the Codex TOML into a temp
directory and parses it with Python's `tomllib` — a warning, not a failure, on a
machine without Python 3.11+. It does not compare against the rendered copy in
`.codex/generated-agents/`, so a Codex copy left stale by an edit without `sh mac` goes
undetected.

Adding or editing an agent is live on Claude Code and Cursor through the
directory link; Codex needs `sh mac` to regenerate. Like every link `mac`
makes, an existing real `~/.claude/agents`, `~/.cursor/agents`, or
`~/.codex/agents` directory is moved to `<dir>.backup` on the first run; a user
with their own agents there moves them into `agents/` afterwards.

The rendered TOML is what Codex loads as instructions, so no agent may write
it: Claude Code denies `Edit` and sandboxed writes to
`.codex/generated-agents/` and `~/.codex/agents/`, Cursor denies
`Write(~/.codex/agents/**)` beside its existing `Write(**/.codex/**)`, and
Codex's `.codex/** = "read"` already covers the repository copy. Only `mac`,
run by a person, writes it. The source in `agents/` stays as writable as
`skills/`: editing it is ordinary work on this repository.

**Rejected:**

- **An orchestrator subagent running the whole pipeline.** It could not ask the
  user to agree a slice, approve a push, or settle a design question, which
  are the points where the pipeline needs a person.
- **Per-stack agents (Rails, Ember, TableKit).** Rules load by path and skills
  trigger on their own, so a stack agent adds a delegation hop and no knowledge.
- **Hand-maintained TOML beside the Markdown.** Two copies of every body drift;
  one source and a generator cannot.
- **Relying on Cursor's `~/.claude/agents` compatibility alone.** Cursor would
  also load the Codex TOML from `~/.codex/agents`, and which copy wins a name
  tie between those two is undocumented — the TOML winning drops `readonly`.
- **Rendering into `.codex/agents/`.** Inside this repository that is a
  project-scope directory for Cursor and Codex both, and would outrank the
  Markdown there.

**Evidence:** `agents/`, `scripts/gen-codex-agents`, the agent checks in
`scripts/check-payload`, `spec/agents-fixture/`, and the dispatch points in
`skills/feature-dev/references/PHASES.md`, `skills/cold-read/SKILL.md`, and
`skills/fan-out/SKILL.md`.
