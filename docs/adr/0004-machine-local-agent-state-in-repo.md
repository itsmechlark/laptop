# Machine-local agent state lives in the repo, git-ignored

Location decision superseded by
[ADR 0008](0008-provision-agent-state-as-real-directories.md).

**Context:** Two workflows need state that outlives a session: `standup` has to
see what it promised last time, and rejections that belong to no single codebase
would otherwise be re-argued in every repo. All three clients sandbox writes, so
that state has to sit somewhere all three already grant.

**Decision:** The directories live in the repo — `.agents/standup/` and
`.agents/out-of-scope/` — created by `mac`, linked to `~/.agents/standup` and
`~/.agents/out-of-scope`, and git-ignored. `out-of-scope` is deliberately not
namespaced under a skill: `triage` writes it, `slice` and `draft-spec` read it,
so it is shared project memory rather than one skill's private state.

**Consequences:** No per-client wiring is needed — `~/.agents` is already a
write root in all three sandbox configs, so both directories are writable
without a new grant. The ignore rules are load-bearing: the journal holds
client-facing status in plaintext inside a repository that is published, and
committing it once is a leak that a later deletion doesn't undo. State is
machine-local, so a new machine starts empty and nothing syncs between them.
The journal prunes to 14 days; the rejections never prune, because outliving
the ticket is the point.

**Rejected:** A location outside the repo, such as `~/.local/state/laptop`.
Better on privacy grounds — no ignore rule to get wrong — but it needs a new
write grant in each of the three sandbox configs, mirrored under the parity
rule, for state no reviewer ever reads.
