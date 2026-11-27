# Tracing how a key is used

<!-- cspell:ignore activerecord activemodel formatjs Öffnen Offen uppercasing -- Rails i18n namespaces, a CLI name, German examples, and a case-transform verb -->

The source text alone rarely settles a translation. "Book" is a verb on a button and a noun in a heading. "Open" is a state in a status badge and an action in a menu. "%{count} left" could mean seats, days, or attempts. The call site settles each one, so trace every key in the change set before anyone translates it.

## Finding the call sites

**Ask the tooling first.** Where the repo has it, it resolves lookups that grep can't:
- `i18n-tasks find <key or pattern>` lists usages and understands Rails lazy lookup; `i18n-tasks unused` lists keys it can't find.
- `formatjs extract --extract-source-location` records each message's file and line.
- A gettext `.po` already carries `#:` references.

None of these sees every dynamic key, so treat "unused" as a lead to check, not a verdict.

Otherwise, remember that the key in the locale file is often not the string the code contains. Search in three passes: the full key, then its last segment or two (for lazy and prefixed lookups), then its parent prefix next to an interpolation (for dynamic keys). Each framework hides keys its own way:

| Framework | Where the key comes from | How to find it |
| --- | --- | --- |
| Rails views, controllers, mailers | Lazy lookup: `t(".title")` in `app/views/orders/show.html.erb` reads `orders.show.title`, and a partial drops its underscore (`_form` → `orders.form.title`). In a controller it is `<controller path>.<action>.<key>`, namespace included (`admin.orders.create.notice`). A mailer's default subject is `<mailer name>.<action>.subject` | Grep the last segment (`".title"`), then keep the hits whose file path rebuilds the key |
| Rails components | ViewComponent sidecar files (`*.yml` beside the component) hold their own translations, scoped to the component, outside `config/locales` | Translate the sidecars too; `t(".key")` inside the component reads its sidecar first |
| Rails models | `activerecord.` (or `mongoid.`, or `activemodel.` for form objects) `attributes.<model>.<attr>` feeds `human_attribute_name` and form labels; `models.<model>` feeds `model_name.human(count:)`; `errors.models.<model>.attributes.<attr>.<error>` feeds validation messages; `helpers.submit.<action>` labels form buttons | No literal key in the code: find the model, attribute, or validation the path names |
| Rails, any layer | Dynamic keys: `t("statuses.#{order.status}")`, `t(:"#{prefix}.title")`; fallbacks: `t(key, default: [:other_key, "Text"])` | Grep the static prefix. Every value the interpolated part can take is a call site |
| i18next, react-i18next | `useTranslation("ns")`, `t("ns:key")`, the `keyPrefix` option, `<Trans i18nKey>`; plural chosen by `count`, variant by `context` | Grep the key without its namespace, then confirm the namespace at the call site |
| FormatJS, react-intl | `defineMessages`, `<FormattedMessage id>`, `intl.formatMessage({ id }, values)` | Grep the id. The `values` object shows what fills each argument |
| ember-intl | `{{t "key" name=…}}`, `this.intl.t("key", { … })` | Grep the key |
| vue-i18n | `$t("key")`, `t("key")`, `<i18n-t keypath="key">`, `v-t`; single-file components can carry their own messages in an `<i18n>` block | Grep the key, including `keypath=`, and translate the `<i18n>` blocks too |
| gettext | The msgid is the text. `#:` comments in the `.po` list each call site as `file:line`; `pgettext` adds context, `ngettext` plurals | Read the `#:` references directly |
| Flutter gen-l10n | `AppLocalizations.of(context)!.keyName(args)` | Grep the key as a method name |
| Android | `R.string.key` and `@string/key`; plurals through `getQuantityString(R.plurals.key, count)` | Grep the key |
| Apple | `String(localized:)`, `NSLocalizedString`, SwiftUI `Text("…")`; the key is often the English text itself, as in gettext | Grep the source text, then the key |

A key with no call site is one of three things: dynamic, consumed by a framework convention (the model-attribute case), or dead. Say which. Don't translate a key you have shown to be dead; list it in the report as a deletion candidate instead.

## What to read at each call site

| Read | Because |
| --- | --- |
| Part of speech and sense | A verb, a noun, and a state translate to different words, and often to different forms: Japanese 予約する against 予約, German "Öffnen" against "Offen". |
| What fills each placeholder | A count makes it a plural. A person's name may need an honorific or a case ending. A formatted date or price arrives already localized, so don't wrap it in words that assume an order. A noun translated from another key is a composition risk. Raw user input can be empty or long. |
| Concatenation and fragments | `t("a") + " " + t("b")`, a label followed by a value, or a sentence split across keys around a link: translate the fragments together as one sentence, and report a composition warning where the target word order cannot fit the pieces. |
| The surface it renders on | Buttons, tabs, and table headers have little room. An email subject is plain text, and so is a push notification. An SMS drops from 160 to 70 characters a segment (GSM-7 against UCS-2) as soon as one character falls outside GSM-7. That is any non-Latin script, but also a curly quote, `…`, or letters like `ő` and `ș`, so on SMS surfaces use straight quotes and three periods even where [LANGUAGES.md](LANGUAGES.md) prefers typographic ones. Alt text and `aria-label` are read aloud, so no visual abbreviations. A page title shows in tab strips and search results. |
| CSS case transforms | A label rendered through `text-transform: uppercase` should keep the source casing in the file. Pre-uppercasing breaks German `ß`, Turkish `i`, and Greek accents. The browser gets them right only when the page declares the language (`<html lang="tr">`), so a missing `lang` is worth reporting as a code issue. |
| Markup handling | An `_html` key, `html_safe`, `dangerouslySetInnerHTML`, or `<Trans>` components mean the tags must survive. A plain-text surface (email subject, SMS, `aria-label`) must not receive any. |
| Reuse | One key rendered in several places (a button and a heading) needs one translation that fits all of them. Where a language needs different words, report that the key should be split. That is a code change for the user, not something to work around in the translation. |
| Audience | The route, layout, or namespace (`admin/`, `staff/`, a mailer's recipient) says whether customers or staff read it, which sets the register. |
| Plural driving | A plural key looked up without `count` picks no form: Rails returns the whole hash, and i18next misses the bare key and shows it. An ICU `select` needs a branch, or `other`, for every value its argument takes, so check the enum or the column it comes from. |

## What to record

One line per key, carried into the change set shown to the user and split across the worker brief's "Used as" and "Inserted values" columns:

```text
orders.show.cancel: button in the order sheet (customer), ≤ 16 chars; no placeholders; also used as the cancel dialog's title
mailer.reminder.subject: email subject (customer), plain text, ≤ 60 chars; %{shop} = the shop's display name, not translated
statuses.<value>: badge (staff), dynamic via t("statuses.#{status}"); a state, not an action
```
