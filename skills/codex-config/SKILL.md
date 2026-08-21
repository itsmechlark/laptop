---
name: codex-config
description: Review, create, migrate, and validate OpenAI Codex CLI configuration and command-execution policy. Use when editing .codex/config.toml, config.toml.template, managed requirements.toml, or .codex/rules/*.rules; changing permission profiles, sandbox or network policy, hooks, or feature flags; or troubleshooting codex execpolicy. Not for general Codex setup, product questions, model selection, or API usage.
compatibility: Requires Bash and Python 3.11+ or tomli. Runtime and execpolicy checks require the Codex CLI.
---

# Codex configuration

Change version-sensitive Codex configuration without weakening its effective
permission, approval, filesystem, or network policy.

## When to use this skill

- Review or edit Codex `config.toml`, `config.toml.template`, or
  `requirements.toml` files.
- Migrate between legacy sandbox settings and permission profiles.
- Create or debug `.codex/rules/*.rules`, `prefix_rule`, or lifecycle hooks.
- Diagnose ineffective domain restrictions, profile conflicts, or
  `codex execpolicy` failures.
- Validate generated configuration against the installed Codex CLI.
- Do not use for general Codex installation, account, model, pricing, or API
  questions.

## Gotchas

- **Treat configuration as executable security policy.** Never weaken a deny,
  approval boundary, secret isolation rule, or network restriction merely to
  make validation pass.
- **Inspect the effective stack, not one file.** User, project, profile, CLI,
  and managed layers can conflict even when each file is valid alone.
- **Do not mix permission profiles with legacy sandbox settings.** Determine
  which permission model the target Codex versions support before migrating.
- **Supply managed requirements from lowest to highest precedence.** Scalars
  and lists override while tables and restrictive policy have field-specific
  composition behavior.
- **A domain table is not enforcement by itself.** Profile domain rules require
  an active local or administrator-managed network proxy.
- **`prefix_rule` matches exact argv prefixes.** Use a deterministic hook when
  a dangerous option can legally move elsewhere in argv; hooks supplement
  sandbox and approval boundaries rather than replace them.

## Workflow

1. Inventory every active config, profile, managed-requirements, CLI override,
   and rules layer. Record the installed and deployed Codex versions.
2. Read only the references needed for the change:
   - [PERMISSIONS.md](references/PERMISSIONS.md) for permission profiles,
     filesystem access, sandbox migration, and network policy.
   - [REQUIREMENTS.md](references/REQUIREMENTS.md) for administrator-managed
     requirements, precedence, and compatibility.
   - [RULES-AND-HOOKS.md](references/RULES-AND-HOOKS.md) for execpolicy rules,
     exact-prefix coverage, inline cases, and hooks.
   - [VALIDATION.md](references/VALIDATION.md) for validator arguments,
     templates, evidence, and completion checks.
3. Verify changed or unclear behavior against current official OpenAI
   documentation and the target binary. Report a compatibility boundary when
   the documentation and deployed version disagree.
4. Make the smallest policy-preserving change. Add `match` and `not_match`
   cases for every non-trivial `prefix_rule`.
5. Run [the bundled validator](scripts/validate) with every active file, fix
   every failure, then run repository-specific policy checks.

## Validation

Run `scripts/validate --help` before composing the command. Repeat `--config`,
`--requirements`, and `--rules` for every active layer. Pass template values as
explicit `--replace TOKEN=VALUE` arguments. When the Codex invocation uses
`--sandbox`, pass the same mode to the validator. The validator never guesses
local placeholders and never modifies source files.

Successful work has evidence that:

- Config and requirements TOML parse and satisfy static/effective invariants.
- The installed Codex CLI loads each rendered config when available.
- Each changed rules file loads through `codex execpolicy check` and its inline
  cases pass.
- Repository policy regression checks pass.

If Codex is unavailable, use `--no-runtime` for static checks and report runtime
and execpolicy validation as **not run**.

## Completion report

State the target Codex version, files changed, exact validation command, checks
that passed, checks not run and why, and every deliberate security trade-off.

## Attribution

- [OpenAI Codex permissions](https://developers.openai.com/codex/permissions)
- [OpenAI Codex configuration reference](https://developers.openai.com/codex/config-reference)
- [OpenAI Codex managed configuration](https://learn.chatgpt.com/codex/enterprise/managed-configuration)
- [OpenAI Codex rules](https://developers.openai.com/codex/rules)
- [OpenAI Codex hooks](https://developers.openai.com/codex/hooks)
- [OpenAI Codex developer commands](https://developers.openai.com/codex/developer-commands)
- [OpenAI Codex configuration schema](https://developers.openai.com/codex/config-schema.json)
