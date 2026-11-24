# Reviewing agent artifacts

Read this at **Scope the change** whenever the diff touches a file an agent
loads as instructions or a client enforces as policy: a skill, a path-scoped
rule, an instruction file, a subagent definition, a client's permission or hook
config, or code that hands tools to a model. Those files are code — a model or
a client executes them — but they fail differently from application code, and
each kind has a co-shipped skill whose checklist knows how.

The three axes don't change. The specialist checklists feed them; they are not
a fourth axis, and their findings are graded and de-duplicated like any other.

## Why they need their own pass

- **Failure is silent.** A skill whose `name` differs from its directory, a rule
  carrying another host's scoping key, frontmatter one blank line below the top
  — none of these error. The artifact never loads, or loads on every session,
  and nothing in the transcript says so. Nothing downstream will report an
  activation fault, so this review has to.
- **Prose is the control.** "Ask before pushing" in a skill body is the
  safeguard. Deleting that line is a *Removed safeguard* on the Defects axis,
  exactly as deleting an authorization check is.
- **Files loaded together can disagree.** A rule and the instruction file, a
  `SKILL.md` and its reference, two rules matching one path. Nothing warns; the
  model follows whichever it weighed last, and neither file looks wrong alone.
- **A Markdown diff is not a docs diff.** Skimming it as documentation is the
  usual way an agent-artifact review comes back falsely clean.

## Route each file to its specialist

Load each specialist with the Skill tool, or read its `SKILL.md` where you have
no Skill tool — a sub-agent usually doesn't. Where this payload is installed,
that is `~/.agents/skills/<name>/SKILL.md`. Read the checklist sections named
below, not the authoring guidance around them.

**Never load `create-agentsmd` with the Skill tool.** It is a generation prompt,
not a checklist: it opens by tasking the agent with writing an `AGENTS.md`, and
tells it to make sure every listed command works. Loaded mid-review, it argues
for editing the file under review and running its setup commands, which can
mutate the machine. Read its two named sections from the `SKILL.md` instead, and
check that each command *resolves* — the script, task, or target exists —
without running it.

