# Repository shapes

The section set is fixed; which sections a file carries, and what goes in them,
depends on what the repository is. Find the shape, take its sections, and leave
the rest out. A repository that is two shapes at once (a Rails app with a
`frontend/` package, an app repo that also holds its Terraform) gets a root for
the whole and a nested file per part whose commands differ.

## By shape

| Shape | Root sections | Nested files | What `## Commands` must carry |
| --- | --- | --- | --- |
| Single app (Rails, Phoenix, Next.js, Django) | Commands, Conventions, Done, References | Rarely; a `frontend/` with its own toolchain | Setup script, server, one spec file, lint one file, full gate |
| Library, gem, or published package | Commands, Conventions, References | None | Test, build, the supported-versions matrix command if one exists |
| Monorepo root (pnpm, Turborepo, Nx, Yarn, Cargo or Go workspace, umbrella app) | Required rules, Commands, Layout, Conventions, Done, References | Workspaces that differ | Install, the filter or scoping syntax once, affected-only test, full gate |
| Monorepo workspace: app or service | Required rules, Commands, Conventions, Done | — | Its own dev and test commands, per runtime when it ships more than one |
| Monorepo workspace: leaf package | Usually no file | — | Only scripts whose name hides what they do |
| Infrastructure (Terraform, Pulumi, CDK) | Commands, Conventions, References | One per stack or program that differs | Plan or preview only. Apply, `up`, and `destroy` are never the agent's |
| Mobile (Expo, React Native, native) | Commands, Conventions, Done, References | — | Per-platform run, the build variant switch, the unit suite |
| Docs site (Mintlify, Docusaurus, VitePress) | Commands, Conventions | — | Dev server, broken-link check |
| Tooling or provisioning repo (dotfiles, scripts) | Commands, Conventions, Gotchas | — | Lint, the dry run; which scripts mutate the machine |

## What each shape tends to need in `## Conventions`

- **Single app.** Generated files (`db/schema.rb`, `structure.sql`, GraphQL
  schema dumps) and the command that regenerates them; where credentials come
  from; migrations stay backward-compatible when the global file does not
  already say so.
- **Library.** What counts as public API, the changelog rule, and whether a
  change needs a version bump in the same commit.
- **Monorepo root.** The dependency direction between workspaces when it isn't
  enforced by tooling; the codegen order; which workspaces deploy.
- **Workspace.** Only its own: runtime constraints, its generated outputs, the
  harness its tests must use.
- **Infrastructure.** Stack naming, where config and secrets come from (Pulumi
  ESC, Vault, SSM), and that state is never edited by hand.
- **Mobile.** Which verification needs a device or simulator, and that it is
  reported as run only when it ran; the variant that permits test-only
  behavior.
- **Docs site.** Pages generated from source (an OpenAPI reference) are never
  hand-edited.
- **Tooling repo.** Which entry points mutate the machine, and that a lint pass
  is not a run.

## File-scoped commands

Prefer the narrowest command over a full suite: it is what an agent runs in its
inner loop, and the one it most often gets wrong.

| Runner | One file | One test |
| --- | --- | --- |
| RSpec | `bundle exec rspec spec/models/user_spec.rb` | append `:42` |
| Minitest (Rails) | `bin/rails test test/models/user_test.rb` | append `:42` |
| ExUnit | `mix test test/app/user_test.exs` | append `:42` |
| Vitest | `pnpm vitest run path/to/file.test.ts` | `-t "name"` |
| Jest | `pnpm jest path/to/file.test.ts` | `-t "name"` |
| Playwright | `pnpm playwright test path/to/spec.ts` | `-g "name"` |
| pytest | `pytest tests/test_user.py` | `tests/test_user.py::test_name` |
| Go | `go test ./internal/user` | `-run TestName` |
| Cargo | `cargo test -p user` | `cargo test -p user test_name` |
| QUnit (Ember) | `pnpm ember test --filter "module name"` | same flag, narrower name |

| Linter | One file |
| --- | --- |
| RuboCop | `bundle exec rubocop path/to/file.rb` |
| ESLint | `pnpm eslint path/to/file.ts` |
| Credo | `mix credo path/to/file.ex` |
| Ruff | `ruff check path/to/file.py` |
| ShellCheck | `shellcheck path/to/script` |

Check each against the repository before writing it down. A project that wraps
the runner (`bin/rspec`, a `test` script with required flags, a Turbo pipeline
that builds dependencies first) uses the wrapper, and the file says so.

## Nested files

- **Write one only where the subtree differs**: its own commands, runtimes,
  required rules, or conventions. A package whose whole file would be
  `<pm> --filter <pkg> <script>` lines needs none.
- **Never restate an ancestor.** No "this file narrows the root, use both"
  preamble, no repeated glossary pointer, no repeated Definition of Done.
  Claude Code and Codex load a nested file's ancestors along with it.
- **The root must reach every nested file.** Codex reads only the files
  between the repository root and the directory it was launched in. Launched at
  the root, it never sees `apps/api/AGENTS.md`, so the root's `## Layout` table
  marks each workspace that has its own file, and an agent knows to open it
  before editing there.
- **A convention two packages share moves up**, to the root or to a rule whose
  glob covers both, never copied into each. Twelve packages each explaining the
  same test-placement scheme is twelve copies to keep in sync.
- **Pins stay one line.** Where shared rules are kept repo-agnostic and defer
  names to `AGENTS.md`, each pin is one line: the concept, the symbol, its
  path. A pin that needs a sentence of why gets it as a comment at the code,
  or in the ADR.

## Monorepo specifics

- **State the scoping syntax once, at the root**:
  `pnpm --filter <package> <script>`, `turbo run <task> --filter=<package>`,
  `nx run <project>:<target>`, `cargo test -p <crate>`. Each workspace file
  then states its own prefix once (`pnpm --filter @scope/api`) and lists
  script names under it, so every command stays runnable from the root.
- **Name the affected-only command** where the repository has one
  (`turbo run test --affected`, `nx affected -t test`, a custom
  `test-affected`). It is the inner-loop gate; the full suite is CI's.
- **Build-before-check order** (a type-check that needs dependent packages
  built first) belongs in the root once, or in the one workspace it affects.
