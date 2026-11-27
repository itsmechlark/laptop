---
name: translate-locales
description: Translate new or changed i18n strings from the source locale into every other locale an app ships, keeping placeholders, plural forms, markup, and established terminology intact — Rails I18n YAML, ICU messages (ember-intl, FormatJS/react-intl, Flutter ARB), i18next and vue-i18n JSON, gettext .po, Java .properties, and the XML and string-catalog formats. Use when asked to translate new keys, fill in missing translations, sync locale files after editing en.yml or en.json, localize a feature, or check translations for broken placeholders, mixed scripts, or plural-form drift. Not for wiring lookups into code, and not for translating prose documents.
argument-hint: "[keys, base ref, locales, or extra context]"
---

# Translate locales

Carry new and changed source-locale strings into every other locale file an app ships, in the register each language expects, without breaking the placeholders, plurals, and markup the runtime depends on.

Extra context from the invocation: `$ARGUMENTS`.

## When to use this skill

- A change added or reworded strings in the source locale (`en.yml`, `en.json`, `messages.pot`) and the other locales are behind
- Filling every gap in a locale file, or bootstrapping the keys of one feature across all locales
- Auditing existing translations for defects a reader cannot see — a renamed placeholder, a Latin letter inside a Cyrillic word, a translated ICU keyword, a plural set the runtime will not pick
- Not for moving hardcoded strings into the i18n layer: that is ordinary code work, and this skill starts once the source-locale keys exist
- Not for README, docs, or marketing pages: those are prose, with no key structure to preserve

## Gotchas

- **A changed source string makes every existing translation stale.** A key that is present in a target file is not necessarily done. When the English value changed, retranslate it everywhere, unless the change cannot alter the meaning (a typo or punctuation fix). List the keys you decided not to retranslate, and why.
- **A deleted key plus an added key with the same source text is a rename.** Move the existing translations to the new path. Don't delete them and machine-translate from scratch, which throws away work a human may have reviewed.
- **Never round-trip a locale file through a YAML or JSON dumper.** `YAML.dump`, `yaml.safe_dump`, and `JSON.stringify` rewrite quoting, line wrapping, key order, comments, and anchors on every line of a file that can run to 15,000 lines. Insert or replace only the changed entries as text, then parse the file to prove it still loads. The one exception is a repo that runs its own normalizer (`i18n-tasks normalize`, a TMS export with a fixed sort); run that tool instead.
- **The plural forms a file needs come from the app's pluralizer, not from CLDR alone.** Plain Rails I18n without `rails-i18n` picks `:one` or `:other` for every locale, so a CLDR-correct Japanese entry with only `other` raises on `count: 1`. With a CLDR backend, Arabic needs all six forms. The evidence is the set the target file already uses for most of its plurals. Match that set, and let the checker flag drift.
- **Homoglyphs, decomposed accents, and zero-width characters are invisible in review.** A model writing Russian slips Latin `a e o p c x` into Cyrillic words, or writes the preposition "с" as a Latin `c`. Run `scripts/check-locales` on every file you touch; reading the diff will not catch them.
- **Null is not empty.** In Rails and i18next a null value counts as missing: the lookup falls back to the default locale or reports a missing translation. `""` renders nothing. Copy a null from the source as null, and write `""` only where the target language genuinely needs no text.
- **Never translate the machinery:** placeholders (`%{name}`, `{name}`, `{{name}}`, `%(name)s`, `%1$s`), ICU keywords (`plural`, `select`, `one`, `other`, `=0`) and `#`, HTML tags and attributes, i18next `$t(...)`, vue-i18n `@:key` links, Lokalise `[%key:...%]` references, URLs, and brand names. Translating `other` inside an ICU message breaks it at runtime.
- **The target file's terminology beats your preference.** If `de.yml` says "Buchung" for "booking" two hundred times, don't introduce "Reservierung". Build the glossary from the existing files before translating, and give it to every worker.
- **Grepping for the key misses most of its uses.** Rails lazy lookup (`t(".title")`), model-attribute and validation keys that no code spells out, and dynamic keys (`t("statuses.#{status}")`) all reach the locale file without the key appearing in the source. A key with no grep hit is not proof it's dead, and the source text alone doesn't say whether "Book" is a verb or a noun. Trace the usage before translating.
- **A fragment composed at runtime may be untranslatable as written.** `"%{count} %{unit} left"` with a noun inserted cannot agree in case (Russian), gender (French), or particle (Japanese) for every value. Report it as a composition warning, with the key, the locale, and the grammar that breaks. Don't paper over it with an awkward translation.
- **A translation management system may own the target files.** With Lokalise, Crowdin, Phrase, or Transifex configured, the next pull can overwrite a hand-edited file. Read the config for facts (locale list, excluded keys, which locales humans maintain), and say in the report that the edits need to reach the TMS too.
- **Existing FAILs in a file are not yours to fix unasked.** Large locale files carry legacy defects. Scope the checker with `--keys-file` to the keys you wrote; report anything older as a finding, not an edit.

