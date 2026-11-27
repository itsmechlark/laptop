# Locale formats by library

<!-- cspell:ignore hôtel -- a French apostrophe-escaping example -->

How each i18n library stores messages, and what a translation must preserve. Find the format the repository uses, and read only that section.

Rules that hold everywhere:

- Keep every placeholder spelled exactly as in the source, but move it wherever the target grammar puts it.
- Keep markup tags balanced and their attributes untranslated.
- Insert or replace only the changed entries, at the same relative position as in the source file. Never reserialize the whole file.
- Parse the file after editing. `scripts/check-locales` parses the formats marked ✓ below.

| Library / platform | File | Placeholder | Plurals | Checker |
| --- | --- | --- | --- | --- |
| Rails I18n, Hanami | `config/locales/<lng>.yml` | `%{name}` | nested `one:`/`other:` keys | ✓ |
| ember-intl | `translations/<lng>.yaml\|json` | ICU `{name}` | ICU `{n, plural, …}` | ✓ |
| FormatJS / react-intl | `lang/<lng>.json`, extracted or compiled | ICU `{name}` | ICU | ✓ |
| i18next / react-i18next | `locales/<lng>/<ns>.json` | `{{name}}` | `key_one`, `key_other` siblings | ✓ |
| vue-i18n | `locales/<lng>.json\|yaml` | `{name}`, `@:key` | `a \| b \| c` pipes | ✓ (pipes unchecked) |
| Flutter gen-l10n | `lib/l10n/app_<lng>.arb` | ICU `{name}` | ICU | ✓ |
| Angular `@angular/localize` | `messages.<lng>.xlf` | `<x id="…"/>` | ICU inside `<target>` | ✗ |
| gettext (Phoenix, Django, Rails, PHP) | `<lng>/LC_MESSAGES/<domain>.po` | `%{name}`, `%(name)s`, `%s` | `msgstr[n]` | ✓ |
| Java / Spring | `messages_<lng>.properties` | `{0}` MessageFormat | ICU choice | ✓ |
| Android | `res/values-<lng>/strings.xml` | `%1$s`, `%d` | `<plurals>` | ✗ |
| Apple | `Localizable.xcstrings` | `%@`, `%lld`, `%1$@` | `variations.plural` | ✗ |

## Rails I18n YAML

