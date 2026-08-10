# Authoring and reviewing skills

The decisions behind each step of the two flows in `SKILL.md`, plus the case that
comes up most often in practice: turning an existing prompt or instructions file
into a skill.

## Creating a skill

### 1. Name the trigger before writing anything

Write down the 3–5 things a user would actually say when they want this skill.
Their words, not the codebase's.

```
"review this PR"
"is this ready to merge"
"check my diff before I push"
```

This list is the specification for the `description`, and it's also the honest
test of whether the skill should exist. If you can't produce the list, the
content is a standard (always-on instructions) or a file-type convention (a
path-scoped rule) — not a skill.

Then check the neighbors. List the sibling skills' descriptions and look for
keyword overlap. Two skills competing for "review" means the host picks close to
arbitrarily, and the loser is dead weight. Fix it by narrowing both descriptions
and stating the boundary in each — described by scope, not by name: "Not for
reviewing feedback you received on a PR."

Naming the neighbor instead is a dangling pointer wherever that skill isn't
installed, and skills install one at a time. If they genuinely ship together and
a name reads better, ask the user first and add it only if they agree.

### 2. Frontmatter

Directory name and `name` must match exactly. Write the `description` from the
trigger list, front-loading the capability:

```yaml
---
name: code-review
description: Review a diff for correctness, security, and maintainability before
  it ships. Use when asked to review code or a PR, check a diff before pushing,
  or judge whether a change is ready to merge.
---
```

Field-by-field rules and the failure modes: [FRONTMATTER.md](FRONTMATTER.md).

### 3. Draft the body

Write the sections the skill actually has content for, in this order of value:

1. `## Gotchas` — if the domain has traps, this is the whole reason the skill
   earns its context. Write it first.
2. `## When to use this skill` — restates the triggers so the agent can confirm
   it loaded the right thing, and notice when it didn't.
3. `## Workflows` — only for procedures where sequence genuinely matters.
4. Everything else, if warranted.

The filter for every line: **would the agent have got this right without it?**
Standard syntax, common library usage, anything on the first page of the official
docs — cut it. What survives is internal convention, non-obvious defaults,
version-specific quirks, and the domain knowledge that isn't written down.

Per-section guidance and prose style: [SECTIONS.md](SECTIONS.md).

### 4. Move the bulk out

`SKILL.md` is the always-loaded-on-match tier, so it pays for every line. Exhaustive
tables, complete API surfaces, and workflows past ~5 steps go in `references/`
with a one-line stub and a link from the body.

Say explicitly that references are read as needed. Without that, agents tend to
pull every linked file at once and defeat the point of the split.

What goes where — `references/` vs `assets/` vs `templates/` vs `scripts/`:
[RESOURCES.md](RESOURCES.md).

### 5. Validate

Run the checks in `SKILL.md`'s Validation section, then test discovery (below).

## Converting a prompt or instructions file

Existing prompts, always-on instruction files, and rules convert to skills
readily, but three things usually need changing.

**The trigger is missing.** An always-on file never needed one — it was simply
present. A skill needs a `description` that earns its way into context, so the
trigger list from step 1 is net-new work, not a rewrite.

**Host-specific framing has to go.** Product names, UI affordances, and
tool-specific instructions ("use the editor's refactor command") don't survive
the move to another agent. Rewrite in terms of the capability, not the product.
Non-portable frontmatter keys go in `metadata`.

**Always-on content is usually too broad.** A file that applied to all work often
bundles three or four separable capabilities. Split them: several small skills
with sharp descriptions beat one that fires for everything and helps with nothing.

Keep the original's attribution and license if you're adapting someone else's
work.

## Reviewing a skill

Work outside in — discovery first, because a skill that never loads makes the
quality of its body irrelevant.

| Check | Failure looks like |
| --- | --- |
| Does the description contain the user's words? | Skill never fires |
| Does it collide with a sibling? | Fires unpredictably, or never |
| Is the body teaching what the model knows? | Context spent, behavior unchanged |
| Are the gotchas real, with reasons? | Rules get rationalized away |
| Is exhaustive detail in `references/`? | Every match pays for the rare case |
| Do reference chains go more than one hop? | Turns burned, thread lost |
| Any secrets or machine-specific paths? | Skill can't travel; possible leak |
| Does it name another skill, unapproved? | Dangling pointer where that one isn't installed |

The most common real defect is the third row: a body that reads well and changes
nothing, because it explains what the model already does correctly. Delete
generously — a shorter skill that only carries the non-obvious is strictly better
than a complete one.

## Testing discovery

There's no substitute for checking that the skill fires.

1. Take the trigger phrases from step 1. Confirm the `description` literally
   contains those words — not synonyms. Discovery matches on the text present.
2. Start a fresh session and use one of the phrases verbatim. Confirm the skill
   loads.
3. Try an adjacent request that should *not* load it. If it fires anyway, the
   description is too broad, and it's now stealing context from other skills.

A skill that fires on everything is a worse failure than one that never fires:
the first is invisible and costs every session, the second is at least obvious.
