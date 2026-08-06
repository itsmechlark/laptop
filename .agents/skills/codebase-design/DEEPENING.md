# Deepening

How to deepen a cluster of shallow modules safely, given its dependencies. Assumes the vocabulary in [SKILL.md](SKILL.md) — **module**, **interface**, **secret**, **seam**, **adapter**.

Before any of this: confirm the cluster has a **secret** worth hiding ([SKILL.md](SKILL.md#1-list-the-secrets-before-drawing-any-line)). Merging shallow modules that share no design decision produces a bigger shallow module, not a deep one.

## Dependency categories

When assessing a candidate for deepening, classify its dependencies. The category determines how the deepened module is tested across its seam.

### 1. In-process

Pure computation, in-memory state, no I/O. Always deepenable — merge the modules and test through the new interface directly. No adapter needed.

### 2. Local-substitutable

Dependencies that have local test stand-ins (PGLite for Postgres, in-memory filesystem). Deepenable if the stand-in exists. The deepened module is tested with the stand-in running in the test suite. The seam is internal; no port at the module's external interface.

### 3. Remote but owned (Ports & Adapters)

Your own services across a network boundary (microservices, internal APIs). Define a **port** (interface) at the seam. The deep module owns the logic; the transport is injected as an **adapter**. Tests use an in-memory adapter. Production uses an HTTP/gRPC/queue adapter.

Recommendation shape: *"Define a port at the seam, implement an HTTP adapter for production and an in-memory adapter for testing, so the logic sits in one deep module even though it's deployed across a network."*

### 4. True external (Mock)

Third-party services (Stripe, Twilio, etc.) you don't control. The deepened module takes the external dependency as an injected port; tests provide a mock adapter.

## Placing the seam

Dependency category tells you *how* to cross a seam. It doesn't tell you *where* to put one. Three criteria, in order of reliability:

**1. Invariants.** The most concrete rule available, from Evans' AGGREGATE:

> Cluster the ENTITIES and VALUE OBJECTS into "AGGREGATES" and define boundaries around each. Choose one ENTITY to be the "root" of each AGGREGATE, and control all access to the objects inside the boundary through the root.

The payoff is information hiding applied to consistency: "Because the root controls access it cannot be blind-sided by changes to the internals. This makes it practical to enforce all invariants." If a rule must hold across several objects, the seam goes around all of them — and everything inside is reached through one root. A seam that cuts through an invariant guarantees the invariant will eventually be violated, because two callers will each hold half of it.

This is also the answer to the concurrency requirements in AGENTS.md §6: the aggregate root is where the lock or the constraint goes.

**2. Domain contours.** Where no invariant decides it, follow the domain rather than the current code:

> Is this an expedient based on a particular set of relationships in the current model and code, or does it echo some contour of the underlying domain? — Evans, *Conceptual Contours*

**3. Observed change.** The empirical check, and the one that settles arguments:

> When successive refactoring tend to be localized, not shaking multiple broad concepts of the model, it is an indicator of model fit. Encountering a requirement that forces extensive changes in the breakdown of the objects and methods is a message. — Evans

Read the git history for the cluster. If past changes repeatedly touched the same set of files together, that set is a module and the seams inside it are in the wrong place. This turns seam placement from taste into evidence — use it.

## Seam discipline

- **A seam needs a reason: variation, substitution, or translation.** Don't introduce a port unless one applies. Absent all three, it's indirection.
- **Internal seams vs external seams.** A deep module can have internal seams (private to its implementation, used by its own tests) as well as the external seam at its interface. Don't expose internal seams through the interface just because tests use them.

### When one adapter is enough

The older form of this rule — *"one adapter means a hypothetical seam, two adapters means a real one"* — was right about variation and wrong as a general law. It forbids the **anticorruption layer**, where a single adapter is justified not because something varies but because something foreign must be kept out of your model.

Use one adapter deliberately when:

- **Translation.** A third party's or legacy system's model would otherwise leak into yours. The adapter exists to stop that, and it earns its keep on day one with no second implementation in sight. (Evans, *Anticorruption Layer*.)
- **Published contract.** The seam is a commitment to consumers you don't control — a public API, a provider-facing payload. The indirection buys you the freedom to change behind it (AGENTS.md §7).

Everywhere else, hold the line: a port with one production adapter and no test adapter is indirection wearing a pattern's name.

## Pricing the change

Deepening is not free, and a recommendation that omits the price isn't a recommendation. Parnas priced his own:

> If we are not careful the second decomposition will prove to be much less efficient than the first. If each of the functions is actually implemented as a procedure with an elaborate calling sequence there will be a great deal of such calling due to the repeated switching between modules.

His cost was call overhead. Ours are usually these — name whichever apply:

- **Indirection.** Every seam is a hop a reader must follow. A stack trace that crosses four seams is worse than one that crosses none.
- **Debugging across the seam.** Behaviour hidden from callers is also hidden from whoever is holding the pager.
- **Migration.** The cost of moving N call sites, and of the window where both shapes exist. Under AGENTS.md §5, that window is expand/contract and may be long.
- **Being wrong.** The cost of unwinding this if the predicted change never arrives. A wrong abstraction is more expensive than the duplication it replaced.

Then state the alternative you're not taking, including **doing nothing**. If the volatility you're designing against is speculative and the migration is large, "leave it, revisit when the second caller appears" is the correct answer and should be said plainly.

Weigh it against where the module sits: Evans' advice is to "apply top talent to the CORE DOMAIN" and "justify investment in any other part by how it supports the distilled CORE." A generic subdomain does not deserve the same design budget as the thing the business competes on.

## Testing strategy: replace, don't layer

- Old unit tests on shallow modules become waste once tests at the deepened module's interface exist — delete them.
- Write new tests at the deepened module's interface. The **interface is the test surface**.
- Tests assert on observable outcomes through the interface, not internal state.
- Tests should survive internal refactors — they describe behaviour, not implementation. If a test has to change when the implementation changes, it's testing past the interface.
- **Don't assert on what you didn't promise.** A test that pins an incidental ordering converts an implementation detail into a contract — the exact failure Parnas classified as "a design error" in his own circular shifter ([SKILL.md](SKILL.md#anti-patterns)). If callers don't need the guarantee, the test shouldn't demand it.

## Sources

Primary sources for the quotations above are listed in [SKILL.md](SKILL.md#sources) — principally Parnas (1972) on information hiding and the cost of indirection, and Evans (2003) on AGGREGATE, Conceptual Contours, Anticorruption Layer, and Core Domain.
