# Managed requirements

Read this reference for `requirements.toml`, managed permission profiles,
managed hooks, or centrally enforced network policy. Use the current
[managed-configuration documentation](https://learn.chatgpt.com/codex/enterprise/managed-configuration)
and [configuration reference](https://developers.openai.com/codex/config-reference)
as the schema authority.

## Sources and precedence

`requirements.toml` is administrator-enforced policy, not ordinary user
configuration. Supported clients compose these sources from lower to higher
precedence:

1. system requirements;
2. enterprise cloud-managed requirements;
3. supported legacy managed-config fields;
4. platform-managed preferences such as macOS MDM.

Pass files to the bundled validator in that order. Higher-precedence scalar and
list values replace lower ones, tables merge by key, and rules, hooks, and
filesystem restrictions use field-specific composition. Do not infer effective
policy from a clean per-file result.

## Permission profiles

Managed permission-profile allowlists require Codex 0.138.0 or later. Older
clients ignore `allowed_permission_profiles` and managed
`default_permissions`; keep legacy constraints only for an intentional
mixed-version rollout.

Enforce these invariants:

- `default_permissions` names a profile set to `true` in
  `allowed_permission_profiles`.
- Every allowlist entry names a built-in profile or a custom profile defined in
  an active config or requirements layer.
- A requirements-defined custom profile does not collide with a profile from
  user configuration.
- Custom profile names do not use the reserved `:` namespace or `filesystem`.

## Managed network and rules

An `[experimental_network]` allowlist does not activate its proxy. Set
`experimental_network.enabled = true`, and test representative client versions
and operating systems before broad rollout.

Managed `rules.prefix_rules` may only make execution more restrictive: use
`prompt` or `forbidden`, never `allow`. Managed hooks can require
administrator-owned scripts but do not distribute those scripts; verify their
deployment separately.

## Review checks

- Every active layer is present and ordered by precedence.
- Managed defaults select an allowed, defined profile.
- Managed and user-defined profile names do not collide.
- Domain policy explicitly enables `experimental_network`.
- Managed prefix rules use only `prompt` or `forbidden`.
- Every target client supports the selected keys.
