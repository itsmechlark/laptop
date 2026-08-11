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

```sh
brew install shellcheck
```

[ShellCheck]: http://www.shellcheck.net/about.html
[Syntastic]: https://github.com/scrooloose/syntastic
[ALE]: https://github.com/dense-analysis/ale


### Testing your changes

Test your changes by running the script on a fresh install of macOS.
You can use the free and open source emulator [UTM].

Tip: Make a fresh virtual machine with the installation of macOS completed and
your user created and first launch complete. Then duplicate that machine to test
the script each time on a fresh install that's ready to go.

[UTM]: https://mac.getutm.app

License
-------

Copyright © 2011-2025 thoughtbot, inc.
Copyright © 2020-2026 itsmechlark.
It is free software,
and may be redistributed under the terms specified in the [LICENSE] file.

[LICENSE]: LICENSE
