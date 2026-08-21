# Validation and completion

Read this reference when composing the bundled validator command, rendering a
template, or deciding whether a Codex configuration change is complete.

## Sources of truth

Use this precedence when syntax or behavior is unclear:

1. the Codex version that consumes the configuration;
2. current official OpenAI documentation;
3. repository compatibility requirements and tests;
4. old examples, issues, discussions, or model memory.

If documentation and the deployed binary disagree, identify the intended
version boundary instead of silently choosing one.

## Bundled validator

Run `scripts/validate --help` for the current interface. The script is
read-only: it parses source files, renders configs only inside temporary
directories, and invokes the installed Codex CLI when available.

The Bash entrypoint owns discovery and Codex process orchestration. Importable
static policy logic lives in [validate_engine.py](../scripts/validate_engine.py).

| Argument | Use |
| --- | --- |
| `--config PATH` | Add a config TOML or template; repeat for every layer |
| `--requirements PATH` | Add managed requirements from lowest to highest precedence |
| `--rules PATH` | Add an execpolicy rules file; repeat as needed |
| `--replace TOKEN=VALUE` | Supply one explicit template substitution |
| `--sandbox MODE` | Declare the active Codex CLI `--sandbox` override |
| `--managed-proxy` | Declare an active managed proxy only when its requirements file is unavailable |
| `--no-runtime` | Skip installed-Codex and execpolicy checks |

Passing any explicit config, requirements, or rules path disables automatic
discovery. With no explicit paths, the validator checks common project-local
Codex files only.

## Templates

For a generated `config.toml`:

1. pass every substitution explicitly with `--replace TOKEN=VALUE`;
2. statically validate the rendered TOML;
3. make the installed Codex CLI load the rendered temporary config;
4. validate the actual generated file after the project generator runs.

Do not change placeholders or generation semantics merely to satisfy the
validator. It deliberately does not guess project-specific values.

## Completion checks

- Every active config and requirements layer was included.
- TOML parsing and static/effective invariants pass.
- The installed target Codex version loads rendered config when available.
- Changed rules load and inline cases pass.
- Repository-specific policy regression tests pass.
- Any skipped check is named with its reason.
- The report states the target version, changed files, exact commands, results,
  and deliberate security trade-offs.
