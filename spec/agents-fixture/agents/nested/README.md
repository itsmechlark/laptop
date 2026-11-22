The 14th violation, see `../broken-agent.md`: this directory exists inside an
agents root. Claude Code scans subdirectories, while `gen-codex-agents` and
`check-payload` read only the top level.
