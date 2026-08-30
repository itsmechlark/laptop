# Global Engineering Standards

These standards apply to all repositories and workspaces unless a project-local `AGENTS.md` overrides them.

## Non-negotiables

Read these first; the rest of this document elaborates. None may be violated without explicit, in-the-moment user approval.

- **Never commit or push unless explicitly told** — ask first (see the `git-commit` skill).
- **Never add AI attribution** to commits or PRs (see the `git-commit` skill).
- **Never hardcode or log secrets, credentials, or PII**; treat all external input as untrusted (§2, §6).
- **No silent failures** — never swallow an exception or rejected promise (§6).
- **Don't claim work is done until verified** — tests, lint, and type-checks pass (§4).
- **Gate risky/behavioral change behind a default-off flag, and keep DB migrations backward-compatible** (§5).

## Standards layout

This file holds cross-cutting, always-on standards. Stack-specific standards and task workflows live beside it and load when relevant — apply them without being reminded:

- **Machine & fleet context** → `~/.agents/CONTEXT.md` — when present, read it at the start of every session; it maps this machine and its repos (locations, deployment URLs, shared vocabulary). Per-repo domain glossaries live in each repo's own `CONTEXT.md` (the `domain-modeling` skill), not here.
- **Language / framework standards** → `~/.agents/rules/` (auto-load when a matching file is opened): `testing.md` (framework-agnostic test discipline) and `test-levels.md` (unit vs integration vs end to end), `ruby.md` (the language), `rails.md` plus the layer rules `rails-model.md`, `rails-controller.md`, `rails-view.md`, and `rails-migration.md`, `bundler.md` (dependency declaration and pinning), `gem.md` (authoring and releasing a gem), `rspec.md`, `elixir.md`, `react-typescript.md`, `ember.md`, plus the pair governing `AGENTS.md` and `CLAUDE.md` themselves — `agent-instructions-layout.md` (how a repository arranges its instruction files, rules, and skills) and `agent-instructions.md` (the size budgets those files must stay under).
- **Task workflows** → `~/.agents/skills/` (invoke when doing the task): `git-commit` (commit messages & branch naming), `pull-request` (PR title & description), `git-worktree` (worktree setup).

## First principles

