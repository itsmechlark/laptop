---
name: agent-rules
description: Author, review, and fix path-scoped agent rules — the instruction files that load because the agent touched a matching file rather than because someone asked. Covers the frontmatter each host uses (paths, globs plus alwaysApply, applyTo, trigger), scoping a glob to exactly the files a rule governs, keeping a rule short enough to sit in every matching session, and porting one rule across Claude Code, Cursor, Copilot, Windsurf, and Cline. Use when writing or reviewing a rule file, when a rule never loads or loads on everything, when a glob matches the wrong files, or when deciding whether something belongs in a rule rather than a skill or an instruction file.
---

# Agent Rules

Rules are the imposed layer. A skill loads because a request matched it; a rule
loads because the agent touched a file the rule claims. Nobody opts in, so every
session that opens a matching file pays for the rule whether or not it needed
it. Short body, exact glob — those two constraints follow from that one fact,
and most of this skill is their consequences.

**There is no cross-host specification for rules.** Skills have one
([agentskills.io](https://agentskills.io/specification)); rules do not. Six
hosts converged on the same idea — markdown, YAML frontmatter, a glob list — and
then picked five different keys for the glob list and three different shapes for
its value. A rule written for one host is usually *inert* on the next rather
than broken, which is why the failure is so hard to see. Write for the host you
target; port deliberately.

## When to use this skill

- Writing a new rule, or splitting an oversized `AGENTS.md` / `CLAUDE.md` into
  path-scoped rules
- Reviewing a rule before committing it
- A rule never fires, or fires on every file — activation is the usual cause,
  not the body
- Deciding whether something is a rule, a skill, or an always-on instruction
  file
- Porting a rule set to another host, or maintaining one set across several

## Rule, skill, or instruction file?

Three layers. What distinguishes them is what pulls them into context, not what
they are about:

| Layer | Pulled in by | Paid for by | Fits |
| --- | --- | --- | --- |
| Instruction file (`AGENTS.md`, `CLAUDE.md`) | Session start, unconditionally | Every session | Build commands, layout, conventions true everywhere |
| Rule | The agent reading a file the glob matches | Every session that touches one | "Migrations must be reversible", "components take no side effects" |
| Skill | A request matching its description | Only a matching request | "Open a pull request", "drive this test-first" |

The test is one question: **name the thing that should pull it in.**

- You can name a glob → rule.
- You can name the request a user would type → skill. `agent-skills` writes
  those.
- Neither, because it is true of the whole repository → instruction file.
  `create-agentsmd` writes those.

If a rule's glob would have to be `**/*` to cover the cases you have in mind,
it was never a rule — move it to the instruction file, where it will at least
load reliably.

**Rules are guidance, not enforcement.** Every host treats them as context the
model reads and mostly follows. When a constraint has to hold — a command that
must never run, a path that must never be read — it belongs in the host's hooks
or permissions layer, not in a rule. `codex-config` covers that layer for Codex.

## The format landscape

| Host | Location | Scoping key | Always-on form | Cap |
| --- | --- | --- | --- | --- |
| Claude Code | `.claude/rules/**/*.md`, `~/.claude/rules/` | `paths:` — YAML list | Omit `paths` | — |
| Cline | `.clinerules/**/*.md` | `paths:` — YAML list | Omit frontmatter, or `alwaysApply: true` | — |
| Cursor | `.cursor/rules/**/*.mdc` | `globs:` — bare comma-separated string | `alwaysApply: true` | ~500 lines, advisory |
| Windsurf | `.devin/rules/*.md`, `.windsurf/rules/*.md` | `trigger: glob` + `globs:` | `trigger: always_on` | 12,000 chars/file |
| Copilot | `.github/instructions/**/*.instructions.md` | `applyTo:` — comma-separated string | `applyTo: "**"` | — |
| Amazon Q | `.amazonq/rules/**/*.md` | None — all rules always on | (every file) | — |

Note the third column carefully: `paths` takes a YAML sequence, Cursor's `globs`
takes an unquoted comma-separated string that breaks when you quote it or make
it a list, and `applyTo` takes a quoted comma-separated string. Same concept,
three incompatible spellings.

**An unrecognized key is silently dropped, and what happens next differs by
host.** Ship `paths:` to Cursor and the rule has no globs, no description, and
no `alwaysApply` — which is exactly the Apply Manually configuration, so it
waits forever to be @-mentioned. Ship `globs:` to Claude Code and the rule has
no `paths`, which means unconditional: it loads on every session, everywhere.
The same mistake fails closed on one host and wide open on the other.

Per-host frontmatter in full, the load-order and precedence rules, and a porting
recipe: [FORMATS.md](references/FORMATS.md).

## Writing the glob

The glob is the whole interface. A rule with a perfect body and a wrong glob
does nothing; a rule with a thin body and an over-broad glob taxes every session
in the repository.

**Scope to what the rule governs, not to what it mentions.** A rule about
writing migrations belongs on `**/db/migrate/**/*.rb`, not on `**/*.rb` because
migrations happen to be Ruby. The question to answer is "which files would be
wrong if this rule were ignored?"

**Layer broad and narrow instead of writing one clever pattern.** Hosts
concatenate every rule whose glob matches, so a general `**/app/**/*.rb` rule
and a specific `**/app/models/**/*.rb` rule both load on a model, and each can
stay focused. This is the intended shape — resist folding the narrow one into
the broad one with conditionals in prose.

**Anchor patterns with a recursive prefix** unless the rule genuinely only
applies at the repository root. `*.md` matches markdown in the project root
only; `**/*.md` matches it anywhere. In a monorepo the difference is the rule
working or not, and it is invisible until someone opens a file one directory
deeper than you tested.

**Every pattern you add is a permanent context cost.** Before widening a glob to
catch one more case, check whether that case is better served by a second,
narrower rule.

Pattern syntax, brace expansion and its limits, the layering worked through, and
how to test a glob before committing it: [SCOPING.md](references/SCOPING.md).

## Writing the body

A rule loads mid-task, next to code the agent is already editing, and it loads
again and again. Write accordingly:

- **Constraints, not prose.** Bulleted imperatives the agent can check itself
  against. "Rescue specific exceptions, never bare `rescue`" beats a paragraph
  about error-handling philosophy.
- **One concrete example beats three paragraphs.** A short before-and-after, or
  a path to the file in this repository that already does it right. What does
  not belong is the appendix: reference material, multi-step procedures, and a
  catalogue of worked cases go in a skill, loaded on demand. A rule that wants
  an appendix is a rule that should name a skill and stop.
- **Point at canonical files; never copy their contents.** An inlined snippet is
  a second copy nothing keeps in sync, and it goes stale the first time someone
  edits the original — silently, because the rule still reads fine. Name the
  path and let the agent open it.
- **One topic per file.** The filename is the topic; if you need a second
  heading level to organize it, it is two rules.
- **Terse.** Windsurf caps a rule at 12,000 characters and Cursor advises 500
  lines, but the real budget is smaller: this text competes with the code for
  attention every time it loads. Aim for one screen.
- **Say why for anything surprising.** A constraint the agent can see the reason
  for survives contact with a case you did not anticipate; a bare prohibition
  does not.

Four kinds of content reliably fail that trade and should not be here at all:
anything a linter or type-checker already enforces, anything the model already
knows, edge cases that rarely fire, and code the repository already contains.
Write the rule after the *second* time you correct the same mistake, never in
anticipation. Each of those with its worked contrast, plus how to turn a
repeated chat prompt into a rule: [CONTENT.md](references/CONTENT.md).

**Cite outside material where a rule derives from it** — while noticing that
wholesale copying is usually the linter case wearing a citation. A style guide
belongs in a linter, not a rule. Where the fork is genuinely warranted, end the
rule with an attribution section naming the source, maintained the same way a
skill's is — see the `## Attribution` standard in `agent-skills`.

## Gotchas

- **A rule that never fires is almost always an activation problem, not a
  content problem.** Before rewriting the body, confirm the file loaded at all.
  The bisection is: set the host's always-on form temporarily, and if the rule
  starts working, the glob was the fault.
- **Cursor ignores `.md` in `.cursor/rules/`.** The extension must be `.mdc`.
  A plain markdown file there is not a broken rule, it is not a rule.
- **Cursor's `globs` must be unquoted, comma-separated, and space-free.**
  `globs: src/**/*.ts,src/**/*.tsx` works; `globs: "src/**/*.ts"` and the YAML
  list form are both reported to stop matching, and a space after the comma is
  invisible in the editor.
- **A YAML syntax error usually means the whole rule is skipped, silently** — a
  missing closing `---`, `True` instead of `true`, a tab. Cline is the exception
  and fails open, activating the rule with its raw text visible.
- **Frontmatter must start at line 1**, with no blank line and no byte-order
  mark ahead of it. A rule that behaves as though it were always-on when you
  scoped it is the usual symptom.
- **Path-scoped rules do not survive compaction on Claude Code.** The
  project-root instruction file is re-read and re-injected; a rule with `paths:`
  is not, and only comes back the next time a matching file is read. A
  long-running session can silently stop honoring a rule it honored an hour ago.
- **On Copilot, a glob-scoped instruction file reaches fewer surfaces than the
  repository-wide one.** Path-specific instructions on github.com apply to the
  coding agent and code review; do not assume every Copilot surface reads them.
- **Two rules that disagree resolve arbitrarily.** Nothing warns you. When you
  split a broad rule into narrow ones, delete the sentence you moved rather than
  leaving both copies to drift.
- **`[` starts a bracket expression in a glob.** A pattern like `docs [2026/**`
  is invalid and matches nothing; escape it as `docs \[2026/**`.
- **Never put credentials, tokens, or machine-specific paths in a rule.** Rules
  are committed and travel with the repository, and unlike a skill body they are
  loaded without anyone choosing to.

## Validation

These need nothing but a shell. Run from the rules directory:

```sh
for f in *.md; do
  head -1 "$f" | grep -q '^---$' || echo "NO FRONTMATTER  $f"
  wc -c < "$f" | awk -v f="$f" '$1 > 12000 { print "OVER 12KB      ", f }'
done
```

Then confirm each glob matches what you think it does, one pattern at a time:

```sh
git ls-files 'app/models/**/*.rb' | head
```

An empty result means the rule is dead. A result running to thousands of files
means every one of them now pays for the rule.

The rest is judgment:

- [ ] The scoping key is the one this host reads, spelled in the shape this host
      expects
- [ ] The glob matches the files the rule governs — no more, and nothing missing
- [ ] `git ls-files` on each pattern returns a plausible, non-empty set
- [ ] The rule is one topic, and the filename says which
- [ ] Body is constraints, not exposition; long-form has been moved to a skill
- [ ] Nothing here is enforceable by a linter, formatter, or type-checker
- [ ] No copied code — canonical files are referenced by path
- [ ] The rule answers a mistake that actually recurred, not one anticipated
- [ ] Nothing here contradicts the instruction file or another rule that shares
      a matching path
- [ ] Anything surprising carries its reason
- [ ] Frontmatter starts at line 1, parses, and closes
- [ ] No secrets, no machine-specific paths
- [ ] `## Attribution` present, and last, if the rule derives from outside
      material

## References

Read these as needed for the task in hand, not all three upfront.

- [FORMATS.md](references/FORMATS.md) — every host's frontmatter, locations,
  precedence, and limits; porting one rule across hosts; the `.agents/rules/`
  standardization proposal
- [SCOPING.md](references/SCOPING.md) — glob syntax, brace expansion, layering
  broad and narrow rules, and testing a pattern before you commit it
- [CONTENT.md](references/CONTENT.md) — what earns a place in a rule body and
  what does not, the recurrence test, and promoting a repeated chat prompt
- [Claude Code rules](https://code.claude.com/docs/en/claude-md) — `paths:`
  frontmatter and load order
- [Cursor rules](https://cursor.com/docs/rules) — `.mdc` frontmatter and the
  four rule types
- [Copilot custom instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
  — `applyTo:` and instruction file scope

## Attribution

- [Claude Code rules documentation](https://code.claude.com/docs/en/claude-md)
- [Cursor rules documentation](https://cursor.com/docs/rules)
- [GitHub Copilot custom instructions documentation](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)
- [Windsurf rules documentation](https://docs.devin.ai/desktop/cascade/memories)
- [Cline rules documentation](https://docs.cline.bot/customization/cline-rules)
- [agentsmd/agents.md](https://github.com/agentsmd/agents.md/issues/179) - standardized rule format proposal
