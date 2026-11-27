# cspell:disable -- fixtures are translations in several languages, with deliberate typos
"""Regression tests for skills/translate-locales/scripts/check-locales.

Each case writes a source and a target locale file to a temp dir, runs the
checker, and asserts the exit code and the findings it prints. Stdlib only.
The checker runs on the Ruby named by $RUBY (default: `ruby`), so the macOS
system Ruby can be exercised with RUBY=/usr/bin/ruby.

    python3 spec/check_locales_test.py -v
"""

import os
import subprocess
import tempfile
import textwrap
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKER = os.path.join(ROOT, "skills", "translate-locales", "scripts", "check-locales")
RUBY = os.environ.get("RUBY", "ruby")


class CheckLocalesCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, name, content, encoding="utf-8"):
        path = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data = textwrap.dedent(content).lstrip("\n") if isinstance(content, str) else content
        with open(path, "w" if isinstance(data, str) else "wb", **({"encoding": encoding} if isinstance(data, str) else {})) as f:
            f.write(data)
        return path

    def run_checker(self, *args):
        result = subprocess.run([RUBY, CHECKER, *args], capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr

    def keys(self, *keys):
        return self.write("keys.txt", "\n".join(keys) + "\n")

    def assertFinding(self, out, level, check, key, detail=""):
        lines = [line for line in out.splitlines() if line.startswith(level)]
        match = [line for line in lines if line.split()[1] == check and line.split()[2] == key and detail in line]
        self.assertTrue(match, f"no {level} {check} {key} {detail!r} in:\n{out}")

    def assertNoFinding(self, out, check, key):
        hits = [line for line in out.splitlines() if line[:4] in ("FAIL", "WARN") and line.split()[1:3] == [check, key]]
        self.assertFalse(hits, f"unexpected {check} {key}:\n{out}")


class YamlTest(CheckLocalesCase):
    def setUp(self):
        super().setUp()
        self.en = self.write("en.yml", """
            en:
              greeting: "Hello, %{name}!"
              ref: 'See [%key:common.ok%]'
              link: 'Read the <a href="%{url}">terms</a>'
              meet: Meet your friend
              title: Reservations
              note: Thanks
              hint: Free
              gone: Still here
        """)

    def test_flags_each_invisible_defect(self):
        ru = self.write("ru.yml", """
            ru:
              greeting: "Здравствуйте, %{nmae}!"
              ref: 'См.'
              link: 'Прочитайте условия'
              meet: Встреча c другом
              title: Бpони
              note: "Спаси\u200bбо"
              hint: ''
              gone: ~
        """)
        code, out, _ = self.run_checker("--source", self.en, ru)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "greeting", "%{nmae}")
        self.assertFinding(out, "FAIL", "lokalise", "ref")
        self.assertFinding(out, "FAIL", "placeholder", "link")
        self.assertFinding(out, "WARN", "html", "link")
        self.assertFinding(out, "FAIL", "script", "meet", "c (Latin)")
        self.assertFinding(out, "FAIL", "script", "title", "Бpони")
        self.assertFinding(out, "FAIL", "invisible", "note", "ZERO WIDTH SPACE")
        self.assertFinding(out, "WARN", "empty", "hint", "renders nothing")
        self.assertIn("1 key(s) missing", out)

    def test_deliberate_latin_in_cyrillic_text_passes(self):
        en = self.write("en.yml", """
            en:
              dish: Food (a la carte)
              rule: "lowercase a-z only"
              steps: "Tell them (a) the name and (c) the code"
              go: "Back to %{x}"
              mail: Write to apac@example.com today
        """)
        ru = self.write("ru.yml", """
            ru:
              dish: Еда (a la carte)
              rule: "только строчные a-z"
              steps: "Сообщите (a) имя и (c) код"
              go: "Вернуться к %{x}"
              mail: Напишите на apac@example.com сегодня
        """)
        code, out, _ = self.run_checker("--source", en, ru)
        self.assertEqual(code, 0, out)

    def test_decomposed_accents_fail(self):
        fr = self.write("fr.yml", "fr:\n  title: \"Re\u0301servations\"\n")
        code, out, _ = self.run_checker("--source", self.en, fr)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "nfc", "title")

    def test_zero_width_space_is_a_line_break_hint_in_thai(self):
        th = self.write("app_th.yml", "title: \"การจอง\u200bของคุณ\"\n")
        en = self.write("app_en.yml", "title: Your reservations\n")
        code, out, _ = self.run_checker("--source", en, th)
        self.assertEqual(code, 0, out)
        self.assertFinding(out, "WARN", "invisible", "title", "line-break hint")

    def test_message_and_description_keys_stay_separate_in_yaml(self):
        en = self.write("en.yml", "en:\n  flash:\n    message: Saved %{name}\n    description: Shown after %{name}\n")
        ru = self.write("ru.yml", "ru:\n  flash:\n    message: Сохранено %{name}\n    description: Показано после %{nme}\n")
        code, out, _ = self.run_checker("--source", en, ru)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "flash.description")

    def test_source_file_in_the_target_list_is_skipped(self):
        code, out, _ = self.run_checker("--source", self.en, self.en)
        self.assertEqual(code, 0)
        self.assertIn("skipped: this is the source file", out)

    def test_namespace_with_one_top_level_key_is_not_unwrapped(self):
        en = self.write("en/nav.json", '{"nav": {"home": "Home"}, "foot": {"top": "Top"}}')
        ja = self.write("ja/nav.json", '{"nav": {"home": "ホーム"}}')
        code, out, _ = self.run_checker("--source", en, ja)
        self.assertEqual(code, 0)
        self.assertNoFinding(out, "extra", "home")
        self.assertIn("1 key(s) missing", out)

    def test_norwegian_root_that_yaml_reads_as_false_is_unwrapped(self):
        no = self.write("no.yml", "no:\n  title: Bestillinger\n")
        code, out, _ = self.run_checker("--source", self.en, no)
        self.assertNoFinding(out, "extra", "title")


