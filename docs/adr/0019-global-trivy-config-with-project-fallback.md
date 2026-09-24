---
name: global-trivy-config-with-project-fallback
description: Why a machine-wide Trivy config is applied through a bin/trivy shim, only when a repo ships no ./trivy.yaml.
metadata:
  status: accepted
  topic: verification
---

# A global Trivy config with a project-config fallback

**Context:** The Definition of Done gained a dependency-vulnerability gate
(`trivy fs --scanners vuln .` at closeout, `.agents/AGENTS.md` §4), which wants
sane defaults — severity floor, scanners, ignore-unfixed — available in any repo,
not re-specified per project. Trivy reads a `trivy.yaml` from the current
directory but has **no** machine-wide or user-level config discovery: no
`~/.config/trivy`, no XDG fallback. When the default `trivy.yaml` is absent it
silently uses built-in defaults and never looks elsewhere (confirmed against
v0.74.0 and the docs). So "project config wins, else a global default" cannot be
had from Trivy alone — the fallback has to be supplied.

The repo already has the shape for machine-wide tooling config: a tracked file
symlinked into `$HOME` (`srt-settings.json` → `~/.srt-settings.json`) and PATH
shims in `~/.bin` (`bin/srt`, `bin/elixir-ls-mcp`; `~/.bin` is prepended to PATH
in `mac`).

**Decision:** Track `trivy.yaml` at the repo root and symlink it to
`~/.config/trivy/trivy.yaml`, and add a `bin/trivy` shim symlinked to
`~/.bin/trivy`. The shim delegates to the real Trivy untouched when a project
`./trivy.yaml` exists (Trivy reads it natively), and otherwise injects
`--config ~/.config/trivy/trivy.yaml` — the fallback Trivy will not perform
itself. Because `~/.bin` is ahead of Homebrew on PATH, the shim resolves the real
binary by prefix (`/opt/homebrew`, then `/usr/local`) rather than through
`command trivy`, which would re-find the shim and loop. The global defaults scan
`vuln`, `secret`, and `misconfig` at `HIGH`/`CRITICAL`, ignore unfixed findings,
and exit non-zero on a hit.

An env var (`TRIVY_CONFIG`) was rejected: it pins the config path
unconditionally, so a project `./trivy.yaml` would be ignored — the opposite of
project-wins.

The config path (`~/.config/trivy`) and the shim (`~/.bin`) are granted read
access in the Claude and Codex sandboxes so the gate runs confined; Cursor does
not sandbox reads. This follows the parity invariant in
[ADR 0002](0002-one-policy-three-clients.md).

**Consequences:**

- The shim shadows Homebrew's `trivy` on PATH. Anyone invoking `trivy` gets the
  fallback behavior, which is the intent; the real binary is still reachable at
  its Homebrew path.
- Injecting `--config` on the fallback branch relies on the global file always
  existing (it is symlinked by `mac`), so `--config` never errors — including for
  `version`/`--help`, which ignore it.
- The DoD gate's `trivy fs` needs Trivy's vulnerability DB, pulled from a
  registry on first run, and that download cannot complete inside the agent
  sandbox. Verified: with the registry hosts allowlisted they are reachable
  (curl gets the registry's `401`), but the sandbox proxy terminates TLS and
  Trivy's Go runtime on macOS verifies through the Security framework, which
  rejects the proxy's leaf (`tls: failed to verify certificate: OSStatus
  -26276`). `SSL_CERT_FILE` does not help — Go on darwin ignores it and always
  uses the platform verifier — so no allowlist or CA-bundle change makes the
  sandboxed download succeed.
- Resolution: `trivy` runs **unsandboxed with per-use approval**, mirroring
  `srt` — `permissions.ask` `Bash(trivy *)` plus `sandbox.excludedCommands`
  `trivy *` on Claude; a `"trivy"` = `"prompt"` rule on Codex, escalated out of
  Seatbelt by `on-request` approval; Cursor runs it unsandboxed already and
  prompts because it is unlisted. The agent sandbox also captures DNS at a
  level below environment variables, so the DB download cannot complete inside
  an agent session even when unsandboxed. **The vulnerability DB must be
  pre-seeded from a regular terminal** (`trivy image --download-db-only`);
  subsequent `trivy fs` scans in agent sessions use the cached DB. The
  tradeoff: a vulnerability scanner runs without the sandbox's
  network/filesystem confinement. It is read-only in normal use and every
  invocation is gated by an approval prompt, the same trust model as `srt`.
  The registry allowlist entries stay — they are still what a
  non-intercepting sandbox would need.
- `bin/trivy` is not write-guarded the way `bin/srt` is. It wraps a read-only
  scanner, not a gate-bypassing sandbox, so the hijack surface is lower; guarding
  it later is cheap if wanted.
