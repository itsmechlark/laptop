---
name: documents-for-absent-readers-get-a-cold-read
description: Why specs, PRDs, plans, and handoff files are read by a fresh agent before they leave the conversation, and why that agent keeps the instruction files.
metadata:
  status: accepted
  topic: skill-graph
---

# Documents for absent readers get a cold read

**Context:** `draft-spec`, `draft-prd`, `draft-plan`, and `agent-handoff` each
write for a reader who was not in the conversation, and each checked its draft
only in the session that wrote it. That session is the reader least able to see
what the document leaves out: a term defined aloud, a decision settled in chat,
a "new" helper the code already has all read as present from inside it.
`brainstorming`'s spec review said outright that no separate review cycle was
needed. Google's
[Elephant-Goldfish Model](https://github.com/google/elephant-goldfish-model)
is built on the opposite premise — a zero-context "Goldfish" reads the spec so
the authoring "Elephant" doesn't grade its own memory.

**Decision:** Add one invocable skill, `cold-read`, that dispatches a fresh
read-only agent per lens — comprehension, readiness, reuse, at most two — given
the document and repository access and nothing from the conversation. The four
authoring skills invoke it before showing or launching; `brainstorming`'s spec
review routes to it; `.agents/AGENTS.md` §4 states the rule for any document
meant to outlive the conversation. The author triages each finding as fix,
contest, or ask, and gets one re-read. The reader keeps the global and project
instruction files: coldness means no conversation, not no standards.

**Consequences:** Every spec costs one or two extra agents, a plan one, a PRD
one, a handoff file two, and a re-read doubles that at most. A client with no
way to start a fresh agent skips the read and says so instead of
self-reviewing under the name. Agent briefing prompts are excluded explicitly,
or the rule would apply to the reader's own prompt and recurse.

**Rejected:** EGM's full pipeline — five sequential review stages, an
intermediate synthesizer agent, per-reviewer persona files, and up to sixteen
reviewers in one run. One or two cold readers catch the failure that motivated
this; the rest is cost, and EGM's own harness record shows a run cut off by
usage limits mid-pipeline. Also rejected: isolating the reader from instruction
files as EGM's Claude adapters do with `omitClaudeMd`. Those files are what a
real newcomer would also have, and a reader without them flags the team's own
conventions as undefined. A living-spec drift scanner (`egm-drift-report`) was
not adopted: specs here are decision records written path-free, and the lasting
layer is ADRs and lore.
