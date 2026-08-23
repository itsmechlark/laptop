# Laptop

Provisions a macOS machine, and ships the maintainer's AI-agent configuration to
every machine that has run it.

This is the project's glossary. The root context map at `.agents/CONTEXT.md`
shares the filename and nothing else — see **Root context map** below.

## Language

### What ships, and what installs it

**Payload**:
The agent configuration this repo ships to a machine — everything the
provisioner links into `~/.agents`, `~/.claude`, `~/.codex`, and `~/.cursor`.
_Avoid_: cargo

**Published payload**:
The part of the payload `check-payload` takes as its subject: `skills/`,
`rules/`, and the client configs. Narrower than the payload, because a
project-only skill is reachable from neither.

**Global standards**:
`.agents/AGENTS.md` — the maintainer's engineering standards, shipped to every
project on the machine as `~/.claude/CLAUDE.md`. Not this repo's own
`AGENTS.md`, which instructs work *on* the repo and ships nowhere.

**Provisioner**:
`mac` — the POSIX `sh` script that installs packages and runtimes and creates
the symlinks. Idempotent by contract: re-running it is a no-op.

**Client**:
One of the AI coding front-ends this repo configures — Claude Code, Codex,
Cursor. Each owns a dotdir under `$HOME` and expresses the shared policy in its
own schema.

**Parity**:
The invariant that a change to one client's permission, sandbox, hook, env, or
network/filesystem policy is mirrored into every other client's config in the
same commit. Security parity, not identical behavior: the three approval models
differ by design.

### Skills and rules

**Skill**:
A directory under `skills/` with a `SKILL.md`, loaded when invoked — by the
user, or by the model when the description matches.

**Rule**:
A file `rules/<lang>.md` that loads on its own when an open path matches one of
its frontmatter globs. Never invoked.
_Avoid_: skill

**Vendored skill**:
A third-party skill whose body lives in `.agents/skills/<name>/`, is recorded in
`skills-lock.json` with its source and content hash, and reaches `skills/<name>`
by symlink. Not hand-editable: an edit desynchronizes the hash.

**First-party skill**:
A skill authored in this repo, its directory sitting directly under `skills/`
rather than reaching it by symlink. Says who wrote it, not whether it ships — a
project-only skill is first-party too.

**Derived skill**:
A first-party skill authored from outside material, its sources listed in
`skills-provenance.json` and mirrored in the skill's own `## Attribution`. A
subset of first-party, not an alternative to it.

**Relationship**:
How a derived skill tracks one of its sources in `skills-provenance.json`:
`adapted` (forked then diverged, pinned to a `ref`, updated by 3-way reconcile),
`spec` (conforms to an external spec, watch its version), or `inspired-by`
(ideas and terminology only, never synced). One per source, not one per skill.

**Project-only skill**:
A skill that maintains this repo and is deliberately not linked from `skills/`,
so it never ships. Its body sits in `.agents/skills/<name>/` where a vendored
body sits; the missing link is the whole difference.

**Handoff**:
One skill naming another to route work it shouldn't do itself, written
`` `X` skill `` or `` skill `X` ``.

**Flagged skill**:
A skill carrying `disable-model-invocation: true`; the complement is
model-invocable. The key is Claude-only — Codex and Cursor ignore it, so a
flagged skill still auto-fires there.
_Avoid_: user-invoked skill

### Verification

**Fixture**:
A file under `spec/` that `check-payload` reads rather than derives. Most carry
deliberate violations, and there the violation is the assertion: a detection
count that changes fails the run.

**Trigger eval**:
A query set at `spec/trigger-evals/<skill>.json` measuring whether a skill's
description fires on the queries it should and stays quiet on the rest. Run from
a terminal, never in CI.

**Exempt**:
Named on `evals_exempt` or `parity_exempt` in `check-payload` — deliberately
uncovered, not overlooked. A skill leaves `evals_exempt` the first time it
misfires; a `parity_exempt` subject keeps its recorded reason rather than being
dropped.

### Machine-local state

**Root context map**:
`.agents/CONTEXT.md` — a git-ignored, machine-local map of the laptop and its
repos, reached by the four `CONTEXT.md` links. Shares a filename with this
glossary and nothing else: no domain term belongs in it, and no machine path
belongs here.

**Journal**:
`.agents/standup/` — one dated Markdown file per `standup` update, so the next
run can see what was promised. Pruned to 14 days, and git-ignored because the
entries are client-facing status in plaintext.

**Cross-repo rejection**:
A declined request belonging to no single codebase — a standing policy that
would otherwise be re-argued in every repo. Kept in `.agents/out-of-scope/` and
never pruned. A rejection grounded in one codebase goes in that repository's own
`.out-of-scope/` instead.