class PluralTest(CheckLocalesCase):
    def test_russian_one_may_add_count_but_other_must_keep_it(self):
        en = self.write("en.yml", 'en:\n  items:\n    one: One item\n    other: "%{count} items"\n')
        ru = self.write("ru.yml", 'ru:\n  items:\n    one: "%{count} товар"\n    few: "%{count} товара"\n    many: "%{count} товаров"\n    other: товара\n')
        code, out, _ = self.run_checker("--source", en, ru)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "items.other", "dropped %{count}")
        self.assertNoFinding(out, "placeholder", "items.one")

    def test_plural_set_unlike_the_rest_of_the_file_warns(self):
        en_lines = ["en:"] + [f"  k{i}:\n    one: a\n    other: b" for i in range(6)]
        ja_lines = ["ja:"] + [f"  k{i}:\n    other: b" for i in range(5)] + ["  k5:\n    one: a\n    other: b"]
        en = self.write("en.yml", "\n".join(en_lines) + "\n")
        ja = self.write("ja.yml", "\n".join(ja_lines) + "\n")
        code, out, _ = self.run_checker("--source", en, ja)
        self.assertFinding(out, "WARN", "plural", "k5", "usually uses other")

    def test_i18next_plural_missing_other_fails(self):
        en = self.write("en.json", '{"seat_one": "{{count}} seat", "seat_other": "{{count}} seats"}')
        de = self.write("de.json", '{"seat_one": "{{count}} Platz"}')
        code, out, _ = self.run_checker("--source", en, de)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "plural", "seat", "no 'other'")


class ScopeTest(CheckLocalesCase):
    def setUp(self):
        super().setUp()
        self.en = self.write("en.json", '{"cart": {"item_one": "{{count}} item", "item_other": "{{count}} items"}, "hi": "Hi {{name}}"}')
        self.de = self.write("de.json", '{"cart": {"item_one": "{{count}} Artikel", "item_other": "{{cnt}} Artikel"}, "hi": "Hallo {{name}}"}')

    def test_i18next_suffix_keys_in_the_keys_file_reach_the_plural(self):
        code, out, _ = self.run_checker("--source", self.en, "--keys-file", self.keys("cart.item_other"), self.de)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "cart.item.other")

    def test_keys_written_with_the_locale_root_are_normalized(self):
        en = self.write("en.yml", "en:\n  greeting: Hello %{name}\n")
        ja = self.write("ja.yml", "ja:\n  greeting: こんにちは%{nme}\n")
        code, out, _ = self.run_checker("--source", en, "--keys-file", self.keys("en.greeting"), ja)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "greeting")

    def test_a_key_the_source_lacks_is_a_usage_error(self):
        code, _, err = self.run_checker("--source", self.en, "--keys-file", self.keys("hi", "nonexistent.key"), self.de)
        self.assertEqual(code, 2)
        self.assertIn("nonexistent.key", err)

    def test_a_scoped_key_missing_from_the_target_fails(self):
        en = self.write("en.yml", "en:\n  a: One\n  b: Two\n")
        ja = self.write("ja.yml", "ja:\n  a: 一\n  b: ~\n")
        code, out, _ = self.run_checker("--source", en, "--keys-file", self.keys("b"), ja)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "missing", "b")


