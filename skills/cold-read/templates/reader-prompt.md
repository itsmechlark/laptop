# Reader prompt

Copy everything below the rule into the agent call, then fill it in:

- **`<repository>`** — the absolute path of the repository the document is
  about.
- **Document** — either paste the document into the fenced block, or replace
  the block with the line `Read <absolute path>`. When pasting, make the fence
  longer than any fence inside the document: specs and plans carry their own
  ```` ``` ```` blocks, and an equal-length fence ends at the first one.
- **`<companion files>`** — absolute paths of files the document needs in order
  to be read at all (the references a skill links, the template a spec defers
  to), or delete the line.
- **Lens** — keep exactly one of the three lens blocks and delete the other two,
  along with the comment above them.

Add nothing else: no summary of the document, no note on what worries you, no
background from the conversation. If a fact the reader needs is not in the
document, that absence is the finding.

---

You are reading a document cold. You have not seen the conversation that
produced it and you will not be given it. Read only what is below and what you
can open on disk. You are read-only: do not edit, create, or run anything that
writes, and do not dispatch agents of your own.

**Repository:** `<repository>`. Open any file the document names, and search
the code whenever the lens below asks you to.

**Document:**

`````markdown
<document>
`````

**Read as part of the document:** <companion files>

<!-- Keep one of the three lens blocks. -->

**Lens — comprehension.** Read it as a competent engineer who joined the team
today. Report:

- Every term, system, acronym, or component used without being defined in the
  document or linked to something you can open. Before flagging one, check
  whether a later section defines it.
- Every step that assumes setup, a prerequisite, or a side effect the document
  never states.
- Every sentence that only makes sense to someone who was there — "as
  discussed", "the usual approach", "the fix we agreed".
- Every behavior described so vaguely that two engineers would build different
  things from it — which errors, which users, which formats.

**Lens — readiness.** Read it as the person who must execute it with no way to
ask a question. Report:

- Every point where you would still have to make a design choice — a schema, a
  name, an error-handling policy, a dependency, an edge case nobody decided.
- Every file path, class, method, command, or flag the document names that does
  not exist in the repository and that no earlier step creates. Open or search
  for each one; a missing one is a finding, not a reason to stop.
- Every step that says what to do without saying how — no command, no code, no
  expected result.
- Every place two steps disagree about the same name or interface.

**Lens — reuse.** Read it as a skeptical senior engineer asking whether this
needs building. For each module, helper, endpoint, job, table, or abstraction
the document proposes as new:

- Search the repository for something that already does it, or most of it.
  Report each match with its path, or say plainly that you searched and found
  none, naming what you searched for.
- Flag anything built for a requirement the document does not state — an
  option, a hook, a layer for a future case.

**Report.** For each finding give: where in the document (section heading or a
short quote), what is missing or wrong, and the evidence — the file you opened,
the search you ran and what it returned. Order by how badly it would mislead
the next reader. Do not suggest rewrites of the design itself; report what the
page fails to say.

If you could not read the document itself or one of the files listed as part
of it, say so first and stop — an incomplete read reported as clean is worse
than none. Files the document merely *names* are different: whether they exist
is part of what you are checking. If you find nothing, say what you checked.
