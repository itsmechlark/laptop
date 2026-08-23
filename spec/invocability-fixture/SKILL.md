---
name: invocability-fixture
description: Fixture for check-payload's self-test. Not a skill — it lives under spec/, is never symlinked into skills/, and never ships.
---

# Invocability fixture

Four deliberate violations, one of each kind the invocability check exists to
catch. `check-payload` scans this file before it scans the payload: if it does
not find exactly these four, the check itself is broken and the run fails loudly
rather than passing a payload it never really inspected.

Keep all four lines exactly as they are. They are assertions, not prose.

Violation 1 — telling the agent to invoke a skill the Skill tool refuses:

Invoke the `feature-dev` skill to build it.

Violation 2 — describing an invocable skill as user-invoke-only:

`tdd` is user-invoke-only, so read its SKILL.md.

Violation 3 — naming a path-scoped rule as though it were a skill. This is the
form that shipped: `skills/tdd/SKILL.md` carried it from the day the skill was
written until 2026-08-23, and every other check passed the whole time.

For Ruby projects, the `rspec` skill documents the spec conventions.

Violation 4 — naming a skill that does not exist at all. `no-such-skill` is
reserved for this line; don't make it real.

Hand the rollout plan to the `no-such-skill` skill.
