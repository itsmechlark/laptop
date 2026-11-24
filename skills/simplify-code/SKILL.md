---
name: simplify-code
description: Simplify code you just wrote, changed, or point at — reuse existing helpers, flatten nesting, cut redundant abstractions and wasted work, and bring it in line with this repo's documented conventions — without changing what it does, proven by the tests passing before and after. Use when asked to "simplify this", "clean this up", "tidy what I just wrote", "refactor for readability", "make this easier to read", to check your own diff for duplication and wasted work and fix what turns up, or to apply the readability findings from a review of your own change. Edits the code; not for a merge verdict, a bug hunt, answering a reviewer's comments, or deciding where a module boundary belongs.
argument-hint: "[file, function, or fixed point (branch/tag/SHA) to simplify since — omit for uncommitted work]"
---

# Simplify code

Make code easier to read and cheaper to run and change, while it keeps doing exactly what it did. Survey it through five lenses, then apply what holds up in small steps. Every edit is a refactor in the strict sense: behavior in, same behavior out, and a test run that says so.

Target: `$1` — empty means uncommitted work.

Code is easiest to simplify from outside the context that wrote it. When you just wrote the target yourself, dispatch the `simplifier` subagent where the client has it, and wait for it before touching the tree again; otherwise follow this skill in place.

## When to use this skill

- After a change is green, as the refactor step — "clean up what I just wrote", "tidy this before I commit"
- A file or function the user names and finds hard to read — "simplify this", "this is too clever, make it readable" — whether or not it changed recently
- A quality pass over your own diff that fixes what it finds: duplicated helpers, wasted work, special-case patches, convention breaks
- Applying the readability, duplication, and convention findings from a review of your own change, such as `code-review`'s
- Not for a merge verdict or findings left for someone else to act on — that's `code-review`, which reports and never edits
- Not for working through comments a reviewer left on your PR — that's `review-response`, which checks each one before implementing it and drafts the replies
- Not for hunting defects — that's `find-bugs`. A bug found while simplifying is reported, never silently fixed (see Gotchas)
- Not for restructuring across modules — where a seam goes, whether to split or merge a class — that's `codebase-design`
- Not for widening past what was named or changed. Rewriting stable, intentional code nobody pointed at is churn (AGENTS.md §1)

## Gotchas

- **A refactor that changes behavior is a bug with a nice diff.** The edits that look most mechanical are the ones that change semantics: `||` to `??`, a truthiness check to a nil check, `map` to `each`, reordering short-circuit conditions, running sequential calls concurrently, dropping a "redundant" guard that some caller relied on. Read [BEHAVIOR-TRAPS.md](references/BEHAVIOR-TRAPS.md) before an edit of that shape.
- **No passing test, no safe refactor.** If committed code you're about to touch has no test exercising it, write a characterization test first that pins down what it does today, odd parts included. If you can't, say so and confine yourself to edits a reader can verify by eye (renames, local extractions).
- **Inside an uncommitted change, the cleanup belongs to that change.** When the code being simplified is the work in progress itself (TDD's refactor step, `feature-dev`'s review fixes), a branch no test demands is deleted rather than characterized, and the cleanup lands in the same commit as the work. Characterization tests and a separate commit are for code that was already committed.
- **A bug found while simplifying stays a bug until someone decides.** Fixing it inside a "simplify" diff smuggles a behavior change into a refactor, where the reviewer isn't looking for one. Stop, report it with the line and the input that triggers it, and let the user choose: fix it separately, or leave it.
- **Public surface is behavior.** A method name, parameter order, return shape, error class, log line, or serialized key that anything outside the file depends on is a contract. Renaming one is not a simplification. Grep for callers before touching it, and leave it alone if any exist outside the target.
- **Bring no house style.** The repo's documented standards win, then its neighboring code. Where both are silent, leave the existing choice alone rather than swapping in one you prefer.
- **Fewer lines is not the goal.** Fusing unrelated concerns, a nested ternary, a five-step chain on one line, or an inlined helper that had a good name all shrink a diff and cost the reader. Stop when the next cut would make the code slower to understand, even if it would make it shorter.
- **An altitude fix is usually a behavior change.** Replacing a special case with a change to the shared mechanism alters every other caller of that mechanism. Apply it only when tests cover those callers and stay green; otherwise report it, with the general change named.
- **Formatting is the formatter's job.** Don't hand-reflow, reorder imports, or restyle quotes the project's formatter owns. Run it; don't imitate it. Whitespace churn buries the edits that matter.

## Workflow

### 1. Pin the target

Resolve what's in scope before reading code, and say what you resolved:

- **A file or function in `$1`** — that is the whole scope, changed or not. The user asked for it.
- **A fixed point in `$1`** — everything since the merge-base, committed or not: `git diff "$(git merge-base <ref> HEAD)" --name-status` plus `git ls-files --others --exclude-standard`. A `<ref>...HEAD` range reads commits only and misses the work on top of them.
- **Nothing** — uncommitted work: `git diff HEAD --name-status` *plus* `git status --porcelain`, because a new file never `git add`ed shows up in no diff.

