---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# React + TypeScript standards

Universal standards for React + TypeScript. Where a bullet names a library it's an example of the category — use whatever the project already depends on; the principle is what matters.

- **TypeScript strict.** No `any` — use `unknown` + narrowing or precise types; type external boundaries (API responses, component props) explicitly, narrowing there rather than downstream. Model complex flows with discriminated unions or typed error results instead of loose objects. Keep the type-checker (`tsc` or the build's checker) clean.
- **Comments:** production `.ts`/`.tsx` carries none — precise types and names are the documentation. The exceptions are directives the tooling reads (`eslint-disable-*`, `@ts-expect-error`), each with its reason on the line.
- **Zod naming:** reserve the `Schema` suffix for Zod schema values and the types inferred from them (`const UserSchema = z.object(…)`, `type UserSchema = z.infer<typeof UserSchema>`). An inferred type keeps the suffix; a type with no Zod behind it never takes it — so the name alone tells a reader whether a runtime validator exists.
- **Components:** function components + hooks; small, focused, accessible. Build on the project's design system and an accessible primitive library (e.g. Radix, React Aria) rather than hand-rolling UI — don't reimplement accessible dialogs, popovers, menus, etc.
- **Effects are a last resort.** Don't use `useEffect` for derived state (compute it during render) or to respond to user events (do that in the handler); reserve effects for synchronizing with external systems. Don't reach for `useMemo`/`useCallback` until profiling shows a need.
- **State:** keep local state local; manage server state with a dedicated data-fetching/caching library (e.g. TanStack Query) instead of hand-rolling fetch/caching/refetch; use a form library (e.g. react-hook-form) for non-trivial forms. Reach for a state-machine library (e.g. XState) only when state is genuinely complex (many states/transitions) — prefer `useState`/`useReducer` + context for the common cases.
- **Accessibility (a11y):** preserve semantic HTML and your primitives' built-in keyboard/ARIA behavior; label every interactive control. a11y is a requirement, not a follow-up.
- **i18n:** never hardcode user-facing strings — add keys through the project's i18n framework (e.g. i18next).
- **Feature flags:** gate risky or behavior-changing UI behind the project's feature-flag system, off by default.
- **Errors & observability:** surface and report errors to the project's monitoring service (e.g. Sentry); never swallow promise rejections or render silent failures.
- **Monorepo:** in a monorepo (e.g. Nx, Turborepo), respect project boundaries — put shared code in shared packages and don't reach across app internals.
- **Testing:** unit/component tests with a fast runner + Testing Library (assert behavior, not implementation details); end-to-end with a browser runner (e.g. Playwright, Cypress). Write the test first for new behavior and bug fixes — the `tdd` skill covers the red-green-refactor cycle.
