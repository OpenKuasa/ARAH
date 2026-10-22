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
    "iphone/Maps/UI/MailComposer/*.swift",
    # Pages bundled into the apps (FAQ, copyright, desktop welcome).
    "data/faq.html",
    "data/copyright.html",
    "data/welcome.html",
    # Shown on the GitHub repo page.
    "funding.json",
    ".github/FUNDING.yml",
    # Store listings and the release settings that upload them.
    "iphone/metadata/**/*.txt",
    "android/app/src/*/play/**/*.txt",
    "xcode/fastlane/*",
    "iphone/upload_to_appstore.sh",
    "packaging/*.xml",
]
# Source files where only string literals reach users or leave the device (export names, OSM notes and
# changeset tags, support emails, app names); identifiers and comments in them stay upstream's.
CODE_FILES = [
    "libs/map/bookmark_manager.cpp",
    "libs/kml/serdes_gpx.cpp",
    "libs/coding/zip_creator.cpp",
    "libs/editor/osm_editor.cpp",
    "libs/editor/server_api.cpp",
    "libs/platform/platform_mac.mm",
    "libs/platform/platform_linux.cpp",
    "libs/platform/platform_win.cpp",
    "libs/drape/vulkan/vulkan_context_factory.cpp",
    "qt/main.cpp",
    "qt/mainwindow.cpp",
    "qt/CMakeLists.txt",
    "iphone/Maps/Core/Editor/MWMEditorHelper.mm",
    "iphone/Maps/Categories/UIKitCategories.m",
    "android/app/build.gradle.kts",
    "android/app/src/main/java/app/organicmaps/util/Utils.java",
    "android/app/src/main/java/app/organicmaps/help/HelpFragment.java",
    "android/app/src/main/java/app/organicmaps/settings/NavigationSettingsFragment.java",
    "android/sdk/src/main/java/app/organicmaps/sdk/util/Constants.java",
    "android/sdk/src/main/cpp/app/organicmaps/sdk/editor/Editor.cpp",
]
STRING_LITERAL = re.compile(r'"(?:[^"\\]|\\.)*"')
# Credits that name upstream on purpose ("built on CoMaps", "berasaskan CoMaps").
CREDIT = re.compile(r"(based on|built on|berasaskan|dibina (?:atas|berasaskan)|fork of|cabang daripada)\s+"
                    r"(?:<[^>]+>\s*)*(?:co ?maps|organic ?maps)", re.IGNORECASE)
# Placeholder values written into app text; listed per file so --release fails until real values replace them.
PLACEHOLDER_VALUES = re.compile(r"ARAH-ORG|arah\.invalid")
# Keys Arah adds to iOS text. iOS has no per-key fallback to English, so every language needs them.
ARAH_IOS_KEYS = ["about_based_on"]
PBXPROJ = "iphone/Maps/Maps.xcodeproj/project.pbxproj"
PBX_IDENTITY = re.compile(r"PRODUCT_NAME|CFBundleDisplayName|BUNDLE_IDENTIFIER")
# Lines that may keep an upstream name, each with the reason: (path, substring, reason).
ALLOWED_LINES = [
    ("iphone/Maps/CoMaps.plist", "<key>comaps.app</key>",
     "network exception for CoMaps' map servers, which Arah uses until its own hosting (Plan 6)"),
    ("iphone/Maps/CoMaps.plist", "<key>comaps.at</key>", "network exception for incoming CoMaps share links"),
    ("iphone/Maps/CoMaps.plist", "app.comaps.3daction.", "internal home-screen shortcut IDs matched in code"),
    ("iphone/Maps/UI/Information/InformationView.swift", "AboutCoMapsView()",
     "Swift type name; the logo it shows is replaced with the Arah icon (Plan 4)"),
    ("iphone/Maps/Maps.xcodeproj/project.pbxproj", "PRODUCT_NAME = \"CoMaps (Debug)\";",
     "internal product/module name kept for the upstream test target; users see INFOPLIST_KEY_CFBundleDisplayName"),
    ("iphone/Maps/Maps.xcodeproj/project.pbxproj", "PRODUCT_NAME = CoMaps;",
     "internal product/module name kept for the upstream test target; users see INFOPLIST_KEY_CFBundleDisplayName"),
    ("iphone/Maps/Model/Social Media.swift", "return URL(string:",
     "CoMaps social accounts; the section is hidden by ArahConfig.socialMediaEnabled until Arah has accounts"),
    ("xcode/fastlane/Fastfile", "targets: ['CoMaps", "Xcode target names kept for upstream merges"),
    ("xcode/fastlane/Fastfile", "workspace: 'CoMaps.xcworkspace'", "Xcode workspace name kept for upstream merges"),
    ("xcode/fastlane/Fastfile", "scheme: 'CoMaps'", "Xcode scheme name kept for upstream merges"),
    ("iphone/upload_to_appstore.sh", "CoMaps.xcworkspace", "Xcode workspace name kept for upstream merges"),
    ("iphone/upload_to_appstore.sh", "-scheme CoMaps", "Xcode scheme name kept for upstream merges"),
]


def allowed_line(rel, line):
    return CREDIT.search(line) is not None or any(rel == path and sub in line for path, sub, _ in ALLOWED_LINES)
ANDROID_ENTRY = re.compile(r'<(string|plurals) name="([^"]+)"([^>]*)>(.*?)</\1>', re.S)
IOS_LINE = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;')
COMMENT = re.compile(r"^\s*(//|/\*|\*|<!--)")


def expand(root, patterns):
    out = []
    for pattern in patterns:
        out += sorted(os.path.relpath(p, root) for p in glob.glob(os.path.join(root, pattern), recursive=True)
                      if os.path.isfile(p))
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
            if m.group(2) in ALLOWED_KEYS:
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
            if BRAND.search(line) and not COMMENT.match(line) and not allowed_line(rel, line):
                leaks.append(f"{rel}:{n}: {line.strip()[:120]}")
    for rel in expand(root, CODE_FILES):
        for n, line in enumerate(read_lines(root, rel), 1):
            if COMMENT.match(line) or allowed_line(rel, line):
                continue
            if any(BRAND.search(lit) for lit in STRING_LITERAL.findall(line)):
                leaks.append(f"{rel}:{n}: {line.strip()[:120]}")
    for n, line in enumerate(read_lines(root, PBXPROJ), 1):
        if PBX_IDENTITY.search(line) and BRAND.search(line) and not allowed_line(PBXPROJ, line):
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
        if rel.startswith("docs/") or rel == "CLAUDE.md":
            continue
        try:
            lines = read_lines(root, rel)
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for n, line in enumerate(lines, 1):
            if PLACEHOLDER in line:
                found.append(f"{rel}:{n}: {line.strip()}")
    for rel in expand(root, ANDROID_STRINGS + IOS_STRINGS + IOS_PLURALS):
        count = sum(1 for line in read_lines(root, rel) if PLACEHOLDER_VALUES.search(line))
        if count:
            found.append(f"{rel}: {count} placeholder value(s) (Arah website/email placeholders in text)")
    return found


def find_missing_arah_keys(root):
    missing = []
    for rel in expand(root, ["iphone/Maps/LocalizedStrings/*.lproj/Localizable.strings"]):
        keys = {m.group(1) for m in (IOS_LINE.match(line) for line in read_lines(root, rel)) if m}
        missing += [f"{rel}: missing [{key}]" for key in ARAH_IOS_KEYS if key not in keys]
    return missing


def main(argv):
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    if "--root" in argv:
        root = argv[argv.index("--root") + 1]
    leaks = find_brand_leaks(root) + find_missing_arah_keys(root)
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
