---
name: granted-agent
description: Fixture for check-payload's self-test, never shipped.
tools: Read, Edit
readonly: true
---

One violation, see `broken-agent.md`:

13. `readonly: true`, yet the tools grant Edit, so Claude Code would let it
    write where Cursor would not.
