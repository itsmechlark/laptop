# Frontmatter reference

Every field the Agent Skills specification defines, with the rules that cause
validation failures in practice. Two fields are required; the other four are
optional and most skills use none of them.

## `name` (required)

- 1–64 characters
- Unicode lowercase alphanumerics (`a-z`, `0-9`) and hyphens (`-`) only
- Must not start or end with a hyphen
- Must not contain consecutive hyphens (`--`)
- **Must match the parent directory name**

```yaml
# Valid
name: pdf-processing
name: data-analysis
name: code-review

# Invalid
name: PDF-Processing   # uppercase
name: -pdf             # leading hyphen
name: pdf-             # trailing hyphen
name: pdf--processing  # consecutive hyphens
name: pdf_processing   # underscore
```

Name for the capability, not the implementation: `pdf-processing`, not
`pypdf-wrapper`. The name is half of what the agent sees during discovery, so it
should read as a topic a user might ask about.

## `description` (required)

- 1–1024 characters, non-empty
- Describes both what the skill does and when to use it
- Should carry the keywords that identify a relevant task

This is the single highest-leverage line in the file. During discovery the agent
sees `name` and `description` and nothing else.

```yaml
# Good — capability, triggers, and keywords in one pass
description: Extracts text and tables from PDF files, fills PDF forms, and merges multiple PDFs. Use when working with PDF documents, or when the user mentions PDFs, forms, or document extraction.

# Poor — a topic, not an occasion
description: Helps with PDFs.
```

Write it in the user's vocabulary, not the codebase's. If the skill handles what
users call "invoices" and the code calls `BillingDocument`, the description says
invoices.

Three failure modes to check for:

| Symptom | Cause | Fix |
| --- | --- | --- |
| Skill never loads | No trigger phrases | Add "Use when …" with concrete scenarios |
| Loads for the wrong tasks | Keywords too broad | Narrow the scope; name what it is *not* for |
| Competes with a sibling skill | Overlapping keywords | Make the boundary explicit in both descriptions |

## `license` (optional)

A license name, or a pointer to a bundled license file. Keep it short.

```yaml
license: Apache-2.0
license: MIT
license: Proprietary. LICENSE.txt has complete terms
```

Include it when the skill is published or redistributed. If you ship a license
file, bundle it at the skill root as `LICENSE.txt` and reference it here.

## `compatibility` (optional)

- 1–500 characters if present
- Declares environment requirements: intended product, required system
  packages, network access

```yaml
compatibility: Requires git, docker, jq, and internet access
compatibility: Requires Python 3.14+ and uv
```

Most skills should omit this. Use it only for a hard requirement the agent can't
discover on its own — not to record soft preferences, which belong in
`## Prerequisites` in the body where they can be explained.

## `metadata` (optional)

A map of string keys to string values. This is the spec's escape hatch for
anything it doesn't define — clients may store extra properties here without
breaking portability.

```yaml
metadata:
  author: example-org
  version: "1.0"
```

Quote values that would otherwise parse as numbers or booleans (`version: "1.0"`
is a string; `version: 1.0` is a float). Prefix keys distinctively if collisions
with other tooling are plausible.

## `allowed-tools` (optional, experimental)

A space-separated string of tools pre-approved for the skill to run.

```yaml
allowed-tools: Bash(git:*) Bash(jq:*) Read
```

Support varies between agents, and the field is explicitly experimental. Treat
it as a convenience, never as a security boundary: don't write a skill whose
safety depends on the host honoring it.

## Host extensions

Hosts define their own top-level keys — `argument-hint`, `applyTo`,
`disable-model-invocation`, and similar. They are useful, and they are not
portable: another agent ignores them rather than translating them.

If a skill is meant to travel, keep host-specific keys out of the top level and
put anything you need to preserve in `metadata`. If a skill is only ever used on
one host, top-level extensions are fine — just don't expect them to survive a
move.

## Minimal and maximal examples

```yaml
---
name: skill-name
description: A description of what this skill does and when to use it.
---
```

```yaml
---
name: pdf-processing
description: Extract PDF text, fill forms, merge files. Use when handling PDFs.
license: Apache-2.0
compatibility: Requires Python 3.14+ and uv
metadata:
  author: example-org
  version: "1.0"
allowed-tools: Bash(python:*) Read
---
```
