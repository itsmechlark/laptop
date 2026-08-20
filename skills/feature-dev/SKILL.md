---
name: feature-dev
description: Take one new feature slice from idea to reviewed, committed code in a single guided pass — scope it into the smallest shippable slice, build it test-first with strict TDD, review and fix the diff, then commit it. Chains slice → tdd → code review → git-commit. Agnostic to language, framework, and repo. Not for reviewing an existing PR, upgrades, or open-ended design questions.
argument-hint: "[feature or slice to build]"
disable-model-invocation: true
---

# Feature development

You are helping a developer take **one feature slice** from a rough idea to reviewed, committed code. This is not autonomous coding — it's a guided workflow that threads four disciplines: **slicing** to define the work, **TDD** to build it, **code review** to harden it, and a clean **commit** to land it.

The workflow's reason for existing is to resist the pull toward premature code. Each phase earns the next: you don't slice until you understand the feature, you don't build until the slice is sharp, you don't consider it done until the diff is reviewed, and you don't commit until it's green. Hold that line — the value is in the sequence.

**Scope discipline:** this refines and builds exactly **one slice**. If the work is an epic — several independently shippable pieces — surface that during framing and help the user pick the single slice to build now. Building more than one slice per pass defeats the point.

**Leanness discipline:** a small slice does not guarantee a small diff. Slicing controls *what* ships; it does nothing to stop the implementation bloating with speculative abstractions, options nothing uses yet, or defensive branches no test demands. Target a **production-code diff under ~300 lines** (excluding comments, blanks, and tests). Treat it as a design constraint you carry from Phase 3 on, not a gate you discover at the end.

Track the phases (e.g. with `TodoWrite`) so the user can see where they are.

## Phase 1: Frame the work

**Goal:** understand what the user wants, and confirm it's a single slice before investing.

Initial request: `$ARGUMENTS`

If it's unclear, ask what they're building — the problem it solves, who it's for, what "done" looks like. Keep it short; the `slice` skill interrogates scope properly in Phase 3, so here you only need enough to explore the codebase intelligently.

Then make an explicit call on size: **is this one slice, or an epic hiding several?** A slice is something a real user can touch and a stakeholder can see value in, shippable on its own.

- **One slice** → confirm your understanding in a sentence or two and move on.
- **An epic** → say so plainly, help name the pieces briefly, then ask which single slice to build now. If they want the full epic broken down first, that's the `slice` skill's large-feature path on its own — point them there and stop.

## Phase 2: Explore the codebase

**Goal:** ground the slice in how this codebase actually works, so the acceptance criteria are realistic and the implementation follows existing conventions instead of inventing new ones.

This matters most in a mature codebase: the right slice and tests depend on where similar features live, what the testing conventions are, and which abstractions already exist. Skipping it leads to slices that ignore reality and code that fights the grain.

Match the effort to the feature. For a small, well-understood change, a few targeted reads inline are enough. For anything touching unfamiliar territory or spanning layers, launch 2–3 general-purpose subagents in parallel (via the Task tool) as codebase explorers, each on a different angle:

- Find features similar to this one and trace their implementation end to end.
- Map the architecture and conventions for the area this slice touches (wherever it lands — data, domain logic, endpoints, UI, background work).
- Identify the testing patterns relevant to this work: the framework, how tests are structured across layers (end-to-end, integration, unit), and what factories/fixtures/helpers exist.

Ask each explorer for the 5–10 files most worth reading, then **read those files yourself** before proceeding — the subagents build the map, you need the detail in context. Close the phase with a short summary of the patterns that will shape the slice: where the code will live, what it should look like, what to reuse.

## Phase 3: Shape the slice

**Goal:** turn the framed feature into one sharp slice with real acceptance criteria.

**Run the `slice` skill's process** and let it lead the conversation. `slice` is user-invoke-only (`disable-model-invocation: true`), so read its `SKILL.md` and drive its process yourself. Since Phase 1 established this is a single slice, `slice` should sharpen it into one job story (its small-feature path). Feed it what you learned in Phases 1–2 so the conversation starts warm.

What you need out of this phase: a job story with a clear **"ships when"** and concrete **acceptance criteria** — happy path, edge cases, error states. Those aren't paperwork; they become the failing tests in Phase 4. Push until each criterion is specific and verifiable ("a user can X and sees Y") — a vague criterion produces a vague test that proves nothing.

Close with a rough **size budget:** given what Phase 2 revealed, does the slice look buildable in under ~300 lines of production code? If it clearly can't — it spans many layers, or every criterion drags in new machinery — that's usually a signal the slice is still too big, not that the budget is wrong. Interrogate it now, while re-slicing is cheap.

## Phase 4: Build it test-first

**Goal:** implement the slice with strict, outside-in TDD, driven by the acceptance criteria.

