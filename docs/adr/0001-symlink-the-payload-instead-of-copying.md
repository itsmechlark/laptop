# Symlink the payload into the home dotdirs instead of copying it

**Context:** This repo is the single source of truth for how coding agents
behave on every machine that has run `mac`, so an edit to a skill or a rule has
to reach `~/.claude`, `~/.codex`, and `~/.cursor` somehow.

**Decision:** `mac` symlinks whole directories and files — `skills/`, `rules/`,
the client configs — into the home dotdirs rather than copying them.
`symlink_path` returns early when the link already matches, and moves a
pre-existing real file to `<path>.backup` before linking.

**Consequences:** An edit in the repo is live immediately; only a *new*
top-level link needs `sh mac` again. In exchange the checkout becomes
load-bearing at runtime — move or delete it and every client loses its config —
and because the home paths resolve back here while the agent sandbox restricts
the home dotdirs, edits have to go through the repo path or hit a permission
wall. `.codex/config.toml` is the one exception, generated from a template
because Codex needs an absolute Unix-socket path.

**Rejected:** Copying the payload in. It would decouple the machine from the
checkout, but then every payload edit would require re-running a provisioner
that also runs `sudo chsh` and appends to `~/.zshrc` — iterating on a skill
would mean repeatedly running a script that is explicitly not side-effect free.
