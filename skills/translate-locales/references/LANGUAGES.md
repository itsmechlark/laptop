<!-- cspell:disable -->
# Language defaults

How to settle register, address, punctuation, and plural shape for a target language when nothing in the repository has settled it yet. Precedence, highest first:

1. **The existing locale file.** Twenty existing entries show the register, the address form, the quote style, and the terms. Match them, even where this page would choose differently.
2. **The repo's brand and design guides** (`BRAND.md`, `DESIGN.md`, a style guide in `docs/`).
3. **This page.** It encodes widely followed localization practice, not any one product's voice.

When a choice below is marked as a product decision and nothing above settles it, ask once for the whole change set rather than guessing per key.

## Decisions every language needs

**Formal or informal address.** Most languages split "you" into a formal and an informal form (the T–V distinction). The choice belongs to the product, not to the translator, and it follows the domain more than the language. Money, health, legal, government, and transactional messages lean formal. Casual consumer apps lean informal wherever the language's norm allows it. Where a language's software norm is strong, the table says so. Never mix the two forms within one product's locale file.

**Avoid the pronoun where the language allows.** Imperatives, infinitives, impersonal constructions, and noun labels ("Save changes", "Change password") sidestep both the formality question and grammatical gender. This is standard practice in Japanese, Korean, Chinese, Vietnamese, Thai, and Indonesian, and useful everywhere.

**Grammatical gender of the reader.** In languages whose verbs or adjectives agree with the person addressed (Arabic, Hebrew, Hindi, Slavic past tenses, Romance adjectives), prefer constructions that don't agree: plurals, infinitives, nouns, passive voice. Where agreement is unavoidable, follow the file's existing convention. Don't introduce slash forms or new inclusive spellings the file doesn't already use.

**Locale variants are different targets.** `es-ES` and `es-419`, `pt-PT` and `pt-BR`, `zh-Hans`/`zh-CN` and `zh-Hant`/`zh-TW`/`zh-HK`, `fr-FR` and `fr-CA`, and Serbian in Latin or Cyrillic script each carry their own vocabulary and conventions. Translate for the variant the file name states. A bare `es`, `pt`, `fr`, or `zh` file is a product decision: read its existing entries to see which variant it already follows.

**Don't hand-type locale data.** Dates, times, numbers, currencies, percentages, and list joins come from the i18n library's CLDR data (`l()`, `Intl`, `number_to_currency`). A translation that bakes in "1,000.50" or "Jan 5" breaks in every locale whose separators or order differ. This covers numeral systems too: whether Arabic text shows Western or Arabic-Indic digits is the formatter's call, not the string's.

**Length.** Translations of short UI strings typically run 30% or more past English in German, Finnish, Russian, and French, and the expansion on one- and two-word labels is far larger. CJK text usually runs shorter. Respect the length limits the change set records, and prefer the shorter of two equally natural phrasings for buttons, tabs, and table headers.

**Placeholders inside grammar.** A value inserted into a sentence can't take case endings (Slavic, Finnish, Hungarian, Turkish), agree in gender (Romance, Slavic, Arabic, Hebrew), or pick its own particle (Japanese, Korean). Rephrase so the placeholder stands where no inflection is needed, such as a label followed by a colon or a noun phrase, and report a composition warning where no rephrasing works.

## Per language

"Address" names the forms and, where software practice is settled, the usual choice. Plural categories are CLDR cardinal categories. Whether the app needs all of them depends on its pluralizer (see the plural gotcha in SKILL.md), so the target file's existing set still decides.

