---
name: codebase-design
description: Shared vocabulary and method for designing deep modules — find the secrets worth hiding, place the seam on a domain contour, and price the change before making it. Use when the user wants to design or improve a module's interface, find deepening opportunities, decide where a seam goes, make code more testable or AI-navigable, or when another skill needs the deep-module vocabulary.
---

# Codebase Design

Design **deep modules**: a lot of behaviour behind a small interface, placed at a clean seam, testable through that interface. Use this language and these principles wherever code is being designed or restructured. The aim is leverage for callers, locality for maintainers, and testability for everyone.

Depth is the *shape* of a good module. It is not how you find one — that's **volatility**, and it comes first. A module can be perfectly deep and still hide the wrong thing.

## Glossary

Use these terms exactly — don't substitute "component," "service," "API," or "boundary." Consistent language is the whole point.

**Module** — anything with an interface and an implementation. Deliberately scale-agnostic: a function, class, package, or tier-spanning slice. _Avoid_: unit, component, service.

**Interface** — everything a caller must know to use the module correctly *and* everything they may come to rely on: the type signature, but also invariants, ordering constraints, error modes, required configuration, and performance characteristics. Both halves matter — see **Over-promise** below. _Avoid_: API, signature (too narrow — they refer only to the type-level surface).

**Implementation** — what's inside a module, its body of code. Distinct from **Adapter**: a thing can be a small adapter with a large implementation (a Postgres repo) or a large adapter with a small implementation (an in-memory fake). Reach for "adapter" when the seam is the topic; "implementation" otherwise.

**Secret** _(Parnas)_ — the design decision a module hides: the fact that would otherwise have to change in several places at once. A module is named by its secret, not by its step in the processing. _Avoid_: responsibility, concern (too vague to falsify — every module has a "responsibility"; only some have a secret).

**Volatility** — how likely a decision is to change, multiplied by how expensive that change would be. Volatility, not size, decides what belongs behind an interface.

**Depth** — leverage at the interface: the amount of behaviour a caller (or test) can exercise per unit of interface they have to learn. A module is **deep** when a large amount of behaviour sits behind a small interface, **shallow** when the interface is nearly as complex as the implementation.

**Over-promise** — a fact the interface guarantees that no caller needed. Every guarantee is a constraint on all future implementations, so an over-promise costs you options without buying anything. See [Anti-patterns](#anti-patterns).

**Closure** _(SICP; Evans)_ — an operation whose result can be fed back into the same operation. Closure multiplies leverage where depth only adds it — see [COMPOSITION.md](references/COMPOSITION.md).

**Seam** _(Michael Feathers)_ — a place where you can alter behaviour without editing in that place; the *location* at which a module's interface lives. Where to put the seam is its own design decision, distinct from what goes behind it. _Avoid_: boundary (overloaded with DDD's bounded context).

