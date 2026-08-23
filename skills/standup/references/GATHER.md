# Gathering across repos and trackers

## The journal

`~/.agents/standup/YYYY-MM-DD-<audience>.md`, one file per update, written at
Step 6 and read at Step 2. Machine-local, git-ignored, pruned to 14 days. The
path is identical on every client — Claude, Codex, and Cursor each grant write to
that one directory — so the skill doesn't care which agent runs it.

Entries sort lexically because the name starts with an ISO date, which beats
modification time: copying or touching a file reorders `ls -t` and changes
nothing about which update actually came first.

```sh
ls ~/.agents/standup/                          # everything kept
ls ~/.agents/standup/*-client.md | tail -3     # one reader's recent history
```

What to do with the most recent one:

- **Diff the sections, not the prose.** Compare like to like — the mapping
  differs by format, because the three skeletons don't share section names:

  | Format | Promise check | Stall check |
  | --- | --- | --- |
  | Block (client, manager) | last "Up next" vs today's "Done" | "In progress" appearing twice |
  | Terse (team, written) | last "Today" vs today's "Yesterday" | "Blockers" repeating unchanged |
  | Spoken (team, live) | the middle sentence vs today's first | the same blocker named twice |

- **Count days, don't judge them.** "Third day in progress" is a fact worth
  raising. Why it stalled is the user's answer, not yours.
- **Watch for repeated wording.** A line carried over verbatim is the tell that
  the update is being maintained rather than written, and it is exactly what a
  reader reads as no progress.
- **Read the file, don't infer from the filename.** The date in the name is when
  the update was filed, which is not always the stretch it covers.

### Pruning

Two rules: nothing older than 14 days, but never a reader's most recent entry
however old it is. The second is what keeps an infrequent cadence — a monthly
client report — from losing its history before the next one is written.

```sh
cd ~/.agents/standup || exit 0
for reader in $(ls ./*.md 2>/dev/null | sed 's/.*-//; s/\.md$//' | sort -u); do
  newest=$(basename "$(ls ./*-"$reader".md | tail -1)")
  find -L . -name "*-$reader.md" ! -name "$newest" -type f -mtime +14 -delete
done
```

`-L` matters for the same reason it matters in Step 6: `.` here is reached
through a symlink, and BSD `find` will not descend one it was handed unless told
to. Verify a prune actually removed something before believing it did.

When the directory is missing, `mac` has not run on this machine: say so in one
line, skip the journal, and **never create the directory yourself** — a real one
there gets moved aside to `standup.backup` by the next `mac` run, losing the
history it existed to keep. When it exists but the write is refused, report that
plainly too. The skill works without a journal; it just can't tell the user
anything they didn't already know. Never fall back to writing it somewhere else,
least of all into the current repository.

### Without a journal, judge staleness from dwell time

The first run has no history, and dwell time covers the stall half of it for
free:

```sh
git for-each-ref --sort=committerdate refs/heads \
  --format='%(refname:short)  last commit %(committerdate:relative)'
git log --format='%ar' "$(git merge-base HEAD main)..HEAD" | tail -1
gh pr list --author "@me" --json number,title,createdAt --jq \
  '.[] | "\(.number) \(.title) opened \(.createdAt)"'
```

A branch whose first commit is three days old and still unmerged, or a PR open
across two updates, is the same signal the journal gives — arrived at from the
repository instead of from history. What this cannot see is the promise: a date
the user gave the reader in prose exists nowhere in git.

One checkout and one `git log` cover the smallest case: a day spent in a single
repository with nothing filed anywhere. Real days spread wider than that, and the
work that spread is exactly the work people forget to report.

**Everything here is read-only.** Gathering never comments, transitions, assigns,
or closes anything. The tracker tools that can write are the same ones used to
read, so the constraint has to be deliberate: reading a ticket to describe it is
in scope, touching it is not.

**None of it is the update.** Every command below produces a prompt for the
user's memory, never a line of the draft. See the standing rule in
[SKILL.md](../SKILL.md#gotchas) about writing only what the user said.

## Which repos the stretch touched

Ask, then verify — don't assume the current checkout is the whole story:

**"Which repos did you touch? Anything outside this one?"**

When `~/.agents/CONTEXT.md` exists, its **Repos** table already lists every repo
on the machine with its path, so read it first and turn the question into a much
better one: *"I can see api, web, and the admin app — was it all three today, or
just api?"* Recognition beats recall, and a repo the user forgets is a chunk of
the day that goes unreported.

Treat that file as a convenience and never a dependency:

- It's optional and machine-local (git-ignored), so it is frequently absent.
  Absent is normal — fall back to the plain question, and don't suggest creating
  one mid-standup.
- Read only the repo paths. It also holds environment URLs, service names, and
  account handles that have nothing to do with this update.
- It holds no credentials by policy. If something in it looks like one, it is a
  policy violation to report to the user, not a value to use.

Then run the same three commands per repo the user names, oldest window first:

```sh
for repo in ~/Codespace/api ~/Codespace/web; do
  printf '\n=== %s\n' "$repo"
  git -C "$repo" log --since="3 days ago" --author="$(git -C "$repo" config user.email)" --oneline
  git -C "$repo" status --short
done
```

`git -C` avoids leaving the shell somewhere unexpected. Per-repo
`config user.email` matters more than it looks: a work repo overriding the email
is the ordinary case, and hoisting one email across every repo silently returns
nothing for the rest — the failure the empty-log gotcha in
[SKILL.md](../SKILL.md#gotchas) describes.

## The window

- **Three days back by default**, then trim. Monday's "yesterday" is Friday, and
  `--since="yesterday"` on a Monday reports an empty week.
- **`--since` is local time**, so a late-night commit lands on the day the
  machine thinks it is. For anyone reporting into a team a timezone away, ask
  which day the reader considers "yesterday" before trusting the boundary.
- **End of week wants `--since="last monday"`** and grouping by outcome rather
  than by day.

## GitHub, through `gh`

Reviews and issue comments are the work that never shows up in a log, and the
work a teammate is most likely to be waiting on:

```sh
gh pr list --author "@me" --state all --limit 10
gh pr list --search "reviewed-by:@me updated:>=$(date -v-3d +%Y-%m-%d)" --state all
gh issue list --assignee "@me" --state open --limit 10
```

`gh` may not be installed or authenticated. Check once with `gh auth status`; if
it fails, say so in one line and move on to the question. Never block the update
on tooling.

## Jira, through the Atlassian MCP

When the Atlassian MCP is connected, the user's own recently-updated issues are
the closest thing to a ready-made "Done" list for an end-of-week client update.
Search for issues assigned to the current user updated within the window, and
read status, key, and summary.

- **Not connected is the common case.** The MCP needs an interactive OAuth flow,
  which a non-interactive session cannot run. Say once that Jira wasn't reachable
  and ask the user which tickets moved, rather than reporting nothing moved.
- **Never guess a ticket key.** `PROJ-1234` invented from context is worse than
  no reference, because it looks checkable and sends the reader somewhere wrong.
- **A status is not an outcome.** "Moved to Done" is tracker mechanics; the
  update needs what the reader can now do. Use the ticket to jog the memory, then
  write the outcome in the user's words.
- **Tracker items needing work are a different job.** `triage` owns those; it is
  user-invoke-only, so route by reading and following its `SKILL.md`.

## When the stretch has no repository at all

A week of design review, incident response, interviews, or pairing produces
nothing to gather, and the skill still works — Step 2's opening question is the
whole of it. Skip straight there rather than reporting that git found nothing,
which reads as an accusation.