## Workflow

### 1. Discover the setup

Read before writing. None of this should be assumed, because each repository answers differently:

- **Source locale and files** — the format and the file layout: Rails `config/locales/*.yml`, plus `engines/*/config/locales` and `packages/*/` in a monorepo, and translations kept beside components (ViewComponent sidecar YAML, Vue `<i18n>` blocks); `translations/` (ember-intl); `public/locales/<lng>/<ns>.json` (i18next); `lib/l10n/*.arb` (Flutter); `priv/gettext/<lng>/LC_MESSAGES/*.po` (Phoenix); `locale/<lng>/LC_MESSAGES/django.po`; `res/values-<lng>/strings.xml` (Android); `*.xcstrings` (Apple). Each format's rules are in [FORMATS.md](references/FORMATS.md).
- **Base ref** — `git symbolic-ref refs/remotes/origin/HEAD` names the default branch; diff against the merge-base with its remote-tracking form (`origin/develop`), never a stale local branch.
- **Tooling and its config** — `config/i18n-tasks.yml`, or a Lokalise, Crowdin, or Phrase config. These list the shipped locales, the excluded key patterns, and which locales humans maintain.
- **Translator context** — ARB `@key.description`, FormatJS `description`, gettext `#.` extracted comments, or a translator-notes file kept beside the locales. These carry the length limits and tone notes that grepping call sites only guesses at.
- **Product voice** — the repo's `CONTEXT.md` glossary, `BRAND.md`, `DESIGN.md`, and README: who the end users are, the voice and tone the brand guide sets, which product and feature names stay untranslated, and the length and casing limits the design system puts on labels and buttons. A consumer app writes to its customers differently than an admin console writes to staff. Where `BRAND.md` defines the voice per language, it outranks [LANGUAGES.md](references/LANGUAGES.md); the existing locale file still outranks both on terminology.

### 2. Build the change set

Diff the source locale against the base. Sort every key into exactly one bucket: **new**, **changed** (stale everywhere), **renamed** (move translations), **deleted**, or **unchanged but missing** in some locale (gap fill). For each locale, record which keys it needs.

For each key to translate, trace how the application uses it: translator notes first, then every call site, found the way its framework actually references keys ([USAGE.md](references/USAGE.md)). Record one line per key covering:
- the sense it is used in (verb, noun, or state)
- the surface it renders on, and the audience reading it
- what fills each placeholder
- the length limit and markup handling
- whether it is concatenated with other keys or reused in several places

Report a key with no call site as dynamic, convention-driven, or dead. Report a reused key whose uses need different words as one to split.

Build the glossary: the product's domain terms in this change set, and how each target file already renders them.

**Stop and show the change set** — the keys to translate with their context, the renames, the deletions, and any key you are deliberately skipping. Apply deletions and renames only after the user confirms.

### 3. Translate