**Adapter** — a concrete thing that satisfies an interface at a seam. Describes *role* (what slot it fills), not substance (what's inside).

**Leverage** — what callers get from depth: more capability per unit of interface they learn. One implementation pays back across N call sites and M tests.

**Locality** — what maintainers get from depth: change, bugs, knowledge, and verification concentrate in one place rather than spreading across callers. Fix once, fixed everywhere.

## Deep vs shallow

**Deep module** = small interface + lots of implementation:

```
┌─────────────────────┐
│   Small Interface   │  ← Few methods, simple params
├─────────────────────┤
│                     │
│  Deep Implementation│  ← Complex logic hidden
│                     │
└─────────────────────┘
```

**Shallow module** = large interface + little implementation (avoid):

```
┌─────────────────────────────────┐
│       Large Interface           │  ← Many methods, complex params
├─────────────────────────────────┤
│  Thin Implementation            │  ← Just passes through
└─────────────────────────────────┘
```

## The design loop

Run these in order. Steps 1–2 are the ones most often skipped, and skipping them is how you get a tidy decomposition of the wrong thing.

### 1. List the secrets before drawing any line

> We propose instead that one begins with a list of difficult design decisions or design decisions which are likely to change. Each module is then designed to hide such a decision from the others. — Parnas

Write the list first. What is actually likely to change here — a storage format, a wire protocol, an ordering, a pricing rule, a third party's semantics, the sequence in which things get processed? That list *is* the module list. Parnas' own examples of things that earn a module: a data structure together with its accessors ("They are not shared by many modules as is conventionally done"), control-block formats, "character codes, alphabetic orderings, and similar data," and "the sequence in which certain items will be processed."

If you can't name the secret, you haven't found a module — you've found a place to put some code.

### 2. Group by secret, not by step

> it is almost always incorrect to begin the decomposition of a system into modules on the basis of a flowchart […] Since, in most cases, design decisions transcend time of execution, modules will not correspond to steps in the processing. — Parnas

Read your module names in order. If they narrate a runtime sequence, you decomposed a flowchart. See [Anti-patterns](#anti-patterns).

### 3. Check the promise, not just the ask

For every fact the interface reveals, ask: *will I regret guaranteeing this?* The interface should "reveal as little as possible about its inner workings" (Parnas). Usual over-promises: ordering, concrete collection types, error timing, whether work happens eagerly or lazily.

### 4. Place the seam on a contour

Prefer lines that follow the domain over lines that follow the current code's accidents:

> With each decision, ask yourself, Is this an expedient based on a particular set of relationships in the current model and code, or does it echo some contour of the underlying domain? — Evans, *Conceptual Contours*

Invariants are the most reliable contour available — see [DEEPENING.md](references/DEEPENING.md#placing-the-seam).

### 5. Consider composition before depth

If the operations could return their own input type, a small composable interface beats a small bespoke one. Don't reach for a third entry point when closure would have covered the case. See [COMPOSITION.md](references/COMPOSITION.md).

### 6. Price it, then decide

Depth is not free. Parnas paid in call overhead — "If we are not careful the second decomposition will prove to be much less efficient than the first" — and we pay in indirection, cross-seam debugging, and migration cost. Name the price before recommending the change, and put **doing nothing** on the list of options. See [DEEPENING.md](references/DEEPENING.md#pricing-the-change).

## Anti-patterns

**The flowchart decomposition.** Modules named for processing steps: `RequestParser`, `OrderValidator`, `PriceCalculator`, `OrderPersister`. Each has one method and real logic behind it, so each passes the deletion test *individually* — but the same type flows through all four, so any change to it touches all four. Depth measured per-module cannot detect this; only the secrets list can. Tell: the module names, read in order, describe a sequence.

**The over-promised interface.** Parnas' own worked example, and the best one available. His circular shifter carefully hid *how* shifts were stored, then specified the *order* of the resulting list:

> By prescribing the order for the shifts we have given more information than necessary and so unnecessarily restricted the class of systems that we can build without changing the definitions […] must clearly be classified as a design error.

Hiding the hard part is not enough if you leak an incidental guarantee alongside it. (Modern restatement: Hyrum's Law — with enough callers, every observable behaviour becomes a dependency, whether you promised it or not.)

**Depth by facade.** One entry point in front of N shallow modules, where callers still have to understand all N to use it correctly. The interface got smaller; the thing you must learn didn't. Test: can a caller succeed knowing only the facade?

**The single-adapter port.** Indirection introduced for a variation that never came. See the seam rule below.

**The speculative secret.** A module built around a decision nobody expects to change. Volatility is a prediction, and predictions cost something when wrong — one caller is not a pattern.

## Principles

- **Depth is a property of the interface, not the implementation.** A deep module can be internally composed of small, mockable, swappable parts — they just aren't part of the interface. A module can have **internal seams** (private to its implementation, used by its own tests) as well as the **external seam** at its interface.
- **The deletion test.** Imagine deleting the module. If complexity vanishes, it was a pass-through. If complexity reappears across N callers, it was earning its keep.
- **The interface is the test surface.** Callers and tests cross the same seam. If you want to test *past* the interface, the module is probably the wrong shape.
- **A seam needs a reason.** Something **varies**, something must be **substituted** for tests, or something **foreign** must be translated. Absent all three, it's indirection. (This supersedes the older "two adapters" rule, which was right about variation but wrongly forbade a single-adapter anticorruption layer — see [DEEPENING.md](references/DEEPENING.md#when-one-adapter-is-enough).)
- **Depth is local; structure is global.** A codebase of individually deep modules can still be unmaintainable if the `uses` relation has cycles. Parnas: hierarchical structure and clean decomposition are "two desirable but independent properties." See [STRUCTURE.md](references/STRUCTURE.md).
- **Not everything deserves depth.** Evans: "Boil the model down […] Make the CORE small […] Justify investment in any other part by how it supports the distilled CORE." Spend design effort where the system differentiates; take the boring option elsewhere.

## Stance

How to behave when applying this skill — the difference between naming good design and practising it.

- **Diagnose before prescribing.** Name the failure the current design *causes*, with evidence from the code — a change that touched six files, a test that can't be written, a bug that recurred. A recommendation with no diagnosis is a preference. (Rumelt's kernel: diagnosis → guiding policy → coherent action.)
- **The null option is always on the table.** "Leave it alone" is a real recommendation. Say it out loud when the change doesn't pay, rather than proposing the least-bad restructure.
- **Price every seam.** Indirection, debugging across it, migration cost, and the cost of being wrong. State the number or the shape of it.
- **Say what you rejected.** A design presented without its discarded alternatives can't be reviewed, only accepted.
- **Don't design past the evidence.** Two call sites are a pattern; one is a coincidence. Prefer a concrete duplicate today over a speculative abstraction that has to be unwound.
- **The theory isn't in the code.** Naur's point: the design rationale can't be recovered from the source by reading it. Reconstruct it (history, tests, ask) before rewriting — and when a decision holds still, hand off to `domain-modeling` to record it in `CONTEXT.md` or an ADR. Don't duplicate that machinery here.

## Designing for testability

Good interfaces make testing natural:

1. **Accept dependencies, don't create them.**

   ```typescript
   // Testable
   function processOrder(order, paymentGateway) {}

   // Hard to test
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Return results, don't produce side effects.**

   ```typescript
   // Testable
   function calculateDiscount(cart): Discount {}

   // Hard to test
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Small surface area.** Fewer methods = fewer tests needed. Fewer params = simpler test setup.

Once the interface is designed, use the `tdd` skill to drive the implementation — the interface becomes the test surface, and outside-in TDD ensures nothing ships without a failing test demanding it.

## Relationships

- A **Module** has exactly one **Interface** (the surface it presents to callers and tests).
- A **Module** hides exactly one **Secret**; the secret is chosen by **Volatility**.
- **Depth** is a property of a **Module**, measured against its **Interface**.
- A **Seam** is where a **Module**'s **Interface** lives.
- An **Adapter** sits at a **Seam** and satisfies the **Interface**.
- **Depth** produces **Leverage** for callers and **Locality** for maintainers.
- **Closure** produces leverage multiplicatively where **Depth** produces it additively.
- Modules are ordered by a **uses** relation, which must stay acyclic ([STRUCTURE.md](references/STRUCTURE.md)).

## Rejected framings

- **Depth as ratio of implementation-lines to interface-lines** (Ousterhout): rewards padding the implementation. We use depth-as-leverage instead.
- **Depth as method count.** A closed, composable interface of five orthogonal operations looks "shallower" than three bespoke entry points and is far more powerful. Count what a caller must *learn*, not what they may *call* ([COMPOSITION.md](references/COMPOSITION.md)).
- **"Interface" as the TypeScript `interface` keyword or a class's public methods**: too narrow — interface here includes every fact a caller must know, and every fact they may come to rely on.
- **"Boundary"**: overloaded with DDD's bounded context. Say **seam** or **interface**.
- **Decomposition by processing step**: the default, and almost always wrong (Parnas). Decompose by secret.

## Going deeper

- **What to hide, and where to cut** — this file, [The design loop](#the-design-loop).
- **Structure across modules** — see [STRUCTURE.md](references/STRUCTURE.md): the `uses` relation, layering, the prune test, and team seams.
- **Composable interfaces** — see [COMPOSITION.md](references/COMPOSITION.md): closure, additivity, and when composability beats depth.
- **Deepening a cluster given its dependencies** — see [DEEPENING.md](references/DEEPENING.md): dependency categories, seam placement, pricing, and replace-don't-layer testing.
- **Exploring alternative interfaces** — see [DESIGN-IT-TWICE.md](references/DESIGN-IT-TWICE.md): spin up parallel sub-agents to design the interface several radically different ways, then compare on depth, locality, and seam placement.

## Attribution

- [mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/codebase-design) - codebase-design, MIT
- David L. Parnas, *On the Criteria To Be Used in Decomposing Systems into Modules*
- Abelson & Sussman, *Structure and Interpretation of Computer Programs*
- Eric Evans, *Domain-Driven Design*
- Michael Feathers, *Working Effectively with Legacy Code*
- Alistair Cockburn, *Hexagonal Architecture*
- John Ousterhout, *A Philosophy of Software Design*
- Peter Naur, *Programming as Theory Building* (1985)
- Melvin Conway, *How Do Committees Invent?* (1968)
- Richard Rumelt, *Good Strategy Bad Strategy*
- Forsgren, Humble & Kim, *Accelerate*
