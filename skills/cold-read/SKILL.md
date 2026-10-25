---
name: cold-read
description: Have a fresh agent with none of this conversation read a document before it reaches someone who wasn't there — a spec, implementation plan, PRD, handoff, or design — and report what a newcomer can't follow, which decisions it still leaves to the implementer, and what it proposes building that already exists. Use when asked for a cold read, fresh eyes on a draft, an unbiased read, whether a doc stands on its own, or whether an agent could implement this without coming back to ask. Not for reviewing code changes, and not for interviewing the user about a plan.
argument-hint: "[document path, or the draft in the conversation] [comprehension|readiness|reuse, up to two]"
---

# Cold read

Hand a document to a reader who has none of the context that produced it, and find out what it fails to say. **The session that wrote a document is the worst one to review it**: everything the conversation settled feels written down whether it is or not, and a self-review reads the author's memory as much as the page. A fresh agent reads only the page.

Arguments: `$ARGUMENTS`. Any word that names a lens — `comprehension`, `readiness`, `reuse` — selects that lens; the rest is the target, a file path or a description of a draft in this conversation. No target means the draft most recently produced in this conversation; with no draft either, ask what to read and stop there.

## When to use this skill

- A spec, plan, PRD, or handoff file is about to go to someone who wasn't in the conversation — a teammate, a contractor, an unattended agent, your own next session
- `draft-spec`, `draft-prd`, `draft-plan`, and `agent-handoff` call it before showing or launching; `brainstorming`'s spec review points here for the pass it cannot do itself
- The user asks for fresh eyes, an unbiased read, or whether a document stands on its own
- Not for code — a diff is `code-review`'s, and the adversarial hunt is `find-bugs`
- Not for challenging the thinking behind a plan with the person who holds it — that is `grilling`, an interview, where this is a read
- Not for a document whose only reader is the author, mid-task. Nobody cold will ever read it
- Not for the prompt you brief an agent with — that is read once by the agent it was written for, and a cold read of it would recurse

## The reader gets the page, never the conversation

What the reader receives decides whether the read is cold. Give it:

- **The document**, pasted verbatim, or its absolute path when it is already a file
- **The companion files** the document depends on to be read at all — the references a skill links, the template a spec defers to — named as part of the target, not left for the reader to discover
- **Read access to the repository the document is about**, named by absolute path, so it can check every file, symbol, and existing capability itself
- **One lens** — what to look for, from the table below

Never give it your summary of the document, what the conversation decided, which parts you are unsure of, or what you expect it to find. **A reader handed your hypothesis returns it confirmed**, and a reader handed your summary reviews the summary.

Coldness here means no conversation, not no standards. A fresh agent still loads the global and project instruction files, as a newcomer to the team would have them; that is intended, and there is nothing to switch off.

## Lenses

One reader per lens, at most two lenses per document, dispatched in the same response so they read in parallel.

| Lens | The question |
| --- | --- |
| **comprehension** | Could a competent newcomer follow this with nothing else? Every term, system, and prerequisite is defined in the document or linked; nothing leans on "as discussed" |
| **readiness** | Could someone execute this without making a single design choice? Every point where the implementer would still have to decide something, and every named path, symbol, or command that does not exist and that nothing in the document creates |
| **reuse** | Does anything the document proposes as new already exist? The reader must search the code for an equivalent before clearing each one |

**Choosing them.** Lenses named in the arguments, or by the calling skill, are the choice. Otherwise: comprehension is the default for any document; add readiness when someone will execute it step by step; add reuse when it proposes building a module, helper, endpoint, job, or table. So a spec or design that introduces something takes comprehension and reuse, a plan takes readiness, a handoff takes comprehension and readiness, and a PRD, ADR, README, or note takes comprehension alone. When three apply, keep the two whose miss would cost most — readiness for anything an agent will run unattended — and name the one you dropped.

The prompt for each lens is in [templates/reader-prompt.md](templates/reader-prompt.md).

## Workflow

1. **Pick the lenses** and name them to the user in one line before dispatching.
2. **Dispatch** a fresh agent per lens with the filled prompt. It must be able to read whole files and search the code; tell it it is read-only, which the prompt does. A search-only explorer that returns excerpts is the wrong type, and so is any agent that inherits this conversation.
3. **Triage every finding** into exactly one of:
   - **Fix** — the document is missing something it should say.
   - **Contest** — the finding is wrong. Name the line of the document or the file in the code that answers it.
   - **Ask** — the finding is a decision nobody made. Only the user can settle it; a fix you invent here is the assumption the read exists to catch.

   A finding that is partly right splits: fix the part that holds, contest the rest. Two readers landing on the same gap are one finding.
4. **Apply the fixes only to a draft this session is writing.** Any other document — committed, someone else's, vendored — gets the triaged findings as a report, and editing it is a separate request.
5. **Report** to the user: the lenses run, what you fixed, what you contested and why, and the questions that are theirs. Those questions hold the document back from being published, launched, or handed off until the user answers them — or accepts a default, which then goes into the document labeled as one (a spec's Further Notes, a handoff file's Constraints).
6. **Re-read at most once**, and only when the fixes or the user's answers changed what the document decides rather than how it says it. A second round of findings after that is residue — report it and stop.

## Gotchas

- **No fresh agent available means no cold read.** Where the host has no way to start one, say so and stop. A calling skill then carries on without the read and tells the user the document was not read cold. Reviewing the draft yourself and calling it cold is the failure this skill exists to replace.
- **A reader's finding is a claim, not a verdict.** Verify each one against the document and the code before acting on it — a reader with no context is wrong in its own direction, flagging terms the document defines two sections down.
- **"No findings" needs the same scrutiny.** Check that the report quotes the document and names files it opened. A reader that could not open the target, or never searched the code, has not read anything. Dispatch it once more with the document pasted rather than pointed at — that retry is not the step 6 re-read — and if it still cannot read, report the read as incomplete rather than clean.
- **A finding that only the conversation answers is a Fix, not a Contest.** If your rebuttal is "we agreed that earlier", the agreement is missing from the page, and that is exactly what the reader found.
- **Don't fix toward the reader's taste.** The lens asks whether a newcomer can follow the document, whether it can be executed, and whether it reinvents something. A reader preferring another design is out of scope — contest it or pass it to the user as a question; never rewrite the decision to satisfy it.
- **Paste a draft; point at a file.** An unsaved draft exists only in the conversation, and writing it to disk just to be read creates a file nobody asked for. A document already on disk is passed by absolute path, wherever it lives — `~/.agents/specs/` is as readable as the repository.

## References

Read this when you reach step 2.

- [templates/reader-prompt.md](templates/reader-prompt.md) — the reader prompt, its slots, and the instruction block for each lens

## Attribution

- [google/elephant-goldfish-model](https://github.com/google/elephant-goldfish-model) - Elephant-Goldfish Model, Apache-2.0
