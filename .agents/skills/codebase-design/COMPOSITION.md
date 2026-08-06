# Composition

Depth is not the only way to get leverage, and in some designs it's the weaker one. This file covers **closure** and **additivity** — two ways an interface can pay back more than the sum of its entry points. Assumes the vocabulary in [SKILL.md](SKILL.md).

## The correction

The depth heuristic says: fewer entry points, more behaviour behind each. Taken naively, it scores a composable interface of five orthogonal operations as *worse* than three bespoke ones, because it counts methods.

That's backwards. Five operations that compose give you the products of their combinations; three bespoke entry points give you three. **Count what a caller must learn, not what they may call.** Five operations sharing one type and one mental model is less to learn than three unrelated ones — and it covers cases you never anticipated.

## Closure

> an operation for combining data objects satisfies the closure property if the results of combining things with that operation can themselves be combined using the same operation […] Closure is the key to power in any means of combination. — SICP §2.2

Evans arrives at the same place from the domain side:

> Where it fits, define an operation whose return type is the same as the type of its argument(s) […] A closed operation provides a high-level interface without introducing any dependency on other concepts. — *Closure of Operations*

That last clause is the one to notice: closure buys expressive range **without adding vocabulary**. A closed operation doesn't drag a new type into the caller's head. This is why a query builder, a parser combinator, a middleware chain, or an aggregation pipeline can express enormous variety through a handful of names.

**The test:** can the output of an operation be fed back into that operation? If `filter(x) → x`, callers can chain, nest, and factor out fragments without your help. If `filter(x) → FilterResult`, they can do exactly what you anticipated and nothing more.

**Where it applies:** collections, queries, specifications, validation rules, transformations, permissions, money and quantities, time ranges. Anywhere a caller might reasonably want to say "and also."

**Where it doesn't:** operations that cross a seam with side effects (`charge`, `send`, `deploy`), or that change the kind of thing under discussion. Forcing closure on those produces a type that lies about what it is.

## Additivity

The other multiplier, and the one that decides whether adding a case means editing existing code:

> data-directed programming […] allows individual data representations to be designed in isolation and then combined additively (i.e., without modification) — SICP §2.4.3

> by combining pre-existing modules that were designed in isolation, we need conventions that permit programmers to incorporate modules into larger systems additively, that is, without having to redesign or reimplement these modules. — SICP §2.4

This is open/closed with a mechanism attached. The test is mechanical: **to add the next variant, how many existing files must change?** If the answer is "one — the new one," the design is additive. If it's "the new one plus a switch statement plus an enum plus a factory," it isn't, and each of those is a place a future contributor will forget.

Additivity and depth pull in the same direction — both concentrate change — but additivity is checkable in a way depth isn't. Prefer it as evidence.

## Choosing between them

Both are leverage. They answer different questions.

| | **Depth** | **Closure** |
|---|---|---|
| Gives you | Behaviour per entry point | Combinations across entry points |
| Best when | The set of use cases is known and bounded | Callers will want things you can't enumerate |
| Fails by | Growing a new entry point per use case | Letting callers build things you can't support |
| Caller needs | To find the right method | To understand one type well |

**When both are available, prefer closure** — it survives requirements you didn't foresee, which is the case depth handles worst. A deep module meets an unanticipated use case by growing a fourth entry point; a closed one meets it by composition the caller writes themselves.

**Prefer depth when you need to constrain.** Closure hands callers a combinatorial space, and you own every point in it — including the combinations you never tested, the ones with pathological performance, and the ones that violate an invariant you assumed. If the operations touch money, permissions, or anything with a consistency requirement, a bounded interface you can reason about exhaustively is the safer instrument. Closure exposes range; depth exposes only what you chose.

The honest failure mode of this file: closure is seductive, and a combinator library built for three call sites is over-engineering with better literature behind it. The evidence rule from [SKILL.md](SKILL.md) still applies — two call sites are a pattern, one is a coincidence.

## Wishful thinking

The procedure for actually arriving at either:

> We are using here a powerful strategy of synthesis: wishful thinking. — SICP §2.1.1

Write the caller first, as though the interface you want already exists. Then implement it. This is the fastest way to discover that the interface you were about to build has a parameter no caller can supply, an ordering no caller cares about, or three entry points where one composable operation would do.

Do it in the actual call sites, not in the abstract — the second and third call site are where the wrong interface reveals itself.

## Checklist

- [ ] Where a return type could match its argument type, it does.
- [ ] Callers can chain and nest operations without a helper from you.
- [ ] Adding the next variant touches one file.
- [ ] The interface was written from a real call site before it was implemented.
- [ ] Where closure was rejected, it was for constraint or side effects — not habit.
