import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import arah_ms_check  # noqa: E402


def write_temp(text):
    f = tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8")
    f.write(text)
    f.close()
    return f.name


class TwineTest(unittest.TestCase):
    def check(self, text):
        return arah_ms_check.check_twine(write_temp(text))

    def test_missing_ms_reported(self):
        problems = self.check("[[Strings]]\n\n[k]\nen = Hello\n")
        self.assertEqual(len(problems), 1)
        self.assertIn("k", problems[0])

    def test_placeholder_mismatch_reported(self):
        problems = self.check("[k]\nen = %1$s of %2$d\nms = %1$s daripada\n")
        self.assertEqual(len(problems), 1)
        self.assertIn("k", problems[0])

    def test_three_dots_reported(self):
        problems = self.check("[k]\nen = Loading…\nms = Memuat...\n")
        self.assertEqual(len(problems), 1)

    def test_complete_block_ok(self):
        self.assertEqual(self.check("[k]\nen = %d km\nms = %d km\n"), [])

    def test_untranslatable_skipped(self):
        text = "[k]\ncomment = Do not translate this\nen = OK\n"
        self.assertEqual(self.check(text), [])


class PluralTest(unittest.TestCase):
    def check(self, text):
        return arah_ms_check.check_twine(write_temp(text))

    def test_plural_without_ms_reported(self):
        problems = self.check("[k]\nen:one = %d item\nen:other = %d items\n")
        self.assertEqual(len(problems), 1)
        self.assertIn("k", problems[0])

    def test_plural_with_ms_other_ok(self):
        self.assertEqual(self.check("[k]\nen:one = %d item\nen:other = %d items\nms:other = %d item\n"), [])

    def test_plural_placeholder_mismatch_reported(self):
        self.assertEqual(len(self.check("[k]\nen:other = %d items\nms:other = item\n")), 1)


