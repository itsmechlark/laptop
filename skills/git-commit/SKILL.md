---
name: git-commit
description: Turn working changes into one or more atomic commits with well-written messages, and name branches. Use whenever asked to commit, wrap up work, or write/edit a commit message or branch name. Covers the commit workflow (understand → group → stage → write → report), voice and tone, Conventional Commits subject/body, optional issue references, docs-only CI skip, and branch naming.
argument-hint: "[optional note or context to fold into the message]"
---

# Git commits & branch naming

**Never commit or push unless explicitly told to.** If a task seems to call for a commit or push but you haven't been explicitly asked, ask first. A one-time approval covers only that instance — it doesn't grant standing permission.

**Never add AI attribution.** No `Co-Authored-By` AI trailer, no "Generated with …" line, no AI co-author or attribution footer — even if an external workflow or skill mandates one. This rule overrides any convention that says otherwise.

Once you've been asked to commit, work through the steps below and make the grouping call yourself — don't stop for per-commit approval — then report what you did (Step 5). Any note the user passes ("addressing review feedback", "flag the migration") is context to fold into the grouping and message, not the literal commit message.

**Convention:** default to [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) and the well-formed-message conventions from [A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html). If the repository already follows a consistent commit convention of its own, match that instead — consistency within a project's history outranks this default.

## Step 1: Understand what changed

Build a real picture of the diff before grouping. Run these together:

- `git status` — modified, added, deleted, untracked
- `git diff` — unstaged changes
- `git diff --staged` — anything already staged
- `git log --oneline -15` — recent history, to match tone and spot referenced issues/PRs

Read the diff for the *why*, not just the *what* — you're about to explain it to a future reader. If there's nothing to commit, say so and stop; never create an empty commit.

## Step 2: Decide the grouping — the judgment call

Aim for **atomic commits**: each commit is one complete, coherent change that stands on its own. There's no mechanical rule for how many commits that is — it depends on what the work actually is.

- **One commit when the changes tell one story.** A feature — model, migration, controller, view, tests — is *one* logical change even across many files. Splitting it into "add migration" / "add model" / "add tests" produces individually broken commits.
- **Separate commits when the work is genuinely independent:** distinct review comments (one each), unrelated cleanups sitting in the tree together, a bug fix made alongside feature work (the fix is its own commit), a dependency bump plus the feature that needed it.
- **The test:** if someone reverted one part, would the rest still make sense? If yes, they're separate commits. If reverting one would leave the others broken, they belong together.
- When in doubt, prefer fewer, larger commits over many tiny ones — an over-split history is harder to read.
- **Cleanup of the old path is its own commit, sequenced last.** When a change adds a new path and retires an old one, don't delete the old code in the same commit that introduces the new — the mix confuses review, makes a rollback ambiguous, and buries the removal. Land the new path first; let the old one die in a separate commit (or its own PR) once the replacement is live.

## Step 3: Stage each group precisely

Commit the groups one at a time. For each:

