# Scoping a rule

The glob decides whether a rule ever runs and what it costs when it does. This is
the part to spend time on.

## Pattern syntax

Hosts differ on frontmatter but agree on glob semantics. Read `*` as "within one
directory" and `**` as "at any depth":

| Pattern | Matches | Does not match |
| --- | --- | --- |
| `*.md` | `README.md` | `docs/guide.md` |
| `**/*.md` | `README.md`, `docs/guide.md` | — |
| `src/*.py` | `src/foo.py` | `src/foo/bar.py` |
| `src/**/*.py` | `src/foo.py`, `src/a/b/c.py` | `lib/foo.py` |
| `src/**/*` | Everything under `src/` | Files outside `src/` |
| `**/spec/**/*.rb` | A `spec/` directory at any depth | `app/models/user.rb` |
| `**/db/migrate/**` | Any migrations directory | `db/schema.rb` |

**Anchor with `**/` unless the rule is genuinely root-only.** `Gemfile` matches
the root Gemfile; `**/Gemfile` matches every Gemfile in a monorepo. Testing from
the repository root hides this difference — the pattern works on the file you
tried and fails one directory deeper.

**A directory pattern needs a file part.** `src/**` matches files under `src/`;
`src/**/*.ts` matches only the TypeScript ones. Reach for the second unless the
rule really governs every file type in there.

## Brace expansion

`src/**/*.{ts,tsx}` is shorthand for two patterns. Support and limits vary:

- Groups **multiply**. `{a,b}/{c,d}/*.{ts,tsx}` is eight patterns, not three.
- Claude Code budgets a rule's whole `paths` list at 1,000 expanded patterns and
  4 MiB. Over budget, the pattern is used *unexpanded* — its literal braces then
  match no file, so the rule quietly covers nothing.
- Windsurf has been reported not to combine extensions with braces at all.

When a brace group grows past two or three alternatives, write the patterns out.
The expansion is a convenience, not a feature to lean on.

## The bracket trap

`[` opens a bracket expression such as `[abc]`. A pattern containing a `[` that
cannot be read as one — `photos [2026/**` — is invalid and matches nothing.
Escape it: `photos \[2026/**`. Other patterns in the same rule keep working, so
the symptom is a rule that fires on some of its files and not others.

## Scope to what the rule governs

The question is not "what language is this?" but **"which files would be wrong if
this rule were ignored?"**

| Rule | Wrong glob | Right glob | Why |
| --- | --- | --- | --- |
| Migrations must be reversible | `**/*.rb` | `**/db/migrate/**/*.rb` | Every Ruby file paid for a rule about twelve of them |
| Components take no side effects | `**/*.tsx` | `**/components/**/*.tsx` | Pages and layouts are `.tsx` too, and the rule is false for them |
| Test names describe behavior | `**/*.rb` | `**/*_spec.rb`, `**/spec/**/*.rb` | The rule is about specs, not about Ruby |
| Dependency pinning policy | `**/*` | `**/Gemfile`, `**/*.gemspec`, `**/package.json` | Manifest files are nameable; enumerate them |

An over-broad glob is not a harmless approximation. It puts text about
migrations in front of an agent editing a serializer, every time, and the cost is
paid by everyone on the repository forever.

## Layering broad and narrow

Hosts concatenate **every** rule whose glob matches. That makes layering the
intended shape, not a workaround:

```
rules/rails.md          paths: **/app/**/*.rb, **/config/**/*.rb
rules/rails-model.md    paths: **/app/models/**/*.rb
rules/rails-migration.md paths: **/db/**/*.rb
```

Editing `app/models/booking.rb` loads the first two. Editing
`db/migrate/20260101_add_index.rb` loads the third alone. Each file stays about
one thing.

Two consequences worth planning for:

- **Do not restate the broad rule in the narrow one.** Both load; the duplicate
  only creates a second copy to drift out of sync, and two rules that disagree
  resolve arbitrarily with no warning.
- **A file matched by four rules pays for four.** Layering is cheap only when
  each layer is short. If the stack for one file type runs past a screen or two,
  merge or cut rather than adding another layer.

## Test a pattern before committing it

Nothing in any host tells you a glob matched nothing. Check it yourself:

```sh
git ls-files 'app/models/**/*.rb' | head
git ls-files 'app/models/**/*.rb' | wc -l
```

Read both numbers:

- **Zero** — the rule is dead. Usually a missing `**/` prefix, a directory that
  does not exist under that name, or a brace group that did not expand.
- **In the thousands** — every one of those files now carries this rule. Either
  narrow it, or confirm the rule is genuinely true of all of them.

`git ls-files` uses git's own pathspec matching rather than the host's, so treat
it as a sanity check on breadth, not as proof of activation. For that, load the
host and confirm: Cursor lists active rules in Settings → Rules, and Claude
Code's `InstructionsLoaded` hook logs which files loaded and why.

## Deciding a rule is not a rule

Two shapes mean the content belongs elsewhere:

- **The glob wants to be `**/*`.** The content is true of the whole repository —
  put it in the instruction file, where it loads reliably and where a reader
  expects to find it.
- **You cannot name a glob at all**, only an occasion ("when we cut a release",
  "before opening a PR"). That is a skill.

A rule scoped to everything is the worst of both: it costs what an instruction
file costs, and on Claude Code it disappears after compaction while the
instruction file does not.
