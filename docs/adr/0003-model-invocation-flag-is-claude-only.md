# The model-invocation flag narrows Claude only; the skill body carries the guarantee

**Context:** Some skills are expensive to auto-invoke because firing has
consequences outside the conversation — a write to a tracker (`triage`), a long
workflow ending in a commit (`feature-dev`), text drafted for a client
(`standup`). `disable-model-invocation: true` stops Claude reaching for them.
Codex and Cursor ignore the key, so on those two clients the same skill
auto-fires like any other.

**Decision:** Flag those skills anyway, *and* write the guard into the body —
`triage` drafts and asks before writing, `standup` never sends. The frontmatter
narrows when Claude reaches for a skill; the body is what stops the side effect
on every client.

**Consequences:** A flagged skill whose only protection is the flag is protected
on one client in three, so for anything outward-facing the flag is never
sufficient on its own. Flagging also changes how siblings hand off: the Skill
tool refuses a flagged target, so a handoff has to say *read and follow its
`SKILL.md`* instead of "invoke" it — mis-worded handoffs fail the build via
`check-payload`'s invocability check rather than failing at runtime. Mid-chain
skills that others call constantly stay invocable, because every caller pays
the indirection.

**Rejected:** Treating the flag as the guarantee — the assumption this record
exists to deny, and the one a reader is most likely to arrive with. Dropping the
flag and relying on the body alone was the other option: it would remove the
handoff-wording constraint, but it also gives up the only lever that narrows
Claude's own skill selection, and the expensive-misfire cases are precisely the
ones worth narrowing.
