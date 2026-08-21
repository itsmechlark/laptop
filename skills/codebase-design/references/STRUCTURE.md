# Structure

Depth is a property of one module. This file is about the relationships *between* modules — the part a per-module criterion cannot see. Assumes the vocabulary in [SKILL.md](../SKILL.md) — **module**, **interface**, **secret**, **seam**.

A codebase of individually deep modules can still be unmaintainable. Parnas separates the two properties explicitly:

> we must conclude that hierarchical structure and "clean" decomposition are two desirable but independent properties of a system structure.

You need both. Deep modules give you locality; structure gives you the ability to reason about, reuse, and dismantle the system.

## The uses relation

The relation that matters is **uses** (Parnas: "uses" or "depends upon"), and it must be a **partial order** — no cycles.

Parnas makes a subtle point worth keeping: state the relation between *programs*, not modules, because "in many cases one module depends upon only part of another module." A module that depends on one function of another is not in the same position as one that depends on all of it. When you draw the graph, draw what is actually used.

**A cycle is a message.** Two modules that use each other almost always share one secret that got split across both. The fix is usually not an interface to break the cycle — it's to find the decision that was cut in half and put it back in one place. Reach for dependency inversion only when the shared thing is genuinely two secrets with an unfortunate call direction.

## The prune test

The most checkable structural test in the literature:

> The existence of the hierarchical structure assures us that we can "prune" off the upper levels of the tree and start a new tree on the old trunk. — Parnas

Concretely: **delete the top layer. Is what remains still useful to somebody?**

Parnas' own examples — "the symbol table can be used in other applications; the line holder could be the basis of a question answering system." If cutting the top leaves nothing coherent, your layering is decorative: the lower levels were written to serve exactly one caller and encode its assumptions.

Two benefits fall out of the partial order, and they're worth naming separately when you justify a design:

1. Upper levels are **simplified** because they use the services of lower ones.
2. Upper levels are **removable** — you can retire a product surface without dismantling the system underneath.

If your design delivers neither, the layers are costing you indirection and returning nothing.

## Abstraction barriers

SICP's framing of the same structure, from the caller's side:

> the underlying idea of data abstraction is to identify for each type of data object a basic set of operations in terms of which all manipulations of data objects of that type will be expressed, and then to use only those operations in manipulating the data. — SICP §2.1.2

The operative word is **only**. A barrier that most code respects and three call sites bypass is not a barrier — it's a convention, and the three call sites are where your next migration will stall. When you place a barrier, check for the bypasses; when you find them, either bring them through the interface or admit the barrier isn't there.

Each layer should have its own vocabulary. If the names in the upper layer are the names from the lower layer, you have one layer written twice.

## Team seams

Seams are also organisational. Parnas devotes a section to it, contrasting the two KWIC decompositions:

> The development of those formats will be a major part of the module development and that part must be a joint effort among the several development groups.

versus the information-hiding version, where "the interfaces are more abstract; they consist primarily in the function names and the numbers and types of the parameters […] the independent development of modules should begin much earlier."

The design question this raises is practical: **for each seam, who owns each side?** A seam whose two sides are owned by the same person is cheap to move and cheap to get wrong. A seam between teams is expensive to move and must be specified more carefully — it is a commitment, and changing it needs the deprecation path that AGENTS.md §7 (*Engineering leverage & judgment*) describes.

Conway's Law is the general statement: system structure tends to mirror the communication structure of the organisation that builds it. Use it in both directions — as a prediction of what you will get by default, and as a constraint on seams you're proposing to introduce. A seam that cuts against the team structure will erode.

*Accelerate* supplies the empirical backing: loose coupling and independent deployability are the strongest architectural predictors of delivery performance. This is the argument to reach for when someone asks why the structural work is worth doing.

## Comprehensibility

Parnas' test for whether the decomposition worked at all, on the flowchart version:

> The system will only be comprehensible as a whole. It is my subjective judgment that this is not true in the second modularization.

Ask it directly: **can a new maintainer understand this module without understanding its siblings?** If understanding `Output` requires knowing how `Alphabetizer` builds its tables, the seam between them is carrying design decisions it shouldn't. This is the human-scale version of the deletion test, and it's the one that matters most for a codebase an agent has to navigate — context is finite, and a system comprehensible only as a whole doesn't fit in it.

## Checklist

- [ ] The `uses` graph is acyclic. Cycles have been traced to a split secret, not patched with an interface.
- [ ] Cutting the top layer leaves something a different caller could use.
- [ ] Each layer has its own vocabulary, not the layer below's names.
- [ ] No call sites bypass a barrier you claim exists.
- [ ] Every cross-team seam is deliberate, specified, and has an owner on each side.
- [ ] Each module can be understood without understanding its siblings.
