---
paths:
  - "**/app/views/**/*"
  - "**/app/helpers/**/*.rb"
  - "**/app/components/**/*.rb"
  - "**/app/components/**/*.erb"
---

# Rails view standards

Templates, partials, helpers, and view components. Application-wide conventions are in `rails.md`; what the action hands the template is in `rails-controller.md`.

- Pass locals to partials. Never read an instance variable inside one — a partial that reaches for `@user` can only be rendered from the one action that happens to set it.
- Never reference a model class from a view. Whatever the template needs, the action or a presenter should already have handed it.
- Put application-wide partials in `app/views/application`.
- Use `link_to` for GET and `button_to` for every other verb, so the request doesn't depend on JavaScript that may not have loaded.
- Use `_url` for named routes in mailer views; `_path` in ordinary templates.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails) - rails, MIT
