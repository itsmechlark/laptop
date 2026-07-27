---
name: git-commit
description: Conventions for writing git commits and branch names. Use whenever creating a git commit, writing or editing a commit message, or naming/creating a git branch. Covers Conventional Commits format, scope, subject length, body wrap, optional issue references, docs-only CI skip, and branch naming.
---

# Git commits & branch naming

**Never commit or push changes unless explicitly told to.** If a task seems to call for a commit or push but you have not been explicitly instructed to do so, ask first. A one-time approval applies only to that instance — it does not grant standing permission for future commits or pushes.

**Never add AI attribution to commits.** No AI `Co-Authored-By` trailer, no "Generated with …" line, and no other AI co-author or attribution footer — even if a default workflow suggests one.

When you are explicitly asked to commit, follow [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) and the well-formed message conventions from [A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html). Match whatever convention the repository's existing history already uses.

Format:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

- **Types:** `feat` (new feature → MINOR), `fix` (bug fix → PATCH), plus `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test`.
- **Scope** (optional) is in parentheses and names the affected area — a component, package, module, or feature/domain the change touches (e.g. `feat(auth): …`, `fix(parser): …`). Match it to the part of the codebase actually changed; check the repo's existing history for the naming convention it uses, and omit the scope if the project doesn't use one.
- **Description** is required, lowercase, imperative mood ("add", not "added"/"adds"), no trailing period; immediately after `: `. Aim for a subject line (type + scope + description) of **50 characters or fewer**, and never exceed **72** (hard limit).
- **Body** (optional) starts one blank line after the subject. Wrap it at **72 characters**. Explain **what** and **why**, not *how* (the diff already shows how). Use hyphen bullets with blank lines between them when listing multiple points. The wrap does not apply to footer lines such as URLs.
- **Breaking changes:** add `!` before the colon (`feat(api)!: …`) and/or a `BREAKING CHANGE:` footer (uppercased) → SemVer MAJOR.
- **Footers** follow git-trailer convention, one blank line after the body (e.g. `Refs: #123`, `Reviewed-by: …`).
- **Issue reference (only if the project uses one):** if the work maps to a tracked issue, reference it the way the repository already does — a git trailer (`Refs: #123`) or a plain issue URL on its own line after a blank line. Don't fabricate a reference if the project doesn't track issues, and don't leave a placeholder; if the project's convention requires a key you don't have, ask for it rather than guessing.
- **Skip CI on docs-only commits.** When a commit is `docs`-only (changes nothing CI validates — no code, config, or tests) and the project's CI honors it, include `[skip ci]` (or the equivalent `[ci skip]`) on its own line in the body. Never add it to a commit that touches code, config, or tests.

## Branch naming

Name branches `<type>-<short-slug>`, optionally prefixed with an issue key when the project tracks work in an issue tracker: `[<issue-key>-]<type>-<short-slug>`.

- `<issue-key>` — the tracker key, kept as-is (e.g. `ABC-1234`), when applicable.
- `<type>` — the Conventional Commit type the work maps to (`feat`, `fix`, `chore`, …), lowercase.
- `<short-slug>` — a few lowercase, hyphen-separated words describing the change.

Examples: `feat-getting-started`, `ABC-1234-fix-null-check`. Branch from the repository's default branch unless told otherwise.
