---
name: local-overlay-for-internal-skills-and-rules
description: Why internal (non-public) skills and rules live in a machine-local, git-ignored overlay linked into the public payload, not in skills-lock.json or a separate directory.
metadata:
  status: accepted
  topic: skills
---

# A machine-local overlay for internal skills and rules

**Context:** Some skills and rules are specific to private codebases — for
example `tablekit-css` and `tablekit-react`, exported from
`@tablecheck/tablekit-*` npm packages via `tablekit-config skills install`.
The `laptop` repo is public. Vendoring private content here would publish it;
a separate `~/.agents/local-skills` directory would require every client to
read a second directory, which none of them do. The need is to make internal
skills discoverable globally without shipping their content.

**Decision:** `.agents/local/skills/<name>/` and `.agents/local/rules/<name>.md`
are the overlay store. The top-level `.agents/local/` is excluded in `.gitignore`
with a single entry that reveals no internal names. `mac` links each overlay
entry into `skills/` or `rules/` (relative target `../.agents/local/...`, the
same form vendored skills use), then registers the linked name in
`.git/info/exclude` so git never tracks it. Links are idempotent: a second `mac`
run changes nothing. Dangling links — from a removed overlay entry — are pruned
on the next run rather than left as broken symlinks. Every client discovers the
overlay through the existing `~/.agents/skills` symlink; no client-policy change
is needed.

`scripts/check-payload` identifies overlay links by their `readlink` target
(`../.agents/local/...`) and skips them in every linting loop: frontmatter,
size, resource links, anchor resolution, orphan references, invocability, citation,
provenance/attribution, rules frontmatter, glob coverage, and Cursor sync. The
dangling-symlink check also skips them, since CI runs without the overlay and
`mac` prunes stranded links on-machine. A self-test in `check-payload` verifies
the detection pattern fires correctly before any of those loops run.

**Consequences:** Internal skills and rules are available globally on any machine
that has exported them into `.agents/local/` and re-run `mac`. They do not appear
in CI, in the repo, or in the published `skills-lock.json`. Overlay content is
unversioned relative to the repo — it is pinned to whatever package version the
operator last exported from. Projects that vendor their own copy (e.g.
`portal-frontend/.claude/skills/`) take precedence because the project scope wins
over the user scope in Claude Code's resolution order.

The operator populates the overlay once per machine, typically with:

```sh
cd ~/Codespace/portal-frontend
npx tablekit-config skills install tablekit-css tablekit-react \
  --dir ~/Codespace/laptop/.agents/local/skills
sh ~/Codespace/laptop/mac
```

Refresh with `skills update --dir ...` and re-run `mac`. Worktrees do not inherit
overlay links — the exclude entry is per-clone, not per-worktree, and `mac` links
into `skills/` in the main checkout — so a worktree created after the overlay was
added sees it; one created before may not until `mac` is run again.

**Rejected:**
- Vendoring into `skills-lock.json`: that file is tracked and published; any
  content it references would ship.
- A separate `~/.agents/local-skills` dir: no client reads a second skills
  directory, and adding one would require editing every client's config (parity
  invariant, see ADR 0002).
- Per-project `.claude/skills/` only: correct for package-versioned content but
  not for internal skills that are company-wide rather than package-bound.

**Extends:** [ADR 0020](0020-local-overlay-for-the-project-glossary.md) (git-ignored
local overlays, `.git/info/exclude` rather than `.gitignore` for per-reader
exclusions). This ADR uses `.gitignore` for the store root (`.agents/local`)
rather than `info/exclude`, because the store root is stable and universal — every
checkout should ignore it — while individual linked names in `skills/` and `rules/`
are per-machine and use `info/exclude`.
