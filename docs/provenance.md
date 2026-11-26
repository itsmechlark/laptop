# Provenance: vendored and derived skills and rules

How outside material enters `skills/` and `rules/`, and how its lineage is
recorded. `check-payload` enforces the agreement between the records and the
files; see [verification.md](verification.md).

## Vendored skills

Third-party skills live in `.agents/skills/<name>/`, are recorded in
`skills-lock.json` with their source and content hash, and are exposed through a
symlink at `skills/<name>` → `../.agents/skills/<name>`. Don't hand-edit vendored
content: it desynchronizes the recorded hash. Re-vendor from upstream and update
`skills-lock.json` instead.

That includes prose you'd otherwise be free to add — a cross-reference into a
vendored skill is still a hand-edit. Point at it from a first-party skill
instead, which costs nothing and keeps the hash honest. Genuinely need the
divergence? Reclassify the skill as `adapted` in `skills-provenance.json` first,
so the fork is recorded rather than silent.

## Derived skills and rules

First-party skills and rules authored from outside material are tracked in
`skills-provenance.json` and `rules-provenance.json` (both hand-owned; `npx
skills` never touches either). Verbatim copies → `skills-lock.json`; our own
work from a source → the matching provenance record. Rules have no vendored
tier, so every rule is first-party and every rule with outside lineage is
recorded. Each subject maps to a **list** of sources (one skill or rule can
draw on several). Every source carries a `relationship`:

- `adapted` — forked then diverged; pinned to a `ref`. Update = 3-way reconcile
  (`git diff <ref>..HEAD -- <path>`, port the non-conflicting upstream changes),
  then bump that source's `ref` + `reviewed`. Never overwrite.
- `spec` — conforms to an external spec; watch the spec URL/version.
- `inspired-by` — ideas/terminology only, no `ref`; attribution, not synced.

Every source also carries a `type` — what kind of thing it is, which decides
its `## Attribution` form. The `types` map at the top of each provenance file
defines them; add one there, in both files, before using it.

Keep the human-readable `## Attribution` section in each derived `SKILL.md` and
`rules/<name>.md` as the reader-facing attribution — the same flat-list format
in both, defined by the `agent-skills` skill, with the provenance record as its
machine-readable mirror.

**`check-payload` fails the run when the two disagree**, for skills and rules
alike: a recorded subject with no `## Attribution`, a bullet count that doesn't
match the source count, a section that isn't last in the file, an em dash where
the format is ` - `, a GitHub bullet that doesn't name its recorded `origin`,
an `## Attribution` with no record behind it, or a record naming a file that no
longer exists. The single exemption is a vendored skill, whose lineage lives in
`skills-lock.json` and whose body is not ours to annotate.

## Keeping both in step

Update both the provenance and the `## Attribution` whenever a first-party
skill or rule changes — they are part of the change, not a follow-up:

- New skill or rule from outside material → add the `skills.<name>` or
  `rules.<name>` entry + `## Attribution`.
- New influence on an existing one → append source + add to `## Attribution`.
  A source in a provenance record without a matching `## Attribution` entry is
  the common miss.
- Reconciled upstream (`adapted`/`spec`) → bump `ref`/`version` + `reviewed`.
- Purely local change → no `ref` change; `inspired-by` sources never carry one.

Several subjects may pin the same upstream path — the five Rails rules all pin
`thoughtbot/guides` at `rails`. Each carries its own `ref`, so porting a change
into one never licenses bumping another.

Run the `update-provenance` project skill to detect upstream drift and walk the
reconcile per subject; it reads and writes both records. It never edits a
`SKILL.md` or a rule on its own authority, so the `## Attribution` change is
always yours to make: every source in a subject's provenance list must have a
matching entry in its `## Attribution`, and the reverse.
