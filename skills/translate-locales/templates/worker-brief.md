# Translate into <LOCALE> — <PRODUCT>

You are translating new and changed interface strings into **<LANGUAGE> (<LOCALE>)** for <PRODUCT>, <one line: what it is and who reads the text>. Edit only `<TARGET FILE>`. Other workers are editing the other locales at the same time.

<!-- For a catalog holding every locale in one file (.xcstrings, multi-language XLIFF), replace the line above with: "Do not edit any file. Return your translations as a key → text table; one writer applies every locale." and drop "How to edit the file". -->

The keys file lists source keys as dotted paths. If the checker exits 2, a listed key does not exist in the source. Report that; don't edit around it.

## Keys

<!-- One row per key. "Status": new / changed (the existing translation is stale) / gap. "Used as" and "Inserted values" come from tracing the key's call sites. -->

| Key | Source (<SOURCE LOCALE>) | Status | Used as | Inserted values |
| --- | --- | --- | --- | --- |
| `<full.dotted.key>` | `<source value, verbatim>` | new | button, verb, customer-facing; ≤ 20 chars; also the dialog title | `%{shop}` = shop display name, untranslated |

Translate each key for the use described, not for the bare English. Where the uses listed for one key would need different words in <LANGUAGE>, or an inserted value can't fit the grammar, translate the most visible use and report it.

## Glossary — how this file already says it

| Source term | Use in <LOCALE> |
| --- | --- |
| <order> | <ご注文> |

Brand and product names that stay as written: <names>.

## How to write it

<Paste the voice and tone from BRAND.md (its section for this language, where it has one), the label length and casing limits from DESIGN.md, and from LANGUAGES.md the "Decisions every language needs" section, this language's table row, and "Script integrity", with any product decision (address form, locale variant) already resolved. BRAND.md wins where they disagree.>

<Paste the section of FORMATS.md for this file format.>

Always:

- Keep every placeholder, ICU keyword, `#`, tag, link reference, and URL exactly as written in the source. Only their position may change.
- Match the plural forms this file already uses for most of its plural entries: <the set, for example `one, other`>.
- Match the file's existing terms (above), quote style, and indentation.

## How to edit the file

1. Find each key's position: the same parent and the same relative order as in the source file.
2. Insert the new entries, or replace the stale values, as **text**. Never load and re-dump the whole file through a YAML or JSON library: that rewrites every line.
3. Parse the file once to confirm it still loads.
4. Run the checker on your keys only, and fix every FAIL:

   ```sh
   ruby <CHECKER PATH> --source <SOURCE FILE> --keys-file <KEYS FILE> <TARGET FILE>
   ```

## Report back

- Keys written (count), and any key you skipped, with the reason
- **Composition warnings**: any key where an inserted value (`%{name}`, `{count}`) cannot be grammatically right for every value in this language. Give the key and the grammar that breaks (case, gender, particle, vowel harmony).
- Checker output: FAILs fixed, and the WARNs you left with the reason
- **Usage conflicts**: keys whose listed uses need different words in this language (a candidate to split), with the word each use needs
- Anything in the source that looked wrong or ambiguous
