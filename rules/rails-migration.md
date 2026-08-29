---
paths:
  - "**/db/**/*.rb"
  - "**/db/structure.sql"
---

# Rails migration and schema standards

Migrations, the schema they produce, and seed data. Application-wide conventions are in `rails.md`; the models that read this schema are in `rails-model.md`.

- Push integrity to the database (NOT NULL, foreign-key + unique constraints, indexes on foreign keys and lookup columns), give every foreign key an explicit `on_delete` behavior, and set default values here rather than in the model.
- Keep migrations reversible and backward-compatible (expand/contract) so a deploy can roll back without stranding in-flight data.
- Once a migration is merged to `main`, don't edit it — write another one. Someone has already run it.
- Use SQL inside a migration, not ActiveRecord models: the model will change and the migration will quietly stop meaning what it did when it ran.
- Name columns for what they hold — `_at` for datetimes, `_on` for dates, `_time` for a time of day — and back a boolean concept with a timestamp (`published_at`, `deleted_at`) when *when* it happened is worth knowing.
- Keep `db/schema.rb` (or `db/structure.sql`) in version control. `db/seeds.rb` is for data every environment needs; development-only seed data belongs in its own task.

Adapted from thoughtbot's [Rails guide](https://github.com/thoughtbot/guides/tree/main/rails) (MIT).
