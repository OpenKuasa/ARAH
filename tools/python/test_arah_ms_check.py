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


REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


class RepoTest(unittest.TestCase):
    """Checks on the real Arah data files."""

    def test_android_build_keeps_malay(self):
        with open(os.path.join(REPO, "android", "gradle.properties"), encoding="utf-8") as f:
            line = next(l for l in f if l.startswith("supportedLocalizations="))
        self.assertIn("ms", line.strip().split("=", 1)[1].split(","))

    def test_all_strings_have_malay(self):
        for name in ("strings.txt", "types_strings.txt", "sound.txt"):
            self.assertEqual(arah_ms_check.check_twine(os.path.join(REPO, "data", "strings", name)), [], name)

    def test_reviewed_terms(self):
        """Pins corrections from the Malay language review."""
        def ms(name, key):
            return arah_ms_check.read_twine(os.path.join(REPO, "data", "strings", name))[key]["ms"]

        self.assertEqual(ms("strings.txt", "button_layer_outdoor"), "Aktiviti Luar")
        self.assertEqual(ms("strings.txt", "carplay_roundabout_exit"), "Jalan keluar %@")
        self.assertEqual(ms("sound.txt", "take_the_1_exit"), "Ambil jalan keluar pertama.")
        self.assertEqual(ms("types_strings.txt", "type.place.hamlet"), "Kampung Kecil")
        self.assertEqual(ms("types_strings.txt", "type.highway.tertiary"), "Jalan Tertiari")
        self.assertEqual(ms("types_strings.txt", "type.natural.water"), "Badan Air")
        self.assertEqual(ms("types_strings.txt", "type.place.suburb"), "Kawasan Bandar")
        self.assertEqual(ms("types_strings.txt", "type.leisure.adult_gaming_centre"), "Pusat Mesin Slot")

    def test_reviewed_search_terms(self):
        def ms_line(path, first):
            block = open(os.path.join(REPO, "data", path), encoding="utf-8").read().split("\n" + first + "\n", 1)[1]
            return next(l for l in block.split("\n\n", 1)[0].split("\n") if l.startswith("ms:"))

        self.assertNotIn("tol", ms_line("categories.txt", "highway-motorway_junction")[3:].lower().split("|"))
        self.assertNotIn("Gorengan", ms_line("categories_cuisines.txt", "cuisine-friture|@fastfood"))
        self.assertNotIn("parkir", ms_line("categories.txt", "amenity-parking|amenity-parking_entrance|@category_parking"))


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
