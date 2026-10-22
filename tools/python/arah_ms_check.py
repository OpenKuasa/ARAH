#!/usr/bin/env python3
"""Checks that Arah's Malay (ms) translations are complete and well-formed.

Usage: arah_ms_check.py FILE... [--allow-missing]
       arah_ms_check.py --changed-english TWINE[,TWINE...] FILE...

FILE is a Malay file compared with the same platform's English file:
  - Android res/values-ms/*.xml (English: res/values/*.xml)
  - iOS ms.lproj/*.strings and *.stringsdict (English: en.lproj/)
  - data/translations/{sound,categories}-strings/ms.json/localize.json (English: en.json/)
  - Twine files (*.txt with [key] blocks) and data/categories*.txt, as on Organic Maps.
Reports keys without Malay, Malay text whose placeholders differ from English, plurals without
an "other" form, and "..." instead of the ellipsis character. Exits 1 if anything is reported.

--changed-english lists keys of English platform FILEs whose English differs from the Twine
files' English (where Arah's Malay was written), so reused Malay can be retranslated.
"""
import collections
import json
import os
import plistlib
import re
import sys
import xml.etree.ElementTree as ET

PLACEHOLDER = re.compile(r"%(\d+\$)?(?:ll?[du]|\.\d+f|[@dsfu%])|%#@\w+@|\{[^}]*\}|<[^>]+>")
KEY_LINE = re.compile(r"^\[([^\[\]]+)\]$")
VALUE_LINE = re.compile(r"^([A-Za-z]+(?:-[A-Za-z]+)?(?::[a-z]+)?)\s*=\s?(.*)$")


def placeholders(text):
    return collections.Counter(m.group(0) for m in PLACEHOLDER.finditer(text))


def check_text(where, en, ms):
    problems = []
    if placeholders(en) != placeholders(ms):
        problems.append(f"{where}: placeholders differ: en={en!r} ms={ms!r}")
    if "..." in ms:
        problems.append(f"{where}: use '…' instead of '...': {ms!r}")
    return problems


def read_twine(path):
    blocks = {}
    key = None
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            m = KEY_LINE.match(line)
            if m:
                key = m.group(1)
                blocks[key] = {}
                continue
            m = VALUE_LINE.match(line)
            if key and m:
                blocks[key][m.group(1)] = m.group(2)
    return blocks


def check_twine(path):
    problems = []
    for key, values in read_twine(path).items():
        if "do not translate" in values.get("comment", "").lower():
            continue
        if "en:other" in values:
            # Plural block: Malay has no plural, so one "other" form covers every count.
            if "ms:other" not in values:
                problems.append(f"{path}: [{key}] has no ms")
            else:
                problems += check_text(f"{path}: [{key}]", values["en:other"], values["ms:other"])
            continue
        if "en" not in values:
            continue
        if "ms" not in values:
            problems.append(f"{path}: [{key}] has no ms")
            continue
        problems += check_text(f"{path}: [{key}]", values["en"], values["ms"])
    return problems


def check_categories(path):
    problems = []
    with open(path, encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f if not line.startswith("#")]
    block = []
    for line in lines + [""]:
        if line.strip():
            block.append(line)
            continue
        if block:
            langs = {entry.split(":", 1)[0]: entry.split(":", 1)[1] for entry in block[1:] if ":" in entry}
            if "en" in langs and "ms" not in langs:
                problems.append(f"{path}: {block[0]} has no ms")
            elif "ms" in langs and "..." in langs["ms"]:
                problems.append(f"{path}: {block[0]}: use '…' instead of '...'")
        block = []
    return problems


def android_text(el):
    """Element text with child markup (e.g. links) kept as tags, so lost markup shows as a placeholder change."""
    parts = [el.text or ""]
    for child in el:
        attrs = "".join(f' {k}="{v}"' for k, v in child.attrib.items())
        parts.append(f"<{child.tag}{attrs}>{android_text(child)}</{child.tag}>{child.tail or ''}")
    return "".join(parts)


def read_android(path):
    """Returns {name: text} for strings and {name: {quantity: text}} for plurals, skipping untranslatables."""
    out = {}
    for el in ET.parse(path).getroot():
        if el.get("translatable") == "false":
            continue
        if el.tag == "string":
            out[el.get("name")] = android_text(el)
        elif el.tag == "plurals":
            out[el.get("name")] = {item.get("quantity"): android_text(item) for item in el}
    return out


