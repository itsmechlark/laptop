---
name: withheld-agent
disallowedTools: Edit, Write, NotebookEdit
---

Two violations, see `broken-agent.md`:

10. No description.
11. `disallowedTools` withholds every write tool, yet `readonly` is not set.
    Claude Code would deny writes and Cursor would allow them.
