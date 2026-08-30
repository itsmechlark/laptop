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
- Prevent N+1 with `includes`/`preload`/`eager_load` and catch regressions with the `bullet` gem; batch large reads with `find_each`/`in_batches`; wrap multi-step writes in a transaction.
- Reach for [Pundit](https://github.com/varvet/pundit) when access to models or data needs restricting, so authorization lives in one auditable place rather than spread across callers.
- Use ActiveStorage for uploads that belong to a record, and never point a test at a live storage backend.

## Attribution

- [thoughtbot/guides](https://github.com/thoughtbot/guides/tree/main/rails) - rails, MIT
