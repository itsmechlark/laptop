# Close the feedback loop with backward handoff edges

**Context:** The first-party skill graph runs forward — design to build to ship —
but learning does not flow back. code-review measures against the repo's
documented conventions yet records none when it keeps flagging the same
undocumented thing; review-response never routes a thread that settles a durable
decision to an ADR, nor a placement complaint to codebase-design; and
agent-skills and agent-rules, a documented pair, point only one way. The single
memory loop that exists — triage's out-of-scope, read by slice and draft-spec —
captures rejections at intake, not lessons from shipped work.

**Decision:** Add five backward handoff edges, all body-only, no new skill: (a)
code-review surfaces a recurring or undocumented Standards finding as a candidate
for a rule or an ADR; (b) review-response routes a thread that settles a
hard-to-reverse decision to domain-modeling for an ADR; (c) review-response
routes a placement or wrong-abstraction comment to codebase-design; (d) standup
points a problem that has carried across updates at its durable home
(domain-modeling, agent-rules, or triage) without hosting the look-back itself;
(e) agent-skills names agent-rules as the home for a path-scoped rule. Each edge
only surfaces the capture; the target skill owns the write and its gate.

**Consequences:** A convention found in review reaches the baseline the next
review reads. A durable decision leaves the PR thread and lands in docs/adr/. No
new skill surface, no trigger-eval pairing, no provenance record, no
client-policy mirror — the edges are live via symlink on save. Cross-cycle
distillation of recurring themes is deliberately not built (see Rejected).

**Rejected:** Folding a retro cadence into standup. standup is outward-facing —
client, manager, team, draft-never-send — and already declares retros out of
scope; a retro is inward-facing, feeding the team's own durable memory. Merging
the two would break the audience separation of AGENTS.md §3. A dedicated retro
skill was weighed and deferred rather than rejected: the edges deliver per-change
capture now, and a look-back node can be added later if recurring-pattern capture
proves worth its own trigger-eval-paired surface.

**Evidence:** `skills/code-review/SKILL.md`, `skills/review-response/SKILL.md`,
`skills/standup/SKILL.md`, `skills/agent-skills/SKILL.md` — the four skills whose
handoff sections carry the edges.
