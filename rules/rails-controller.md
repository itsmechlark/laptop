---
paths:
  - "**/app/controllers/**/*.rb"
  - "**/app/mailers/**/*.rb"
  - "**/config/routes.rb"
---

# Rails controller and routing standards

The request layer: what a route exposes and what an action is allowed to do. Application-wide conventions are in `rails.md`; what the action renders is in `rails-view.md`.

- Prefer resource routing to hand-written routes, and name what you expose with `:only` rather than subtracting with `:except`. Avoid `member` and `collection` routes — a route that doesn't fit the resource usually wants a controller of its own. Order resourceful routes alphabetically.
- Instantiate one object per action and expose one instance variable to the view. A second is usually the action doing two things.
- Order a controller's contents filters → public methods → private methods.
- Use `_url` for named routes in redirects and mailer views; `_path` everywhere else.
- Keep query logic in the model. A controller that writes SQL or chains conditions is holding knowledge the model can't test or reuse.

Adapted from thoughtbot's [Rails guide](https://github.com/thoughtbot/guides/tree/main/rails) (MIT).
