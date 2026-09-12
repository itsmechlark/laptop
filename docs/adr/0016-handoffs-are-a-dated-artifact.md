---
name: agent-handoff-artifact
description: The handoff becomes a dated file under the ADR 0014 opt-in, and its launch stops naming one client.
metadata:
  status: accepted
  topic: artifact-frontmatter
---

# Handoffs become a dated artifact with a client-agnostic launch

Extends [ADR 0014](0014-fall-back-to-a-global-home-when-the-repo-has-not-opted-in.md)
with a ninth root, and overrides the one-line exclusion
[ADR 0013](0013-one-frontmatter-shape-for-authored-artifacts.md) made of this
skill.

**Context:** `claude-handoff` wrote a summary to a temp file, passed it to
`claude --bg`, and let it go. ADR 0013 excluded it from the artifact frontmatter
standard on exactly that basis — "a temp file consumed once by a subagent" — and
ADR 0014's table has no row for it, because a file that lives for one command
has nowhere to fall back to.

Two problems followed from that shape. The skill named one client in its own
name and hardcoded that client's flag, while the payload ships to three under the
parity rule ([ADR 0002](0002-one-policy-three-clients.md)) — a Codex user
invoking it got a skill that launched Claude. And a handoff that exists only as a
prompt cannot be read by anyone. The state the last session stopped at is
recoverable only by asking the agent that received it, and nothing anywhere
records that a handoff happened at all.

**Decision:** The skill is `agent-handoff`, and the handoff is a durable dated
artifact rather than a prompt.

It is written as `<YYYYMMDDHHMMSS>-<kebab-slug>.md` to `docs/handoffs/` where the
repository has one, else to `~/.agents/handoffs/` carrying `metadata.repo`. ADR
0014's rule governs it unchanged: the directory's existence is the opt-in, and
the skill never creates the repo path. `mac` provisions the ninth root as a real
directory ([ADR 0008](0008-provision-agent-state-as-real-directories.md)) and all
three clients grant it write.

It carries ADR 0013's three-key block, with `metadata` holding `status`
(`open`, `done`, `superseded`), `topic`, `agent`, `repo`, and `supersedes`. This
overrides that ADR's exclusion, which rested entirely on a premise that no longer
holds. `topic` earns its place immediately: it is the join key that already
threads a spec to its plan to the lore note, and the handoff is the link that was
missing between the plan and the note.

Supersession works as lore's does — the predecessor's `status` flips, the
successor names it, the link is one-directional. A handoff is never edited after
it is written except to flip that field, so what the previous agent believed
survives being wrong.

The body comes from a template under `templates/`, not from the skill prose, and
filling it is mandatory rather than suggested. A handoff is the one artifact here
routinely written by one agent and read by a different one, so the shape holding
still across clients is most of its value — a Codex handoff and a Claude handoff
that organize the same facts differently force the reader to parse before it can
read. The template also carries the section the prose kept losing: `Gates`, which
says what was run and what came back, and without which the next agent either
re-runs a full suite or assumes a green it has no evidence for.

The launch becomes the second half rather than the point. The prompt is a pointer
to the file, the user names the agent and their choice wins, and an unnamed agent
defaults to the client actually running. Per-client invocation is resolved from
`--help` at launch time rather than hardcoded, behind six stated principles, so a
client the table does not list can still be launched and a flag that moved is
caught rather than silently opening an interactive session nobody watches.

**Consequences:** The artifact chain closes. A PRD, the slices cut from it, the
spec, the plan, the handoff, and the lore note now share one `topic`, and the
handoff is the only one of them that says where the work stopped.

A handoff is now reviewable, committable, and searchable, which also means it is
publishable by accident. The redaction gotcha carries more weight than it did
when the file lived for one command in `$TMPDIR`.

The directory grows and nothing prunes it. `standup` prunes to 14 days because a
journal is read by recency; a handoff chain is read by `topic` and stays short
per topic, so supersession is the whole mechanism and a sweep would erase the
part worth keeping.

All three launch forms were confirmed against the installed CLIs, and they are
not symmetric: only Claude Code backgrounds itself, while `codex exec` and
`cursor-agent --print` run in the foreground and return when the work is done.
A handoff meant to be unattended therefore needs the shell to detach two of the
three, and the user has to be told which kind they got. The table is a dated
snapshot rather than the instruction — principle 3 is what keeps a flag that
moves from turning into a launch that silently does something else.

The word "handoff" now carries two senses here: the cross-skill routing the
invocability check enforces, and this artifact. `CONTEXT.md` records both, the
way it already separates the two `CONTEXT.md` files.

**Rejected:** A `latest.md` singleton, overwritten per task, which is the shape
the convention was borrowed from. It needs no timestamp, no slug, and no
supersession field, and it always answers "what is the current baton" in one
path. It was rejected on two counts. The chain is the value — an overwritten file
erases why the previous agent stopped, which is the question asked most often
after a handoff goes wrong. And a singleton cannot live in a flat global root
shared across projects, so the repo-opt-in path and the fallback path would have
needed two different shapes.

Also rejected: generalizing only the launch and leaving the summary ephemeral.
It is much the smaller change and fixes the client-lock complaint on its own. It
was rejected because the client-lock was the lesser of the two problems; a
handoff nobody can read is the one that costs a session.

Also rejected: hardcoding all three clients' flags into a table and keeping it
current. It reads better than "consult `--help`" right up until a flag changes,
at which point the skill launches something other than what it says it does.

**Evidence:** `skills/agent-handoff/SKILL.md`,
`skills/agent-handoff/templates/handoff.md`, `mac`,
`.claude/settings.json`, `.codex/config.toml.template`, `.cursor/cli-config.json`