**Run the `tdd` skill's process** without shortcuts (it's also user-invoke-only — read its `SKILL.md` and drive the red-green-refactor loop yourself). Hand it the acceptance criteria as the specification: each criterion is a behavior that needs a failing test before any production code exists.

The skills fit together: `slice` produced the observable behaviors, and TDD drives them outside-in — start with a high-level test for the "ships when" behavior, let its failure push you down through the layers, write minimal code at each. The slice is done when every criterion is covered by a test you watched fail and then pass, and the suite is green with pristine output. Honor the Iron Law: no production code without a failing test first.

**Keep the implementation lean.** Take TDD's "minimal code to pass" literally:

- Don't introduce an abstraction (a shared object, a base class, a config option) until a *second* caller needs it. One caller is not a pattern.
- Don't add error handling, branches, or parameters no failing test demands.
- Reuse what Phase 2 surfaced instead of building parallel machinery.

**Size checkpoint before review.** When every criterion is green, measure the production diff against the budget — e.g.:

```
git diff --stat "$(git merge-base HEAD <base>)"...HEAD -- ':(exclude)<test-dirs>'
```

(Use whichever branch the slice was cut from as `<base>`, and exclude this project's test directories. It counts comments and blanks, so discount those by eye.) At or under budget → move to review. Over budget → make an explicit, written call among three options and tell the user which applies:

- **Accidental complexity** — over-abstraction, dead flexibility, code no criterion demanded. Simplify now. The common case.
- **Essential complexity** — the slice genuinely spans enough layers that the code can't be smaller without losing behavior. Legitimate, but say *why* in a sentence or two.
- **The slice was too big** — if the size traces to scope, the honest fix is upstream: return to the Phase 1/3 decision, ship the smaller piece, defer the rest.

This is advisory, not a hard gate — a justified large diff may proceed. What's not allowed is drifting past the budget without noticing.

## Phase 5: Review the diff

**Goal:** catch the bugs, quality issues, and convention violations TDD won't surface, then fix them.

TDD proves the slice does what the criteria demanded; it doesn't prove the code is simple, secure, or idiomatic. Run a code review over the **slice's diff** (the changes since the branch point) and apply the fixes — via your `/code-review` command (e.g. `/code-review high --fix`) or the `code-review` skill. Use a higher effort level for security-sensitive or subtle logic, a lower one for trivial changes. A good review also hunts for simplification and reuse, so treat it as a second pass on leanness after the Phase 4 checkpoint.

Because the fixes edit code outside the red-green-refactor loop, **re-run the full suite** with the project's test command once they finish, to confirm nothing regressed. If a fix changed behavior not yet covered by a test, add the missing test — failing first, per Phase 4 — so the correction can't silently regress. Then summarize what the review changed: what it fixed, anything it flagged but deliberately left, and confirmation the suite is green.

## Phase 6: Summary

**Goal:** close the loop. Mark the todos complete and give a short summary:

- **What shipped** — the slice in one line the user could paste into a PR description.
- **Acceptance criteria** — confirm each is met and tested.
- **Key decisions** — anything notable from slicing, testing, or review.
- **Files changed** — the diff at a glance, with the production-code line count against the ~300 budget (restate the justification if it ran over).
- **Next steps** — if this was one slice of a larger epic, name the slices still waiting.

## Phase 7: Commit the slice

**Goal:** land the finished, reviewed slice as a clean commit.

**Invoke the `git-commit` skill** (via the Skill tool). Everything in the working tree is *one coherent slice*, so `git-commit` should land it as a single atomic commit rather than splitting it — the logic, its schema change, the handler, the UI, and the tests all tell one story. The exception is anything genuinely independent that snuck in (an unrelated cleanup, a drive-by fix from the review); let `git-commit` make that call.

Feed it the slice's "ships when" line as context so the message explains *why* the slice exists, not just what changed. If Phase 5 flagged a risk or deliberate trade-off, mention it so it lands in the message too. `git-commit` stops at creating commits — it does not push or open a PR. Leave the branch ready for the user to push and open the PR themselves.

## Notes on the disciplines

Each piece is rigorous on its own; your job is to run them in sequence and keep the handoffs clean, not to water them down.

- `slice` is Socratic — it leads the user to define the work through questions. Let it; don't pre-answer.
- `tdd` is strict about order. Don't let the momentum of a clear slice tempt you into code before the test.
- The code review does the reviewing and fixing; your job after it runs is to confirm the suite is still green and that any behavior it changed is covered by a test.
- `git-commit` makes the atomic-commit call itself. Expect a single commit for one coherent slice — don't pre-split, but hand it the "ships when" context.

`slice` and `tdd` are user-invoke-only, so the Skill tool refuses them — **read and follow their `SKILL.md` directly**. `git-commit` has no such restriction; invoke it through the Skill tool. Whatever the reason a phase's skill can't be invoked, follow its `SKILL.md` rather than skipping the phase. The sequence is the point.
