# Keeping the diff lean

Slicing controls *what* ships. It does nothing to stop the implementation of a perfectly-sized slice bloating with speculative abstractions, options nothing uses yet, and defensive branches no test demanded. This is the separate constraint.

## The budget

**Under ~300 lines of production code** — excluding tests, comments, and blank lines.

Carry it from Phase 3 onward as a design constraint, not as a gate discovered at the end. A 900-line diff noticed at the Phase 4 checkpoint means the last two hours went into code you are about to delete; the same number predicted at Phase 3 costs one re-slicing conversation.

It is advisory. A justified large diff may proceed. What is not allowed is drifting past it without noticing.

## While you build

Take TDD's "minimal code to pass" literally:

- **Don't introduce an abstraction until a second caller needs it.** A shared object, a base class, a config option, an interface with one implementation — one caller is not a pattern.
- **Don't add error handling, branches, or parameters no failing test demands.** If you can't name the test that would catch its absence, it isn't behavior, it's decoration.
- **Reuse what Phase 2 surfaced** instead of building parallel machinery beside it. A second helper doing what an existing one already does is worse than the awkward call into the first.
- **Three similar lines beat a premature abstraction** (AGENTS.md §1). Duplication is cheap to remove later; the wrong abstraction is not.

## Measuring before review

When every acceptance criterion is green, measure the production diff against the base the slice was cut from:

```sh
git diff --stat "$(git merge-base HEAD <base>)"...HEAD -- ':(exclude)<test-dirs>'
```

Substitute the branch the slice came off for `<base>`, and this project's test directories for `<test-dirs>` — `spec/`, `test/`, `__tests__/`, whatever Phase 2 found. The count includes comments and blank lines, so discount those by eye rather than chasing an exact number.

## When it runs over

Make an explicit call among three, and tell the user which applies:

- **Accidental complexity** — over-abstraction, dead flexibility, code no criterion demanded. Simplify now; this is the common case, and the fix is deletion.
- **Essential complexity** — the slice genuinely spans enough layers that the code cannot be smaller without losing behavior. Legitimate, but say *why* in a sentence or two, so the justification survives into the commit message. It still commits as one slice here; whether the *review* is worth splitting into layers is a PR-time question, and `pull-request`'s SPLITTING.md answers it.
- **The slice was too big** — if the size traces to scope rather than to style, the honest fix is upstream: return to the Phase 1/3 decision, ship the smaller piece, defer the rest. Re-slicing after the tests exist costs more than re-slicing before, and still costs less than reviewing a diff nobody can hold in their head.

The third is the one that gets rationalized into the second. If the criteria themselves each dragged in new machinery, that is scope, not essential complexity.

## After review

`code-review` hunts for simplification and reuse on its Standards axis, so treat its findings as a second pass on leanness. A duplication or dead-flexibility finding there is the budget check catching what the line count missed — an over-abstracted 200-line diff is still over-abstracted.
