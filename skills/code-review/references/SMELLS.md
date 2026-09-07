# The smell baseline

Twelve smells from Fowler, *Refactoring* (2nd ed.), ch. 3. This is the Standards
axis's floor — what's left when neither the repo nor the global standards speak
to the code. It is the weakest of the three source tiers, so everything here is
a judgment call.

Read it when working the Standards axis. When that axis runs as a sub-agent,
give the agent this file's path — it has no other access to the baseline.

**Three rules bind how you use it:**

- **The repo overrides.** Where a documented standard endorses something here,
  drop the smell. Where the repo is silent, the global standards
  (`~/.agents/AGENTS.md`, plus whichever `rules/*.md` matched the changed paths)
  still sit above this list.
- **Label it, never assert it.** "possible Feature Envy", not "Feature Envy
  violation". Only a documented limit makes a finding firm, and a linter usually
  owns that limit already — skip anything a linter, formatter, or type-checker
  enforces.
- **Count what's countable.** Some of these are defined by a number: extent,
  ratio, length, scatter. Give the figure. "possible Message Chains (4 hops)" is
  falsifiable; "possible Message Chains" is an opinion. A count is evidence for a
  judgment call, never what promotes one to firm.

| Smell | What it looks like | Fix | Count to report |
| --- | --- | --- | --- |
| **Mysterious Name** | Name doesn't reveal intent | Rename; if no honest name comes, the design is murky | — |
| **Duplicated Code** | Same shape in more than one hunk | Extract, call from both | Duplicated lines, and how many sites |
| **Feature Envy** | A method reaches into another object's data more than its own | Move it onto that data | Foreign accesses against own |
| **Data Clumps** | The same fields keep traveling together | Bundle into one type | — |
| **Primitive Obsession** | A primitive standing in for a domain concept | Give the concept a small type | — |
| **Repeated Switches** | The same `switch`/`if`-cascade on one type recurs | Polymorphism, or one shared map | Sites switching on the same type |
| **Shotgun Surgery** | One logical change forces scattered edits | Gather what changes together | Files the one change touched |
| **Divergent Change** | One module edited for unrelated reasons | Split so each changes for one reason | — |
| **Speculative Generality** | Abstraction for needs the spec doesn't have | Delete, inline back | — |
| **Message Chains** | Long `a.b().c().d()` navigation | Hide the walk behind one method | Hops |
| **Middle Man** | A class that mostly delegates onward | Cut it, call the target directly | Delegating methods against total |
| **Refused Bequest** | A subclass ignoring most of what it inherits | Prefer composition | — |

**A smell you keep flagging is a missing standard.** Say so in the report: it's
a candidate for a path-scoped rule (`agent-rules`) or an ADR
(`domain-modeling`), not one more finding about this diff.

**Where a smell is really a misplaced seam, name it as one.** "This class does
two things" is a design finding, not a rename — `codebase-design` has the
vocabulary for where the boundary belongs.
