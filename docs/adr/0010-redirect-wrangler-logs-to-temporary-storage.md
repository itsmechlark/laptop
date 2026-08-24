# Redirect Wrangler logs to temporary storage

**Context:** Wrangler writes logs under
`~/Library/Preferences/.wrangler/logs`, which is outside the Codex developer
profile's writable roots. Commands could otherwise run, but each log attempt
reported a filesystem permission error.

**Decision:** Set `WRANGLER_LOG_PATH=/tmp/wrangler` in the Codex subprocess
environment so Wrangler writes beneath the already-writable temporary root.

**Consequences:** Wrangler runs without a user-preferences write grant or
generated log files in project workspaces. Its logs are ephemeral and may
disappear between runs, and the override needs revalidation if Wrangler changes
the environment variable's behavior.

**Rejected:** Granting write access to `~/Library/Preferences/.wrangler` would
widen the sandbox for mutable tool state. Persisting logs in a workspace would
add generated noise to project state, while setting the path to `$TMPDIR` in
Codex config would pass a literal value rather than expand the shell variable.
