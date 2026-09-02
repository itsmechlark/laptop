---
paths:
  - "**/app/controllers/**/*.rb"
  - "**/app/mailers/**/*.rb"
  - "**/config/routes.rb"
---

# Rails controller and routing standards

The request layer: what a route exposes and what an action is allowed to do. Application-wide conventions are in `rails.md`; what the action renders is in `rails-view.md`.

- Prefer resource routing to hand-written routes, and name what you expose with `:only` rather than subtracting with `:except` — `:except` silently exposes whatever a future action adds. Avoid `member` and `collection` routes: a route that doesn't fit the resource usually wants a controller of its own. Order resourceful routes alphabetically.
- Instantiate one object per action and expose one instance variable to the view. A second is usually the action doing two things.
- Order a controller's contents filters → public methods → private methods.
- Redirect with `_url`, and use `_path` for every other named route in this layer.
- Keep query logic in the model. A controller that writes SQL or chains conditions is holding knowledge the model can't test or reuse.
- Controllers speak HTTP only — parse the request, delegate to a model or PORO, render the response. A long action is business logic that has escaped the model.
- Permit request parameters explicitly with strong parameters; never `params.permit!`, which trusts whatever the client sends.
- Require authentication by default and authorize every action, scoping records to the current user — an action that skips the check is an IDOR waiting to happen (authorize through the project's authorization library, per `rails-model.md`).
- Keep CSRF verification on for browser-facing controllers, and never `redirect_to params[...]` without validating the target — an unchecked redirect hands your domain to an attacker.
- Re-render a failed form with `status: :unprocessable_entity`. Turbo replaces the form only on a 4xx/5xx and silently drops a 200.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails) - rails, MIT
- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails/ai-rules) - rails AI rules, MIT
