# The cost axis

Waste is work nothing decides on. The audit finds it, the guardrails stop you
recommending a fix that trades safety for minutes, and the ranking keeps the
report short enough to act on.

## Audit order

1. `.github/workflows/*.yml` — every file, including the ones nobody edits
2. Run history, where `gh` is available
3. Docs stating what CI is expected to prove, which is how you tell a redundant
   check from a required one

Start with the five cheap wins, in this order:

1. Missing dependency caches
2. Missing `concurrency` cancellation
3. Over-broad workflow triggers
4. Duplicate coverage across files or jobs
5. Expensive jobs that run on every change regardless of scope

```sh
rg -n "on:|concurrency:|paths:|paths-ignore:|strategy:|matrix:|cache:" .github/workflows
```

Where `.github/workflows/` is missing or empty, there is nothing to audit. Get
the baseline first — triggering events, required checks, runtime versions, the
repo's validation policy — and propose a small workflow that proves the core
checks, rather than a matrix nobody asked for.

## Guardrails

Check every candidate fix against these **before** it reaches the report. A
recommendation that fails one is dropped, not caveated.

1. **Does not hide required validation.** Anything covering release, schema,
   migration, or shared-library correctness stays, however rarely it fires.
2. **Does not reduce parallelism without justification.** Drop it unless the
   user put cost ahead of latency *and* the new critical path stays within
   1.25× the original.
3. **Preserves documented matrix legs.** A leg backed by an explicit version or
   platform commitment is a promise; only undocumented breadth is waste.
4. **Write-back jobs get opt-in triggers.** A formatter or bot job that mutates
   the branch automatically is flagged, not dropped — recommend the opt-in.
5. **Repo changes stay separate from org settings.** A fix mixing editable YAML
   with organization or account settings splits into two recommendations,
   because only one of them is in the user's hands.

## Ranking

From the candidates below, keep only those with audit evidence behind them that
also pass every guardrail, rank by estimated daily minutes saved (per-run
saving × runs per day), and report at most three. A long wishlist is what makes
these reports go unread.

1. Dependency caching with lockfile-based keys
2. `concurrency` cancellation, added or corrected
3. Duplicate workflow coverage removed — before merging any jobs
4. Triggers narrowed safely
5. Matrix breadth matched to the decision
6. Independent jobs parallelized off the critical path

### Canonical shapes

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

```yaml
- uses: actions/cache@<sha>
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

The key must contain the lockfile hash, or a dependency bump restores a stale
cache and the job fails in a way nobody attributes to caching.

## Severity

Every finding carries a severity in the report, and a cost finding earns its from
the same daily-minutes estimate the ranking uses — not from how easy it is to fix:

- **HIGH** — a dominant cost driver: the heavy job on the critical path, or the
  matrix that runs on every change and dwarfs everything else in runner spend.
- **MEDIUM** — measurable waste that is not the biggest line item: a missing
  cache on a moderate job, an over-broad trigger firing something mid-weight.
- **LOW** — minor waste worth noting once: no `concurrency` on a cheap workflow,
  breadth a little wider than the decision needs.

Severity ranks the finding; the measured or estimated minutes justify it, so give
both. Where run history is missing, say the severity is from static analysis —
the same caveat the report's first line already carries.

## Matrix breadth

Match breadth to the decision being made, not to the maximum the platform
allows:

| Change | Matrix |
| --- | --- |
| Release, or explicit compatibility validation | Full |
| Runtime, plugin, packaging, framework integration | Reduced compatibility set |
| Ordinary code change | One representative latest-version leg |
| Clearly non-runtime change | No heavy test job, where lighter protection exists |

## Trigger and job scoping

- `paths` / `paths-ignore` where a whole workflow genuinely should not run for
  a class of files.
- Job-level gating where event filters are too coarse — a small change-detection
  job emitting explicit outputs (`runtime_relevant`, `run_tests`) that downstream
  jobs gate on.
- Explicit changed-file detection over clever filter expressions when
  reliability matters more than brevity.
- **Do not merge jobs blindly.** Separate jobs that preserve parallelism and
  shorten the critical path are doing their job.
- A workflow-only change that still runs the full suite is evidence the gating
  model is too broad.
- Label-triggered jobs must listen for `labeled` and usually `unlabeled`, or the
  job never re-evaluates when the label changes.

## Validating a fix

Prefer live proof:

- Fire `workflow_dispatch` workflows once
- Verify stale-run cancellation with two quick pushes
- Verify path gating with an incremental ignored-only change on an existing
  branch — **the first push to a new branch is not a valid test**, it touches
  everything
- Confirm heavy jobs actually skip in the UI rather than assuming they would

Unexpected live behavior is a real bug even when the YAML looks correct. Where
live validation is impossible, say so in the report instead of implying it ran.

## Reporting savings honestly

Separate three numbers that answer different questions:

- PR wall-clock time
- Total runner time across jobs
- Work avoided entirely

A change can cut runner spend without improving the fastest feedback path, and
merging parallel jobs does exactly that. Never claim exact minutes without
before/after run data, and name the confounders when you have it — cache
warm-up, changed matrix breadth, a different runner, an unusually small PR.

Where the data is not there:

> I can report the efficiency mechanisms that changed, but not exact minutes
> saved without comparing before/after runs.

For a follow-up pass, compare setup time against execution time, check what the
heavyweight wrapper actions really enforce, and re-check after caches warm.
Report the next few highest-value opportunities, not everything remaining.
