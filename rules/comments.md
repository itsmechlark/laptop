---
paths:
  - "**/*.rb"
  - "**/*.rake"
  - "**/*.gemspec"
  - "**/*.js"
  - "**/*.jsx"
  - "**/*.mjs"
  - "**/*.cjs"
  - "**/*.ts"
  - "**/*.tsx"
  - "**/*.ex"
  - "**/*.exs"
---

# Code comments

When a comment earns its place, and when the code should carry the meaning instead. Language-agnostic — this loads for Ruby, JavaScript, TypeScript, and Elixir, with the language rules alongside it.

- A comment is a smell, not a goal, and rare by default. The names, the code, the tests, and the commit message carry the meaning; a comment is the last resort once none of them can.
- Before writing one, work the ladder in order — applying each only where it fits, because a manufactured extraction is its own smell: **rename** a method, variable, or class to state the intent; **extract** a confusing expression into a well-named function, or a missing concept into its own object or module; let a **test** tell the story of the behavior and its edge cases; put the *why* and the history in the **commit message**. A comment is what's left when none of those reach it.
- Reach for it only when the rationale matters but the commit message sits too far from the code for the next reader to find it there.
- Explain *why*, never *what* — the code already shows what it does, so narrating it is noise. The rare exception is genuinely dense mechanics, an algorithm whose steps aren't self-evident, where naming each one earns its keep.
- No narration and no commented-out code. A `TODO` is allowed only where it points to a tracking ticket for deliberate, recorded debt; a bare `TODO`, a changelog, or a decision log belongs in the tracker, an ADR, or the commit message, not the source.
- This governs explanatory comments in implementation, not two things it leaves alone: tooling directives the linter or compiler reads (`# rubocop:disable`, `eslint-disable-*`, `@ts-expect-error`), and the documentation layer where a language expects it — Elixir's `@moduledoc`/`@doc`, or doc comments a project publishes its API reference from. Follow the language's convention there.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/blob/main/rails/ai-rules/rules/comments.md) - rails AI rules code comments, MIT
