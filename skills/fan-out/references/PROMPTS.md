# Writing a fan-out prompt

An agent starts with an empty session. Everything it needs to succeed is in the
prompt, or it isn't anywhere.

## Anatomy

| Section | Purpose |
| --- | --- |
| **Goal** | What to accomplish — one sentence, one problem |
| **Context** | The error output, failing test names, file paths, or symptoms, pasted in full |
| **Constraints** | What not to change, and what not to do at all |
| **Expected output** | What to return: a diagnosis, a summary of the change, a recommendation |

The Context section is where fan-out usually fails. A path is cheap to paste and
expensive for the agent to find; a stack trace it has to reproduce is a stack
trace it may reproduce differently.

**Use one return shape for every agent in the fan-out.** Identical sections in
every report make the results comparable, contradictions obvious, and a missing
answer visible — three bespoke shapes turn integration into translation.

## Constraints every prompt carries

Beyond the scope boundary specific to the domain, these four are not optional.
An agent working alone would be right to do any of them; an agent that is one of
five is not.

- **Verify before committing.** "Run the tests covering your change, and paste
  the command and its result in your report." Three branches of unverified
  commits are worse than three agents that failed honestly, and the pasted
  output is what makes "fixed" checkable instead of merely claimed
  (AGENTS.md §4, *Definition of Done*).
- **Do not push, open a pull request, merge, or touch any other branch.** Commit
  on your own branch and stop. This is the one class of agent mistake that
  editing a file can't undo, and pushing unasked violates the global standard
  besides.
- **Do not dispatch agents of your own.** Recursive fan-out multiplies work
  nobody is watching.
- **Do not touch the shared files** — lockfiles, `db/schema.rb`, migrations,
  locale files, barrel exports — unless this domain owns them, and say which
  agent does own them when one has to.

## Template

```
[Goal — one sentence stating what to accomplish]

Context:
[Paste the error output, failing test names, relevant file paths, or symptoms.
Include everything the agent needs to locate and understand the problem.]

Constraints:
- Only modify files in [scope]
- Do not change [out-of-scope areas]
- Do not touch [shared files: lockfiles, schema, migrations, locales]
- Do not push, open a PR, merge, or switch branches
- Do not dispatch agents of your own
- Run the tests covering your change before you commit

When done, return:
- What you found (root cause)
- What you changed and why
- The verification you ran, with the command and its output
- Any concerns or open questions
```

For an agent that edits files, two more instructions are mandatory — entering
its worktree first and committing before it finishes. Both are in
[WORKTREES.md](WORKTREES.md).

## Quality checklist

- Could a colleague who joined the team this morning act on this prompt with
  nothing else? If not, what's missing is what to add.
- Does it contain the actual error output, not the phrase "the failing tests"?
- Does it say what's out of scope, not only what's in scope?
- Does it carry the four constraints above?
- Does it say what to return, in the same shape as its siblings?
- Is it one problem? A prompt covering two is a partition that wasn't finished.

## Common mistakes

| Mistake | Fix |
| --- | --- |
| **Too broad** — "fix all the tests" | One problem per agent — "fix the 3 timing failures in `abort.test.ts`" |
| **No context** — "fix the race condition" | Paste the error output, name the file, describe the symptom |
| **Referenced context** — "the bug we discussed" | Paste it; the agent was not in that conversation |
| **No constraints** — the agent refactors the neighbourhood | State the scope, the shared files, and the four prohibitions |
| **No output spec** — "fix it" | "Return: root cause, what you changed, verification run, open questions" |
| **Per-agent output shapes** — three reports, three formats | One return contract for the whole fan-out |
| **A flaky failure taken at its word** — one lucky green run reported as fixed | "Run the spec 10 times and report the pass count", or keep flakes out of the fan-out |
| **Related problems split apart** — fixing one may fix the other | Investigate together first; fan out only what's genuinely independent |
| **No worktree for an agent that edits or runs anything** — concurrent writes collide | Create worktrees per `git-worktree`; see [WORKTREES.md](WORKTREES.md) |
| **No commit instruction** — the change strands unmerged | "Commit your changes on this branch before you finish" |

## Worked example

Three unrelated test files failing, dispatched in one response:

```
Agent("Fix the 3 timing failures in agent-tool-abort.test.ts: <pasted output>")
Agent("Fix batch-completion-behavior.test.ts — tools not executing: <pasted output>")
Agent("Fix tool-approval-race-conditions.test.ts — execution count is 0: <pasted output>")
```

All three run concurrently because they were issued together. Split across three
responses, they run one after another for no benefit.
