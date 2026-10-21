#!/usr/bin/env python3
"""Finds user-visible CoMaps / Organic Maps branding left in Arah, and lists ARAH-PLACEHOLDER values.

Usage: arah_brand_check.py [--root DIR] [--release]

Exits 1 if branding leaks remain, or (with --release) if any placeholder is left.
"""
import glob
import json
import os
import plistlib
import re
import subprocess
import sys

BRAND = re.compile(r"co ?maps|organic ?maps|omaps\.app", re.IGNORECASE)
PLACEHOLDER = "ARAH-PLACEHOLDER"

# String keys whose text must keep the upstream name (license attribution).
ALLOWED_KEYS = {"about_based_on"}

# User-visible app text, in every language.
ANDROID_STRINGS = ["android/app/src/main/res/values*/*.xml", "android/sdk/src/main/res/values*/*.xml"]
IOS_STRINGS = ["iphone/Maps/LocalizedStrings/*.lproj/*.strings"]
IOS_PLURALS = ["iphone/Maps/LocalizedStrings/*.lproj/*.stringsdict"]
JSON_STRINGS = ["data/translations/sound-strings/*.json/localize.json"]
# Files where every non-comment line ships as identity or builds an outgoing link.
PLAIN_FILES = [
    "iphone/Maps/CoMaps.plist",
    "iphone/Maps/*.entitlements",
    "iphone/Maps/Classes/Share/*.mm",
    "iphone/Maps/UI/Information/*.swift",
    "iphone/Maps/Model/Social Media.swift",
    "iphone/Maps/UI/Settings/CustomMapServerView.swift",
]
PBXPROJ = "iphone/Maps/Maps.xcodeproj/project.pbxproj"
PBX_IDENTITY = re.compile(r"PRODUCT_NAME|CFBundleDisplayName|PRODUCT_BUNDLE_IDENTIFIER")
ANDROID_ENTRY = re.compile(r'<(string|plurals) name="([^"]+)"([^>]*)>(.*?)</\1>', re.S)
IOS_LINE = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;')
COMMENT = re.compile(r"^\s*(//|/\*|\*|<!--)")


def expand(root, patterns):
    out = []
    for pattern in patterns:
        out += sorted(os.path.relpath(p, root) for p in glob.glob(os.path.join(root, pattern)))
    return out


def read_text(root, rel):
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def read_lines(root, rel):
    return read_text(root, rel).split("\n")


def find_brand_leaks(root):
    leaks = []
    for rel in expand(root, ANDROID_STRINGS):
        text = read_text(root, rel)
        for m in ANDROID_ENTRY.finditer(text):
            if 'translatable="false"' in m.group(3) or m.group(2) in ALLOWED_KEYS:
                continue
            if BRAND.search(m.group(4)):
                line = text.count("\n", 0, m.start()) + 1
                leaks.append(f"{rel}:{line}: [{m.group(2)}] {m.group(4).strip()[:120]}")
    for rel in expand(root, IOS_STRINGS):
        for n, line in enumerate(read_lines(root, rel), 1):
            m = IOS_LINE.match(line)
            if m and m.group(1) not in ALLOWED_KEYS and BRAND.search(m.group(2)):
                leaks.append(f"{rel}:{n}: [{m.group(1)}] {m.group(2)[:120]}")
    for rel in expand(root, IOS_PLURALS):
        with open(os.path.join(root, rel), "rb") as f:
            data = plistlib.load(f)
        for key, entry in data.items():
            if BRAND.search(json.dumps(entry, ensure_ascii=False)):
                leaks.append(f"{rel}: [{key}]")
    for rel in expand(root, JSON_STRINGS):
        for key, value in json.loads(read_text(root, rel)).items():
            if BRAND.search(value.get("defaultMessage", "")):
                leaks.append(f"{rel}: [{key}] {value['defaultMessage'][:120]}")
    for rel in expand(root, PLAIN_FILES):
        for n, line in enumerate(read_lines(root, rel), 1):
            if BRAND.search(line) and not COMMENT.match(line):
                leaks.append(f"{rel}:{n}: {line.strip()[:120]}")
    for n, line in enumerate(read_lines(root, PBXPROJ), 1):
        if PBX_IDENTITY.search(line) and BRAND.search(line):
            leaks.append(f"{PBXPROJ}:{n}: {line.strip()}")
    return leaks


def tracked_files(root):
    try:
        out = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True, check=True).stdout
        return [p for p in out.split("\n") if p]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs]


def find_placeholders(root):
    found = []
    for rel in tracked_files(root):
        if rel.startswith(("3party/", "tools/python/arah_brand_check.py", "tools/python/test_arah_brand_check.py")):
            continue
        if rel.startswith("docs/"):
            continue
        try:
            lines = read_lines(root, rel)
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for n, line in enumerate(lines, 1):
            if PLACEHOLDER in line:
                found.append(f"{rel}:{n}: {line.strip()}")
    return found


def main(argv):
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]
    leaks = find_brand_leaks(root)
    placeholders = find_placeholders(root)
    for line in leaks:
        print("LEAK", line)
    for line in placeholders:
        print("PLACEHOLDER", line)
    print(f"{len(leaks)} leak(s), {len(placeholders)} placeholder(s)")
    failed = bool(leaks) or ("--release" in argv and bool(placeholders))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