| Language | Address | Script and punctuation | CLDR plurals |
| --- | --- | --- | --- |
| Arabic (ar) | Prefer impersonal and plural constructions; MSA, not dialect | RTL. Arabic comma `،`, semicolon `؛`, question mark `؟` | zero one two few many other |
| Bengali (bn) | আপনি formal, তুমি informal | Bengali script, `।` as full stop | one other |
| Chinese, Simplified (zh-CN, zh-Hans) | 你 is common in consumer apps; 您 is more deferential, for service and finance | Simplified characters. Full-width `，。：；？！（）`, `“”` quotes | other |
| Chinese, Traditional (zh-TW, zh-Hant, zh-HK) | 你 or 您, as for Simplified | Traditional characters, with Taiwan or Hong Kong vocabulary per the locale. Full-width punctuation, `「」` quotes | other |
| Czech (cs) | vy formal (capitalized "Vy" in direct address is common), ty informal | `„“` quotes | one few many other |
| Danish (da) | du is the software norm | `»«` or `„“` quotes | one other |
| Dutch (nl) | u formal, je informal; consumer apps often use je | `‘’` or `“”` quotes | one other |
| Finnish (fi) | Impersonal and passive constructions are the norm; sinä when needed | `””` quotes | one other |
| French (fr) | vous; tu only for a deliberately casual brand | No-break space (U+00A0 or U+202F) before `: ; ! ?` and inside `« »` in fr-FR; fr-CA spaces only before `:` | one many other |
| German (de) | Sie formal, du informal; consumer brands increasingly use du | Capitalize nouns. `„“` quotes. Keep `ß` (de-CH writes `ss`) | one other |
| Greek (el) | εσείς formal, εσύ informal | `;` is the question mark. `«»` quotes | one other |
| Hebrew (he) | Prefer infinitive, plural, and impersonal forms; no niqqud | RTL. `״` and `׳` in abbreviations, not ASCII quotes | one two other |
| Hindi (hi) | आप | Devanagari, `।` as full stop | one other |
| Hungarian (hu) | Ön formal, te informal; many apps use te | `„”` quotes | one other |
| Indonesian (id) | Anda | Latin script, standard punctuation | other |
| Italian (it) | Lei formal (often capitalized), tu informal; consumer apps often use tu | `«»` or `“”` quotes | one many other |
| Japanese (ja) | No pronoun. です/ます in sentences, plain noun phrases for labels | Full-width `、。` and `「」`. No spaces between words | other |
| Khmer (km) | Polite, neutral register; avoid the pronoun | No spaces between words; U+200B marks break points | other |
| Korean (ko) | No pronoun. 합니다체 or 해요체, both standard in software; pick one per product | Spaces between words. `.` and `,` | other |
| Lao (lo) | Polite, neutral register; avoid the pronoun | No spaces between words; U+200B marks break points | other |
| Malay (ms) | anda | Latin script, standard punctuation | other |
| Norwegian Bokmål (nb) | du is the software norm | `«»` quotes | one other |
| Persian (fa) | شما | RTL. `،` comma, `؟` question mark, ZWNJ (U+200C) inside words | one other |
| Polish (pl) | Pan/Pani is formal and gendered, so apps usually use the informal ty or impersonal forms | `„”` quotes | one few many other |
| Portuguese (pt-BR) | você | `“”` quotes | one many other |
| Portuguese (pt-PT) | Impersonal or third person; você reads oddly to many readers | `«»` or `“”` quotes | one many other |
| Romanian (ro) | dumneavoastră formal, tu informal | `„”` quotes; comma-below `ș ț`, not cedilla `ş ţ` | one few other |
| Russian (ru) | вы, capitalized "Вы" in direct address to one person | `«»` quotes, `—` dash | one few many other |
| Spanish (es-ES) | usted formal, tú informal; consumer apps in Spain usually use tú | `¿?` and `¡!` openers. `«»` or `“”` quotes | one many other |
| Spanish (es-419) | usted or tú by country and domain; tú is widespread in consumer apps | `¿?` and `¡!` openers | one many other |
| Swedish (sv) | du is the software norm | `””` quotes | one other |
| Tagalog/Filipino (tl, fil) | kayo/ninyo formal, ka/mo informal; English loans for technical terms are normal | Latin script | one other |
| Thai (th) | No pronoun, no gendered particles (ครับ/ค่ะ mark the writer's gender) | No spaces between words; spaces separate phrases; U+200B marks break points | other |
| Turkish (tr) | siz formal, sen informal | Dotted and dotless i are distinct letters (`İ i`, `I ı`) | one other |
| Ukrainian (uk) | ви, capitalized "Ви" in direct address | `«»` quotes; Ukrainian letters `і ї є ґ`, not Russian substitutes | one few many other |
| Vietnamese (vi) | bạn is the software norm | Latin script with every tone mark | other |

## Script integrity

- Every letter belongs to the language's script. Latin lookalikes inside Cyrillic or Greek text (`a e o p c x y`) are the classic generation error, including a single-letter word such as the Russian preposition "с". The checker reports them.
- Text is NFC-normalized: `é` is one code point, not `e` plus a combining accent.
- Zero-width characters belong only where the script uses them: U+200B as a break hint in Thai, Lao, Khmer, and Burmese, and U+200C/U+200D for shaping in Persian and Indic scripts.
- In right-to-left languages, store text in logical order. Never reverse a placeholder, tag, or number to make it look right in an editor, and don't insert bidi control characters unless the existing file already uses them for that construct.

## A language not listed

Look up its CLDR plural categories and its formal/informal address forms. Then read twenty existing entries in its file and match their register, punctuation, and quote style. Note in the report that no default existed.
