# Recording a spec and slice as done

When the branch implements a spec, or one slice of a slice list, the PR is where that work becomes finished. Update the records before opening, so a spec doesn't sit `accepted` and a criterion doesn't sit unchecked after the code has landed.

## Find them

- The spec is the one the user, the branch name, or the linked issue names. Otherwise look for a spec whose `metadata.tickets` holds the issue key.
- Look in the repository's `docs/specs/` when it exists, else in `~/.agents/specs/` for a file whose `metadata.repo` is this repository's name. Slice lists live in `docs/slices/` or `~/.agents/slices/` the same way.
- A spec written for a slice carries `metadata.part-of: slice/<list-name>#<id>`. That names the list (the file whose `name` is `<list-name>`) and the slice within it. A branch cut for a slice with no spec names the slice directly.
- Nothing found means nothing to update: say so. Never create a spec or list for this, and never pick between several candidates; ask.

## The spec

- Only `metadata.status: accepted` moves to `done`. A `draft` was never agreed, a `superseded` spec is frozen, and a `done` one needs nothing. Leave those and say which you found.
- It is met when every user story and implementation decision in the spec is delivered by the diff. Read the spec against the diff; a green suite doesn't answer this. If part is missing, leave it `accepted` and name what remains in the report.
- A spec that indexes a set reaches `done` only when its last member does.
- Opening as a draft means the work isn't ready, so the spec stays `accepted`. Say so in the report.
- The edit is the one `status` line. The body is frozen once the spec is `done`.

## The slice

- Check a criterion (`- [ ]` to `- [x]`) only when the diff shows it: a test that pins it, or verification you ran and can name. Don't infer it from the spec reaching `done` — the list is the record of what was verified, and the slice skill keeps it that way.
- A criterion the diff doesn't satisfy stays unchecked. One the PR deliberately drops from scope is not yours to rewrite; tell the user, since re-cutting belongs to `slice`.
- When every criterion in the slice is checked, the slice is done: say so plainly. When every slice in the list is done, set the list's `metadata.status: done`.
- Touch nothing else in the list.

## Where the edit lands

- **In the repository** (`docs/specs/`, `docs/slices/`): the edit sits in the working tree, and the PR carries only what is committed. Tell the user the change is waiting for a commit before the push, and don't commit it yourself (`git-commit` covers the message).
- **Under `~/.agents`**: outside the repository, so write it directly; there is nothing to commit. It is recorded before the merge, so say that in the report.
- **On a tracker**: don't transition a status or tick a criterion in someone else's system. Name what needs updating and leave it.
