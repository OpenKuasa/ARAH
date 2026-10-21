#!/usr/bin/env python3
"""Finds user-visible Organic Maps branding left in Arah, and lists ARAH-PLACEHOLDER values.

Usage: arah_brand_check.py [--root DIR] [--release]

Exits 1 if branding leaks remain, or (with --release) if any placeholder is left.
"""
import os
import re
import subprocess
import sys

BRAND = re.compile(r"organic ?maps|omaps\.app", re.IGNORECASE)
PLACEHOLDER = "ARAH-PLACEHOLDER"

# String keys whose text must keep the Organic Maps name (license attribution).
ALLOWED_KEYS = {"about_based_on"}

KEY_LINE = re.compile(r"^\s*\[([^\[\]]+)\]\s*$")
VALUE_LINE = re.compile(r"^\s*([a-z]{2,3}(?:-[A-Za-z]+)?(?::[a-z]+)?)\s*=")

STRING_FILES = ["data/strings/strings.txt", "data/strings/types_strings.txt", "data/strings/sound.txt"]
# Files where every non-comment line is user-visible or ships as identity.
PLAIN_FILES = [
    "iphone/Maps/OMaps.plist",
    "iphone/Maps/OMaps-Debug.entitlements",
    "iphone/Maps/OMaps-Release.entitlements",
    "libs/drape_frontend/gui/copyright_label.cpp",
    "libs/map/share.cpp",
    "libs/ge0/url_generator.cpp",
]
PBXPROJ = "iphone/Maps/Maps.xcodeproj/project.pbxproj"
PBX_IDENTITY = re.compile(r"PRODUCT_NAME|CFBundleDisplayName|PRODUCT_BUNDLE_IDENTIFIER")


def read_lines(root, rel):
    path = os.path.join(root, rel)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return f.read().split("\n")


def find_brand_leaks(root):
    leaks = []
    for rel in STRING_FILES:
        key = None
        for n, line in enumerate(read_lines(root, rel), 1):
            m = KEY_LINE.match(line)
            if m:
                key = m.group(1)
                continue
            if VALUE_LINE.match(line) and BRAND.search(line) and key not in ALLOWED_KEYS:
                leaks.append(f"{rel}:{n}: [{key}] {line.strip()}")
    for rel in PLAIN_FILES:
        for n, line in enumerate(read_lines(root, rel), 1):
            if BRAND.search(line) and not line.strip().startswith("//"):
                leaks.append(f"{rel}:{n}: {line.strip()}")
    for n, line in enumerate(read_lines(root, PBXPROJ), 1):
        if PBX_IDENTITY.search(line) and re.search(r"Organic Maps|organicmaps", line):
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