For the last two, simplify the changed hunks and what they directly touch, not the rest of each file. An empty set is a stop: ask what to simplify rather than widening to the whole file or the repo.

### 2. Learn the standards that apply

Read whatever exists: the user-level and repo-root `AGENTS.md`/`CLAUDE.md`, any in a directory above a file in scope (it governs only files below it), path-scoped rules for the file types in scope, the linter and formatter config, and two or three neighboring files in the same directory. The neighbors settle what the documents leave open: error-handling style, naming, how much a function does before it gets split.

### 3. Establish the baseline

Find and run the tests that exercise the target. Record the command and the result. **If they fail before you've touched anything, stop.** A refactor can't be checked against a red baseline. Report the failure and let the user decide.

Where committed code lacks coverage, add a characterization test now, as its own step, and check it passes against the unchanged code.

### 4. Survey through five lenses

Read every hunk in scope and the function around it, and list candidates before editing anything. Each names the file and line, the simpler form, and what leaving it costs.

- **Reuse** — the target hand-rolls something the codebase already provides. Search the shared and utility modules and the target's neighbors for it; a candidate names the existing function to call.
- **Simplification** — state that duplicates or could be computed from other state, near-identical blocks that differ in a value or two, nesting that guard clauses would flatten, nested ternaries, dead code and unused parameters, a wrapper with one caller and no added meaning, an option nothing sets, comments that restate the code.
- **Efficiency** — the same value computed or fetched more than once, a query inside a loop, independent calls made one after another, slow work added to boot or to a path that runs on every request, a long-lived closure that pins a large scope in memory.
- **Altitude** — a symptom patched with a special case where the shared mechanism underneath is what's wrong. A candidate names the change to that mechanism that would make the special case unnecessary.
- **Conventions** — a break of a rule found in step 2. It counts only when you can quote both the rule and the offending line; a preference you can't source is not a finding.

Skip any lens with nothing real to report rather than padding it. If a lens turns up a correctness bug, it goes in the report, not in the edit list.

### 5. Apply in small steps

Work the list smallest and safest first: deletions and renames, then flattening, inlining, and extraction, then reuse, then efficiency, and altitude last. Extract a repeated block once it has three real copies, not two.

Run the baseline tests after each logical step, not once at the end. A failure then points at one edit instead of twenty. A candidate you can't apply safely becomes a finding in the report.

### 6. Verify and report

Re-run the baseline tests, then the project's linter, formatter, and type-checker on the touched files. Then report:

- What you changed, grouped by lens, not file by file
- What you found and deliberately left alone, and the reason: public surface, missing coverage, an altitude change with untested callers, a cut that would cost clarity
- Any bug you found and did not fix
- The commands you ran and their results

When the target was already committed, keep the simplification a separate commit from any behavior change around it, so a revert of one never takes the other (AGENTS.md §7). Committing is the user's call.

## Examples

Collapse a nested ternary into a guard-clause chain:

```javascript
// before
const status = isLoading ? 'loading' : hasError ? 'error' : isComplete ? 'complete' : 'idle';

// after
function statusOf({ isLoading, hasError, isComplete }) {
  if (isLoading) return 'loading';
  if (hasError) return 'error';
  if (isComplete) return 'complete';
  return 'idle';
}

const status = statusOf({ isLoading, hasError, isComplete });
```

Inline a wrapper whose name says less than its body:

```ruby
# before
def has_items?(items) = items.any?
return unless has_items?(reservations)

# after
return if reservations.empty?
```

Safe only if `reservations` never holds `nil` or `false`: `[nil].any?` and `[nil].empty?` are both false, so the two guards disagree on it. On an ActiveRecord relation `any?` is defined as `!empty?`, so there the inversion is exact — see [BEHAVIOR-TRAPS.md](references/BEHAVIOR-TRAPS.md#ruby-and-rails).

Leave a readable chain alone. Splitting `orders.filter(paid).map(total).reduce(sum, 0)` into three named intermediates makes it longer, not clearer, when each step already has a good name. Break a chain up when a step's intent isn't obvious from its callback, not because it is a chain.

## References

Read as needed, not upfront.

- [BEHAVIOR-TRAPS.md](references/BEHAVIOR-TRAPS.md) — rewrites that look equivalent and aren't: language-agnostic, efficiency, JavaScript/TypeScript, Ruby/Rails, and Elixir

## Attribution

- [getsentry/skills](https://github.com/getsentry/skills/tree/main/skills/code-simplifier) - code-simplifier, Apache-2.0
- [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md) - code-simplifier, Apache-2.0
- Claude Code built-in `/simplify` skill
