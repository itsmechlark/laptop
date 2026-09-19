# The security axis

Four questions, in this order. The first one decides how much the rest matter:
an injection sink in a workflow with no secrets and a read-only token is a
different finding from the same sink on `pull_request_target`.

## 1. What privilege does each trigger carry?

| Trigger | Who can fire it | `GITHUB_TOKEN` | Secrets | Risk |
| --- | --- | --- | --- | --- |
| `push` | Collaborators | read/write | yes | Low — trusted authors |
| `pull_request`, same-repo branch | Collaborators | read/write | yes | Low |
| `pull_request` **from a fork** | Anyone | **read-only** | **no** | Low by design |
| `pull_request_target` | Anyone with a fork | read/write | yes | **High** |
| `workflow_run` | Fires after another workflow | read/write | yes | **High** |
| `issue_comment`, `issues` | Anyone | read/write | yes | **High** |

The trap is the fork row. It is safe *because* GitHub strips the token and
withholds secrets, so a maintainer who needs a secret on fork PRs finds it
missing and switches to `pull_request_target` — handing a write token and every
secret to arbitrary contributors. Read a `pull_request_target` as evidence
someone already hit this.

One repository setting reopens the fork row without any `pull_request_target`:
**Settings → Actions → General → "Send secrets to workflows from fork pull
requests"** and its write-token companion. Both are off by default; if either is
on, fork `pull_request` runs get secrets or a write token and the row is no
longer low-risk. It is an Actions-settings finding, not a YAML one, so it belongs
in its own recommendation rather than mixed with a workflow edit — the user
changes it in the UI, and only they can.

### Why `pull_request_target` is dangerous

It checks out the *base* repository's workflow definition, so a fork cannot
change what runs — and it runs with full privilege. The danger is a workflow
that then explicitly checks out the fork's code and executes it:

```yaml
# DANGEROUS — RCE against a write token and every secret
on: pull_request_target
jobs:
  build:
    steps:
      - uses: actions/checkout@<sha>
        with:
          ref: ${{ github.event.pull_request.head.sha }}   # the fork's code
      - run: npm install && npm test                        # runs it
```

`npm install` alone runs lifecycle scripts from the PR. Under
`pull_request_target` those scripts read `secrets.*` and push with the token.

### The two-workflow fix

An unprivileged workflow runs the untrusted code; a privileged one consumes
only its output, as data.

```yaml
# 1) Unprivileged — runs untrusted code, read-only token, no secrets
on: pull_request
permissions:
  contents: read
jobs:
  build:
    steps:
      - uses: actions/checkout@<sha>
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@<sha>
        with: { name: pr, path: dist/ }
```

```yaml
# 2) Privileged — triggered by the first, never runs fork code
on:
  workflow_run:
    workflows: ["PR Build"]
    types: [completed]
permissions:
  pull-requests: write
jobs:
  comment:
    steps:
      - uses: actions/download-artifact@<sha>   # data only, never executed
```

Labelling, commenting, or sorting on event *metadata* under a privileged
trigger is fine. Running the contributor's code is not.

## 2. Where does untrusted input reach a shell?

`${{ <expr> }}` is substituted into the script as text before the shell runs, so
any expression resolving to contributor-controlled data is a command-injection
sink. These are the contexts an outsider sets:

| Context | Set by |
| --- | --- |
| `github.event.issue.title` / `.body` | Issue author |
| `github.event.pull_request.title` / `.body` | PR author |
| `github.event.pull_request.head.ref` / `.head.label` | PR author (branch name) |
| `github.head_ref` | PR author (branch name) |
| `github.event.comment.body` | Commenter |
| `github.event.review.body` / `.review_comment.body` | Reviewer |
| `github.event.commits.*.message`, `head_commit.message` | Commit author |
| `github.event.commits.*.author.email` / `.name` | Commit author |
| `github.event.pages.*.page_name` | Wiki editor |

A branch named `$(<attacker-command>)`, or an issue titled `"; <attacker-command> #`,
becomes shell.

```yaml
# VULNERABLE
- run: |
    echo "Reviewing: ${{ github.event.pull_request.title }}"
    git checkout ${{ github.head_ref }}

# SAFE — ${{ }} appears only on the env: side, assigned as a value
- env:
    PR_TITLE: ${{ github.event.pull_request.title }}
    HEAD_REF: ${{ github.head_ref }}
  run: |
    echo "Reviewing: $PR_TITLE"
    git checkout "$HEAD_REF"
```

Always quote the shell variable, or word-splitting and globbing reopen part of
the hole.

`actions/github-script` takes the same rewrite — pass through `env:` and read
`process.env.TITLE`, never interpolate into `script:`. For a composite or JS
action's `with:` inputs, whether interpolation is safe depends on what the
action does with the input; pass through `env:` when in doubt, or validate first
(a branch name should match `^[A-Za-z0-9._/-]+$`).

**Audit method:** grep every `run:` and `script:` for `${{`, resolve what each
expression points at, and rewrite any that a non-collaborator can set.
Server-controlled values — `github.actor`, `github.repository`, `github.sha` —
are not attacker-set, though the `env:` rewrite costs nothing there either.

### The other sink: `$GITHUB_ENV` and `$GITHUB_OUTPUT`

