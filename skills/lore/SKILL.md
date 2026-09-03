---
name: lore
description: Write a lore note — the in-tree record of what a piece of work taught about the codebase, kept next to the code instead of in a PR description nobody reads twice. Use when asked to write, add, or update lore, to put an implementation summary in the lore folder, to record what an investigation or root-cause analysis found, or to capture what a session learned before the context is gone. Most work earns no note, and this says so rather than writing one. Not for the PR description or commit message of a change, not a status update, and not context handed to another session.
argument-hint: "[what the note is about]"
---

# Lore notes

A lore note records **what the work taught about the codebase** — the mechanism that cost hours to find, the alternative that was tried and rejected, the thing deliberately left broken. It lives in the repository, so it survives the branch, the PR, and the next context window.

Subject: `$ARGUMENTS`. Empty means the note covers whatever the session just finished — say what you think that is before writing, so a wrong guess costs a sentence rather than a file.

Everything else about the change already has a home. The commit says why this diff. The PR description says what changed and how it was tested. The ADR records the decision the codebase must live with. **A lore note that repeats any of them is waste** — it costs a reader a stop and teaches them the directory is filler. [BOUNDARIES.md](references/BOUNDARIES.md) has the full map.

## When to use this skill

- Asked to write, add, or update lore, or to file an implementation summary in the `lore` folder
- An investigation, root-cause analysis, or harden pass turned up something the diff won't show
- A session found non-obvious behavior in a dependency or in code nobody on the team wrote
- Work spanned several PRs and no single PR description holds the arc
- Not for the PR description, the commit message, or the branch name — `pull-request` and `git-commit`
- Not for a hard-to-reverse architectural decision — that is an ADR, via `domain-modeling`
- Not for seeding the next session's context — that is `claude-handoff`
- Not for a status update to a person — that is `standup`
- Not for explaining code to the user right now, with no file written — that is `explain`

## The two gates

Both must pass before a single word gets written.

### 1. The repository already has a lore directory

```sh
[ -d "$(git rev-parse --show-toplevel)/lore" ] || echo "no lore directory"
```

