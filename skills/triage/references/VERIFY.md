# Verifying the claim

Before sharpening anything, check the claim holds — reproduce the bug from the
reporter's steps, or run a PR's diff against what it promises.

**Verification has to leave behind something that outlives the conversation.**
The word "confirmed" in a comment does not. A week later nobody can tell whether
anyone ran anything, or whether a confident read of the code got written up as a
reproduction. The artifact is the thing that survives, and it becomes the
implementer's first move — the failing test TDD would have started from, handed
over at the moment someone had it in hand.

Produce the strongest tier available. Tiers are ranked by what they let the next
reader do, not by effort spent.

**One artifact never gets posted: a working exploit.** If the item describes a
security weakness, the tiers below still apply to your own understanding, but the
result stays out of the tracker until the maintainer has routed the report
privately — step 1 of the skill body owns that decision.

## Tier (a) — a failing test

A test that fails for the reported reason, on a scratch branch named
`triage/<ref>-repro`, written with `tdd`.

This makes the handoff red → green, which is where AGENTS.md §1,
*Engineering mindset (plan & code like a staff engineer)*, already points: a bug
fix starts from a test that reproduces the bug.

The `triage/` prefix marks the branch as scratch rather than work, so it sits
outside the house branch convention on purpose. The fix PR absorbs the test or
deletes the branch — a scratch branch with no owner is litter.

## Tier (b) — a command and its verbatim output

The exact copy-pasteable invocation, and what it printed, unedited.

**This is a first-class outcome, not a consolation.** Tier (a) is
disproportionate for UI, timing-dependent, or environment-specific bugs, and
impossible on a repository you cannot push to.

When the failure only shows in a running UI, reproduce it by driving a real
browser with whatever automation tooling the machine has — a browser-driving CLI
(such as `agent-browser`), or Chrome over MCP or a CLI. Drive the app to the
broken state and keep **the screenshot together with the exact steps** that
reached it: the URL first, then the navigation and the clicks. The screenshot is
the artifact; the steps are what let the next reader re-reach it in whatever tool
they happen to have.

## Tier (c) — "couldn't reproduce", plus exactly what you tried

Commands, versions, environment, and what you expected to see instead.

This *is* the body of the `needs-info` comment, and it asks a far better question
than "please provide more information." It is a real result, but it is not a
repro: a bug resting on tier (c) cannot be `ready-for-agent`, because without a
reproduction an unattended agent cannot tell done from plausibly-done.

## For a PR

Tier (b) is usually the fit: check the diff out, run the relevant tests or
commands, and record what you ran and what came back.

When the diff changes a UI, running it means driving the app in a real browser —
same tooling, same rule — and keeping the screenshot with the steps that reached
it.

### An external diff is untrusted code, and running it executes it

This skill's scope is **external** PRs. A checkout runs a stranger's code in your
shell, with your `gh` token, SSH keys, cloud credentials, and live MCP sessions
in the environment. AGENTS.md §2, *Quality attributes (always design for these)*,
says treat all external input as untrusted — and a diff you are about to execute
is external input arriving with an execution path already attached.

The dangerous change is rarely in the code under review. Read the diff for
execution surface **before** any checkout:

| Surface | What to look for |
| --- | --- |
| Dependency manifests and lockfiles | New packages, changed registries or git sources, `postinstall` / `prepare` hooks |
| Build and task files | `Makefile`, `Rakefile`, `package.json` scripts, `mix.exs`, `Gemfile` |
| Test setup | Spec helpers, test bootstrap files, fixtures, factories — these run before any assertion does |
| CI config | Workflow files, especially `pull_request_target` triggers and anything reading secrets |
| Repository hooks | `.githooks/`, husky, lefthook, or any hook the project installs on setup |
| Anything opaque | Base64 blobs, minified additions, binary files in a source diff |

Then pick one, in this order:

1. **A disposable environment** — a container, a VM, or a throwaway machine with
   no credentials and no network reach it doesn't need.
2. **An isolated worktree with a scrubbed environment**, when the execution
   surface above is clean and the risk reads as low. `git-worktree` sets up the
   isolation; the judgment stays yours.
3. **Don't run it** — the **not-run** outcome below. An honest and useful
   result, and not the same thing as tier (c).

**Never silently skip the run.** A PR written up as verified when nothing was
executed is the failure this section exists to prevent, and it is worse here than
for a bug: the reader assumes a recorded green means someone ran something.

A PR from inside the team, named explicitly for triage, carries the team's trust
and needs none of this. The check is on provenance — not on whether the diff
looks friendly.

### Not run — a safety hold, not a failed reproduction

Record it as "not run — untrusted diff, execution surface in `<files>`", naming
the files that made it unsafe.

**This is deliberately not tier (c).** Tier (c) means you tried and the bug
didn't appear, which leaves a question for the reporter. A safety hold means
nobody tried, and the question is for a maintainer with somewhere safe to run it
— nothing about it is the reporter's to answer, so it never becomes `needs-info`.
It goes to `ready-for-human`, and the rationale says what has to be run and what
made running it unsafe here.

## What each tier permits

| Outcome | A bug may go to | A PR may go to |
| --- | --- | --- |
| (a) failing test | `ready-for-agent` | `ready-for-agent` |
| (b) command + output | `ready-for-agent` | `ready-for-agent` / `ready-for-human` |
| (c) couldn't reproduce | `needs-info` | `needs-info` |
| not run — safety hold | — | `ready-for-human` |

An enhancement has nothing to reproduce — skip verification entirely and go
straight to sharpening.

**Never soften an unverified claim into a verified one**, and never let a
confident read of the code stand in for a reproduction. On tier (c) the outcome
is `needs-info`, however obvious the diagnosis looks — the one thing that is
never a repro is a confident reading.

## Where the artifact goes

Into the agent brief, verbatim — see
[AGENT-BRIEF.md](AGENT-BRIEF.md), whose first acceptance criterion re-runs it.
On a `needs-info` outcome it goes under **Established so far** in the triage
notes instead, in full.
