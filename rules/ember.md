---
paths:
  - "**/*.js"
  - "**/*.hbs"
  - "**/*.emblem"
---

# Ember standards

These apply to **Ember apps**. The `**/*.js` glob is deliberately broad, so if a JavaScript file isn't part of an Ember app — a Node script, build config, or another framework — ignore this file and follow that project's conventions instead.

- **Match the project's Ember version and paradigm.** Classic and Octane are different frameworks wearing one name: check which the surrounding files use before writing a component, and never mix the two or introduce syntax, addons, or APIs the installed version doesn't have.
- Use **Ember Data** — models, adapters, serializers — for the data layer, and the project's established session and auth addon. Bespoke `fetch` logic in a component bypasses the store's identity map and caching, and then two parts of the app disagree about the same record.
- Follow the project's template syntax (Handlebars, or Emblem where used) and its styling conventions.
- Test with the project's Ember test framework, commonly QUnit via `ember-qunit`: unit, rendering, and acceptance tests as `testing-levels.md` divides them.
