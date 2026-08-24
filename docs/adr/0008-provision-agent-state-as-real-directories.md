# Provision agent state as real directories, not symlinks

Supersedes the location decision in
[ADR 0004](0004-machine-local-agent-state-in-repo.md).

**Context:** ADR 0004 placed `standup/` and `out-of-scope/` inside the repo
(`.agents/standup/`, `.agents/out-of-scope/`), git-ignored them, and symlinked
them to `~/.agents/`. That worked until Codex's Seatbelt sandbox began rejecting
symlinked writable roots: `writable root ~/.agents/out-of-scope contains symlink
component; symlinked writable roots are not supported`. The error prevents
thread creation entirely.

**Decision:** `mac` provisions `~/.agents/standup/` and `~/.agents/out-of-scope/`
as real directories (`mkdir -p`) instead of creating them in the repo and
symlinking. The directories are already under `~/`, so they persist across
checkouts without gitignore discipline. The Codex and Claude sandbox configs
both grant writes to `~/.agents/standup` and `~/.agents/out-of-scope`
explicitly, narrowing the `~/.agents` read grant.

**Consequences:** Codex's Seatbelt sandbox accepts the writable roots.
Claude's sandbox already handled symlinks, so the change is neutral there. The
repo-side `.agents/standup` and `.agents/out-of-scope` gitignore rules stay as
defensive guards against accidental creation. A machine that already ran `mac`
has the old symlinks; re-running `mac` replaces them: the migration loop removes
the symlink, creates a real directory, and copies existing content from the old
symlink target so no journal entries or rejection records are lost.

**Rejected:** Removing the per-directory write grants and relying solely on the
`~/Codespace` write grant (which covers the symlink targets inside the repo).
That would work for Claude but not for Codex, where the real paths are now under
`~/.agents/`, outside `~/Codespace`.
