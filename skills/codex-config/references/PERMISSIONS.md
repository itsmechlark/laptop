# Permission profiles and network policy

Read this reference for permission profiles, filesystem access, sandbox
migration, or command-network restrictions. Permission profiles are beta and
version-sensitive; verify material changes against the target Codex binary and
[official permissions documentation](https://developers.openai.com/codex/permissions).

## Permission model

Permission profiles combine filesystem and network policy. They do not compose
with the legacy sandbox model.

Reject an effective configuration that mixes either `default_permissions` or
`[permissions]` with `sandbox_mode`, `sandbox_workspace_write`, or a CLI
`--sandbox` override. A managed `allowed_permission_profiles` requirement
selects the profile model; remove legacy sandbox settings before deploying it.
Pass the active CLI sandbox mode to the bundled validator with `--sandbox MODE`.

Prefer extending `:read-only` or `:workspace` when its baseline protections
should carry forward. A custom profile should add only the access its workflow
needs.

## Filesystem rules

Filesystem decisions are `read`, `write`, and `deny`. More-specific paths
override broader paths; at the same path, restrictive precedence is
`deny > write > read`.

For `read` and `write`, prefer a portable subset:

- an exact path, such as `.codex/config.toml` or `~/Codespace`;
- a simple trailing subtree, such as `.codex/**` or `docs/**`.

Reserve arbitrary recursive or mid-path globs for `deny`. The bundled validator
rejects broader `read`/`write` patterns because their resolution is easy to
misread and less portable.

Rules under `[permissions.<profile>.filesystem.":workspace_roots"]` are
relative to every effective workspace root. Use `.` for the root and reject
parent traversal such as `../other-repo`.

Unbounded `**` deny globs may need `glob_scan_max_depth` on Linux, WSL, and
native Windows. Use a positive, deliberately bounded depth when the target
platform requires pre-expansion.

## Network rules

`network.enabled = true` permits command networking; it does not activate
domain filtering. Profile domain rules require either:

```toml
[features]
network_proxy = true
```

or enabled administrator-managed `[experimental_network]` requirements.
Without an active proxy, direct command networking bypasses the domain table.

Domain forms differ:

- `example.com` matches the exact host;
- `*.example.com` matches subdomains only;
- `**.example.com` matches the apex and subdomains;
- `*` permits all public destinations and needs explicit justification.

Deny rules override allow rules. Keep local binding, upstream proxies,
non-loopback listeners, broad Unix-socket access, and similar escape hatches
disabled unless the workflow requires them. Allowed Unix sockets should use
absolute paths.

## Review checks

- No permission-profile/legacy-sandbox mixing.
- No arbitrary `read` or `write` glob.
- Workspace-relative paths do not escape with `..`.
- Recursive deny globs have appropriate scan-depth handling.
- Domain rules have an active proxy.
- Broad network and local-network exceptions are intentional.
