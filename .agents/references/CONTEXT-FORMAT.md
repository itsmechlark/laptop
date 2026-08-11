<!--
Root CONTEXT.md — a machine-local map of this laptop and the repos on it.

Setup: copy this template to `.agents/CONTEXT.md` (git-ignored), fill it in, and
run `mac`. `mac` symlinks it into ~/.agents and every agent client (~/.claude,
~/.codex, ~/.cursor) so they all read the same context. Delete this comment once
you've filled it in.

Scope — this is the ROOT context; it stops at the repo boundary:
  - Belongs here: repo locations, deployment URLs, shared infrastructure,
    org/account handles, and vocabulary identical across every repo.
  - Belongs in a repo's own CONTEXT.md (the domain-modeling skill): that
    project's domain glossary. Link to it from Repos; don't copy its terms up.
  - Never here: secrets, tokens, passwords. Names and URLs only.

Delete any section you don't need, and each _italic hint_ as you fill it in.
-->

# <your name>'s laptop

_One line: whose machine this is and what it's mostly used for._

> **Names, paths, and URLs only — never secrets, tokens, or passwords.**

**Last reviewed:** <YYYY-MM-DD>

## Machine

_Where the toolchain lives, so an agent doesn't have to guess._

- **OS / arch**: macOS Tahoe 26.x, Apple Silicon
- **Homebrew prefix**: `/opt/homebrew`
- **Language versions**: asdf (`~/.asdf`) — Ruby 3.x, Node 22.x
- **Code root**: `~/Codespace`

## Repos

_Every repo you work in: where it lives, what it's for, and where its own domain
glossary is. Link out — don't restate the glossary here._

| Repo | Path | Purpose | Domain glossary |
| --- | --- | --- | --- |
| example-api | `~/Codespace/example-api` | Rails booking backend | its `CONTEXT.md` |
| example-web | `~/Codespace/example-web` | React/TS storefront | its `CONTEXT.md` |

## Environments

_How to reach each app, per environment. URLs only._

| App | Local | Staging | Production |
| --- | --- | --- | --- |
| example-api | http://localhost:3000 | https://staging.example.com | https://app.example.com |
| example-web | http://localhost:5173 | https://staging.web.example.com | https://www.example.com |

## Services & accounts

_Shared infrastructure and where to find it — identifiers, never credentials._

- **Error tracking**: Sentry — `<org>`
- **CI**: GitHub Actions
- **Issue tracker**: Jira — `<site>.atlassian.net`, project keys `<KEY>`
- **Chat**: Slack — `<workspace>.slack.com`
- **Git host / org**: GitHub — `<org>`

## Shared vocabulary

_Only terms that mean the same thing in **every** repo. Anything repo-specific
belongs in that repo's `CONTEXT.md`._

**<Term>**:
<One or two sentences: what it is.>
_Avoid_: <synonyms not to use>
