---
name: explain
description: Explain what a piece of code does — a specific file, class, or method in close detail, or a user-facing flow as a concise system overview. Use when asked what something does, how a flow works, where something is handled, or to build a mental model of unfamiliar code before changing it. Also for a product person asking how the product behaves today — what happens when a customer does X, whether staff can do Y — answered in plain language with no code. What it does and why, never whether it's good — no review, no edits.
argument-hint: "[file path, class name, method, flow, or product question]"
context: fork
agent: Explore
---

# Explain

Hand someone a working mental model of code they have to navigate — what it does, how it does it, and what would surprise them — without judging it and without touching it.

Subject: `$ARGUMENTS`. Empty means the subject is whatever the conversation is already looking at; when there is nothing to take, ask which file or flow before researching anything. Otherwise do the research and deliver the whole explanation in one pass — there is no round trip to ask which mode was meant.

There are two readers, an engineer (the default) and a product person. The research is identical for both; only the delivery differs.

## When to use this skill

- Someone asks what a file, class, module, or method does
- A product person asks how the product behaves today — what happens when a customer does something, whether staff can do something — and needs the answer without code
- Someone asks how a user-facing flow works end to end, or where a behavior is handled
- Unfamiliar code has to be understood before it can be changed safely
- Onboarding: a new joiner, a contractor, or an agent needs the shape of an area
- Not for judging the code — correctness, security, performance, and maintainability verdicts belong to `code-review`, and an adversarial defect hunt to `find-bugs`
- Not for writing up requirements or a proposed change — that's `draft-prd`
- Not for changing anything, including the rename or doc comment the explanation makes obvious — that's `tdd`'s work, behind a test
- Not for a term the code uses two ways (`domain-modeling`) or a question that is really about where a seam belongs (`codebase-design`)
- Not for explaining a language feature, a library, or a stack trace in the abstract: those need no codebase read and no skill loaded

## Pick the reader

You cannot ask who is reading, so decide from the request. **Default to the engineer.** Use the product register only when the request is phrased around what customers, guests, or staff do rather than around code, or asks outright for plain or non-technical language ("for a PM", "no code please", "does the product support…"), and names no code identifier. Any file path, class, or method name in the request means engineer, whatever else it says, and a bare "how does checkout work?" with no such signal stays engineer too. When the signals conflict or are thin, stay with the engineer.