class IcuTest(CheckLocalesCase):
    def test_formatjs_wrapper_is_unwrapped_and_translated_keywords_fail(self):
        en = self.write("en.json", '{"t": {"defaultMessage": "{n, plural, one {# table} other {# tables}}", "description": "header"}}')
        fr = self.write("fr.json", '{"t": {"defaultMessage": "{n, plural, un {# table} other {# tables}}", "description": "header"}}')
        code, out, _ = self.run_checker("--source", en, fr)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "icu", "t", "'un'")

    def test_select_options_must_match_the_source(self):
        en = self.write("en.arb", '{"g": "{sex, select, male {He} female {She} other {They}}"}')
        de = self.write("de.arb", '{"g": "{sex, select, mann {Er} female {Sie} other {Sie}}"}')
        code, out, _ = self.run_checker("--source", en, de)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "icu", "g", "select")

    def test_apostrophe_before_a_brace_quotes_it_in_icu(self):
        en = self.write("app_en.arb", '{"w": "Welcome to {venue}"}')
        fr = self.write("app_fr.arb", '{"w": "Bienvenue à l\'{venue}"}')
        code, out, _ = self.run_checker("--source", en, fr)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "w")

    def test_apostrophe_is_plain_text_outside_icu(self):
        en = self.write("en.json", '{"w": "Welcome to {venue}"}')
        fr = self.write("fr.json", '{"w": "Bienvenue à l\'{venue}"}')
        code, out, _ = self.run_checker("--source", en, fr)
        self.assertEqual(code, 0, out)

    def test_i18next_nesting_and_vue_links_are_placeholders(self):
        en = self.write("en.json", '{"a": "See $t(common.terms)", "b": "Go @:nav.home now"}')
        de = self.write("de.json", '{"a": "Siehe Bedingungen", "b": "Jetzt los"}')
        code, out, _ = self.run_checker("--source", en, de)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "a", "$t(common.terms)")
        self.assertFinding(out, "FAIL", "placeholder", "b", "@:nav.home")


class GettextTest(CheckLocalesCase):
    def test_header_fuzzy_and_entries_without_blank_lines(self):
        po = self.write("ja/LC_MESSAGES/default.po", """
            msgid ""
            msgstr ""
            "Plural-Forms: nplurals=1; plural=0;\\n"

            #, fuzzy
            msgid "Hello %{name}"
            msgstr "こんにちは"
            msgid "Bye %{name}"
            msgstr "さようなら%{nam}"
            msgid "One booking"
            msgid_plural "%{count} bookings"
            msgstr[0] "%{count}件"
            msgstr[1] "%{count}件"
        """)
        code, out, _ = self.run_checker(po)
        self.assertEqual(code, 1)
        self.assertFinding(out, "WARN", "fuzzy", "Hello")
        self.assertFinding(out, "FAIL", "placeholder", "Bye", "%{nam}")
        self.assertFinding(out, "FAIL", "plural", "One", "nplurals=1")

    def test_python_printf_and_brace_formats(self):
        po = self.write("fr.po", """
            msgid ""
            msgstr "Plural-Forms: nplurals=2; plural=(n > 1);\\n"

            msgid "Welcome %(user)s, %d items"
            msgstr "Bienvenue %(usr)s, %d articles"

            #, python-brace-format
            msgid "Welcome to {venue}"
            msgstr "Bienvenue à l'{venue}"
        """)
        code, out, _ = self.run_checker(po)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "Welcome", "%(usr)s")
        self.assertNotIn("{venue}", out)


class PropertiesTest(CheckLocalesCase):
    def test_escaped_backslash_does_not_continue_the_line(self):
        en = self.write("messages.properties", "path=C:\\\\\nnext=Go {0}\n")
        de = self.write("messages_de.properties", "path=C:\\\\\nnext=Los {9}\n")
        code, out, _ = self.run_checker("--source", en, de)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "placeholder", "next")
        self.assertNoFinding(out, "placeholder", "path")

    def test_latin1_file_and_lone_apostrophe(self):
        en = self.write("messages.properties", "forget=Don't forget {0}\nplain=Caf\\u00e9\n")
        fr = self.write("messages_fr.properties", "forget=N'oubliez pas {0}\nplain=Caf\xe9\n".encode("latin-1"))
        code, out, _ = self.run_checker("--source", en, fr)
        self.assertEqual(code, 1)
        self.assertFinding(out, "FAIL", "apostrophe", "forget")
        self.assertNotIn("parse", out)


class UsageTest(CheckLocalesCase):
    def test_unsupported_format_is_a_usage_error(self):
        en = self.write("en.yml", "en:\n  a: b\n")
        xlf = self.write("messages.fr.xlf", "<xliff/>")
        code, _, err = self.run_checker("--source", en, xlf)
        self.assertEqual(code, 2)
        self.assertIn("unsupported format", err)

    def test_unparseable_target_fails(self):
        en = self.write("en.yml", "en:\n  a: b\n")
        ja = self.write("ja.yml", "ja:\n  a: [unclosed\n")
        code, out, _ = self.run_checker("--source", en, ja)
        self.assertEqual(code, 1)
        self.assertIn("FAIL  parse", out)


if __name__ == "__main__":
    unittest.main()
