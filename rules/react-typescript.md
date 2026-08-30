---
paths:
  - "**/*.ts"
  - "**/*.tsx"
---

# React + TypeScript standards

The TypeScript bullets apply to any `.ts`/`.tsx`. The React ones are deliberately reached by the same broad glob — if the file isn't part of a React app, a build script or a Node service, ignore them. Where a bullet names a library it's an example of the category: use whatever the project already depends on.

- **No `any`.** Use `unknown` plus narrowing, or a precise type. Type the external boundaries — API responses, component props — explicitly and narrow there, so a shape error surfaces at the edge rather than as `undefined` deep in a render. Model complex flows with discriminated unions or typed error results instead of loose objects.
- **Reserve the `Schema` suffix for Zod.** `const UserSchema = z.object(…)` and the type inferred from it both keep the suffix; a type with no Zod behind it never takes it — so the name alone tells a reader whether a runtime validator exists.
- **Effects are a last resort.** Don't use `useEffect` for derived state (compute it during render) or to respond to a user event (do that in the handler); reserve effects for synchronizing with external systems. Don't reach for `useMemo`/`useCallback` until profiling shows a need.
- **Keep local state local**, manage server state with a dedicated fetching and caching library (e.g. TanStack Query) rather than hand-rolling fetch, cache, and refetch, and use a form library for non-trivial forms. Reach for a state machine only when the states and transitions are genuinely many — `useState`/`useReducer` plus context covers the common cases.
- **Build on an accessible primitive library** (e.g. Radix, React Aria) rather than hand-rolling dialogs, popovers, or menus, and don't defeat what it gives you: keep the semantic element, keep its keyboard and ARIA behavior, and label every interactive control.
- **Never hardcode user-facing strings** — add keys through the project's i18n framework.
- **Never swallow a promise rejection or render a silent failure.** Surface an error state the user can act on and report the error to the project's monitoring service.
- **In a monorepo, respect project boundaries.** Shared code goes in a shared package; don't reach across another app's internals.
- Test with a fast runner plus Testing Library, and end-to-end with a browser runner. `testing.md` and `testing-levels.md` load on the test files themselves.
