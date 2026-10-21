import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import arah_brand_check  # noqa: E402


def make_repo(files):
    root = tempfile.mkdtemp()
    for rel, text in files.items():
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return root


class BrandCheckTest(unittest.TestCase):
    def test_leak_found(self):
        root = make_repo({"data/strings/strings.txt": "[about]\nen = About\nru = О «Organic Maps»\n"})
        leaks = arah_brand_check.find_brand_leaks(root)
        self.assertEqual(len(leaks), 1)
        self.assertIn("data/strings/strings.txt", leaks[0])
        self.assertIn("Organic Maps", leaks[0])

    def test_joined_spelling_found(self):
        root = make_repo({"data/strings/strings.txt": "[telegram_url]\nen = https://t.me/OrganicMapsApp\n"})
        self.assertEqual(len(arah_brand_check.find_brand_leaks(root)), 1)

    def test_allowed_not_reported(self):
        root = make_repo({"data/strings/strings.txt": "[about_based_on]\nen = Based on Organic Maps\n"})
        self.assertEqual(arah_brand_check.find_brand_leaks(root), [])

    def test_placeholder_listed(self):
        root = make_repo({"libs/platform/arah_config.hpp": "x = 1;  // ARAH-PLACEHOLDER: x\n"})
        found = arah_brand_check.find_placeholders(root)
        self.assertEqual(len(found), 1)
        self.assertIn("ARAH-PLACEHOLDER", found[0])

    def test_release_fails_on_placeholder(self):
        root = make_repo({"libs/platform/arah_config.hpp": "x = 1;  // ARAH-PLACEHOLDER: x\n"})
        self.assertEqual(arah_brand_check.main(["--root", root]), 0)
        self.assertEqual(arah_brand_check.main(["--root", root, "--release"]), 1)


if __name__ == "__main__":
    unittest.main()