**If it isn't there, stop and say so.** Do not create it, do not pick a different directory, and do not write a `lore/README.md` telling the team how notes should look. This convention is personal — it applies to notes written here, never to the repository's other contributors or their existing files. See [Gotchas](#gotchas).

### 2. The note survives the deletion test

Ask it literally: **if this note vanished, what would the next person have to rediscover?**

If the answer is "nothing — they would read the diff, the PR, or the commit", there is no note to write. Say that in one line and stop. Most work does not earn one, and the alternative is a directory of files restating diffs — which is how a lore directory becomes something nobody opens.

A note passes the gate when it holds at least one of these four. Worked examples of each, drawn from real findings: [BOUNDARIES.md](references/BOUNDARIES.md).

| It records | Because |
| --- | --- |
| Mechanism in code you didn't write | A framework or library that defies its own docs is not in anyone's diff |
| A rejected alternative | The diff shows what was built, never what was tried and abandoned |
| Something deliberately left alone | Reviewed-and-not-changed leaves no trace at all |
| A cross-PR arc | No single PR description spans a four-PR migration |

`path:line` anchors are not a fifth category — they are how the four above get recorded. A note whose only content is where the scary code lives fails this gate.

## Workflow

### 1. Run both gates

In order. Gate 1 is a directory check; gate 2 is a question you answer out loud before writing. If gate 2 produces only "it summarizes the change", stop.

### 2. Pick the kind and check for a predecessor

Five kinds, one per note — `plan`, `implementation`, `investigation`, `decision`, `operation`. What each is for, and where a harden pass lands: [KINDS.md](references/KINDS.md).

Then look for what this note continues:

```sh
grep -l 'topic: <topic>' lore/*.md
```

A match means the earlier note gets `status: superseded` and this one lists it in `supersedes:` — the arc is the value, so never edit the predecessor's body to hold the new finding.

The link is deliberately one-directional: the successor names the predecessor, and the predecessor is found again through `topic`. Don't invent a `superseded-by:` field to close the loop — it would mean editing a merged note every time a successor lands, which is the thing the frozen-body rule exists to prevent.

### 3. Write it

Copy [assets/lore-note.md](assets/lore-note.md) to `lore/YYYYMMDD-HHMM-<slug>.md`, taking the timestamp from `date +%Y%m%d-%H%M` and never from memory.

Fill the frontmatter, then the lead paragraph, then only the sections that have something in them. **Omit every empty section** — a heading with nothing under it is the filler this skill exists to prevent (AGENTS.md §8).

Four rules decide the prose:

- **Never narrate the diff.** No file-by-file walk, no changed-files list, no test counts. All three are in the PR.
- **Every claim about code carries `path:line`.** It is what makes the note checkable a year later, when the line has moved and the claim has to be re-verified.
- **Present tense for what is true, past tense for what was done.** A note written in the future tense is a plan wearing an implementation's clothes.
- **500 words, and that is a ceiling rather than a target.** Past it the note is a subsystem manual, which has a different lifetime and needs a home that gets updated in place — say so and stop rather than growing it.

### 4. Stop

Do not commit it. The note is part of the change and gets staged with everything else, by `git-commit`, when the user asks.

## Gotchas

- **Never impose this on the repository.** No `lore/README.md`, no edit to a tracked `CLAUDE.md`, `AGENTS.md`, or `.claude/commands/` file to make the team follow it. In a shared repo those files are everyone's; this convention is one person's. The notes themselves are additive and land in a normal commit.

- **Never restructure someone else's lore.** Existing files predate this convention and most were written by other people or other tools. Adding frontmatter to them, retitling them, or "fixing" their sections is churn in a shared repo that buys the user nothing. Flipping `status:` on a note that already *has* frontmatter is the one exception, and it is maintenance rather than restructuring — [KINDS.md](references/KINDS.md) has when.

- **The note comes after verification, never from the plan.** A note written mid-work records what was believed, and the belief is usually what changed. Write it once the work holds.

- **Don't edit a merged note except to mark it superseded.** A dated record that gets rewritten is not a record. A root-cause note whose conclusion is corrected a week later ends up contradicting its own filename — that correction is a second note, not an edit.

- **A `plan` note is closed out, not deleted.** When the implementation note lands, flip the plan to `status: superseded` and name it in `supersedes:`. Deleting it erases the arc, which is the part a PR description can't hold.

- **`kind: operation` is usually not worth writing.** A backport or cherry-pick whose note would be a lead paragraph plus a commit list fails gate 2. Write one only for the conflict resolution that will recur.

- **Don't reach for lore when the finding has a stronger home.** A decision that is hard to reverse, surprising, and the result of a real trade-off is an ADR — all three, or it is lore. A convention that should govern every future edit of a file type is a path-scoped rule, via `agent-rules`.

- **Take the timestamp from `date`.** Both the filename prefix and the sort order depend on it, and a wrong one puts the note in the wrong place in the arc forever.

## Troubleshooting

| Issue | Solution |
| --- | --- |
| A command or workflow says to write lore, but gate 2 fails | The gate wins. Say in one line what the note would have restated and where that already lives, then skip it. |
| The repo has no `lore/` | Stop. Don't create it and don't substitute `docs/`. Tell the user, and let them decide whether the repo gets one. |
| The finding is worth 3,000 words | Then it isn't a note. Say so — a subsystem reference has a different lifetime and needs a home that gets updated in place, which a dated file never gets. |
| Two notes for one piece of work, hours apart | One supersedes the other. Pick the one that turned out to be true, flip the other, and link them by `topic`. |
| Unsure whether it's lore or an ADR | Apply the three ADR tests (hard to reverse, surprising, real trade-off). All three hold → ADR via `domain-modeling`. Any missing → lore. |
| Unsure whether it's lore or the PR description | Ask which one outlives the branch and is readable with no network. If the answer is "either", it's the PR's. |
| The user wants a note on every change | Say once what that produces: a directory whose signal-to-noise drops until nobody opens it. Then follow their call — it's their directory. |
| You read a note whose body no longer matches the code | Flip it to `status: historical` in that turn, if it has frontmatter to flip. Nobody sweeps the directory, so this is the only moment that information exists — [KINDS.md](references/KINDS.md). |

## References

Read these when a step points at them.

- [BOUNDARIES.md](references/BOUNDARIES.md) — the overlap map against commits, PRs, ADRs, handoffs and status updates, with the failure each overlap causes
- [KINDS.md](references/KINDS.md) — the five kinds, every frontmatter field and why two obvious ones are absent, supersession, and the discovery queries
- [assets/lore-note.md](assets/lore-note.md) — the template to copy