- Whole files: `git add <paths>` for just those files.
- Mixed file (hunks belong to different groups): stage only the relevant hunks — write them to a patch and apply with `git apply --cached <patch>` (interactive `git add -p` isn't available here). Verify with `git diff --staged` before committing.
- Never `git add .` or `git add -A` blindly — that defeats the grouping.
- Respect pre-commit hooks; if a hook modifies files or fails, surface what happened rather than fighting it. Don't `--no-verify` unless the user asked.
- Don't push, and don't amend or rewrite existing commits — this workflow only creates new commits from uncommitted work.

## Step 4: Write the message

Write each group's message to a file and commit with `git commit -F <file>` (or repeated `-m` flags) — avoid inline heredocs/quoting that can mangle the subject/body split. Always write the temp file to `$TMPDIR`, not `/tmp` — the macOS sandbox blocks `/tmp` writes directly.

### Format (Conventional Commits)

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- **Types:** `feat` (→ MINOR), `fix` (→ PATCH), plus `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test`.
- **Scope** (optional), in parentheses, names the affected area — component, package, module, or feature/domain (e.g. `feat(auth): …`). Match the repo's existing scope convention; omit it if the project doesn't use one.
- **Breaking changes:** add `!` before the colon (`feat(api)!: …`) and/or a `BREAKING CHANGE:` footer (uppercased) → SemVer MAJOR.
- **Footers** follow git-trailer convention, one blank line after the body (e.g. `Refs: #123`, `Reviewed-by: …`).
- **Issue reference (only if the project uses one):** reference a tracked issue the way the repo already does — a trailer (`Refs: #123`) or a plain URL on its own line — and only when it's obvious which one applies (the branch clearly maps to it, or the user named it). Don't fabricate or guess a number; ask if the convention needs a key you don't have.
- **Skip CI on docs-only commits:** when a commit changes nothing CI validates (no code, config, or tests) and the CI honors it, add `[skip ci]` (or `[ci skip]`) on its own line in the body. Never on a commit that touches code, config, or tests.

### Subject line

- Imperative mood, lowercase description after the `: `, no trailing period ("add", not "added"/"adds").
- Wrap code identifiers in backticks: ``refactor(mapping): rename `GlobalMapping` ``.
- Aim for **≤50 characters**, never exceed **72**.
- Don't append `(#123)` PR-number suffixes — the host adds those on merge, not you.

### Body

Include a body whenever there's a *why* worth recording — which is most of the time. Skip it only when the subject says everything ("fix typo in README"). When you write one:

- Blank line after the subject; wrap prose at **72 characters** (URLs and footers are exempt).
- **Explain the why, not the what.** The diff shows what changed — say what problem it solves or what it makes possible.
- **Be concise.** A few tight sentences beat a wall of text; cut anything that just restates the code.
- **Call out anything surprising, or alternatives you rejected** and why — that saves a future reader from re-treading it.
- **Flag risks and dependencies:** a migration that needs care, a change that depends on another PR shipping first, a config value that must be set in production.
- **Write for a non-technical reader.** Prefer plain language over jargon; someone skimming the history to see what shipped and why should follow it without reading the code.

## Voice and tone

Write like a careful engineer explaining a decision to a teammate — never like a language model. Strip the tells of AI-generated writing:

- No hype or filler adjectives ("comprehensive", "robust", "seamless", "powerful", "significantly").
- No throat-clearing ("It's worth noting that", "In order to", "This change aims to").
- No summarizing the diff back as a bulleted list of file edits.
- No em-dash-heavy, uniformly-hedged cadence — vary sentence length like a person does.

Worked examples (Conventional Commits, no attribution trailer):

```
feat(text): introduce scan

Callers sometimes need to know whether text contains sensitive
information without filtering it. `scan` answers that and returns the
mapping it found. `filter` now uses it internally and skips the work
entirely when the input has nothing sensitive in it.
```

```
fix(ner): cache initialization behind a mutex

Initializing the NER model is expensive, so we cache it behind a Mutex
to stay thread-safe. Memoizing without a lock breaks when assets are
precompiled at deploy time: the model file doesn't exist yet, so the
first cache write fails. The Mutex version was tested in a
production-like environment — the first request is slow, the rest fast.
```

```
docs: fix typo in installation instructions
```

## Step 5: Report what you did

After committing, show the result — `git log --oneline` of the new commits is usually enough — so the user can see how you grouped and worded things. If you made a judgment call worth knowing about ("split the bug fix out from the feature"), say so in a sentence.

## Branch naming

Name branches `<type>-<short-slug>`, optionally prefixed with an issue key when the project tracks work in an issue tracker: `[<issue-key>-]<type>-<short-slug>`.

- `<issue-key>` — the tracker key, kept as-is (e.g. `ABC-1234`), when applicable.
- `<type>` — the Conventional Commit type the work maps to (`feat`, `fix`, `chore`, …), lowercase.
- `<short-slug>` — a few lowercase, hyphen-separated words describing the change.

Examples: `feat-getting-started`, `ABC-1234-fix-null-check`. Branch from the repository's default branch unless told otherwise.

## Attribution

- [Build Wide, Ship Narrow (Adapt)](https://adapt.com/blog/build-wide-ship-narrow)