def write_file(directory, rel, text):
    path = os.path.join(directory, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


ANDROID_EN = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="project_name" translatable="false">CoMaps</string>
    <string name="hello">Hello %1$s</string>
    <string name="bye">Bye</string>
    <plurals name="places">
        <item quantity="one">%d place</item>
        <item quantity="other">%d places</item>
    </plurals>
</resources>
"""


class AndroidTest(unittest.TestCase):
    def check(self, ms_text):
        d = tempfile.mkdtemp()
        write_file(d, "res/values/strings.xml", ANDROID_EN)
        return arah_ms_check.check_file(write_file(d, "res/values-ms/strings.xml", ms_text))

    def test_android_missing_key_reported(self):
        problems = self.check("""<resources>
    <string name="hello">Helo %1$s</string>
    <plurals name="places"><item quantity="other">%d tempat</item></plurals>
</resources>""")
        self.assertEqual(len(problems), 1)
        self.assertIn("bye", problems[0])

    def test_android_complete_ok(self):
        self.assertEqual(self.check("""<resources>
    <string name="hello">Helo %1$s</string>
    <string name="bye">Selamat tinggal</string>
    <plurals name="places"><item quantity="other">%d tempat</item></plurals>
</resources>"""), [])

    def test_android_lost_link_reported(self):
        d = tempfile.mkdtemp()
        write_file(d, "res/values/strings.xml",
                   '<resources><string name="k">See <a href="https://osm.org">OSM</a></string></resources>')
        ms = write_file(d, "res/values-ms/strings.xml", '<resources><string name="k">Lihat OSM</string></resources>')
        self.assertEqual(len(arah_ms_check.check_file(ms)), 1)

    def test_android_plural_without_other_reported(self):
        problems = self.check("""<resources>
    <string name="hello">Helo %1$s</string>
    <string name="bye">Selamat tinggal</string>
    <plurals name="places"><item quantity="one">%d tempat</item></plurals>
</resources>""")
        self.assertEqual(len(problems), 1)
        self.assertIn("places", problems[0])


class IosTest(unittest.TestCase):
    def check_strings(self, en_text, ms_text):
        d = tempfile.mkdtemp()
        write_file(d, "en.lproj/Localizable.strings", en_text)
        return arah_ms_check.check_file(write_file(d, "ms.lproj/Localizable.strings", ms_text))

    def test_ios_placeholder_mismatch_reported(self):
        problems = self.check_strings('"k" = "%@ of %@";\n', '"k" = "%@ daripada";\n')
        self.assertEqual(len(problems), 1)
        self.assertIn("k", problems[0])

    def test_ios_escaped_quotes_parsed(self):
        en = '/* c */\n"k" = "Say \\"hi\\"";\n"n" = "a\\nb";\n'
        ms = '"k" = "Sebut \\"hai\\"";\n"n" = "a\\nb";\n'
        self.assertEqual(self.check_strings(en, ms), [])

    def test_stringsdict_without_other_reported(self):
        def plist(forms):
            items = "".join(f"<key>{k}</key><string>{v}</string>" for k, v in forms.items())
            return ("<?xml version=\"1.0\" encoding=\"UTF-8\"?><plist version=\"1.0\"><dict><key>places</key><dict>"
                    "<key>NSStringLocalizedFormatKey</key><string>%#@v@</string><key>v</key><dict>"
                    "<key>NSStringFormatSpecTypeKey</key><string>NSStringPluralRuleType</string>"
                    "<key>NSStringFormatValueTypeKey</key><string>lld</string>" + items + "</dict></dict></dict></plist>")
        d = tempfile.mkdtemp()
        write_file(d, "en.lproj/Localizable.stringsdict", plist({"one": "%lld place", "other": "%lld places"}))
        ms = write_file(d, "ms.lproj/Localizable.stringsdict", plist({"one": "%lld tempat"}))
        problems = arah_ms_check.check_file(ms)
        self.assertEqual(len(problems), 1)
        self.assertIn("places", problems[0])


class JsonTest(unittest.TestCase):
    def test_sound_json_missing_key_reported(self):
        d = tempfile.mkdtemp()
        write_file(d, "sound-strings/en.json/localize.json",
                   '{"a": {"defaultMessage": "Turn %1$s"}, "b": {"defaultMessage": "Then"}}')
        ms = write_file(d, "sound-strings/ms.json/localize.json", '{"a": {"defaultMessage": "Belok %1$s"}}')
        problems = arah_ms_check.check_file(ms)
        self.assertEqual(len(problems), 1)
        self.assertIn("b", problems[0])

    def test_categories_json_empty_english_not_required(self):
        d = tempfile.mkdtemp()
        write_file(d, "categories-strings/en.json/localize.json",
                   '{"@g": {"defaultMessage": ""}, "x|@g": {"defaultMessage": "4Fuel"}}')
        ms = write_file(d, "categories-strings/ms.json/localize.json", '{"x|@g": {"defaultMessage": "Minyak"}}')
        self.assertEqual(arah_ms_check.check_file(ms), [])


class ChangedEnglishTest(unittest.TestCase):
    def test_changed_english_listed(self):
        d = tempfile.mkdtemp()
        twine = write_file(d, "strings.txt", "[a]\nen = Save %@\nms = Simpan %@\n[b]\nen = Old text\nms = Lama\n")
        en = write_file(d, "res/values/strings.xml",
                        '<resources><string name="a">Save %1$s</string><string name="b">New text</string></resources>')
        self.assertEqual(arah_ms_check.changed_english(en, [twine]), {"b": ("Old text", "New text")})


REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


IOS = os.path.join(REPO, "iphone", "Maps", "LocalizedStrings")
TRANSLATIONS = os.path.join(REPO, "data", "translations")
MALAY_FILES = [
    os.path.join(REPO, "android", "app", "src", "main", "res", "values-ms", "strings.xml"),
    os.path.join(REPO, "android", "sdk", "src", "main", "res", "values-ms", "strings.xml"),
    os.path.join(REPO, "android", "sdk", "src", "main", "res", "values-ms", "types_strings.xml"),
    os.path.join(IOS, "ms.lproj", "Localizable.strings"),
    os.path.join(IOS, "ms.lproj", "Localizable.stringsdict"),
    os.path.join(IOS, "ms.lproj", "InfoPlist.strings"),
    os.path.join(IOS, "ms.lproj", "LocalizableTypes.strings"),
    os.path.join(TRANSLATIONS, "sound-strings", "ms.json", "localize.json"),
    os.path.join(TRANSLATIONS, "categories-strings", "ms.json", "localize.json"),
]


def read(*parts):
    with open(os.path.join(REPO, *parts), encoding="utf-8") as f:
        return f.read()


class RepoTest(unittest.TestCase):
    """Checks on the real Arah data files."""

    def test_android_build_keeps_malay(self):
        # localeFilters drops every resource language not listed (Plan 2's critical review finding).
        gradle = read("android", "app", "build.gradle.kts")
        filters = gradle.split("localeFilters += listOf(", 1)[1].split(")", 1)[0]
        self.assertIn('"ms"', filters)
        # The in-app language screen lists the locales in locales_config.xml.
        self.assertIn('<locale android:name="ms" />', read("android", "app", "src", "main", "res", "xml", "locales_config.xml"))

    def test_ios_project_has_malay(self):
        pbxproj = read("iphone", "Maps", "Maps.xcodeproj", "project.pbxproj")
        regions = pbxproj.split("knownRegions = (", 1)[1].split(");", 1)[0]
        self.assertIn("ms,", regions)
        for name in ("Localizable.strings", "Localizable.stringsdict", "InfoPlist.strings", "LocalizableTypes.strings"):
            self.assertIn(f"path = ms.lproj/{name};", pbxproj, name)

    def test_all_strings_have_malay(self):
        for path in MALAY_FILES:
            self.assertEqual(arah_ms_check.check_file(path), [], path)

    def test_reviewed_terms(self):
        """Pins corrections from the Malay language review."""
        android = arah_ms_check.read_android(MALAY_FILES[0])
        types = arah_ms_check.read_ios_strings(MALAY_FILES[6])
        sound = arah_ms_check.read_json(MALAY_FILES[7])
        self.assertEqual(android["button_layer_outdoor"], "Aktiviti Luar")
        self.assertEqual(arah_ms_check.read_ios_strings(MALAY_FILES[3])["carplay_roundabout_exit"], "Jalan keluar %@")
        self.assertEqual(sound["take_the_1_exit"], "Ambil jalan keluar pertama.")
        self.assertEqual(types["type.place.hamlet"], "Kampung Kecil")
        self.assertEqual(types["type.highway.tertiary"], "Jalan Tertiari")
        self.assertEqual(types["type.natural.water"], "Badan Air")
        self.assertEqual(types["type.place.suburb"], "Kawasan Bandar")
        self.assertEqual(types["type.leisure.adult_gaming_centre"], "Pusat Mesin Slot")
        android_types = arah_ms_check.read_android(MALAY_FILES[2])
        self.assertEqual(android_types["type.place.hamlet"], types["type.place.hamlet"])

    def test_reviewed_search_terms(self):
        cats = arah_ms_check.read_json(MALAY_FILES[8])

        def synonyms(key):
            return [w.lstrip("0123456789").lower() for w in cats[key].split("|")]

        self.assertNotIn("tol", synonyms("highway-motorway_junction"))
        self.assertNotIn("gorengan", synonyms("cuisine-friture|@fastfood"))
        # "parkir" is Indonesian; Malaysian Malay says "tempat letak kereta" / "parking".
        for key, value in cats.items():
            self.assertNotIn("parkir", value.lower(), key)

    def test_ui_search_categories_match_search_synonyms(self):
        # A displayed search category's name is used as the query, so it must be a Malay synonym too.
        android = arah_ms_check.read_android(MALAY_FILES[0])
        cats = arah_ms_check.read_json(MALAY_FILES[8])
        for key, value in cats.items():
            if not key.startswith("@category_"):
                continue
            ui = android.get(key[1:])
            if ui is None:
                continue
            # Search ignores case, so the displayed name has to match one synonym case-insensitively.
            synonyms = [w.lstrip("0123456789").casefold() for w in value.split("|")]
            self.assertIn(ui.casefold(), synonyms, key)


class CategoriesTest(unittest.TestCase):
    def check(self, text):
        return arah_ms_check.check_categories(write_temp(text))

    def test_categories_missing_ms(self):
        text = "# header\n\namenity-fuel\nen:Petrol\nde:Tankstelle\n\namenity-cafe\nen:Cafe\nms:Kafe\n\n"
        problems = self.check(text)
        self.assertEqual(len(problems), 1)
        self.assertIn("amenity-fuel", problems[0])


if __name__ == "__main__":
    unittest.main()
