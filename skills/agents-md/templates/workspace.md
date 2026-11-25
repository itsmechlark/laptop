# <workspace path>

<One line: what this workspace is, its package name, and the runtimes it
supports.>

## Required rules

- `.agents/rules/<rule>.md`: `<glob it covers>`

## Commands

Run each as `<scoping prefix, e.g. pnpm --filter @scope/api> <script>`. Only the
scripts whose names don't say enough.

| Task | Command |
| --- | --- |
| Dev | `<script>` |
| Test one file | `<script> <path>` |

## Conventions

- <A rule true for this workspace and nowhere else.>
- Never hand-edit `<generated path>`; regenerate with `<script>`.

## Done

- <Only the delta from the root's Done: a runtime it lacks, an extra gate.>

## Gotchas

- <A trap specific to this workspace, in two lines at most.>
