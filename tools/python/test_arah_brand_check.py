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
    def test_android_leak_found(self):
        root = make_repo({"android/app/src/main/res/values-ru/strings.xml":
                          '<resources>\n    <string name="k">О «CoMaps»</string>\n</resources>\n'})
        leaks = arah_brand_check.find_brand_leaks(root)
        self.assertEqual(len(leaks), 1)
        self.assertIn("[k]", leaks[0])

    def test_untranslatable_skipped(self):
        root = make_repo({"android/app/src/main/res/values/strings.xml":
                          '<resources>\n    <string name="project_name" translatable="false">CoMaps</string>\n'
                          '</resources>\n'})
        self.assertEqual(arah_brand_check.find_brand_leaks(root), [])

    def test_ios_leak_found(self):
        root = make_repo({"iphone/Maps/LocalizedStrings/ms.lproj/Localizable.strings":
                          '/* About CoMaps */\n"k" = "Versi CoMaps: %@";\n'})
        leaks = arah_brand_check.find_brand_leaks(root)
        self.assertEqual(len(leaks), 1)
        self.assertIn("[k]", leaks[0])

    def test_url_leak_found(self):
        root = make_repo({"iphone/Maps/UI/Information/InformationView.swift":
                          '        openUrl(URL(string: "https://www.comaps.app/news/")!)\n'})
        self.assertEqual(len(arah_brand_check.find_brand_leaks(root)), 1)

    def test_attribution_allowed(self):
        root = make_repo({"iphone/Maps/LocalizedStrings/en.lproj/Localizable.strings":
                          '"about_based_on" = "Based on CoMaps";\n'})
        self.assertEqual(arah_brand_check.find_brand_leaks(root), [])

    def test_old_brand_still_found(self):
        root = make_repo({"android/sdk/src/main/res/values/strings.xml":
                          '<resources><string name="t">https://t.me/OrganicMapsApp</string></resources>\n'})
        self.assertEqual(len(arah_brand_check.find_brand_leaks(root)), 1)

    def test_placeholder_listed(self):
        root = make_repo({"libs/platform/arah_config.hpp": "x = 1;  // ARAH-PLACEHOLDER: x\n"})
        found = arah_brand_check.find_placeholders(root)
        self.assertEqual(len(found), 1)
        self.assertIn("ARAH-PLACEHOLDER", found[0])

    def test_bundle_identifier_setting_found(self):
        root = make_repo({"iphone/Maps/Maps.xcodeproj/project.pbxproj": "\t\t\t\tBUNDLE_IDENTIFIER = app.comaps;\n"})
        self.assertEqual(len(arah_brand_check.find_brand_leaks(root)), 1)

    def test_allowed_line_not_reported(self):
        root = make_repo({"iphone/Maps/CoMaps.plist": "\t\t\t<key>comaps.app</key>\n\t\t\t<string>CoMaps</string>\n"})
        leaks = arah_brand_check.find_brand_leaks(root)
        self.assertEqual(len(leaks), 1)
        self.assertIn("<string>CoMaps</string>", leaks[0])

    def test_instructions_not_listed(self):
        root = make_repo({"CLAUDE.md": "values are marked `ARAH-PLACEHOLDER`.\n"})
        self.assertEqual(arah_brand_check.find_placeholders(root), [])

    def test_release_fails_on_placeholder(self):
        root = make_repo({"libs/platform/arah_config.hpp": "x = 1;  // ARAH-PLACEHOLDER: x\n"})
        self.assertEqual(arah_brand_check.main(["--root", root]), 0)
        self.assertEqual(arah_brand_check.main(["--root", root, "--release"]), 1)


if __name__ == "__main__":
    unittest.main()