The product register changes what the reader sees, not what you do: trace the code, read the history, follow the indirection. [Product register](#product-register) below says how to deliver it.

## Pick the mode from the subject

| The subject is | Mode | Deliverable |
| --- | --- | --- |
| A file path, class, module, or method | **Code explanation** | Four prose sections, in close detail |
| A user action, feature, or flow — "password reset", "checkout" | **Flow explanation** | A diagram, then a three-part summary |
| A product question — "can staff refund a deposit?", "what happens if a guest cancels late?" | **Product answer** (product register only) | The direct answer, then the conditions behind it |

A name that is both a feature and a class is a flow: explain the flow and name the class as its entry point, because the wider answer contains the narrower one. A product question that is really about how a whole flow works is a flow explanation in the product register, diagram included; one that can be answered yes, no, or "depends" is a product answer.

## Code explanation

**Read the history before the code.** `git log --oneline -15 <file>`, then `git log -1 -p <file>`. Commit messages carry the *why* the code cannot: the bug that forced a guard, the workaround for someone else's API, the refactor that left a seam behind. Anything that reframes the code belongs in the explanation, not just in your head.

Then read the code and explain in this order.

### 1. What it does — one paragraph

Plain English, no jargon, no code. What goes in, what comes out, what changes as a result — described from outside the implementation, the way you would tell it to whoever asked for the feature.

### 2. How it does it — the path through the logic

Narrate the meaningful chunks in order. For each: what the step does, why it happens here rather than elsewhere, and what would break without it. Skip the obvious — a reader who needs strong-params or pattern matching explained is not the reader. Spend the words on the parts that need interpretation.

### 3. Patterns and conventions in use

Name the patterns and say why they show up here: a service object with one public `call`, a query object keeping query logic out of the model, `delegate` avoiding a Law of Demeter violation, a GenServer holding state that a table would hold elsewhere. Where a pattern is used off-label, say so neutrally — understanding requires knowing when something is unusual, and that is still a description, not a verdict.

### 4. What to watch out for

Non-obvious behavior, implicit dependencies, and what would surprise a maintainer: ordering that matters, a callback with side effects, state that outlives the call, a config value that decides the branch. Not a critique — "here is what you need to know to work safely in this area."

## Flow explanation

Find every entry point first, then trace each one through the codebase — route handlers, service objects, models and callbacks, background jobs, mailers, outbound calls — following the failure paths as well as the one that works. Entry points hide in more places than the route table: scheduled jobs, queue consumers, webhooks, admin actions, rake or mix tasks, console scripts.

Then deliver a **diagram** and a **summary**:

1. **Diagram** — states, transitions, decision points, and terminal states, in box-drawing characters. Behavior, not call stacks. Conventions and a worked example: [FLOW-DIAGRAM.md](references/FLOW-DIAGRAM.md).
2. **Summary** — three sections in plain English:
   - **Entry points** — every way the flow can start, one sentence each on what triggers it and what it does.
   - **Branching logic** — the conditions that choose the path: feature flags, state checks, validations, guard clauses, authorization.
   - **Side effects** — everything with consequences outside the flow: jobs enqueued, mail sent, external APIs called, broadcasts, cache and state writes. This is the section someone reads before touching the code.

## Product register

For a product reader, every sentence is in outcome language: what a person can do, what they see, what the business gets. Never show them a file path, a class or method name, an HTTP verb or route, a command, a library name, or a skill name. Name entry points by what a person does ("a guest taps Cancel in the booking widget"), not by route or job. The translation table and a worked example are in [PRODUCT.md](references/PRODUCT.md).

- **Code explanation** keeps *What it does*. *How it does it* becomes **The steps, in order**. *Patterns and conventions* is dropped; it only matters to engineers. *What to watch out for* becomes **Limits and surprises**: settings that vary per customer, timing, and what happens elsewhere (emails, charges).
- **Flow explanation** keeps the diagram, with entry points named as user actions and decisions phrased as business questions. The summary becomes **Ways it starts**, **What decides the outcome** (business rules, settings, permissions), and **What else happens** (emails, charges, notifications, other systems told).
- **Product answer** is four parts: **Answer** (yes, no, or "depends on …", first and in one sentence), **When and how**, **Limits and exceptions**, **What I couldn't confirm**.
- **Completeness still applies.** "Ways it starts" is the same every-entry-point claim, so run the same search; a product reader cannot spot the path you left out.
- **Say what you could not confirm.** Behavior that lives in another service, varies by customer configuration, or cannot be read off the code is reported as "I couldn't confirm whether…", never stated as a product fact.

## Gotchas

- **Leaking the register.** A product answer that only makes sense with the code in view has not been translated yet. A config key or flag name becomes "a setting each restaurant can turn on"; a callback becomes "it also sends…". Reread the answer as someone who has never seen the repository.

- **Explain the code in front of you, not the library it calls.** The failure is describing what a framework or gem *normally* does and skipping what this code does with it — an overridden callback, a monkey patch, a wrapper that swallows the return, a version whose behavior changed. When the path goes through a dependency, open the installed copy: that is the one that runs.

- **Never edit, not even the one-line fix.** A typo, the rename that would settle the confusion you just described, a doc comment — all out of scope, and the read-only fork this skill runs in enforces it. Name what you found, say which skill owns it, and stop there.

- **"I could not resolve this" beats a plausible mechanism.** Metaprogramming, dynamic dispatch, `method_missing`, and runtime configuration all produce paths that cannot be read off the source. Say which branch you could not settle and what would settle it. An invented explanation is indistinguishable from a verified one to the reader, and they will act on it.

- **Follow the indirection — it is exactly the half the reader cannot follow alone.** Callbacks, concerns and mixins, middleware, decorators, `around` filters, observers, and enqueued jobs all run code that never appears in the file you were pointed at. A file-local explanation of behavior that lives in five includes is worse than none, because it reads as complete.

- **An entry point you did not search for is not an absent one.** "Every way this flow starts" is a completeness claim, so make the search deserve it: the route table, the job and queue definitions, the task files, and the callers of the entry class — with `find -L` wherever the tree mixes real directories and symlinks (AGENTS.md §4, *Definition of Done*). Missing an entry point has consequences: someone changes the flow and breaks the path you never mentioned.

- **The returned explanation is the entire output.** Running forked means nothing survives but the text you hand back — no follow-up action, no "I'll check that next", no note left in a scratch file. Everything you learned that matters has to be in the answer.

## Tone

Clear and direct. You are translating, not teaching and not judging: no hedging, no throat-clearing, no verdicts on the code's quality. The reader should finish able to navigate the area and say what would break if they changed it.

For a product reader, talk the way a good PM talks to a colleague: short sentences, the business's own words, no engineering shorthand.

## References

Read these when they apply, not upfront.

- [FLOW-DIAGRAM.md](references/FLOW-DIAGRAM.md) — what the diagram shows, the box-drawing conventions, and a worked example of a full flow explanation
- [PRODUCT.md](references/PRODUCT.md) — for a product reader: the product words for every technical finding, diagram conventions, and a worked example

## Attribution

- [thoughtbot/rails-consultant](https://github.com/thoughtbot/rails-consultant/tree/main/skills/explain) - explain, MIT
