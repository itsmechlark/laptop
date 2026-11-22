---
name: not-the-filename
description: "Fixture for check-payload's self-test. Not an agent; it lives under spec/ and never ships."
tools:
  - Read
  - Grep
skills:
  - feature-dev
  - no-such-skill
  - tdd
model: sonnet
mcpServers:
  - github
---

# Agent definition fixture

Thirteen deliberate violations across this file, `withheld-agent.md`,
`granted-agent.md`, and the `nested/` directory beside them. `check-payload`
scans this directory before it scans `agents/`: if it does not find exactly
thirteen, the check itself is broken and the run fails loudly. Keep every line
as it is. They are assertions, not prose.

Nine live in this file:

1. The name in the frontmatter does not match the filename.
2. The description is quoted, which the Codex generator would copy verbatim.
3. The tools, written as a block list, grant no Edit or Write, yet `readonly`
   is not set.
4. It preloads `feature-dev`, a flagged skill. The body names
   ~/.agents/skills/feature-dev/SKILL.md, so only the flag fires.
5. It preloads `no-such-skill`, which does not exist. The body names
   ~/.agents/skills/no-such-skill/SKILL.md, so only the absence fires.
6. It preloads `tdd`, which exists and is not flagged, but the body never names
   its path.
7. The model is a Claude alias rather than inherit.
8. It sets `mcpServers`, a capability grant only Claude Code honors.
9. The body holds the TOML literal-string delimiter: '''
