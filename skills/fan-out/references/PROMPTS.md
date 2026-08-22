# Writing a fan-out prompt

An agent starts with an empty session. Everything it needs to succeed is in the
prompt, or it isn't anywhere.

## Anatomy

| Section | Purpose |
| --- | --- |
| **Goal** | What to accomplish — one sentence, one problem |
| **Context** | The error output, failing test names, file paths, or symptoms, pasted in full |
| **Constraints** | What not to change; where the scope ends |
| **Expected output** | What to return: a diagnosis, a summary of the change, a recommendation |

The Context section is where fan-out usually fails. A path is cheap to paste and
expensive for the agent to find; a stack trace it has to reproduce is a stack
trace it may reproduce differently.

## Template

```
[Goal — one sentence stating what to accomplish]

Context:
[Paste the error output, failing test names, relevant file paths, or symptoms.
Include everything the agent needs to locate and understand the problem.]

Constraints:
- Only modify files in [scope]
- Do not change [out-of-scope areas]
- [Any other boundary]

When done, return:
- What you found (root cause)
- What you changed and why
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
- Does it say what to return, in the shape you want to integrate?
- Is it one problem? A prompt covering two is a partition that wasn't finished.

## Mistake to fix

| Mistake | Fix |
| --- | --- |
| **Too broad** — "fix all the tests" | One problem per agent — "fix the 3 timing failures in `abort.test.ts`" |
| **No context** — "fix the race condition" | Paste the error output, name the file, describe the symptom |
| **Referenced context** — "the bug we discussed" | Paste it; the agent was not in that conversation |
| **No constraints** — the agent refactors the neighbourhood | State the scope and what's off-limits |
| **No output spec** — "fix it" | "Return: root cause, what you changed, open questions" |
| **Related problems split apart** — fixing one may fix the other | Investigate together first; fan out only what's genuinely independent |
| **No worktree for an editing agent** — concurrent edits collide | Create worktrees per `git-worktree`; see [WORKTREES.md](WORKTREES.md) |
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
