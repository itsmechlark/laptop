# Spec document reviewer

A self-review checklist to run after writing a spec document during the
architectural path. Fix issues inline — no separate review cycle needed.

## When to run

After writing the spec (via `draft-spec` or directly) and before asking the user
to review it. The goal is to catch problems the user shouldn't have to.

## Review checklist

### 1. Placeholder scan

Look for unfinished content:

- Any "TBD", "TODO", "FIXME", or "to be determined"
- Empty or stub sections (a heading with no content beneath it)
- Vague requirements ("appropriate", "as needed", "etc.", "various")
- Ellipses standing in for real content ("the system will handle auth, logging,
  ...")

**Fix:** fill in the content from the brainstorming conversation, or remove the
section if it's genuinely not needed. If the answer is unknown, say so
explicitly — "unresolved: we need to decide X before implementing Y" — rather
than leaving a placeholder that looks like an oversight.

### 2. Internal consistency

Check that the parts agree with each other:

- Does the architecture match the feature descriptions? If the design says
  "single service" but a feature describes cross-service communication, one is
  wrong.
- Do data models match the API contracts? Fields mentioned in one should appear
  in the other.
- Are naming conventions consistent throughout? The same concept should use the
  same term everywhere.
- Do error-handling descriptions align with the happy-path flows?

**Fix:** resolve the contradiction toward whichever version was validated during
the brainstorming conversation. If you can't tell, flag it for the user.

### 3. Scope check

Verify the spec is implementable as one coherent unit:

- Can this be implemented in a single planning pass, or does it describe
  multiple independent subsystems?
- Are there features that could ship independently with no dependency on the
  rest?
- Is the spec describing a platform where a single vertical slice would be more
  appropriate?

**Fix:** if the spec needs decomposition, flag it — `slice` can break the work
into shippable pieces after the user reviews. Don't split the spec itself;
instead note which sections are candidates for independent slices.

### 4. Ambiguity check

Look for requirements a reasonable person could interpret two different ways:

- "The system should handle errors gracefully" — which errors? What's graceful?
- "Users can manage their settings" — which settings? What operations?
- "Support multiple formats" — which ones, specifically?
- Conditional behavior without defined conditions — "if the user has
  permissions" without specifying which permissions

**Fix:** pick the interpretation that was discussed during brainstorming and make
it explicit. If neither interpretation was discussed, pick the simpler one, state
it, and flag the decision for the user.

### 5. Completeness check

Verify the spec covers what the brainstorming conversation settled:

- Every design decision from the conversation should appear somewhere in the
  spec
- Trade-offs that were discussed and resolved should be recorded (in
  implementation decisions or further notes), not silently dropped
- Constraints the user mentioned (timeline, compatibility, performance) should
  be visible

**Fix:** add the missing content from the conversation. If a decision was made
but the reasoning wasn't captured, add a brief note on why.

## Presenting to the user

After the self-review, ask the user to review the written spec:

> "Spec written to `<path>`. I've reviewed it for placeholders, consistency,
> scope, and ambiguity. Please take a look and let me know if you want any
> changes before we move to implementation planning."

Wait for the user's response. If they request changes, make them and re-run the
relevant review checks. Only proceed to implementation once the user approves.
