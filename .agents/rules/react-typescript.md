---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# React + TypeScript standards

- **TypeScript strict.** No `any` — use `unknown` + narrowing or precise types; type external boundaries (API responses, component props) explicitly. Keep `tsc` / `vite-plugin-checker` clean.
- **Components:** function components + hooks; small, focused, accessible. Build on the `@workspace/ui` design system and Radix primitives rather than hand-rolling UI — don't reimplement accessible dialogs, popovers, menus, etc.
- **State:** server state via TanStack Query (don't hand-roll fetch/caching/refetch); model complex UI state with XState machines; forms with react-hook-form. Keep local state local.
- **Accessibility (a11y):** preserve semantic HTML and Radix's built-in keyboard/ARIA behavior; label every interactive control. a11y is a requirement, not a follow-up.
- **i18n:** never hardcode user-facing strings — add keys via i18next / react-i18next.
- **Feature flags:** gate risky or behavior-changing UI behind DevCycle (`@devcycle/react-client-sdk`).
- **Errors & observability:** surface and report errors to Sentry; never swallow promise rejections or render silent failures.
- **Monorepo:** this is an Nx workspace (`apps/*`, `libs/*`) — respect project boundaries, put shared code in `libs/`, and don't reach across app internals.
- **Testing:** Vitest + Testing Library for unit/component tests (assert behavior, not implementation details); Cypress / Playwright for end-to-end.