- **A handful of keys into a few locales:** do it inline.
- **Otherwise, one worker per locale, all dispatched in one response.** `fan-out` covers the dispatch. Each worker gets a brief filled in from [templates/worker-brief.md](templates/worker-brief.md): the change set, the glossary for its language, its rules from [LANGUAGES.md](references/LANGUAGES.md) with the address form and locale variant already decided, and its format's section of [FORMATS.md](references/FORMATS.md). A worker without the Skill tool can't read this file by name, so the brief must stand on its own.
- **Past ~50 keys, batch them in ~30s.** Run the batches one after another, with all locales in parallel within a batch, so no worker's context overflows.

Each worker edits only its own locale's file, so parallel workers never touch the same file. A catalog that holds every locale in one file (`.xcstrings`, a multi-language XLIFF) breaks that: there, workers return their translations instead of editing, and one writer applies them all.

### 4. Verify

Run the checker over every touched file, scoped to the keys that changed:

```sh
printf '%s\n' <changed keys> > "$TMPDIR/keys.txt"
ruby <this skill>/scripts/check-locales --source config/locales/en.yml \
  --keys-file "$TMPDIR/keys.txt" config/locales/*.yml
```

It parses YAML, JSON, ARB, `.po`/`.pot`, and `.properties` on any Ruby from 2.6 up, stdlib only, and skips the source file if the glob includes it. List the keys as the source names them, as dotted paths; a leading locale root (`en.`) and an i18next plural suffix (`_one`, `_other`) are folded in. A listed key the source doesn't have stops the run with exit 2 rather than checking nothing.

Every FAIL in scope gets fixed:
- a listed key that is missing, empty, or null in a target
- a parse error
- a placeholder, `$t()` nesting, vue-i18n link, or Lokalise reference that drifted, or a plural `other` form that dropped one
- a broken ICU message: a translated keyword, select options that differ from the source, a missing `other`
- a lone apostrophe in a `.properties` MessageFormat pattern
- a mixed-script word, or a lone Latin lookalike between Cyrillic words
- a non-NFC string or a stray zero-width character
- a plural without `other`, or a `.po` form count that disagrees with `Plural-Forms`

Read each WARN and decide: changed HTML tags, an empty string, a translation identical to the source, a plural set unlike the rest of the file, a gettext `fuzzy` flag. ICU apostrophe quoting applies to `.arb` files, and to any source with typed ICU arguments; force it either way with `--icu` or `--no-icu`. For XML and string-catalog formats the checker does not parse, use the checks in [FORMATS.md](references/FORMATS.md).

Then run the repo's own gates: `i18n-tasks missing` and `i18n-tasks normalize --pattern=<changed files>` where i18n-tasks is installed, `msgfmt --check` for gettext, and the i18n specs if the suite has them.

### 5. Report

- The keys updated, with their English values, and the per-locale count
- Renames moved and deletions applied
- Keys deliberately not retranslated, each with its reason
- Keys with no call site (dynamic, convention-driven, or dead), and reused keys that should be split
- Composition warnings, when there are any
- Checker results: FAILs fixed, WARNs left with the reason, and legacy defects found outside the change set
- Whether a TMS needs the edits pushed

## Auditing existing translations

Run the checker over whole files with no `--keys-file`, and with `--max 0` to see every finding. Group the findings by check, then by locale. Lead the report with the FAIL categories, because those break at runtime or render wrong. Terminology drift (a glossary term rendered two ways in one file) is the one check the script cannot make; sample it by grepping the source terms. Report only, and edit nothing until the user picks what to fix.

## References

Read these as needed, not upfront.

- [USAGE.md](references/USAGE.md) — finding a key's call sites per framework (lazy lookup, model attributes, dynamic keys, namespaces) and what each call site tells the translation
- [FORMATS.md](references/FORMATS.md) — per library and file format: placeholder syntax, plural shape, where context lives, how to insert without reformatting, and the native validator
- [LANGUAGES.md](references/LANGUAGES.md) — when the existing file and the brand guide are silent: the decisions every language needs (address, variant, gender, length, placeholders in grammar), then per-language address forms, punctuation, and CLDR plural categories
- [templates/worker-brief.md](templates/worker-brief.md) — the per-locale brief a translation worker receives
- `scripts/check-locales` — the integrity checker; `--help` for usage

<!-- cspell:ignore Buchung Reservierung -- the German terminology example in Gotchas -->
