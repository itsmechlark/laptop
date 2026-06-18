---
name: git-commit
description: Conventions for writing git commits and branch names in TableCheck repos. Use whenever creating a git commit, writing or editing a commit message, or naming/creating a git branch. Covers Conventional Commits format, scope (engine/feature), subject length, body wrap, the required Jira ticket link, docs-only CI skip, and branch naming.
---

# Git commits & branch naming

**Never commit or push changes unless explicitly told to.** If a task seems to call for a commit or push but you have not been explicitly instructed to do so, ask the user first. A one-time approval applies only to that instance — it does not grant standing permission for future commits or pushes.

**Never add AI attribution to commits.** No `Co-Authored-By: Claude` trailer, no "Generated with Claude Code" line, and no other AI co-author or attribution footer — even if a default workflow suggests one.

When you are explicitly asked to commit, all commits must follow [Conventional Commits v1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) and the well-formed message conventions from [A Note About Git Commit Messages](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).

Format:
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]

https://tablecheck.atlassian.net/browse/HDR-XXXX
```

- **Types:** `feat` (new feature → MINOR), `fix` (bug fix → PATCH), plus `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test`.
- **Scope** is in parentheses and names the affected area. Use one of:
  - **An engine of the codebase** — the engine's name as found in the repo's `engines/` folder (e.g. `feat(billing): ...` for `engines/billing`). Prefer this when the change is contained to a single engine.
  - **An engineering or product feature** — the feature/domain the change belongs to (e.g. `feat(checkout): ...`, `fix(auth): ...`).
  - Match the scope to the directory/engine the change actually touches; check the `engines/` folder to find the correct name before guessing.
- **Description** is required, lowercase, imperative mood ("add", not "added"/"adds"), no trailing period; immediately after `: `. Aim for a subject line (type + scope + description) of **50 characters or fewer**, and never exceed **72** (hard limit).
- **Body** (optional) starts one blank line after the subject. Wrap it at **72 characters**. Explain **what** and **why**, not *how* (the diff already shows how). Use hyphen bullets with blank lines between them when listing multiple points. The 72-character wrap does **not** apply to the Jira ticket link line — leave it on its own line, unwrapped.
- **Breaking changes:** add `!` before the colon (`feat(api)!: ...`) and/or a `BREAKING CHANGE:` footer (uppercased) → SemVer MAJOR.
- **Footers** follow git-trailer convention one blank line after the body (e.g. `Refs: #123`, `Reviewed-by: ...`).
- **Jira ticket link (required):** end every commit message with the related Jira ticket as a plain URL (not a Markdown link), on its own line preceded by a blank line — `https://tablecheck.atlassian.net/browse/HDR-1073`. The URL is always `https://tablecheck.atlassian.net/browse/<TICKET-KEY>`. It is exempt from the 72-character body wrap. If no ticket key is known, ask the user for it rather than omitting the link.
- **Skip CI on docs-only commits.** When the commit is `docs`-only (changes nothing CI validates — no code, config, or tests), include `[skip ci]` on its own line in the body so Semaphore CI doesn't run and waste resources (`[ci skip]` is equivalent). Never add it to a commit that touches code, config, or tests.

## Branch naming

Name branches `<ticket-key>-<type>-<short-slug>`:
- `<ticket-key>` — the Jira key, kept as-is (e.g. `HDR-1089`).
- `<type>` — the Conventional Commit type the work maps to (`feat`, `fix`, `chore`, …), lowercase.
- `<short-slug>` — a few lowercase, hyphen-separated words describing the change.

Example: `HDR-1089-feat-turnover-aware-matrix`. Branch from the app's default branch (see CLAUDE.md §4, App & codebase locations). If no ticket key is known, ask the user rather than guessing.
