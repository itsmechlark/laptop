# Checks

Four read-only checks, each run from the repository root. They list files with
`git ls-files` rather than walking the tree: git reports a symlink without
following it, so vendored skill bundles reached through `skills/<name>` or
`.claude/skills` stay out, and `node_modules`, `vendor/bundle`, and worktrees
under `.claude/worktrees/` are never listed. `-co --exclude-standard` includes
a new file that is not committed yet. A skill bundle's own `AGENTS.md` is not an
instruction file for the repository, so every listing excludes `skills/`
directories. A repository that ships an `AGENTS.md` as cargo, such as a global
standards file installed onto other machines, still shows up; judge that file
by where it is installed, not by its place in this tree.

None of them invokes a build tool. A check that ran `make` or `mix` to prove a
target exists would execute the repository's code, and in a review that code
comes from the change under review.

## Budget

Each chain is every `AGENTS.md` Codex loads when launched in that file's
directory: the root's, each ancestor's, and its own. The global
`~/.codex/AGENTS.md` loads separately and is not counted. Claude Code's limit is
per file, in characters, so that column is the file alone.

```sh
cd "$(git rev-parse --show-toplevel)" || exit 1
cap=$(sed -n 's/^project_doc_max_bytes *= *\([0-9][0-9]*\).*/\1/p' ~/.codex/config.toml 2>/dev/null)
echo "codex cap: ${cap:-32768 (default; ~/.codex/config.toml unset or unreadable)}"
cap=${cap:-32768}
git ls-files -co --exclude-standard -- ':(glob)**/AGENTS.md' ':(exclude,glob)**/skills/**' |
while read -r f; do
  total=0; p=$(dirname "$f")
  while :; do
    [ -f "$p/AGENTS.md" ] && total=$((total + $(wc -c < "$p/AGENTS.md")))
    [ "$p" = . ] && break; p=$(dirname "$p")
  done
  chars=$(wc -m < "$f"); flag=
  [ "$total" -gt "$cap" ] && flag=" [over codex cap]"
  [ "$chars" -gt 40000 ] && flag="$flag [over claude 40k chars]"
  printf '%6d chain  %6d chars  %4d lines  %s%s\n' "$total" "$chars" "$(wc -l < "$f")" "$f" "$flag"
done | sort -rn
```

A sandbox may refuse to read `~/.codex/`; the first line then says the default
is assumed. Ask the developer for the configured cap rather than reporting
against 32 KiB when the machine may have raised it.

## Paths

From the directory of the file being checked. Each backticked token holding a
`/` must exist relative to that directory or to the repository root.
Placeholders, globs, package scopes, URLs, shebangs, elided paths, and `~`
paths are skipped.

```sh
top=$(git rev-parse --show-toplevel)
grep -oE '`[^` ]+/[^` ]*`' AGENTS.md | tr -d '`' | grep -v '[<*{$@:~#…]' | sort -u |
  while read -r p; do [ -e "$p" ] || [ -e "$top/$p" ] || echo "missing: $p"; done
```

Read each hit before acting on it. False positives: an import specifier
written without its extension (`src/api/errors` for `src/api/errors.ts`), an
`owner/repo` slug, a git-ignored path absent from this checkout, and a
directory the file names conditionally ("where the repository keeps `lore/`").

## Commands

Every command in a `## Commands` table names something that exists. Check by
reading the definition, never by running the tool:

| Tool | Exists when |
| --- | --- |
| npm, pnpm, Yarn, Bun | `jq -r '.scripts \| keys[]' <workspace>/package.json` lists it |
| Turborepo | the task is a key under `tasks` (or `pipeline`) in `turbo.json` |
| Make | `grep -qE '^<target>:' Makefile` |
| Just | `grep -qE '^<recipe>( [^:]*)?:' justfile` |
| Rake | `grep -rqE "task[ (]+:?['\"]?<name>" Rakefile lib/tasks` |
| Mix | an `aliases` entry in `mix.exs`, or `lib/mix/tasks/<name>.ex`, or a task the stack ships (`mix test`) |
| `bin/` script | the file exists and is executable |

A wrapper the repository insists on (`bin/rspec`, a `test` script with required
flags, a Turbo task that builds dependencies first) is the command to record,
not the tool it wraps.

## CLAUDE.md links

Every `AGENTS.md` has a `CLAUDE.md` beside it, and that `CLAUDE.md` is a symlink
whose target is exactly `AGENTS.md`. A tracked `CLAUDE.md` that is a real file
is a copy that will drift.

```sh
cd "$(git rev-parse --show-toplevel)" || exit 1
git ls-files -co --exclude-standard -- ':(glob)**/AGENTS.md' ':(exclude,glob)**/skills/**' |
while read -r f; do
  c="$(dirname "$f")/CLAUDE.md"
  [ -L "$c" ] && [ "$(readlink "$c")" = AGENTS.md ] || echo "not a link to AGENTS.md: $c"
done
git ls-files -s -- ':(glob)**/CLAUDE.md' ':(exclude,glob)**/skills/**' |
  awk '$1 != "120000" { print "real file, not a link: " $4 }'
```

Both print nothing when the layout is right.
