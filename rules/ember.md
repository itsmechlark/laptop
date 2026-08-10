---
paths:
  - "**/*.js"
  - "**/*.hbs"
  - "**/*.emblem"
---

# Ember standards

These apply to **Ember apps**. The `**/*.js` glob is broad, so if a JavaScript file isn't part of an Ember app — a Node script, build config, or another framework — ignore these rules and follow that project's conventions instead.

- **Match the project's Ember version and paradigm.** Follow the existing idioms (classic/pre-Octane vs Octane); don't mix paradigms or introduce syntax, addons, or APIs incompatible with the version in use.
- Use **Ember Data** (models/adapters/serializers) for the data layer and the project's established session/auth addon; follow existing patterns rather than bespoke fetch logic.
- Follow the project's template syntax (Handlebars/HTMLBars, or Emblem where used) and its styling conventions.
- Lint with `eslint-plugin-ember` + Prettier and keep it clean.
- Test with the project's Ember test framework (commonly QUnit via ember-qunit) — unit, integration/rendering, and acceptance tests as appropriate.
