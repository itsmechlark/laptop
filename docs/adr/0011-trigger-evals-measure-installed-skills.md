# Trigger evals measure the installed skills, not an isolated copy

**Context:** The eval used to install a probe skill into a throwaway project and
point `CLAUDE_CONFIG_DIR` at a fresh directory, so the maintainer's own skills
could not steal a trigger from the description under test. That isolation
measured nothing at all, silently: credential discovery is scoped to the config
dir, so `claude -p` under a fresh one exits `Not logged in · Please run /login`
even with a valid keychain grant. Every query failed identically and scored as a
miss, which is indistinguishable from a description that does not fire. Seeding
the throwaway directory with the account state from `~/.claude.json` does not
restore it — only copying the live OAuth token into each one would.

**Decision:** A run measures each skill where `mac` already installed it, since
`skills/` *is* `~/.claude/skills` (ADR 0001), using an empty temp project as cwd
and the default config dir. A probe skill is installed only for `--description`,
where a candidate rewrite has nowhere else to live. The default model is
`sonnet` — the one the maintainer actually works in — rather than the cheapest
one that runs.

**Consequences:** ADR 0007's shared query pools now do what that record claims.
Adjacent skills load and compete, so a pool genuinely establishes which of a
pair wins; under isolation the sibling was never present, and every negative
label passed for free against a competitor that did not exist. The cost is that
a result depends on the machine's whole installed skill population, plugins
included — faithful to how a skill is really reached, but reproducible only
against the same payload, so a surprising score is worth re-reading in that
light before editing a description. Sonnet also costs materially more than
haiku, which stays available through `EVAL_MODEL` as a smoke pass; a description
failure must not be read off it, because haiku answers a fair share of these
queries directly instead of reaching for a skill. Measuring `codex-config` moved
from 8/16 to 16/16 on that change alone. One detection rule narrowed as a
consequence: the `Read` fallback counts only in probe runs, because a real skill
name can appear in a file path merely because the query named it.

**Rejected:** Copying the OAuth token into every throwaway config dir. It would
have preserved isolation, but it writes a live credential in plaintext once per
query — a worse problem than the skill collision it solves.
`--setting-sources project` was the other candidate and does not do the job:
tested, it still loaded the user's skills. Keeping the isolation and accepting
the null results was never an option, but it is what shipped for months, which
is the reason this record exists.
