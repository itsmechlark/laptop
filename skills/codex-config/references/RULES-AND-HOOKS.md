# Execpolicy rules and hooks

Read this reference when changing `.rules` files, `prefix_rule`, or lifecycle
hooks. Verify syntax against the current [rules](https://developers.openai.com/codex/rules)
and [hooks](https://developers.openai.com/codex/hooks) documentation.

## Exact-prefix semantics

`prefix_rule` compares an argv list position by position. A union such as
`["apply", "destroy"]` means alternatives at one position; it does not search
the whole command.

When several rules match, the most restrictive result wins:

`forbidden > prompt > allow`

Do not assume this rule:

```python
prefix_rule(pattern = ["git", "push", "--force"], decision = "forbidden")
```

also catches:

```text
git push origin main --force
git -C repo push --force origin main
```

When a dangerous flag can move, either enumerate a small complete set of
canonical forms or enforce the semantic prohibition in a deterministic hook.
Do not build a brittle permutation list that only appears exhaustive.

## Inline cases and runtime checks

Give each non-trivial rule representative `match` and `not_match` cases. Include
at least one plausible bypass shape for a security-sensitive rule.

Test actual decisions with:

```bash
codex execpolicy check --pretty \
  --rules path/to/default.rules \
  -- command arg1 arg2
```

Repeat `--rules` when the effective policy loads more than one file.

Codex can split simple linear `bash -lc`, `bash -c`, `zsh`, and `sh` command
chains before evaluation. Advanced shell features can leave the entire shell
invocation opaque. Never depend on shell splitting as the only control for a
hard security invariant.

## Hooks

Use hooks for deterministic semantic checks that exact prefixes cannot express,
such as:

- a dangerous option appearing anywhere in argv;
- a global option moving a subcommand's position;
- a worktree destination escaping an allowed parent;
- structured tool input that needs validation before execution.

Prefer repository-controlled scripts over large inline commands. Resolve
repository-local scripts from the Git root because Codex may start in a
subdirectory. A hook may deny an operation, but it does not replace filesystem,
network, or approval boundaries.

## Review checks

- Patterns reflect exact argv-prefix semantics.
- Normal option reordering cannot bypass a hard deny.
- Non-trivial rules have positive and negative inline cases.
- Representative `codex execpolicy check` cases pass.
- Hooks are deterministic, fail visibly, and preserve independent sandbox
  boundaries.
