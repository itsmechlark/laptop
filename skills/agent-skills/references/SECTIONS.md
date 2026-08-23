# Writing the body sections

The body loads only after the skill activates, so it can afford detail the
description can't. Each section below is optional — include it when the skill
has something to put there, and cut it otherwise. An empty heading is worse than
a missing one.

## `# Title`

One sentence stating what the skill enables, specific to the domain. Avoid
restating the name.

```markdown
# Webapp testing

Drive a real browser against a local web application to verify behavior,
capture screenshots, and read console output.
```

## `## When to use this skill`

A bullet list of concrete scenarios. This restates the description's triggers in
the agent's own reading order and lets it confirm it loaded the right skill —
and, just as usefully, notice that it didn't.

```markdown
## When to use this skill

- User asks to test a web application in a browser
- User needs screenshots for visual regression comparison
- User wants frontend behavior debugged from console logs
```

State the exclusions too when a neighboring skill could plausibly claim the
task, described by scope rather than by name: "Not for unit-testing pure
functions." Naming the neighbor assumes it's installed alongside this one — ask
the user before writing one in.

## `## Prerequisites`

Only for tools, services, or configuration the agent cannot assume are present.
Give exact install commands, not names of things to install.

```markdown
## Prerequisites

- [Playwright](https://playwright.dev/) — `npm install -D @playwright/test`
- At least one browser engine — `npx playwright install chromium`
```

If there are no external dependencies, drop the section entirely.

## `## Workflows`

Numbered steps for repeatable procedures where sequence genuinely matters:
build, deploy, environment setup, release. Describe **what to accomplish** at
each stage rather than hardcoding file paths or line numbers, so the steps
survive a refactor and adapt across project layouts.

```markdown
## Workflows

### Deploy to staging

1. Build the project: `npm run build`
2. Run pre-deploy validation: `npm run validate`
3. Deploy: `npm run deploy -- --env staging`
4. Verify the health endpoint returns 200
```

Past roughly five steps, move the workflow into `references/` and link to it
from a short stub here. For multi-stage work, a checklist of steps that each
point at their own reference section keeps the thread recoverable if the run is
interrupted:

```markdown
- [ ] Configure environment — [SETUP.md](references/SETUP.md#environment)
- [ ] Build — [SETUP.md](references/SETUP.md#build)
- [ ] Deploy to staging — [DEPLOY.md](references/DEPLOY.md#staging)
- [ ] Run validation — [DEPLOY.md](references/DEPLOY.md#validation)
- [ ] Promote to production — [DEPLOY.md](references/DEPLOY.md#production)
```

For open-ended work — debugging, refactoring, review — give decision criteria
instead. Numbered steps imply a sequence that doesn't exist, and the agent
follows them off a cliff. Steps pinned to file paths and line numbers fail the
same way, one refactor later:

```markdown
# Too rigid — breaks the moment the file moves
1. Open src/api/handlers.ts
2. Find processOrder
3. Add a try-catch around lines 45-60

# Flexible — survives refactors
When fixing error handling in API handlers:
- Every database operation needs an error path
- Use the project's ErrorHandler utility (references/ERRORS.md)
- Log with enough context to debug in production
```

## `## Gotchas`

The highest-value section in most skills: proactive warnings that prevent a
mistake before it happens, as distinct from `## Troubleshooting`, which cleans
up afterwards. Bold the constraint, then give the reason — a rule without a
reason gets rationalized away the first time it's inconvenient.

```markdown
## Gotchas

- **Never** call `billing.charge()` without checking `user.hasPaymentMethod`
  first — the SDK throws an unrecoverable error instead of returning a failure.
- The `currency` field expects ISO 4217 codes, not display names. Agents
  routinely write "dollars" where the API needs "USD".
```

Treat it as a living section. Every time an agent gets something wrong with this
skill loaded, that's a missing gotcha — add it rather than re-explaining in the
next session.

Good sources of gotchas: non-obvious defaults, arguments whose absence changes
behavior silently, version-specific quirks, operations that look idempotent and
aren't, and anything where the intuitive call is the wrong one.

## `## Troubleshooting`

Reactive fixes for known failures, as a symptom → solution table. Keep each row
self-contained and actionable; a row that says "check your configuration" is
noise.

```markdown
## Troubleshooting

| Issue | Solution |
| --- | --- |
| Plugin won't connect | Confirm both servers are up: `npm run start:all` |
| Browser blocks localhost | Allow local network access, or try another browser |
| Tool execution times out | Ensure the plugin UI is open and reads "Connected" |
```

## `## References`

Links to bundled files, external documentation, and related skills. Use relative
paths for bundled files, and say when to read them — otherwise the agent either
ignores the list or reads all of it.

```markdown
## References

- [API.md](references/API.md) — complete signatures and return types
- [ERRORS.md](references/ERRORS.md) — every error code this service returns

Read these as needed for the current task. Do not read them all upfront.
```

<a id="attribution"></a>

## `## Attribution`

The last section in the file, present only when the skill derives from outside
material. It is a flat Markdown bullet list with one bullet per source, in the
same order as the `sources` array in the machine-readable provenance record.
Do not add subsections or relationship labels — provenance records whether a
source is adapted, a specification, or inspiration.

Use the source's kind to choose the plain form:

- Repository: `[mattpocock/skills](https://github.com/mattpocock/skills/tree/main/skills/engineering/domain-modeling) - domain-modeling, MIT`
- URL: `[Agent Skills specification](https://agentskills.io/specification)`
- Book or other literature: `Martin Fowler, *Refactoring* (2nd ed.), ch. 3 — code smells`

For a repository, link to the repository and source path, then give the source
name and license; omit the path or license when it is not recorded. For a URL,
link the source title directly. For literature, use a readable citation and an
optional concise note. Exclude machine metadata such as commit refs, review
dates, and pinned versions; those belong in the provenance record. Keep the
section a 1:1 human projection of that record: nothing here that is not
recorded there, and no recorded source omitted. A skill with no outside lineage
has no `## Attribution` section at all — never an empty one.

## Style

- **Imperative mood.** "Run the migration", not "You should run the migration."
- **Exact commands**, with the flags that matter, in fenced blocks.
- **Show expected output** where the agent needs to recognize success or failure.
- **Tables for lookup material**, prose for reasoning. Don't bury a parameter
  list in a paragraph.
- **No filler.** Cut anything the model already knows; every line should change
  behavior.
