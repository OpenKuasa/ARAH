#!/usr/bin/env python3
"""Checks that Arah's Malay (ms) translations are complete and well-formed.

Usage: arah_ms_check.py FILE... [--allow-missing]

FILE is a Twine strings file (data/strings/*.txt) or data/categories*.txt.
Reports blocks without Malay, Malay text whose placeholders differ from English,
and "..." instead of the ellipsis character. Exits 1 if anything is reported.
"""
import collections
import re
import sys

PLACEHOLDER = re.compile(r"%(\d+\$)?[@dsfu%]|%l[du]|\{[^}]*\}|<[^>]+>")
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


def main(argv):
    allow_missing = "--allow-missing" in argv
    problems = []
    for path in [a for a in argv if not a.startswith("--")]:
        found = check_categories(path) if "categories" in path else check_twine(path)
        if allow_missing:
            found = [p for p in found if not p.endswith("has no ms")]
        problems += found
    for p in problems:
        print(p)
    print(f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