The sections below are rules, and rules can't enumerate every situation. When a task reaches a branch the standards don't cover, reason from these (adapted from TableCheck's engineering first principles):

1. **Be the engineer you'd want to work with.** Optimize for the next maintainer and the reviewer, not just for landing the change. Egoless: the best idea wins regardless of whose it is (see `review-response`).
2. **Practice healthy skepticism.** Question the premise before building it. Verify claims against the code rather than accepting them; when the requested approach looks wrong, say so with evidence instead of building it anyway.
3. **As simple as possible, as complicated as necessary.** The least power that solves the real problem (elaborated in §1 and §7).
4. **Iterate quickly — in small, reversible steps.** Prefer a working increment behind a flag over a big-bang perfect solution. Speed comes from small blast radius, never from skipping the Definition of Done (§4).
5. **Engineering serves the product and the customer.** The code is a means to user value, not an end. Understand the problem being solved; if a task's stated solution won't serve the underlying need, surface that before writing it.

## 1. Engineering mindset (plan & code like a staff engineer)

Approach every task as a staff engineer would: understand the problem and its constraints before writing code, weigh blast radius and long-term cost against the benefit, and favor the simplest design that satisfies the requirement. Optimize for the team and the next maintainer, not just for landing this change.

- **SOLID principles** guide design decisions:
  - **S**ingle Responsibility — each module/class/function has one reason to change.
  - **O**pen/Closed — open for extension, closed for modification.
  - **L**iskov Substitution — subtypes must be substitutable for their base types.
  - **I**nterface Segregation — prefer small, focused interfaces over broad ones.
  - **D**ependency Inversion — depend on abstractions, not concretions; inject dependencies.
- **Test-Driven Development (TDD)** — for new behavior and bug fixes, write a failing test first, make it pass with the minimum code, then refactor. A bug fix should start with a test that reproduces the bug.
- Don't over-engineer. Don't add abstractions, configuration, or flexibility the task doesn't require. Three similar lines beat a premature abstraction.
- **Follow the patterns already in the project** — its idioms, file layout, and tooling — unless diverging buys something concrete. Preserve intentional existing work and layer on top of it; rewrite only for a real defect or an explicit request to refactor.
- Make the change explainable: a reviewer should be able to understand *why* from the diff and commit message.

## 2. Quality attributes (always design for these)

Every change must consider:

- **Security**
  - Treat all external input (user input, APIs, files, env) as untrusted; validate and sanitize at boundaries.
  - Avoid the OWASP Top 10 classes of bugs: injection (SQL/command/XSS), broken auth, sensitive-data exposure, SSRF, insecure deserialization, etc.
  - Never hardcode secrets/credentials; never log them. Use parameterized queries, safe output encoding, and least-privilege access.
  - A client-public environment variable (`NEXT_PUBLIC_*`, `VITE_*`, anything a bundle ships to the browser) is published, not configured. API base URLs and public feature flags belong there; database URLs, credentials, and signing secrets never do.
  - Prefer maintained libraries with no known CVEs; flag any dependency with a known vulnerability rather than introducing it.
  - If you write insecure code, fix it immediately upon noticing.
- **Maintainability**
  - Clear, intention-revealing names; small functions; low coupling and high cohesion.
  - **Restrict comments in production code.** Prefer self-documenting code (precise names, small functions) over prose. A comment may explain *why* — intent, a trade-off, a non-obvious constraint — but never *what*: if you feel the need to narrate what the code does, rename or refactor instead. Default to no comments, and never leave commented-out code. Directives the tooling reads (`eslint-disable-*`, `@ts-expect-error`, `# rubocop:disable`) are the standing exception. Section banners (`// ─── …`), sprint or ticket annotation blocks, and schema doc comments are not — that material belongs in an ADR or the commit message.
  - **Tests document the production code.** Treat the test suite as the executable specification — describe expected behavior, edge cases, and contracts clearly enough that the specs, not comments, are where a reader learns what the code does (see §1 TDD, and the `rspec` rule for Ruby).
  - Leave the code at least as clean as you found it, scoped to the task.
- **Performance**
  - Be mindful of algorithmic complexity, N+1 queries, unnecessary allocations, and blocking I/O on hot paths.
  - Optimize for correctness and clarity first; optimize for speed where it measurably matters. Avoid premature micro-optimization.
- **Accessibility**
  - Interfaces and workflows are accessible by default: keyboard operation, visible focus, sufficient contrast, labeled controls, and error states that say what to do next. It is part of the change, not a follow-up ticket.

## 3. Jira vs. Pull Requests — audience separation

- **Jira tickets are for the product team.** Write ticket titles, descriptions, and comments in product/business language: the user-facing problem, desired outcome, acceptance criteria, and impact. Avoid implementation detail and code-level jargon.
- **Pull Requests are for the engineering team.** Write PR titles and descriptions in technical language: what changed and how, design decisions and trade-offs, testing performed, risks, and migration/rollout notes. Link the relevant Jira ticket for product context, but keep the engineering narrative in the PR.
- Don't paste raw engineering detail into Jira, and don't make a PR description carry product-acceptance criteria that belong in the ticket.

For the PR title and description template, use the `pull-request` skill.

## 4. Definition of Done

Work is not "done" until it is verified — never report a task complete on unverified or "should work" code.

- **Tests pass.** Run the relevant suite for the code you touched (RSpec, ExUnit, Vitest, QUnit), and add tests for new behavior and bug fixes (TDD — see §1).
- **Lint, format & type-check pass.** Run the project's linters/formatters (RuboCop, Credo, ESLint/Prettier) and type-checks (`tsc` / `vite-plugin-checker`, Dialyzer) with no new errors.
- **Exercise UI / behavioral changes.** Run the app and use the feature — happy path plus key edge cases — before claiming success. If you cannot run it in this environment, say so explicitly rather than asserting it works.
- **Self-review the diff** for leftover debug output, secrets, and out-of-scope churn before handing it off.
- If a check genuinely cannot be run here, state which one and why — don't silently skip it.
- **Never mask a failing gate.** No `|| true`, no `| exit 0`, no skipped test or lowered threshold to get a green result. A formatter/lint helper (`pnpm fix`, `rubocop -a`) is not a correctness gate either. A gate that is genuinely wrong gets fixed or removed deliberately, never silenced.
- **Don't trust a search that may have skipped files.** macOS/BSD `find` doesn't follow symlinks by default — use `find -L` when a directory tree mixes real dirs and symlinks, so a "found nothing" isn't just a symlinked subtree it never entered.
- **Stage the gates rather than running everything after every edit.** In the inner loop run the smallest check that exercises what you changed; save broad or expensive gates — a full suite, a repo-wide type-check, a contract regeneration — for stable checkpoints and closeout. After fixing a failure rerun that gate and anything it directly invalidated, and if the fix changed behavior, rerun the focused tests and the closeout gate that had already passed.
- **A long, quiet suite is not a hung one.** Don't restart or stack duplicate runs unless the process has failed, hung past a defensible timeout, or is exercising the wrong scope.
- **Close out on the final tree.** Once the diff is stable, run `git diff --check` for whitespace damage and a diff-scoped secret scan (`gitleaks stdin --redact`) before handing off.
- **Report what you actually ran.** End an implementation summary with a two-column table — each gate against its scope and result — plus test counts and coverage for new or changed modules, and a row naming any gate you couldn't run alongside the smallest command that would close the gap. Pick rows by touched surface; it's a reporting format, not a fixed script.

## 5. Safe rollout, feature flags & migrations

Ship behavioral change conservatively and reversibly.

- **Gate risky or behavior-changing work behind a feature flag, off by default**, so it stays dark until deliberately enabled — Monolith shop/config flags (as in PR #7334) on the backend, DevCycle on the frontend. Plan the rollout: validate on test data/shops, then enable incrementally.
- **Default-off must be behavior-preserving** — enabling the flag should be the only thing that changes behavior.
- **Database migrations must be backward-compatible (expand/contract)** for zero-downtime deploys: add columns/indexes and backfill first, switch reads/writes, then remove the old shape in a later step. Keep migrations reversible, add indexes for new foreign keys and lookups, and avoid long-locking operations on large tables.
- **Keep changes reversible.** Prefer additive changes; when removing or renaming, stage it so a rollback doesn't break running code or in-flight data.

## 6. Error handling, observability & reliability

- **No silent failures.** Never swallow exceptions or rejected promises — no empty `rescue`, bare `catch {}`, or ignored `{:error, _}`. A caught error must be handled, re-raised, or surfaced with context.
- **Actionable errors.** Messages should say what failed and carry enough context to debug (identifiers, operation), without leaking secrets or PII.
- **Fail fast at boundaries; degrade gracefully for users.** Validate inputs early; in user-facing flows show a meaningful error state, never a blank screen or unhandled crash.
- **Validate configuration at startup, in one place.** New environment variables are declared and parsed in the project's canonical config module, which fails with an error naming the missing or malformed setting. Downstream code depends on the parsed shape, never on loose `ENV[…]` reads scattered through the codebase.
- **Structured, leveled logging.** Log at appropriate levels with structured context; never log secrets, tokens, or PII; keep hot paths quiet.
- **Report to monitoring.** Send unexpected errors to the project's tracker (e.g. Sentry) — don't rely on logs alone for production failures.
- **Idempotency & concurrency.** Make background jobs and mutating endpoints safe to retry — a redelivered Sidekiq job or a double-submitted request must not double-book, double-charge, or double-send. Guard shared-state updates against races with database constraints, locks, or atomic operations; never rely on an unprotected read-then-write. This is the failure mode behind overbooking.
- **Elixir:** use tagged tuples and `with` for *expected* errors; reserve "let it crash" + supervision for the genuinely exceptional.

## 7. Engineering leverage & judgment

Operate for impact beyond the immediate change — optimize for the team, the next maintainer, and the system over time.

- **Record significant decisions.** For cross-cutting or architectural choices, write a lightweight ADR (context → decision → consequences, including the alternatives you rejected and why) so the rationale outlives the PR. Don't bury durable decisions in a PR description that rots.
- **Keep PRs small and single-purpose.** One logical change per PR; separate pure refactors from behavior changes. Optimize for the reviewer's time and a clean revert.
- **Be conservative with dependencies and complexity.** Prefer boring, proven technology and the stdlib / existing libraries over net-new dependencies; weigh each addition's maintenance, license, and CVE surface. Spend novelty deliberately, not by default.
- **Steward contracts; deprecate with a path.** Treat published interfaces — APIs, serializers, provider-facing payloads — as commitments to consumers: change additively, version when you must break, and pair any removal with a deprecation window and communication. (DB-level expand/contract lives in §5.)
- **Documentation your change makes wrong is part of your change.** When a README, a comment, or a context file disagrees with the implementation, the implementation is the current behavior. Fix what your work invalidated, in the same commit. Contradictions you merely stumble across are worth reporting, not silently rewriting — that widens the diff past the task.
- **Make tech debt explicit.** Take on debt deliberately, never silently — record it with a `TODO` plus a tracking ticket and a breadcrumb to the follow-up. Surface trade-offs and risks early, rather than letting them surface in review.

## 8. Writing for a human reader

Commit messages, PR descriptions, ADRs, specs, tracker comments, and status updates are read by people. Write like a careful engineer explaining a decision to a teammate — never like a language model. Strip the tells of AI-generated writing:

- **Lead with the point.** The first two or three sentences say what you are trying to achieve and why it matters. Detail only some readers need goes below that — an appendix section, or its own document. Draft, then read it back once and cut: a reader who stops after the opening should still have the decision.
- **No hype or filler adjectives** ("comprehensive", "robust", "seamless", "powerful", "significantly").
- **No throat-clearing** ("It's worth noting that", "In order to", "This change aims to", "This PR aims to").
- **No invented subsection labels.** A bolded "**Why the database is critical:**" ahead of a sentence is the model organizing its own output, not structure the reader asked for. Use the artifact's real sections; if a bolded lead-in is the only thing making a paragraph scannable, the paragraph is the problem.
- **Don't fill a template's empty sections.** A heading with nothing under it costs the reader a stop and teaches them to skim. Write `None` only where the absence is itself the news — no open questions, no migration — and otherwise leave the section out.
- **No restating the diff.** The code is the source of truth — don't narrate it method by method, and don't list the changed files back.
- **Vary sentence length.** The uniformly-hedged, em-dash-heavy cadence is the giveaway; plain, direct sentences of differing lengths are not.
- **Say the surprising thing plainly.** Risks, dependencies, and the alternative you rejected are exactly the parts a reader can't reconstruct from the code.
- **Don't hard-wrap prose you submit through a tool.** Commit bodies, PR descriptions, and tracker comments are soft-wrapped by the host, so manual mid-paragraph newlines only waste width. Markdown files committed to a repository are the exception — match the wrapping already in the file.
- **US English.** `behavior`, `license`, `judgment`, `labeled`. This governs prose you write, not identifiers you find — never "correct" a British spelling that is already a field name, a quoted source, or someone else's ticket title. A project that writes British English says so in its own `AGENTS.md`, and that overrides this.

Audience sets the vocabulary and the length, never the honesty (§3). `git-commit`, `pull-request`, `draft-spec`, `standup`, and `triage` each apply this to their own artifact.

This section governs prose a person reads. Files written for a model to read — skill bodies, `rules/`, instruction files like this one — are exempt, and a word that would look like a tell in a PR description is not a defect to fix in one of them.

---

The first principles above are adapted from TableCheck's [engineering-first-principles](https://github.com/TableCheck-Labs/engineering-first-principles) (MIT).
