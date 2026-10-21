#!/usr/bin/env python3
"""Lists translations that may still name upstream in their own script or wording, for a human to review.

Usage: arah_name_check.py [--ref GIT_REF]   (default ref: comaps/main)

For every key whose English at GIT_REF names "CoMaps" or "Organic Maps" (ignoring URLs and email addresses),
prints each translation in the working tree that contains neither "Arah" nor the upstream name. Most are
translations that simply leave the name out; the rest (e.g. a transliterated or translated name) need fixing.
Always exits 0: this is a review list, not a gate.
"""
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import arah_ms_check as strings  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
BRAND = re.compile(r"co ?maps|organic ?maps", re.IGNORECASE)
NOISE = re.compile(r"https?://\S+|[\w.+-]+@[\w.-]+")
SETS = [
    ("android/app/src/main/res/values/strings.xml", "android/app/src/main/res", "values-", "strings.xml"),
    ("android/sdk/src/main/res/values/strings.xml", "android/sdk/src/main/res", "values-", "strings.xml"),
    ("iphone/Maps/LocalizedStrings/en.lproj/Localizable.strings", "iphone/Maps/LocalizedStrings", ".lproj",
     "Localizable.strings"),
    ("iphone/Maps/LocalizedStrings/en.lproj/InfoPlist.strings", "iphone/Maps/LocalizedStrings", ".lproj",
     "InfoPlist.strings"),
]


def english_at(ref, rel):
    text = subprocess.run(["git", "-C", ROOT, "show", f"{ref}:{rel}"], capture_output=True, text=True, check=True).stdout
    suffix = os.path.splitext(rel)[1]
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as f:
        f.write(text)
    try:
        return strings.reader_for(rel)(f.name)
    finally:
        os.unlink(f.name)


def language_files(directory, marker, name):
    base = os.path.join(ROOT, directory)
    for entry in sorted(os.listdir(base)):
        path = os.path.join(base, entry, name)
        if marker in entry and entry not in ("values", "en.lproj") and os.path.exists(path):
            yield path


def main(argv):
    ref = argv[argv.index("--ref") + 1] if "--ref" in argv else "comaps/main"
    count = 0
    for en_rel, directory, marker, name in SETS:
        english = english_at(ref, en_rel)
        keys = [k for k, v in english.items() if isinstance(v, str) and BRAND.search(NOISE.sub("", v))]
        for path in language_files(directory, marker, name):
            values = strings.reader_for(path)(path)
            for key in keys:
                value = values.get(key)
                if isinstance(value, str) and not re.search(r"arah|co ?maps|organic ?maps", NOISE.sub("", value), re.I):
                    print(f"{os.path.relpath(path, ROOT)} [{key}] {value[:100]!r}")
                    count += 1
    print(f"{count} translation(s) without the app name to review")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
