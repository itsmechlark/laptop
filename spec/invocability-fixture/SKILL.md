---
name: invocability-fixture
description: Fixture for check-payload's self-test. Not a skill — it lives under spec/, is never symlinked into skills/, and never ships.
---

# Invocability fixture

Two deliberate violations, one of each kind the invocability check exists to
catch. `check-payload` scans this file before it scans the payload: if it does
not find exactly these two, the check itself is broken and the run fails loudly
rather than passing a payload it never really inspected.

Keep both lines exactly as they are. They are assertions, not prose.

Violation 1 — telling the agent to invoke a skill the Skill tool refuses:

Invoke the `feature-dev` skill to build it.

Violation 2 — describing an invocable skill as user-invoke-only:

`tdd` is user-invoke-only, so read its SKILL.md.