- Root key is the locale (`ja:`). Engines and gems carry their own `config/locales`, so find them all: `git ls-files '*config/locales/*'`.
- `%{name}` interpolation; `%%` is a literal percent. A value under a `_html` key is marked safe, so keep its tags intact.
- Plurals are a hash of CLDR keys under the message. Match the set the target file already uses ([SKILL.md](../SKILL.md#gotchas) explains why the app's pluralizer decides).
- Quote a value only when YAML requires it: a leading `%`, `@`, `` ` ``, `!`, `&`, `*`, `[`, `{`, `|`, `>`, `'`, or `"`; a `: ` or ` #` inside; a bare `yes`, `no`, `on`, `off`, `true`, `false`, or `null`; a value that reads as a number or date. Follow the file's quote style. An apostrophe inside single quotes doubles (`'l''hôtel'`); double quotes are simpler for French and Italian.
- `~` (null) is a missing translation: I18n falls back to the default locale or returns "Translation missing". `""` renders nothing. Mirror a null in the source as `~`, and use `''` only where the language needs no text at all.
- Keep the source's block scalar style and chomping (`|`, `|-`, `>`, `>-`) and the file's indentation.
- `rails-i18n` already ships dates, numbers, and validation messages for most locales. Don't hand-translate keys a gem already provides unless the app overrides them.
- Repo gates: `i18n-tasks missing`, `i18n-tasks normalize`, and the `i18n-tasks` spec when present.

## ICU MessageFormat (ember-intl, FormatJS, Flutter, Angular inside `<target>`)

- `{name}` is an argument. `{n, plural, one {# seat} other {# seats}}` is a plural. Translate only the text inside the branches.
- `plural`, `select`, `selectordinal`, the selector keywords (`zero one two few many other`, `=0`, `=1`, the select values) and `#` stay as-is. `other` is mandatory.
- A target language needs only the plural branches its CLDR rule uses. Japanese needs just `other`; Arabic uses all six. Keep exact-match branches (`=0`) whenever the source has them.
- An apostrophe escapes syntax: `'{'` is a literal brace, and `''` is a literal apostrophe. French and Italian text needs `''` wherever an apostrophe sits next to a brace.
- FormatJS extracted files wrap each message as `{"defaultMessage": "...", "description": "..."}`. The description is translator context; translate `defaultMessage` only. A compiled file (an AST of arrays) is a build artifact. Translate the source catalog and recompile; never edit the AST.
- Flutter ARB: `@key` entries hold the `description` and `placeholders` metadata. Keep them in the source `.arb` only; target `.arb` files carry `@@locale` and the messages. Gate: `flutter gen-l10n`.
- ember-intl gate: `ember intl:missing`, or its lint, where it is configured.

## i18next JSON

- `{{name}}` interpolation, `{{- name}}` unescaped, and `{{value, format}}` formatted. `$t(other.key)` nests another message and stays as-is.
- Plurals are sibling keys suffixed `_zero _one _two _few _many _other` (v21+ JSON format v4). Older `key_plural` and `key_0` files are format v3; follow whichever the file uses. Context variants (`key_male`) also stay as-is.
- `<0>text</0>` and `<strong>` in Trans components: keep the numbered tags and their nesting.
- Namespaces are separate files per locale. The new keys may live in a namespace other than `translation.json`.

## vue-i18n

- `{name}` named and `{0}` list interpolation. `@:key` and `@.lower:key` link other messages and stay as-is.
- Plurals are pipe-separated in one string: `no apples | one apple | {count} apples`. The pipe count is by position, not by CLDR form, so keep the source's count. The checker does not verify pipes; compare them by eye.
- A literal `@`, `{`, `}`, `|` needs `{'@'}` literal syntax. An apostrophe is ordinary text (`l'{venue}` is fine), unlike in ICU.

## gettext `.po`

- The `msgid` is the source text; translate into `msgstr`. Never edit `msgid`. That changes the key, and the `.pot` regenerates it anyway.
- Plurals: `msgstr[0]` … `msgstr[n-1]`, where `n` is the header's `Plural-Forms: nplurals=n`. The form order follows that header's formula, not CLDR names.
- `#,` flags: remove `fuzzy` only after checking the translation. A fuzzy entry is ignored at runtime. Keep `python-format`, `elixir-format`, and the other format flags. `#.` lines are extractor comments, which serve as translator context.
- Placeholders: `%{name}` (Elixir), `%(name)s` and `%s` (Python), `{name}` (Python `str.format`), `%1$s`.
- Gate: `msgfmt --check --check-format -o /dev/null <file>.po`. Phoenix: `mix gettext.extract --merge` before translating, so every `.po` carries the new msgids.

## Java `.properties`

- `{0}` positional MessageFormat arguments. In a message that has arguments, a single quote is an escape: write `''` for an apostrophe.
- Files older than Java 9 are ISO-8859-1, with `\uXXXX` escapes for anything else. Match the existing file's encoding and escaping.

## Formats the checker does not parse

- **Angular XLIFF** (`.xlf`): translate `<source>` into `<target>` per `<trans-unit>`, and set `state="translated"` where the file uses state. `<x id="INTERPOLATION"/>` and `<x id="START_TAG_SPAN"/>` are placeholders; copy them unchanged. Gate: `ng build --localize`, or `xmllint --noout`.
- **Android `strings.xml`**: escape `'` as `\'`, and `&`/`<` as entities. `translatable="false"` entries are never translated. `<plurals>` items use CLDR quantities. Gate: `./gradlew lint`, which reports `MissingTranslation`, `ExtraTranslation`, and `StringFormatMatches`.
- **Apple String Catalog** (`.xcstrings`): one JSON file holds every locale under `strings.<key>.localizations.<lng>.stringUnit`. Set `state` to `translated`; plurals live under `variations.plural`. Edit only the locales you were asked for. The whole file is one catalog, so reformatting it touches every language, and parallel workers must return translations to one writer rather than edit it concurrently. Gate: build in Xcode.
- **Apple `.strings`** (legacy): `"key" = "value";`. Validate with `plutil -lint`.

For these, check placeholder parity by hand: list each source placeholder and confirm the target carries the same set.
