# Bundling resources

A skill directory may contain any files beyond the required `SKILL.md`. Four
folder conventions cover almost everything; the spec names the first three and
permits the rest.

| Folder | Holds | In the spec? | Loaded into context |
| --- | --- | --- | --- |
| `scripts/` | Executable automation | Yes | No — output only, when run |
| `references/` | Docs the agent reads to decide | Yes | Yes, when referenced |
| `assets/` | Static files used **as-is** in output | Yes | No |
| `templates/` | Scaffolds the agent **modifies** | Convention | Yes, when referenced |

```
my-skill/
├── SKILL.md              # required
├── LICENSE.txt           # optional, if published
├── scripts/
│   ├── validate.sh
│   └── extract.py
├── references/
│   ├── API.md
│   └── DEPLOY.md         # a workflow too long for SKILL.md
├── assets/
│   ├── baseline.png      # comparison target, used unchanged
│   └── report.html       # output format, copied verbatim
└── templates/
    ├── scaffold.py       # the agent fills in the logic
    └── config.template   # the agent fills in the values
```

## `assets/` vs `templates/`

The distinction is who changes the file.

**Assets** are consumed unchanged: a `logo.png` embedded in a generated
document, a `report.html` copied as the output format, a `custom-font.ttf`
applied to rendered text. The agent doesn't need to read the bytes.

**Templates** are starting points the agent actively edits: a `scaffold.py`
where it inserts logic, a `config.template` where it fills in values from the
user's requirements, a `hello-world/` project it extends.

**Rule of thumb:** if the agent reads the content and builds on it →
`templates/`. If the file lands in the output as-is → `assets/`.

Getting this wrong is expensive in one direction: an asset misfiled as a
template invites the agent to rewrite a file that was supposed to be canonical.

## `references/`

Documentation loaded on demand. Keep each file focused on one subject — the
agent pays for the whole file when it reads any of it, so one 400-line
`REFERENCE.md` costs more than four 100-line files of which it needs one.

Good candidates:

- Complete API surfaces: signatures, parameters, return shapes
- Exhaustive tables: error codes, config keys, status values
- Workflows longer than ~5 steps
- Domain background that only some tasks need

Reference them by relative path from the skill root, **one level deep**:

```markdown
See [the API reference](references/API.md) for response shapes.
Use [the scaffold](templates/scaffold.py) as the starting point.
```

Avoid chains — a reference that points to a reference that points to a third
costs turns and loses the thread. If two reference files always get read
together, they're one file.

## When to bundle a script

Write a script instead of instructions when:

- The agent would otherwise rewrite the same code every time
- Deterministic reliability matters — file manipulation, API calls, parsing
- The logic is complex enough that pre-tested beats freshly generated
- The operation is self-contained and can evolve on its own
- Testability matters: a script can be unit-tested, a prompt can't
- Predictable behavior is worth more than flexibility

That last group is the real argument. Even a simple operation benefits from
being a script when it will grow, needs identical behavior across invocations,
or will need extending later.

Conversely, don't bundle a script for something the agent does well natively and
that varies per project — you'll spend more maintaining the script than it saves.

## Script requirements

Prefer cross-platform languages:

| Language | Fits |
| --- | --- |
| Python | Complex automation, data processing |
| Node.js | JavaScript-based tooling |
| Bash / POSIX sh | Simple automation, glue |
| pwsh | PowerShell Core environments |

Every bundled script should:

- Document its usage, ideally behind `--help`
- Fail with a clear, actionable message — never exit 0 on failure
- Declare its dependencies, or be self-contained
- Use relative paths; never assume a machine-specific location
- Handle the edge cases the skill's instructions promise it handles

Document parameters as a table so the agent doesn't guess:

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `--input` | Yes | — | File or URL to process |
| `--action` | Yes | — | Operation to perform |
| `--verbose` | No | `false` | Enable verbose output |

## Security

- **Never store credentials or secrets.** Rely on the environment's existing
  credential helpers, and read tokens from the environment at run time.
- **Gate destructive operations** behind an explicit `--force`, and warn before
  anything irreversible.
- **Document network calls.** Say what a script contacts and why; a skill that
  silently reaches the internet is a supply-chain surprise.
- **Treat inputs as untrusted** — a script invoked by an agent gets whatever the
  conversation produced. Quote shell variables and validate before interpolating.

## License file

If the skill is published or redistributed, bundle the license text at the skill
root (conventionally `LICENSE.txt`) and reference it from the `license`
frontmatter field. Update the copyright holder and year — a stale placeholder
copyright is worse than none.
