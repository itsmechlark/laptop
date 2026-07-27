---
paths:
  - "**/*.js"
  - "**/*.hbs"
  - "**/*.emblem"
---

# Ember standards

- Classic **Ember 3.24** on ember-cli — match the existing idioms; do **not** introduce Octane-only syntax, modern addons, or APIs incompatible with this version.
- Use **Ember Data** (models/adapters/serializers) for the data layer and **ember-simple-auth** for session/auth; follow established patterns rather than bespoke fetch logic.
- Templates use **Emblem** (`ember-cli-emblem`) + HTMLBars, styles use Sass — follow the surrounding file's conventions.
- Lint with `eslint-plugin-ember` (airbnb-base) + Prettier and keep it clean.
- Test with **QUnit** via ember-qunit — unit, integration/rendering, and acceptance tests as appropriate.
