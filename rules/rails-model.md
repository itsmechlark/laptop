---
paths:
  - "**/app/models/**/*.rb"
---

# Rails model standards

ActiveRecord, ActiveModel, and the objects that carry domain behavior. Application-wide conventions are in `rails.md`; the schema those models sit on is in `rails-migration.md`.

- Order a model's contents constants → macros → public methods → private methods. Put associations above validations, order each alphabetically, and keep every validation for a column together.
- Use `scope` for a simple, argument-free condition; switch to `def self.method` once it takes arguments or branches, where plain Ruby returns exactly what it says it does.
- Never bypass validations — no `save(validate: false)`, `update_attribute`, or `toggle`. Validate the associated object (`user`), not its foreign-key column (`user_id`), so the check survives an unsaved association.
- Halt an ActiveRecord callback with `throw :abort`, never a bare `false`; raise a domain error when the caller needs to know why it stopped.
- Don't name a method after a column of the same class — the override is invisible at the call site.
- SQL lives here and nowhere else. A `where("inviter_id IS NOT NULL")` in a controller or a view leaks the schema into a layer that can't be tested against it.
- Prevent N+1 with `includes`/`preload`/`eager_load` and catch regressions with the `bullet` gem; batch large reads with `find_each`/`in_batches` and never load an unbounded `Model.all` in a request; wrap multi-step writes in a transaction and raise inside it (`save!`) so a partial failure rolls the whole change back.
- Keep a `.count` out of loops, and reach for `counter_cache` when an association's size is read on a hot path — each is a query you're otherwise paying per iteration.
- Restrict access to models or data through a dedicated authorization library rather than scattering checks across callers, so authorization lives in one auditable, testable place.
- Use ActiveStorage for uploads that belong to a record, and never point a test at a live storage backend.
- Name domain classes after nouns, not actions — no `*Service`, `*Manager`, or `*Handler` suffix — and give them domain verbs (`#complete`, `#submit`, `#deliver`) rather than a generic `.call` or `.perform`.
- Give a validating or form-backed PORO `ActiveModel::Model` so it participates in validations and form helpers like a record does.
- Prefer composition over inheritance, extracting behavior into small focused objects. Feature envy, a long parameter list, a `case` on a type, and mixin abuse are each a domain object trying to be born.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails) - rails, MIT
- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails/ai-rules) - rails AI rules, MIT