IOS_LINE = re.compile(r'^\s*"((?:[^"\\]|\\.)*)"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', re.M)


def read_ios_strings(path):
    with open(path, encoding="utf-8") as f:
        text = re.sub(r"/\*.*?\*/", "", f.read(), flags=re.S)
    return {m.group(1): m.group(2) for m in IOS_LINE.finditer(text)}


def read_stringsdict(path):
    """Returns {key: {quantity: text}}, merging the plural variables of each key."""
    with open(path, "rb") as f:
        data = plistlib.load(f)
    out = {}
    for key, entry in data.items():
        forms = {}
        for name, var in entry.items():
            if isinstance(var, dict):
                forms.update({q: t for q, t in var.items() if not q.startswith("NSString")})
        out[key] = forms
    return out


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return {k: v["defaultMessage"] for k, v in json.load(f).items()}


def english_counterpart(path):
    parts = path.split(os.sep)
    for i, part in enumerate(parts):
        if part == "values-ms":
            return os.sep.join(parts[:i] + ["values"] + parts[i + 1:])
        if part == "ms.lproj":
            return os.sep.join(parts[:i] + ["en.lproj"] + parts[i + 1:])
        if part == "ms.json":
            return os.sep.join(parts[:i] + ["en.json"] + parts[i + 1:])
    raise ValueError(f"not a Malay platform file: {path}")


def reader_for(path):
    if path.endswith(".xml"):
        return read_android
    if path.endswith(".stringsdict"):
        return read_stringsdict
    if path.endswith(".strings"):
        return read_ios_strings
    if path.endswith(".json"):
        return read_json
    raise ValueError(f"unknown file type: {path}")


def check_platform(path):
    read = reader_for(path)
    en, ms = read(english_counterpart(path)), read(path)
    problems = []
    for key, en_value in en.items():
        where = f"{path}: [{key}]"
        if isinstance(en_value, dict):
            forms = ms.get(key)
            if not forms:
                problems.append(f"{where} has no ms")
            elif "other" not in forms:
                problems.append(f"{where}: plural has no 'other' form")
            else:
                problems += check_text(where, en_value.get("other", ""), forms["other"])
            continue
        if not en_value and path.endswith(".json"):
            continue  # Categories groups with no English synonyms of their own.
        if key not in ms:
            problems.append(f"{where} has no ms")
            continue
        if "categories-strings" in path:
            if "..." in ms[key]:
                problems.append(f"{where}: use '…' instead of '...': {ms[key]!r}")
            continue  # Search synonyms are adaptations; placeholders don't apply.
        problems += check_text(where, en_value, ms[key])
    return problems


def check_file(path):
    if path.endswith(".txt"):
        return check_categories(path) if "categories" in os.path.basename(path) else check_twine(path)
    return check_platform(path)


def normalize_english(text):
    """Makes English comparable across Twine, Android and iOS: placeholders and escapes."""
    text = PLACEHOLDER.sub("%", text)
    text = text.replace("\\'", "'").replace('\\"', '"').replace("\\n", "\n")
    return " ".join(text.split())


def changed_english(en_path, twine_paths):
    """{key: (twine English, platform English)} for keys present in both whose English differs."""
    twine = {}
    for t in twine_paths:
        for key, values in read_twine(t).items():
            if "en" in values:
                twine[key] = values["en"]
            elif "en:other" in values:
                twine[key] = values["en:other"]
    out = {}
    for key, value in reader_for(en_path)(en_path).items():
        value = value.get("other", "") if isinstance(value, dict) else value
        if key in twine and normalize_english(twine[key]) != normalize_english(value):
            out[key] = (twine[key], value)
    return out


def main(argv):
    if argv and argv[0] == "--changed-english":
        twines = argv[1].split(",")
        for path in argv[2:]:
            for key, (old, new) in changed_english(path, twines).items():
                print(f"{path}: [{key}] {old!r} -> {new!r}")
        return 0
    allow_missing = "--allow-missing" in argv
    problems = []
    for path in [a for a in argv if not a.startswith("--")]:
        found = check_file(path)
        if allow_missing:
            found = [p for p in found if not p.endswith("has no ms")]
        problems += found
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
