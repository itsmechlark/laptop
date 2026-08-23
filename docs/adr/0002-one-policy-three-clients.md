# One security policy, three client configs, mirrored by hand

**Context:** Claude Code, Codex, and Cursor each read their own config format,
and a machine that has run `mac` runs all three off this repo. A deny that
exists in one client and not the others buys nothing.

**Decision:** `.claude/settings.json` is the canonical statement of the policy.
The Codex and Cursor files translate the same policy into their own schemas, and
any change to one client's permission, sandbox, hook, env, or
network/filesystem policy is mirrored into the others in the same commit. The
target is security parity — the same secret-path and destructive-command
denials, the same attribution-off default — not identical UX.

**Consequences:** One policy change touches three files, and the mirror is a
human obligation. `check-payload` mechanizes the part that can be derived:
secret-path parity takes its subjects from Claude's own `Read()` denials, so
adding a deny there *forces* the two mirrors instead of relying on a reviewer.
Command lists, sandbox roots, and hooks are not derived and stay manual. Where a
policy has no counterpart in a client, the gap is written down rather than
dropped — Cursor has no egress sandbox, no env scrub, and an implicit ask tier.

**Rejected:** Generating all three configs from one source. It would remove the
drift risk, but the schemas don't line up: Claude and Codex are allow-by-default
with deny/ask tiers, Cursor is prompt-by-default with an allowlist, and Cursor
has no sandbox roots, no egress allowlist, and no env scrub to generate into. A
generator would need a policy language expressive enough for those asymmetries
and would still leave the untranslatable ones to hand-written prose. Supporting
one client instead of three was not on the table — all three are in use.
