---
name: agent-skills
description: Author, review, and fix Agent Skills against the agentskills.io specification — SKILL.md frontmatter (name, description, license, compatibility, metadata, allowed-tools), body sections, bundled scripts/references/assets, and progressive disclosure. Use when writing a new skill or SKILL.md, converting a prompt or instructions file into a skill, reviewing or validating an existing skill, deciding what belongs in references/ vs assets/ vs scripts/, splitting an oversized SKILL.md, or diagnosing why a skill is never discovered or invoked.
---

# Agent Skills

Write skills that get **discovered** when they're relevant and **change the
agent's behavior** once loaded. Those are two separate problems: discovery is
won or lost in the `description`, behavior in the body. A skill that fails
either one is dead weight that still costs every session context.

This skill is host-agnostic. It follows the [Agent Skills
specification](https://agentskills.io/specification), which any conforming agent
can load — the word "agent" below means whichever one reads your skill.

## When to use this skill

- Writing a new skill, or converting an existing prompt, rule, or instructions
  file into one
- Reviewing or validating a skill before publishing or committing it
- A skill exists but is never activated — the description is the usual cause
- Deciding whether content belongs in `SKILL.md`, `references/`, `scripts/`, or
  `assets/`
- A `SKILL.md` has grown past ~200 lines and needs splitting

## What a skill is

A self-contained directory pairing instructions with bundled resources — scripts,
references, assets — that any conforming host can load. Unlike always-on rules or
coding standards, which define how *all* work is done, a skill teaches one
task-specific capability and stays out of context until a request matches it.

### Skill, or rule?

Hosts that support both put similar content in very different places. Decide by
what triggers it, not by what it's about:

| The content… | Belongs in |
| --- | --- |
| Applies to every edit of a file type, unprompted | A path-scoped rule |
| Applies to one task, when the user asks for it | A skill |
| Is a standard all work in the repo follows | Always-on instructions |
| Is long detail needed only partway through a task | A skill's `references/` |

If you can't name the request that should load it, it isn't a skill.

## Workflows

### Create a new skill

1. **Name the trigger.** Write the 3–5 phrases a user would type when they want
   this. If none come, stop — see [Skill, or rule?](#skill-or-rule).
2. **Create `<name>/SKILL.md`** with `name` matching the directory, and a
   `description` containing those phrases in the user's own words.
3. **Draft the body** — title, when-to-use, then only what the agent wouldn't
   already get right. Lead with `## Gotchas` if the domain has traps.
4. **Move the bulk out.** Anything exhaustive, or a workflow past ~5 steps, goes
   in `references/` with a link from the body.
5. **Validate** — see [Validation](#validation).

### Review an existing skill

1. **Discovery first.** Does the `description` contain the words a user would
   really type? Does it collide with a sibling skill's keywords?
2. **Cut what the model knows.** Anything on the first page of the official docs
   is costing context and buying nothing.
3. **Check the split** — `SKILL.md` under 500 lines, detail in `references/`,
   no reference chains.
4. **Run the [Validation](#validation) checklist.**

Both flows in full, plus converting an existing prompt or instructions file into
a skill: [AUTHORING.md](references/AUTHORING.md).

## Where skills live

The spec defines the skill *directory*; it does not define where a host looks for
one. **Discovery paths are host-specific — check the docs for your agent.** Most
hosts read a project-local directory that travels with the repository and a
personal one available everywhere, often scoped under their own config directory
(`.github/`, `.claude/`, `.agents/`, …).

Wherever it lands: **every skill is its own directory containing at minimum a
`SKILL.md`**, and the directory name must equal the frontmatter `name`.

## Frontmatter

`SKILL.md` opens with YAML frontmatter, then Markdown.

```yaml
---
name: skill-name
description: What the skill does, and the concrete triggers that should load it.
---
```

| Field | Required | Constraints |
| --- | --- | --- |
| `name` | Yes | 1–64 chars; lowercase `a-z`, `0-9`, and `-` only; no leading or trailing `-`; no consecutive `--`; must match the directory name |
| `description` | Yes | 1–1024 chars, non-empty. States WHAT it does and WHEN to use it |
| `license` | No | A license name, or a pointer to a bundled license file |
| `compatibility` | No | ≤500 chars. Environment requirements. Most skills don't need it |
| `metadata` | No | Map of string keys to string values, for anything the spec doesn't define |
| `allowed-tools` | No | Space-separated pre-approved tools. Experimental — support varies |

Those six fields are the whole portable surface. Any other top-level key is a
host extension and will be ignored elsewhere. Full field reference, plus valid
and invalid examples: [FRONTMATTER.md](references/FRONTMATTER.md).

### The description decides everything

During discovery the agent sees **only** `name` and `description`. A vague
description means the skill is never loaded, no matter how good the body is.

Include three things:

1. **WHAT** it does — the capability
2. **WHEN** to use it — concrete triggers, scenarios, file types, user phrasings
3. **Keywords** a user would actually type

```yaml
# Good — capability, triggers, and keywords
description: Test local web applications with Playwright. Use when asked to verify frontend behavior, debug UI, capture browser screenshots, or check visual regressions.

# Poor — no triggers, no keywords, no capability
description: Web testing helpers.
```

Then check it against the neighbors: if a sibling skill's description competes
for the same keywords, both lose. Narrow both, and draw the boundary by *scope*
rather than by naming the neighbor — see
[Naming another skill](#naming-another-skill).

## Naming another skill

**Don't name one without asking first.** Every skill is its own directory and
installs independently, so the sibling you point at may simply not be there — and
a reference to a skill that doesn't exist sends the agent chasing it at the exact
moment it was already unsure what to do. Your machine having both installed says
nothing about the machine that ends up with one.

State the exclusion in terms of the *task* instead:

```markdown
Not for reviewing feedback you received on a PR.   <!-- routes on any host -->
Not for reviewing PR feedback — that's `review-response`.   <!-- breaks alone -->
```

Where two skills genuinely ship as a unit — a bundle installed together, or a
repo that vendors both — a named reference is fine and often clearer. **Ask the
user before adding one, and add it only if they agree.** Silence isn't approval.

## Body content

The body loads once the skill activates. Sections worth having:

| Section | Purpose |
| --- | --- |
| `# Title` | One sentence on what the skill enables |
| `## When to use this skill` | Concrete scenarios; reinforces the description's triggers |
| `## Prerequisites` | Tools, services, or setup the agent can't assume exist |
| `## Workflows` | Numbered steps for procedures where sequence genuinely matters |
| `## Gotchas` | Proactive warnings — "never do X, because Y" |
| `## Troubleshooting` | Reactive fixes — "if you see X, try Y" |
| `## References` | Links to bundled files and external docs |

Not every skill needs every section. Skip `Prerequisites` when there are no
external dependencies; skip `Workflows` for purely advisory skills. Include
`Gotchas` whenever external tools, APIs, or non-obvious defaults are involved.

How to write each one, plus the prose style to write it in:
[SECTIONS.md](references/SECTIONS.md).

## Bundled resources

| Folder | Holds | Loaded |
| --- | --- | --- |
| `scripts/` | Executable automation | When run |
| `references/` | Docs the agent reads to decide | When referenced |
| `assets/` | Static files used **as-is** in output | Not into context |
| `templates/` | Scaffolds the agent **modifies** and builds on | When referenced |

The spec names the first three; `templates/` is a widely used convention, and
the spec permits any additional directories. **Rule of thumb:** if the agent
reads a file and builds on it → `templates/`; if it's emitted unchanged →
`assets/`.

Reference bundled files by relative path from the skill root, one level deep:

```markdown
See [the API reference](references/API.md) for response shapes.
Run `scripts/validate.sh` after making changes.
```

Choosing between them, when to bundle a script, and script requirements:
[RESOURCES.md](references/RESOURCES.md).

## Progressive disclosure

Three levels, and the whole design follows from them:

| Level | Loads | When |
| --- | --- | --- |
| Metadata (~100 tokens) | `name` + `description` | Always, for every installed skill |
| Instructions (<5000 tokens) | Full `SKILL.md` body | When a request matches |
| Resources | `references/` read, `scripts/` run, `assets/` used | As needed — assets never enter context |

So: install many skills without paying for them; pay for the body only on a
match; keep the expensive detail one hop away. When listing reference files, say
explicitly that they're to be read as needed rather than all upfront — otherwise
the agent tends to pull the lot and defeat the point.

## Writing high-impact skills

**Teach only what the agent doesn't already know.** Standard language syntax,
common library usage, well-documented API behavior — all of it is already in
the model. If it's on the first page of the official docs, leave it out. Spend
the body on internal conventions, non-obvious defaults, version-specific quirks,
and domain workflows that would otherwise be got wrong.

**Respect the discovery budget.** Every installed skill's description shares a
limited slice of context. A bloated description doesn't just waste your own
budget — it crowds out every other skill. Aim for the shortest text that still
carries WHAT, WHEN, and keywords.

**Gotchas are the highest-signal content you can write.** They prevent mistakes
instead of explaining them afterwards. Treat the section as living: every time
an agent produces a wrong result with this skill loaded, add a gotcha. Bold the
constraint, then give the reason.

**Prefer decision criteria over rigid steps.** Reserve numbered steps for
concrete, repeatable procedures — build, deploy, environment setup — where order
genuinely matters. Open-ended work (debugging, refactoring, review) needs room to
adapt, and steps that name file paths and line numbers break at the next
refactor. Worked contrast: [SECTIONS.md](references/SECTIONS.md).

**Split at ~200 lines.** Past that, move detail into `references/` and link to
it. 500 lines is the hard ceiling for `SKILL.md`.

## Gotchas

- **`name` must equal the directory name** — a mismatch is the most common
  validation failure, and typically surfaces as the skill silently never loading.
- **No consecutive hyphens, no leading or trailing hyphen** in `name`. `pdf--x`
  and `-pdf` are both invalid; uppercase is invalid too.
- **Never put host-specific keys at the top level** of frontmatter if the skill
  needs to be portable — the spec's escape hatch is `metadata`. Keys such as
  `argument-hint`, `applyTo`, or `disable-model-invocation` work only on the
  hosts that define them, and are ignored (not merged) elsewhere. A skill that
  will only ever run on one host may use them freely —
  [FRONTMATTER.md](references/FRONTMATTER.md) has the trade-off.
- **Don't quote-wrap `description` out of habit.** YAML quoting is a style
  choice, not a requirement; it's only *needed* when the value starts with a
  special character or contains a `: ` sequence. If you do quote, remember that
  single quotes escape as `''`.
- **A description that describes without triggering never fires.** "Helps with
  PDFs" names a topic, not an occasion. Write the user's words, not yours.
- **Keep reference chains one level deep.** A reference that points at another
  reference that points at a third burns turns and loses the thread.
- **Never bundle credentials or secrets**, and don't write paths that only exist
  on your machine — skills are meant to travel.
- **Never name another skill unless the user approved it.** A cross-reference is
  a dangling pointer everywhere that skill isn't installed. Draw the boundary by
  scope instead — [Naming another skill](#naming-another-skill).

## Validation

The [reference validator](https://github.com/agentskills/agentskills/tree/main/skills-ref)
checks frontmatter validity and naming conventions, if it's installed:

```sh
skills-ref validate ./my-skill
```

It isn't a prerequisite. These checks need nothing but a shell:

```sh
cd my-skill
grep -m1 '^name:' SKILL.md | grep -qw "$(basename "$PWD")" \
  && echo "OK: name matches directory" || echo "FAIL: name/dir mismatch"
wc -l < SKILL.md
grep -oE '\((references|scripts|assets|templates)/[^)]+\)' SKILL.md \
  | tr -d '()' | cut -d'#' -f1 | sort -u | while read -r f; do
      [ -e "$f" ] && echo "OK   $f" || echo "MISS $f"
    done
```

The link check also matches example paths inside fenced blocks, so read a `MISS`
before believing it. The rest is judgment:

- [ ] Frontmatter has valid `name` and `description`; `name` matches the directory
- [ ] `description` carries WHAT, WHEN, and keywords, and stays concise
- [ ] The description literally contains the phrases a user would type
- [ ] No sibling skill competes for the same keywords, or both state the boundary
      by scope rather than by naming each other
- [ ] No other skill is named anywhere in the skill without the user's approval
- [ ] Body teaches what the agent wouldn't already know
- [ ] `## Gotchas` present if there's any non-obvious behavior or common trap
- [ ] `SKILL.md` under 500 lines; split into `references/` at ~200
- [ ] Workflows over ~5 steps moved into `references/` and linked
- [ ] Scripts document their usage and handle errors with clear messages
- [ ] All resource references are relative paths, one level deep
- [ ] No credentials, secrets, or machine-specific paths

## References

Read these as needed for the task in hand, not all upfront.

- [AUTHORING.md](references/AUTHORING.md) — the create and review flows in full,
  and converting an existing prompt or instructions file into a skill
- [FRONTMATTER.md](references/FRONTMATTER.md) — every field, with valid and
  invalid examples
- [SECTIONS.md](references/SECTIONS.md) — how to write each body section
- [RESOURCES.md](references/RESOURCES.md) — scripts, references, assets,
  templates
- [Agent Skills specification](https://agentskills.io/specification) — the
  normative source
- [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) —
  reference validator library
- [anthropics/skills](https://github.com/anthropics/skills) — worked examples

Adapted from [awesome-copilot](https://github.com/github/awesome-copilot)'s
`agent-skills.instructions.md` (MIT), generalized to the Agent Skills
specification and made host-agnostic.
