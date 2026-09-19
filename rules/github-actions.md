---
paths:
  - ".github/workflows/*.yml"
  - ".github/workflows/*.yaml"
  - "**/action.yml"
  - "**/action.yaml"
---

# GitHub Actions standards

What holds every time a workflow or a composite action is written. Auditing
workflows that already exist — a findings report across security and cost — is
the `github-actions` skill.

- **`${{ }}` is pasted into the script as text before the shell runs.** An
  expression carrying data an outside contributor sets is a command-injection
  sink, not a variable. Bind it to `env:` and reference the quoted shell
  variable instead:

  ```yaml
  - env:
      PR_TITLE: ${{ github.event.pull_request.title }}
    run: echo "New PR: $PR_TITLE"
  ```

  The attacker-set contexts are the ones a fork author controls:
  `github.event.issue.*`, `github.event.pull_request.*`, `github.head_ref`,
  `github.event.comment.body`, and commit messages and author fields. The same
  rule governs `actions/github-script` — pass through `env:` and read
  `process.env`, never interpolate into `script:`.
- **Writing untrusted data to `$GITHUB_ENV` or `$GITHUB_OUTPUT` is the same
  injection.** A bare `echo "KEY=$UNTRUSTED" >> "$GITHUB_ENV"` lets a multiline
  value set variables a later step runs under — `LD_PRELOAD`, `NODE_OPTIONS`.
  Validate the value, or write it with a heredoc guarded by a random delimiter,
  never a raw append.
- **Set `permissions:` explicitly.** Absent, the workflow inherits a repository
  default that may be write to everything. Start at `permissions: {}` or
  `contents: read`, then elevate per job to the one scope that job uses.
- **Treat `pull_request_target`, `workflow_run`, `issue_comment`, and `issues`
  as privileged** — they carry a read/write token and secrets, and an outside
  contributor can fire them. A privileged workflow never checks out fork code
  and runs it; `npm install` alone executes lifecycle scripts from the PR. Split
  it: an unprivileged `pull_request` job runs the untrusted code, a privileged
  one consumes its artifact as data. A fork `pull_request` is safe by design
  (read-only token, no secrets) and is not the thing to fix.
- **Pin third-party actions to a 40-character commit SHA**, with the version in
  a trailing comment so a human and Dependabot can both read it. Tags and
  branches are mutable — `@v3` and `@main` can be repointed at code that runs
  with your token.

  ```yaml
  - uses: actions/checkout@8ade135a41bc03ea155e62e844d188df1ea18608 # v4.3.1
  ```

- **Upgrading an action is one action per commit**, to the latest stable major
  that keeps current behavior, resolved to its SHA. Re-run the affected workflow
  afterwards and read the log for new deprecation warnings — a green parse is
  not a passing run.
- **Cancel superseded runs and cache dependencies.** `concurrency` grouped on
  `${{ github.workflow }}-${{ github.ref }}` with `cancel-in-progress: true`,
  and a cache key containing the lockfile hash so a dependency bump invalidates
  it.
- Set `persist-credentials: false` on `actions/checkout` in any job that does
  not push — it writes the token into `.git/config`, where later untrusted code
  can read it.
- Never echo a secret or enable shell tracing in a step that handles one, and
  keep secrets out of jobs that run untrusted code or unpinned third-party
  actions.
- **`secrets: inherit` hands a called workflow every secret.** Pass only the
  named secrets a reusable workflow needs, and pin a third-party reusable
  workflow to a SHA like any other `uses:`.
- Prefer OIDC over long-lived cloud credentials. A stored `AWS_ACCESS_KEY_ID`
  leaks permanently; a requested token expires in minutes. Scope the trust
  policy on the cloud side to the repository, and to the branch or environment
  where that is available.
- Self-hosted runners persist between jobs, so never let a public fork's PR
  reach one.
- **Validate every workflow with `actionlint`.** It parses the YAML,
  type-checks `${{ }}` expressions and context references, checks `needs:` and
  matrix wiring and runner labels, and runs shellcheck over each `run:` block —
  the mechanical errors a green-looking file still carries. It does not flag
  script injection or the trust-boundary problems above, so a clean run clears
  the syntactic floor; it does not replace the review.

## Attribution

- [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-hardening) - github-actions-hardening, MIT
- [github/awesome-copilot](https://github.com/github/awesome-copilot/tree/main/skills/github-actions-runtime-upgrade-conventions) - github-actions-runtime-upgrade-conventions, MIT
