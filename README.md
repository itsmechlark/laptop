Laptop
======

Laptop is a script to set up a macOS laptop for web and mobile development.

It can be run multiple times on the same machine safely.
It installs, upgrades, or skips packages
based on what is already installed on the machine.

Requirements
------------

We support:

* macOS Tahoe (26.x) on Apple Silicon and Intel
* macOS Sequoia (15.x) on Apple Silicon and Intel

Older versions may work but aren't regularly tested.
Bug reports for older versions are welcome.

Install
-------

Clone this repository to a stable location and enter it.
`mac` symlinks directories out of the checkout
(`.agents/`, `rules/`, `skills/`, and the client config) into your home,
so the clone has to stay put:

```sh
git clone https://github.com/itsmechlark/laptop.git
cd laptop
```

Review the script (avoid running scripts you haven't read!):

```sh
less mac
```

Execute the script:

```sh
sh mac 2>&1 | tee ~/laptop.log
```

Optionally, review the log:

```sh
less ~/laptop.log
```

Keep the checkout up to date with `git pull`.
Because `mac` links it rather than copying,
edits to linked rules and skills take effect immediately;
re-run `sh mac` only to pick up new packages or a newly added link.

Optionally, [install thoughtbot/dotfiles][dotfiles].

[dotfiles]: https://github.com/thoughtbot/dotfiles#install

Debugging
---------

Your last Laptop run will be saved to `~/laptop.log`.
Read through it to see if you can debug the issue yourself.
Keep the lines where the script failed — they're the useful part.

What it sets up
---------------

macOS tools:

* [Homebrew] for managing operating system libraries.
* [GPG Suite] for signing commits and encrypting files

[Homebrew]: http://brew.sh/
[GPG Suite]: https://gpgtools.org/

Unix tools:

* [fzf][] for better command history searching
* [Universal Ctags] for indexing files for vim tab completion
* [Git] for version control
* [OpenSSL] for Transport Layer Security (TLS)
* [RCM] for managing company and personal dotfiles
* [reattach-to-user-namespace] for using the macOS clipboard from inside tmux
* [The Silver Searcher] for finding things in files
* [Tmux] for saving project state and switching between projects
* [Vim] for editing text
* [Watchman] for watching for filesystem events
* [Zsh] as your shell

[fzf]: https://github.com/junegunn/fzf
[Universal Ctags]: https://ctags.io/
[Git]: https://git-scm.com/
[OpenSSL]: https://www.openssl.org/
[RCM]: https://github.com/thoughtbot/rcm
[reattach-to-user-namespace]: https://github.com/ChrisJohnsen/tmux-MacOSX-pasteboard
[The Silver Searcher]: https://github.com/ggreer/the_silver_searcher
[Tmux]: http://tmux.github.io/
[Vim]: https://www.vim.org/
[Watchman]: https://facebook.github.io/watchman/
[Zsh]: http://www.zsh.org/

GitHub tools:

* [GitHub CLI] for interacting with the GitHub API

[GitHub CLI]: https://cli.github.com/

Development tools:

* [CSpell] for spell-checking code and prose
* [Gitleaks] for catching secrets in a diff before they are committed
* [Trivy] for scanning dependencies and images for vulnerabilities
* [1Password CLI] for reading secrets without pasting them
* [Claude Code] and [Codex] for agentic coding

[CSpell]: https://cspell.org
[Gitleaks]: https://gitleaks.io/
[Trivy]: https://trivy.dev/
[1Password CLI]: https://developer.1password.com/docs/cli/
[Claude Code]: https://claude.com/product/claude-code
[Codex]: https://developers.openai.com/codex/cli/

Image tools:

* [ImageMagick] for cropping and resizing images

PDF tools:

* [Poppler] for rendering and extracting text from PDFs

[Poppler]: https://poppler.freedesktop.org/

Programming languages, package managers, and configuration:

* [asdf-vm] for managing programming language versions
* [Bundler] for managing Ruby libraries
* [Coreutils] for the GNU versions of core Unix utilities
* [libyaml] for parsing YAML, needed to build Ruby
* [Node.js] and [npm], for running apps and installing JavaScript packages
* [Ruby] stable for writing general-purpose code
* [Yarn] for managing JavaScript packages
* [Rosetta 2] for running tools that are not supported in Apple silicon processors

[Bundler]: http://bundler.io/
[Coreutils]: https://www.gnu.org/software/coreutils/
[libyaml]: https://pyyaml.org/wiki/LibYAML
[ImageMagick]: http://www.imagemagick.org/
[Node.js]: http://nodejs.org/
[npm]: https://www.npmjs.org/
[asdf-vm]: https://github.com/asdf-vm/asdf
[Ruby]: https://www.ruby-lang.org/en/
[Yarn]: https://yarnpkg.com/en/
[Rosetta 2]: https://developer.apple.com/documentation/apple-silicon/about-the-rosetta-translation-environment

Databases:

* [Postgres] for storing relational data
* [Redis] for storing key-value data

[Postgres]: http://www.postgresql.org/
[Redis]: http://redis.io/

It should take less than 15 minutes to install (depends on your machine).

Customize in `~/.laptop.local`
------------------------------

Your `~/.laptop.local` is run at the end of the Laptop script.
Put your customizations there.
For example:

```sh
#!/bin/sh

brew bundle --file=- <<EOF
brew "Caskroom/cask/dockertoolbox"
brew "go"
brew "ngrok"
brew "watch"
EOF

default_docker_machine() {
  docker-machine ls | grep -Fq "default"
}

if ! default_docker_machine; then
  docker-machine create --driver virtualbox default
fi

default_docker_machine_running() {
  default_docker_machine | grep -Fq "Running"
}

if ! default_docker_machine_running; then
  docker-machine start default
fi

fancy_echo "Cleaning up old Homebrew formulae ..."
brew cleanup

if [ -r "$HOME/.rcrc" ]; then
  fancy_echo "Updating dotfiles ..."
  rcup
fi
```

Write your customizations such that they can be run safely more than once.
See the `mac` script for examples.

Laptop functions such as `fancy_echo` and
`gem_install_or_update`
can be used in your `~/.laptop.local`.

See the [wiki](https://github.com/thoughtbot/laptop/wiki)
for more customization examples.

Machine & fleet context (`.agents/CONTEXT.md`)
----------------------------------------------

Drop an optional `.agents/CONTEXT.md` to give every agent client a shared,
machine-local map of this laptop and the repos on it —
where each repo lives, its deployment URLs,
and the vocabulary that means the same thing across projects.
Copy the template to start:

```sh
cp .agents/references/CONTEXT-FORMAT.md .agents/CONTEXT.md
```

Fill it in, then run `mac` again.
The file is git-ignored — it holds names, paths, and URLs, never secrets —
and `mac` symlinks it into `~/.agents`, `~/.claude`, `~/.codex`, and `~/.cursor`
so all three clients read the same context.
Per-repo domain glossaries stay in each repo's own `CONTEXT.md`;
this one stops at the repo boundary.

Standup journal (`.agents/standup/`)
------------------------------------

`mac` creates `.agents/standup/` and links it to `~/.agents/standup`,
where the `standup` skill keeps one dated Markdown file per update.
It reads the most recent one before writing the next,
so it can point out work that has sat in "in progress" for three days
and dates promised last time that nobody has mentioned since.

Nothing to set up — the directory is created on the first `mac` run,
and the skill prunes entries older than 14 days.
It is git-ignored, and that matters:
the entries are client-facing status in plaintext
inside a repository that gets pushed.
All three clients grant write access to that one path,
which is why the skill needs no per-client configuration.

Cross-repo rejections (`.agents/out-of-scope/`)
-----------------------------------------------

`mac` creates `.agents/out-of-scope/` and links it to `~/.agents/out-of-scope`,
wired exactly like the journal above and for the same reason.
The `triage` skill writes a file here when it rejects a request
for a reason that belongs to no single project —
a standing policy such as "no telemetry",
which would otherwise be argued again in every repository.
It sits beside `skills` and `standup` rather than under a skill
because `slice` and `draft-spec` read it too,
before they propose work that may already have been declined.

Rejections grounded in a particular codebase do not go here.
Those belong in that repository's own `.out-of-scope/`, committed,
where a co-maintainer and the next reporter can read them.
Triage checks both places before deciding anything is new.

Unlike the journal, nothing here is pruned:
the reasoning is meant to outlive the ticket that prompted it.

Contributing
------------

Thank you, [contributors]!

[contributors]: https://github.com/thoughtbot/laptop/graphs/contributors

By participating in this project,
you agree to abide by the thoughtbot [code of conduct].

[code of conduct]: https://thoughtbot.com/open-source-code-of-conduct

Edit the `mac` file.
Document in the `README.md` file.
Follow shell style guidelines by using [ShellCheck] and [ALE] or deprecated [Syntastic].
Prose and config are spell-checked with [CSpell], configured by `cspell.json`.
`mac` installs CSpell for you; ShellCheck it does not.

```sh
brew install shellcheck cspell
```

[ShellCheck]: http://www.shellcheck.net/about.html
[Syntastic]: https://github.com/scrooloose/syntastic
[ALE]: https://github.com/dense-analysis/ale


### Testing your changes

Two things need verifying, and which one depends on what you touched. Spelling
is checked across both.

**Changes to `mac`** are tested by running the script on a fresh install of
macOS. You can use the free and open source emulator [UTM].

Tip: Make a fresh virtual machine with the installation of macOS completed and
your user created and first launch complete. Then duplicate that machine to test
the script each time on a fresh install that's ready to go.

**Changes to the agent configuration** — anything under `skills/`, `rules/`, or
the per-client config directories — are tested by `check-payload`. No VM
required:

```sh
shellcheck mac -e SC2039
shellcheck scripts/check-payload
sh scripts/check-payload
```

Both must exit zero before you open a pull request; CI runs them on every PR in
a job of their own. Warnings are advisory and may stand. Failures may not.

A skill or rule adapted from someone else's work has to carry both halves of its
provenance: an entry in `skills-provenance.json` or `rules-provenance.json`, and
a matching `## Attribution` section last in the file, one bullet per recorded
source in the recorded order. `check-payload` fails when the two disagree, so
write them together rather than leaving one as a follow-up.

**Spelling** is checked separately, across every file rather than just the
payload:

```sh
cspell lint --no-progress --dot "**/*"
```

`--dot` is what reaches the per-client config directories; leave it off and most
of the repo goes unchecked. CI runs this in the same job as `check-payload`, so
a misspelling fails the build. Spelling is US English — fix a British spelling in the
prose rather than adding it to `cspell.json`. A genuine project word belongs in
that file's `words` list; a deliberate fragment, like a truncated example,
belongs in a `cspell:ignore` comment beside the line it excuses.

`check-payload` reads its fixtures from `spec/`:

* `spec/rules-cases.txt` — which `rules/` files load for a given path,
  so a typo in a `paths:` glob fails loudly instead of silently never matching
* `spec/invocability-fixture/` and `spec/orphan-fixture/` — deliberate
  violations that prove the checks still fire, one for cross-skill handoffs and
  one for `references/` files nothing links plus links into headings that no
  longer exist. Their contents are assertions, not examples; leave them broken.
  The handoff check covers `rules/` too, and reads four kinds of broken handoff:
  invoking a user-invoke-only skill, calling an invocable one user-invoke-only,
  and naming a "skill" that is really a `rules/` file or does not exist at all.
  The anchor check is what catches a `#section` link left behind by a rename —
  the resource-link check only proves the *file* is there
* `spec/trigger-evals/*.json` — query sets for whether a skill's description
  fires on the requests it should. These need a live model, so they are not part
  of CI — run them with `sh scripts/run-trigger-evals` (all sets) or
  `sh scripts/run-trigger-evals slice` (one), with a logged-in `claude` CLI. To
  iterate on a single query, set `EVAL_QUERY` to a substring of it —
  `EVAL_QUERY="party size" sh scripts/run-trigger-evals domain-modeling` runs
  only the matching queries and writes to `<skill>.subset.json`, leaving the
  full-set artifact intact

Adding a fixture adds an assertion, and `check-payload` validates the fixtures
themselves — an eval set with no negatives, duplicate queries, or a name that
matches no skill is a failure, because it could never catch anything.

[UTM]: https://mac.getutm.app

License
-------

Copyright © 2011-2025 thoughtbot, inc.
Copyright © 2020-2026 itsmechlark.
It is free software,
and may be redistributed under the terms specified in the [LICENSE] file.

[LICENSE]: LICENSE