A step does not have to interpolate `${{ }}` to inject. Appending
attacker-controlled data to the `$GITHUB_ENV` or `$GITHUB_OUTPUT` files sets
variables that *every later step in the job* runs under, and a multiline value
carries its own `KEY=value` lines:

```yaml
# VULNERABLE — a PR body of "innocent\nLD_PRELOAD=/tmp/evil.so" sets LD_PRELOAD
- run: echo "TITLE=${{ github.event.pull_request.body }}" >> "$GITHUB_ENV"
```

The classic payloads are `LD_PRELOAD`, `NODE_OPTIONS`, and `PATH` — each turns a
later step's normal command into code execution. The fix is a heredoc with a
random delimiter the value cannot guess, so injected newlines cannot close it:

```yaml
- env:
    BODY: ${{ github.event.pull_request.body }}
  run: |
    {
      echo "TITLE<<__EOF_$(openssl rand -hex 16)__"
      echo "$BODY"
      echo "__EOF_$(openssl rand -hex 16)__"
    } >> "$GITHUB_ENV"
```

Better still, do not route untrusted input through `$GITHUB_ENV` at all — keep it
in a step-scoped `env:` var. Grep for `>> "$GITHUB_ENV"` and `>> "$GITHUB_OUTPUT"`
the same way you grep for `${{`.

## 3. How wide is the token?

The `GITHUB_TOKEN`'s scope is the blast radius when a step is compromised. With
no `permissions:` block the workflow inherits the repository default, which on
older or permissive repos is write to most scopes.

```yaml
permissions: {}          # deny by default at the top

jobs:
  build:
    permissions:
      contents: read     # checkout only
  comment:
    permissions:
      contents: read
      pull-requests: write   # this job posts a comment; nothing else
```

Scopes are `contents`, `pull-requests`, `issues`, `actions`, `packages`,
`id-token`, `deployments`, `checks`, `statuses`; each `read`, `write`, or `none`.

| Finding | Severity |
| --- | --- |
| No `permissions:` block anywhere | MEDIUM |
| `permissions: write-all` | HIGH |
| A `write` scope the job's steps never use | HIGH |
| Top-level `write` that belongs on one job | MEDIUM |

**OIDC over stored cloud keys.** A leaked `AWS_ACCESS_KEY_ID` is valid until
someone rotates it; an OIDC token expires in minutes and is scoped to the repo.

```yaml
permissions:
  id-token: write        # required to request the token
  contents: read
steps:
  - uses: aws-actions/configure-aws-credentials@<sha>
    with:
      role-to-assume: arn:aws:iam::123456789012:role/my-ci-role
      aws-region: us-east-1
```

Equivalents exist for Azure, GCP, and Vault. Scope the cloud-side trust policy
to the repository and, where available, the branch or environment — otherwise
another repo can assume the role.

**Secret hygiene:** reference secrets only in the jobs that need them; never
`echo` one or enable `set -x` in a step that handles one; never pass one to an
unpinned third-party action.

**Reusable workflows and `secrets: inherit`.** A `uses: ./.github/workflows/x.yml`
or `uses: org/repo/.github/workflows/x.yml@ref` call can forward secrets two ways.
`secrets: inherit` passes *every* secret the caller can see to the called
workflow — fine for a first-party workflow in the same repo, a needless blast
radius for a third-party one. Prefer naming the secrets the callee actually needs:

```yaml
jobs:
  deploy:
    uses: org/shared/.github/workflows/deploy.yml@<sha>
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}   # not: secrets: inherit
```

A third-party reusable workflow is someone else's code running with your secrets
and token, exactly like a third-party action — pin it to a SHA (§4), never a
mutable tag or branch.

## 4. Whose code is this running?

Every `uses:` runs someone else's code with your token, so their integrity is
yours.

```yaml
- uses: some-org/some-action@v3    # mutable — the tag can be moved
- uses: some-org/some-action@3f1e0a9c8b7d6e5f4a3b2c1d0e9f8a7b6c5d4e3f # v3.2.1
```

- Third-party (not `actions/*` or `github/*`) on a tag or branch → **HIGH**.
- `@main` or `@master` → **HIGH** regardless of publisher; that is "latest".
- First-party `actions/*` tag-pinned → LOW; SHA is the hardened recommendation.
- Keep the trailing `# vX.Y.Z` so a human and Dependabot can read the intent.

This is not hypothetical — popular actions have had tags repointed at code that
exfiltrated secrets from every workflow referencing the mutable tag.

Pins go stale, so pair any pinning finding with Dependabot rather than leaving
the repo frozen:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

**Artifacts and caches cross the trust boundary.** An artifact built by an
untrusted `pull_request` is untrusted data: a privileged `workflow_run` may
download it but must never execute it, and should validate paths on extraction
(a crafted artifact can carry `../` entries). Caches can be populated by
less-privileged runs, so cached build output is not trustworthy in a privileged
context.

**Self-hosted runners persist.** GitHub-hosted runners are a fresh VM per job,
destroyed after. A self-hosted one running fork code can leave tools behind for
the next job, read other checkouts and credentials on the machine, and pivot
into the network. Never let a public fork's PR reach one; if unavoidable, use
ephemeral single-use runners and keep secrets away from fork-triggered jobs.

**`actions/checkout` persists credentials** into `.git/config` by default so
later `git` steps can push. Set `persist-credentials: false` in any job that
does not push, especially before it builds or tests untrusted code.
