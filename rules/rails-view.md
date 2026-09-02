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
- Use `_url` for named routes in mailer views — a relative path has nothing to resolve against in an inbox — and `_path` in ordinary templates.
- A view renders data — no calculations, queries, or branchy conditionals. Push display logic into a presenter the action instantiates and hands to the template.
- Helpers are for simple formatting only (dates, money); once one grows past a few lines it's a presenter method, not a helper.
- Never pass user-supplied data through `raw`, `html_safe`, or `<%== %>` — that is how stored XSS reaches the page. Let Rails escape it.
- Keep Stimulus controllers small and single-purpose; reach for a presenter or a partial before writing more JavaScript.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails) - rails, MIT
- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails/ai-rules) - rails AI rules, MIT
