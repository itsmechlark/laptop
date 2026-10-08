---
paths:
  - "**/db/migrate/**/*"
  - "**/migrations/**/*"
---

# Migration testing

Whether a schema migration owes a test of its own, and the shape that test takes. Migration mechanics — expand/contract, never editing a merged migration — are in the global standards and, for Rails, `rails-migration.md`; the discipline every test shares is in `testing.md`.

- **Test a migration that touches data; don't test one that only changes shape.** A migration owes a test when it backfills, transforms, moves, or deletes rows, when a condition decides which rows it touches, or when it adds a constraint existing rows could violate (`NOT NULL`, unique, foreign key, check). It runs once, against data no other test has seen, and the application suite only ever sees an empty database the migration ran against — nothing else exercises it.
- **Pure DDL gets no test of its own** — a new table, a nullable column, an added or dropped index. Its proof is that it applies, plus the integration tests that read and write through the new shape. This is the stated exemption `testing-levels.md` asks for. A test that reads the database catalog or the schema dump to find what the migration just created restates the migration and asserts no behavior.
- **"It applies" has to fail somewhere.** Where the test database is built by replaying the migration chain, every database-backed suite already covers it. Where it is loaded from a schema dump instead, CI also migrates an empty database from scratch. Where migrations declare a rollback, the same step rolls the newest back and forward again. One step for the whole chain, not one test per migration.
- **An index exists for performance, so its proof belongs in the performance suite** if anywhere: a query-plan or query-count assertion on the query it serves, at a size where the plan matters (`performance-testing.md`).
- **Pin the test to its migration, not to the current schema.** In a scratch database named uniquely per run, apply the chain up to the migration before it, seed, snapshot, apply the migration under test, assert, and drop the database in teardown. A test against the shared test database asserts the chain's end state, so a later migration that legitimately changes the shape breaks a test whose migration never changed.
- **Seed and assert in the database's own query language, not through models or factories.** They follow today's schema; the migration ran against yesterday's. Seed only rows the previous application version could actually have written — the constraints and validations it enforced still hold — so the test never passes on data production can't contain.
- **Seed every branch of the selection**: a row that should change, one row per reason a row is left alone, nulls, duplicates, and volume past any limit the old code enforced.
- **Assert what a safe deploy needs**: the rows that should change did; the rows that shouldn't compare equal to the snapshot; a write in the previous application version's shape still succeeds afterwards; and where the migration can run more than once — batched, resumable, or outside a transaction — a second run changes nothing.
- **Apply once per file and keep examples read-only.** An example that must write — the previous-version write — does it inside a rolled-back transaction, so no example's outcome depends on order.
- **One test file per migration, named by its version** — `<version>_<name>` mirrors to `<test root>/migrations/<version>_<name>` with the runner's test suffix. It is frozen with its migration: once merged, neither changes, and both go when the chain is squashed.
- **Where the framework has a separate home for data changes** — a post-deploy task rather than a schema migration — prefer it: the migration stays DDL, and the transform is tested like any job, against the current schema.
