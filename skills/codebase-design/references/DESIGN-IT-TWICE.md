# Design It Twice

When the user wants to explore alternative interfaces for a chosen deepening candidate, use this parallel sub-agent pattern. Based on "Design It Twice" (Ousterhout) — your first idea is unlikely to be the best.

Uses the vocabulary in [SKILL.md](../SKILL.md) — **module**, **interface**, **secret**, **seam**, **adapter**, **leverage**.

## Before you start: is this worth it?

Designing it twice costs several agents and a round of the user's attention. Spend that where it pays.

- **Does the cluster have a secret?** If you can't name the decision that's likely to change, no interface will be better than another — you're arranging code, not designing. Go back to [SKILL.md](../SKILL.md#1-list-the-secrets-before-drawing-any-line).
- **Is this core or generic?** Evans: "Apply top talent to the CORE DOMAIN […] Justify investment in any other part by how it supports the distilled CORE." For a generic subdomain, pick the boring interface and move on.
- **Is doing nothing on the table?** If the honest recommendation is "leave it," say so instead of generating three ways to restructure it.

## Process

### 1. Frame the problem space

Before spawning sub-agents, write a user-facing explanation of the problem space for the chosen candidate:

- The **secret** the deepened module would hide, and the evidence it's volatile — ideally past changes that touched several files together
- The constraints any new interface would need to satisfy
- The dependencies it would rely on, and which category they fall into (see [DEEPENING.md](DEEPENING.md))
- A rough illustrative code sketch to ground the constraints — not a proposal, just a way to make the constraints concrete

Show this to the user, then immediately proceed to Step 2. The user reads and thinks while the sub-agents work in parallel.

### 2. Spawn sub-agents

Spawn 3+ sub-agents in parallel using the Agent tool. Each must produce a **radically different** interface for the deepened module.

Prompt each sub-agent with a separate technical brief (file paths, coupling details, dependency category from [DEEPENING.md](DEEPENING.md), what sits behind the seam). The brief is independent of the user-facing problem-space explanation in Step 1. Give each agent a different design constraint:

- Agent 1: "Minimise the interface — aim for 1–3 entry points max. Maximise leverage per entry point."
- Agent 2: "Design for closure — operations that return their own argument types, so callers compose what you didn't anticipate (see COMPOSITION.md)."
- Agent 3: "Optimise for the most common caller — make the default case trivial."
- Agent 4: "Design for additivity — adding the next variant must touch exactly one file."
- Agent 5 (if applicable): "Design around ports & adapters for cross-seam dependencies."

Agent 2 replaces the older "maximise flexibility" brief, which reliably produced a large configurable interface — a shallow module with options, not a flexible one.

Include both [SKILL.md](../SKILL.md) vocabulary and CONTEXT.md vocabulary in the brief so each sub-agent names things consistently with the architecture language and the project's domain language.

Each sub-agent outputs:

1. Interface (types, methods, params — plus invariants, ordering, error modes)
2. Usage example showing how callers use it, written from a real call site
3. What the implementation hides behind the seam — named as a **secret**
4. What the interface promises that it *could* have withheld, and why that promise is safe to make
5. Dependency strategy and adapters (see [DEEPENING.md](DEEPENING.md))
6. Trade-offs — where leverage is high, where it's thin, and what this design makes hard

### 3. Present and compare

Present designs sequentially so the user can absorb each one, then compare them in prose.

Score each against the same rubric, and say where each one loses:

| Criterion | Question | Source |
|---|---|---|
| **Secret** | Does it hide a decision that's genuinely likely to change? | Parnas |
| **Restraint** | What does it promise that no caller needed? | Parnas' circular-shift retraction |
| **Contour** | Does the seam echo the domain, or this week's code? | Evans |
| **Closure** | Can outputs be fed back into the operations? | SICP / Evans |
| **Additivity** | To add the next variant, how many files change? | SICP §2.4.3 |
| **Depth** | Behaviour exercised per unit of interface learned | Ousterhout |
| **Locality** | Where does change concentrate? | — |
| **Structure** | Does it keep the `uses` graph acyclic? Prunable? | Parnas §Hierarchy |
| **Price** | Indirection, migration, and cost if the prediction is wrong | Parnas §Efficiency |

Restraint and additivity are the two the sub-agents most often lose on, and they're the two a reader is least likely to notice unaided — call them out explicitly.

After comparing, give your own recommendation: which design you think is strongest and why. If elements from different designs would combine well, propose a hybrid. Name the option you rejected and what it would have cost. Be opinionated — the user wants a strong read, not a menu.

If none of them beats the status quo once priced, say that. A round of design that concludes "keep what's there, revisit when the second caller appears" is a successful round.