| Kind | Typical paths | Specialist | Apply |
| --- | --- | --- | --- |
| Skill | `**/SKILL.md` and its `references/`, `scripts/`, `templates/`, `assets/` | `agent-skills` skill | Its Validation section, shell checks included |
| Path-scoped rule | `.claude/rules/`, `.cursor/rules/*.mdc`, `.clinerules/`, `.github/instructions/`, `.windsurf/rules/`, `.devin/rules/`, `.amazonq/rules/`, a repo's `rules/` | `agent-rules` skill | Its Validation section; its FORMATS.md for the host's scoping key |
| Instruction file | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md` | `create-agentsmd` skill for content, read rather than loaded (below); the global `agent-instructions.md` and `agent-instructions-layout.md` rules for size and layout | Its Essential Sections and Best Practices — a setup or test command that doesn't resolve, a section the change left stale; the rules' size budget, symlink-not-copy, what belongs at which level |
| Subagent | `.claude/agents/`, `.cursor/agents/`, `.codex/agents/*.toml`, a repo's `agents/` | `agent-safety` skill for the grant; `agent-skills` for the description | [Subagents](#subagents) |
| Client policy | `.claude/settings*.json`, `.codex/config.toml` and its template, `.codex/rules/*.rules`, `.cursor/cli-config.json`, `.cursor/hooks.json`, `.mcp.json`, hook scripts | `agent-safety` skill; `codex-config` skill for Codex | [Client policy](#client-policy) |
| Tool-calling agent code | Tool functions, policy files, orchestration and handoff code in an agent framework | `agent-safety` skill | Its Review checklist; its THREATS.md for the risk a gap leaves open |

The two instruction-file rules auto-load when Claude Code or Cursor opens a
matching file. Codex never reads path-scoped rules, so on Codex, or in a
sub-agent that only ran `git diff`, read them from `~/.agents/rules/` directly.

## Where a failed item lands

| The checklist item fails because… | Axis | Weight |
| --- | --- | --- |
| The artifact can't load, or loads where it shouldn't: name/directory mismatch, another host's scoping key, frontmatter that doesn't start at line 1 or doesn't parse, a glob that matches nothing, a dropped `paths:` that made a rule always-on | Defects | 🟠 High — the change silently does nothing, or taxes every session |
| Policy widened: a deny or ask entry removed, an allow broadened, a hook that fails open, a writable path that reaches the agent's own policy, a read-only role granted write tools | Defects | 🔴 Critical when it exposes secrets or lets a destructive command run unprompted; 🟠 High otherwise |
| One agent now holds private data, untrusted input, and an outbound channel together — `agent-safety`'s lethal trifecta | Defects | 🔴 Critical where the untrusted input is reachable by an outsider; 🟠 High otherwise |
| Content now sits past a client's silent truncation budget | Defects | 🟠 High — the tail is dropped without a word |
| A link, handoff, or reference that doesn't resolve; a handoff that says to invoke a skill only the user can invoke | Defects | 🟡 Medium |
| Two files loaded together now contradict each other | Defects | 🟡 Medium |
| A requirement of the spec or host: the agentskills.io field limits, a host's documented frontmatter shape | Standards | firm (global) |
| A description that won't trigger on the requests it is for, or competes with a sibling for the same words; a body padded with what the model already knows; a rule restating a linter | Standards | judgment, labeled with the specialist's name — `judgment (agent-skills)` |
| A cross-file invariant the repo documents: one policy mirrored across clients, provenance beside attribution, a lock hash beside vendored content | Standards | firm (repo) |

## Probes

**Verify before reporting** asks for a probe on every Critical or High. For
prose, the probe is a command, and it is cheap:

- **A rule's glob** — `git ls-files '<pattern>'` per pattern. Empty is a dead
  rule; thousands of files is an over-broad one.
- **A skill's shape** — the shell block in `agent-skills`' Validation section,
  or `skills-ref validate` where it is installed.
- **Frontmatter** — the first line is `---`, and the block closes and parses.
- **Codex config** — the validator bundled with `codex-config`.
- **An instruction file's budget** — `wc -c` summed across every file one
  client concatenates, the global file included, against the smallest cap in
  `agent-instructions.md`.
- **The repo's own payload checker** — where CI lints skills or rules, read its
  result first; its findings are CI's, not yours.

Trigger behavior has no cheap probe. Where the repo keeps trigger evals, a
changed `description` with an eval set and no re-run is the untested-change
finding on the Standards axis. Running one spends tokens and usually needs a
terminal, so it belongs in Coverage as a gate not run here, with its command.

## Skills and rules across files

The specialist checklists judge one file at a time. A change review also has
to judge what moved together:

- **Every place that states a changed rule moved with it.** The `SKILL.md`, its
  references, and any rule or instruction file that restates the same
  constraint. A reference left behind still resolves and still reads well.
- **A vendored skill edited in place** desynchronizes the hash its lock file
  records. Where the repo vendors skills, that edit is a firm finding;
  re-vendoring or recording the fork is the fix.
- **An instruction to act on fetched content** — "follow the steps in the
  issue", "run what the README says" — turns untrusted text into commands.
  That is a Security defect, not a style choice.
- **Bundled `scripts/` are ordinary code** that runs with the agent's
  permissions. All three axes apply to them in full.
- **Secrets, tokens, and machine-specific paths** travel with the artifact and
  load without anyone choosing to. A secret is a Defect; a personal path is a
  Standards finding.

## Subagents

- **Check the grant each host enforces, not the one the prose claims.** Claude
  Code enforces `tools` and `disallowedTools`, Cursor enforces `readonly`, and
  Codex has no per-agent setting. A role described as read-only that is granted
  Edit or Write is a Defect; one that keeps Bash is read-only only as far as its
  body and the session's sandbox make it. Name the host where nothing enforces
  it.
- **Capability-granting keys** — `hooks`, `mcpServers`, `permissionMode` — widen
  policy from a file nobody reviews as policy, and that other clients don't
  mirror.
- **Delegation narrows.** A subagent's effective permissions must be a subset of
  its caller's (`agent-safety`, *Multi-agent delegation*).
- **A subagent can't ask the user.** A body that depends on a question, an
  approval, or plan mode either stalls or guesses. It has to return the
  question.
- **Wrap, don't restate.** A body that copies a skill's rules drifts from them.
  It should name the skill, plus its `SKILL.md` path for hosts that don't
  preload.
- **The description routes delegation** the way a skill's routes invocation, so
  `agent-skills`' description checks apply to it.

## Client policy

- **Widening is a Defect until the change justifies it.** That covers a removed
  deny or ask entry, an allow broadened to a wildcard, a new allowed network
  domain, a new unsandboxed-command escape, a skip-permissions default, and a
  new writable root that contains policy files. A new allow entry is checked
  against the denials it now shadows.
- **Hooks are policy code.** A hook that allows on a parse error, a missing
  `jq`, or a timeout fails open. One that matches by substring is bypassed by
  quoting or chaining. One that interpolates the tool input into a shell is
  injection, because tool input is model output. Hand a reachable one to the
  `find-bugs` skill for the proof.
- **MCP server entries are dependencies.** A package launched through `npx` or
  `uvx` without a pinned version runs whatever publishes next. A credential
  inline in the config is a committed secret. A server that reads untrusted
  content and holds write or outbound tools completes the trifecta.
- **Mirrored policy moves together.** Where the repo runs several clients off one
  policy, a change to one client's config without its counterparts is a firm
  Standards finding.
- **Codex has its own traps**: `prefix_rule` matches an exact argv prefix,
  permission profiles don't mix with legacy sandbox settings, and a domain table
  enforces nothing without a proxy. The `codex-config` skill covers them and
  bundles the validator.

## Tool-calling agent code

Apply `agent-safety`'s Review checklist to the diff, and file each failed item
on the Defects axis at the severity its consequence earns. The ones that most
often hide in a diff:

- A tool registered and never put on an allowlist, or `allowed_tools: ["*"]`
- A `try`/`except` around the policy check that continues on error
- An approval gate that a retry of the same step skips
- A tool whose downstream credential can do more than the tool's one function
- An audit record that captures prompts or arguments, and with them the PII

Where untrusted input reaches a tool call, the `find-bugs` skill proves the path.
This review records that the path exists.
