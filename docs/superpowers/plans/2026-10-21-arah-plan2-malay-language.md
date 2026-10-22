# Arah Plan 2: Malay Language — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add natural Malaysian Malay (`ms`) to the app (UI text, map feature types, search, voice directions) and make it the default language on iPhone.

**Architecture:** All text lives in Twine-format files under `data/strings/` (`strings.txt`, `types_strings.txt`, `sound.txt`) plus `data/categories.txt` for search. `tools/unix/generate_localizations.sh` turns them into Android `values-ms/`, iOS `ms.lproj/` and `data/sound-strings/ms.json`. Two small C++ changes register `ms` for search (`CategoriesHolder::kLocaleMapping`) and voice (`routing::turns::sound::kLanguageList`). A coverage checker keeps every Malay entry present and its placeholders intact.

**Tech Stack:** Twine text format, Python 3 (checker + generators), C++ unit tests, Xcode project (`.pbxproj`), Objective-C++ (`iphone/Maps/main.mm`).

**Spec:** `docs/superpowers/specs/2026-10-21-arah-phase1-rebrand-design.md` §4 "Malay language", plus the decisions "Malay default, English available" and "Malay translation done and reviewed by the builder".

### Scope notes (rulings made while planning)
- **Android "Malay by default" moves to Plan 5 (Android).** minSdk is 21, and Android has no system per-app language before 13, so Android needs an in-app "Bahasa" setting. That is Android UI work and needs the Android SDK. The Android Malay *strings* are still generated here.
- **iPhone needs no in-app picker.** iOS shows a per-app Language option in the Settings app once an app has more than one localization. Arah sets Malay once on first launch, and the user can switch there.
- **Country and region names** (`data/countries-strings/`) stay as they are. They are hand-maintained JSON (see `data/CLAUDE.md`), Malaysian names are already Malay, and other countries fall back to English. Deferred.
- **"Organic Maps" stays verbatim** inside Malay strings. Plan 3 replaces the name in every language at once.

## Global Constraints

- Language code `ms` everywhere (Twine, Android `values-ms`, iOS `ms.lproj`, `ms.json`).
- Natural everyday **Malaysian** Malay, not Indonesian and not stiff formal text (spec anti-goal). Address the user as "anda". Indonesian (`id`) may be read as a draft, but every line is rewritten.
- Use the **Glossary** below for every recurring term. Consistency matters more than variety.
- Keep every placeholder exactly as in `en` (`%@`, `%d`, `%s`, `%1$s`, `%2$@`, `%%`, `\n`, HTML tags, `{…}`), with the same set and count; word order may change.
- Use "…" (U+2026), never "...". Don't translate "Organic Maps", "OpenStreetMap" or "ID Editor".
- Never hand-edit generated files. Regenerate with `tools/unix/generate_localizations.sh` and commit generated output **separately**, titled `[strings] Regenerated`.
- Commit format: `[subsystem] Imperative summary` (≤80 chars), `git commit -s`. Source commits use `[strings]`, `[search]`, `[routing]`, `[ios]`.
- Branch `feat-003-malay-language` from `feat-001-arah-phase1-design`. Don't push.

### Glossary (fixed terms)

| English | Malay |
|---|---|
| map | peta |
| bookmark / bookmarks | penanda |
| track (recorded) | jejak |
| route | laluan |
| navigation / navigate | navigasi / navigasi ke |
| search | cari / carian |
| settings | tetapan |
| download / downloaded | muat turun / dimuat turun |
| offline / online | luar talian / dalam talian |
| place | tempat |
| directions | arah |
| traffic | trafik |
| speed camera | kamera laju |
| turn left / right | belok kiri / kanan |
| keep left / right | ikut kiri / kanan |
| roundabout | bulatan |
| exit (highway) | susur keluar |
| toll | tol |
| petrol station | stesen minyak |
| car / walking / cycling | kereta / berjalan kaki / berbasikal |
| mobile data | data mudah alih |
| share | kongsi |
| delete / cancel / save | padam / batal / simpan |
| meters / kilometers | meter / kilometer |
| current location | lokasi semasa |

## Review Focus

1. **Placeholders and formatting survive translation.** A `%1$s` dropped or turned into `%s` crashes or garbles Android, and `%@` in the wrong count crashes iOS. Pinned by the checker's placeholder-parity rule (Task 1) on every file.
2. **First launch on a phone set to English opens in Malay; a user who then picks English stays in English.** Pinned by Task 6's manual check on the simulator (launch, switch to English in Settings, relaunch).
3. **Malay search finds everyday things** whether typed in lower case, without the full word, or with common synonyms (e.g. "minyak", "petronas", "surau", "tandas"). Pinned by Task 3's search test with prefix and synonym queries.
4. **Malay text fits the UI.** Malay runs about 20–30% longer than English; buttons and tab labels must not clip on a small phone. Pinned by Task 6's screenshots on iPhone SE size.
5. **Plurals.** Malay has no grammatical plural; `.stringsdict` entries must still produce a valid "other" form so iOS doesn't show raw keys. Pinned by the checker rule for plural entries (Task 1) and Task 6 screenshots of a list with counts.

---

### Task 1: Malay coverage checker

**Files:**
- Create: `tools/python/arah_ms_check.py`
- Create: `tools/python/test_arah_ms_check.py`

**Interfaces:**
- Produces: CLI `python3 tools/python/arah_ms_check.py <file>... [--allow-missing]`, which exits 1 and lists problems, or exits 0. Functions `check_twine(path) -> list[str]` (strings, types, sound files) and `check_categories(path) -> list[str]`. Tasks 2–5 run it as their failing-then-passing test.

- [ ] **Step 1: Write the failing tests** in `tools/python/test_arah_ms_check.py` (stdlib `unittest`, temp files):
  - `test_missing_ms_reported`: a Twine block `[k]\nen = Hello\n` gives one problem naming `k`.
  - `test_placeholder_mismatch_reported`: `en = %1$s of %2$d` / `ms = %1$s daripada` reports `k` (set of placeholders differs).
  - `test_three_dots_reported`: `ms = Memuat...` is reported (must use "…").
  - `test_complete_block_ok`: `en = %d km` / `ms = %d km` gives no problems.
  - `test_categories_missing_ms`: a category block with an `en:` line and no `ms:` line is reported by its first line; a block with both is fine.
  - `test_untranslatable_skipped`: a Twine block whose only language is `en` and that has a `comment` containing "Do not translate" is skipped.
- [ ] **Step 2: Run** `python3 -I -m unittest tools/python/test_arah_ms_check.py`. Expected: FAIL / ImportError (module missing).
- [ ] **Step 3: Implement** `tools/python/arah_ms_check.py`. Parse Twine blocks as a `[key]` line followed by `lang = text` lines until the next `[`. The placeholder regex is `%(\d+\$)?[@dsfu%]|%l[du]|\{[^}]*\}|<[^>]+>`; compare multisets. Skip blocks that have no `en`. Categories blocks are separated by blank lines, skipping `#` comments.
- [ ] **Step 4: Run** the unit tests. Expected: all PASS. Then run `python3 -I tools/python/arah_ms_check.py data/strings/strings.txt | tail -1`. Expected: exit 1, reporting ~780 missing.
- [ ] **Step 5: Commit** `[tools] Add Arah Malay translation coverage checker`.

### Task 2: Malay voice directions

**Files:**
- Modify: `data/strings/sound.txt` (add `ms = …` to all 107 blocks)
- Modify: `libs/platform/languages.hpp` (`kLanguageList`: add `{"ms", "Bahasa Melayu"}` right after the `id` entry, outside the `#ifdef`)
- Check: `iphone/CoreApi/CoreApi/…/LocaleTranslator.mm` (find with `grep -rn LocaleTranslator iphone`) and Android `LanguageData`: if they map locales explicitly, add `ms`/`ms-MY` → `ms`
- Test: `libs/platform/platform_tests/get_text_by_id_tests.cpp`
- Generated: `data/sound-strings/ms.json`

**Interfaces:**
- Consumes: the Task 1 checker.
- Produces: TTS language code `ms`.

- [ ] **Step 1: Write the failing test.** Add `{"ms", "Bahasa Melayu"}` to `kLanguageList` first: the existing `TtsLanguageListHasSoundStrings` then fails because `ms.json` doesn't exist. Add `UNIT_TEST(GetTextByIdMalayTest)`, which loads `platform::GetJsonBuffer(platform::TextSource::TtsSound, "ms", buf)` and asserts via `ForTestingGetTextByIdFactory(buf, "ms")`:
  - `make_a_right_turn` = `"Belok kanan."`
  - `make_a_slight_right_turn` = `"Ikut kanan."`
  - `in_500_meters` = `"Dalam lima ratus meter."`
  - `you_have_reached_the_destination` = `"Anda telah tiba di destinasi."`
  - `then` = `"Kemudian."`
  (Check the exact keys in `sound.txt`; if a key name differs, use the real key and keep the Malay text.)
- [ ] **Step 2: Run** `cmake --build build-claude --target platform_tests && ctest --test-dir build-claude --output-on-failure -R platform_tests`. Expected: FAIL in `TtsLanguageListHasSoundStrings` (ms) and `GetTextByIdMalayTest`.
- [ ] **Step 3: Translate** all 107 `sound.txt` blocks into spoken Malay: numbers in words, as `id`/`en` do; short sentences that end with ".". Use the Glossary.
- [ ] **Step 4: Check and regenerate.** Run `python3 -I tools/python/arah_ms_check.py data/strings/sound.txt` (expected exit 0), then `tools/unix/generate_localizations.sh` (expected exit 0; `data/sound-strings/ms.json` exists).
- [ ] **Step 5: Run** the platform_tests from Step 2, plus `ctest --test-dir build-claude --output-on-failure -R routing_tests`. Expected: PASS.
- [ ] **Step 6: Commit** `[routing] Add Malay voice directions` (sound.txt, languages.hpp, test, any locale-mapping file), then `[strings] Regenerated` (generated files only).

### Task 3: Malay search categories

**Files:**
- Modify: `libs/indexer/categories_holder.hpp` (append `{"ms", 49}` to `kLocaleMapping` after `zh-Hant`, code 49)
- Modify: `data/categories.txt` (an `ms:` line in every block that has `en:`, including the `@group` definitions), `data/categories_cuisines.txt` (`ms:` wherever `id:` exists)
- Test: `libs/indexer/indexer_tests/categories_test.cpp`; `libs/search/search_tests/` (find the test that loads default categories, e.g. `suggest_tests.cpp` or a `categories_*` test)

**Interfaces:**
- Produces: categories locale code 49 = `ms`.

- [ ] **Step 1: Write the failing tests.**
  - `UNIT_TEST(CategoriesHolder_Malay)`: `MapLocaleToInteger("ms")`, `("ms_MY")`, `("ms-MY")` and `("ms_MY.UTF-8")` all equal 49, and `MapIntegerToLocale(49) == "ms"`. The existing `CategoriesHolder_Smoke` will also check the index.
  - `UNIT_CLASS_TEST(TestWithClassificator, CategoriesHolder_MalaySynonyms)`: with `GetDefaultCategories()`, `ForEachTypeByName(49, …)` (or the equivalent lookup by locale code; read `categories_holder.hpp`) finds the `amenity-fuel` type for `"stesen minyak"` and `"minyak"`, `amenity-toilets` for `"tandas"`, `amenity-place_of_worship-muslim` (or the type the `en` "mosque" block uses) for `"masjid"` and `"surau"`, and `amenity-restaurant` for `"restoran"` and `"kedai makan"`.
- [ ] **Step 2: Run** `cmake --build build-claude --target indexer_tests && ctest --test-dir build-claude --output-on-failure -R indexer_tests`. Expected: FAIL (`ms` unsupported).
- [ ] **Step 3: Add the mapping, then translate** every category block. Include common Malaysian synonyms and brand-neutral everyday words (e.g. fuel: `stesen minyak|minyak|petrol|stesen petrol`; mosque: `masjid|surau`; toilets: `tandas|toilet`; food: `restoran|kedai makan|gerai|mamak` where that fits the type). Use prefix digits the way `en:` does.
- [ ] **Step 4: Check.** Run `python3 -I tools/python/arah_ms_check.py data/categories.txt`. Expected: exit 0.
- [ ] **Step 5: Run** indexer_tests and `search_tests`. Expected: PASS (`CategoriesHolder_Smoke` included).
- [ ] **Step 6: Commit** `[search] Add Malay search categories`.

### Task 4: Malay app strings

**Files:**
- Modify: `data/strings/strings.txt` (~780 blocks)
- Modify: `android/app/src/main/res/xml/locales_config.xml` (add `<locale android:name="ms" />` in alphabetical position)
- Modify: `iphone/Maps/Maps.xcodeproj/project.pbxproj` (add `ms` to `knownRegions`; add `ms.lproj` file references for `InfoPlist.strings`, `Localizable.strings` and `Localizable.stringsdict` to the same variant groups as `id.lproj`, with fresh 24-hex IDs)
- Generated: `android/*/src/main/res/values-ms/*.xml`, `iphone/Maps/LocalizedStrings/ms.lproj/*`

**Interfaces:**
- Consumes: the Task 1 checker.

- [ ] **Step 1: Run the failing check:** `python3 -I tools/python/arah_ms_check.py data/strings/strings.txt`. Expected: exit 1, ~780 missing.
- [ ] **Step 2: Translate** every block, following the Glossary and Global Constraints. Work in batches of ~100 keys, in file order, reading each `comment` and `tags` for context. Plural blocks (`apple-plural` tags, keys with `:one`/`:other` style) get Malay forms for every plural category `en` has.
- [ ] **Step 3: Check.** Run the checker. Expected: exit 0.
- [ ] **Step 4: Regenerate** with `tools/unix/generate_localizations.sh` (expected exit 0). Then `ls android/app/src/main/res/values-ms iphone/Maps/LocalizedStrings/ms.lproj`: expected `strings.xml`, and `InfoPlist.strings`, `Localizable.strings`, `Localizable.stringsdict`.
- [ ] **Step 5: Register `ms`** in `locales_config.xml` and the `.pbxproj`. Then run `plutil -lint iphone/Maps/Maps.xcodeproj/project.pbxproj` (expected OK) and build the iOS app per `CLAUDE.md`, with `-destination` set to the iPhone 17 Pro simulator. Expected: BUILD SUCCEEDED, and `ms.lproj` present inside the built `.app`.
- [ ] **Step 6: Commit** `[strings] Add Malay app translation` (strings.txt, locales_config.xml, pbxproj), then `[strings] Regenerated`.

### Task 5: Malay map feature types

**Files:**
- Modify: `data/strings/types_strings.txt` (~1,390 blocks)
- Modify: `iphone/Maps/Maps.xcodeproj/project.pbxproj` (`ms.lproj/LocalizableTypes.strings` reference, as for `id`)
- Generated: `android/sdk/src/main/res/values-ms/types_strings.xml`, `iphone/Maps/LocalizedStrings/ms.lproj/LocalizableTypes.strings`

- [ ] **Step 1: Run the failing check:** `python3 -I tools/python/arah_ms_check.py data/strings/types_strings.txt`. Expected: exit 1, ~1,390 missing.
- [ ] **Step 2: Translate** in batches of ~200. These are short nouns shown on place pages ("Stesen minyak", "Hospital", "Surau"). Prefer the term a Malaysian would see on a signboard.
- [ ] **Step 3: Check** (expected exit 0), **regenerate** (expected exit 0), add the pbxproj reference, run `plutil -lint` (expected OK), and build iOS (expected BUILD SUCCEEDED).
- [ ] **Step 4: Commit** `[strings] Add Malay map feature type names`, then `[strings] Regenerated`.

### Task 6: Malay by default on iPhone, and on-device check

**Files:**
- Modify: `iphone/Maps/main.mm`

**Interfaces:**
- Produces: `NSUserDefaults` key `ArahDefaultLanguageApplied` (BOOL).

- [ ] **Step 1: Write the check first.** Install the current build on a fresh simulator state (`xcrun simctl uninstall` then install, with the simulator language English via `xcrun simctl spawn <id> defaults write -g AppleLanguages -array en`). Launch and screenshot. Expected (the failing state): the UI is in English.
- [ ] **Step 2: Implement** in `main()` before `UIApplicationMain`: if `ArahDefaultLanguageApplied` is not set, write `AppleLanguages = @[@"ms"]` to the app's standard user defaults, set the flag, and synchronize. Leave it alone on later launches, so a language the user picks in iOS Settings stays.
- [ ] **Step 3: Verify on the simulator** (Review Focus 2 and 4):
  1. Fresh install with the phone in English → launch → UI is in Malay (screenshot of the main screen, search, a place page, the route planner and settings).
  2. Switch the app to English via `xcrun simctl spawn <id> defaults write <bundle id> AppleLanguages -array en`, which mimics iOS Settings → relaunch → UI is in English and stays English after a second relaunch.
  3. Repeat (1) on an iPhone SE–size simulator; check that no button or tab label clips (Review Focus 4). Open a bookmarks list with counts (Review Focus 5).
  4. Start a route and confirm the voice language list shows "Bahasa Melayu" and the first instruction text is Malay.
  Fix any clipped or awkward string in `strings.txt`, then re-check, regenerate and rebuild.
- [ ] **Step 4: Commit** `[ios] Default Arah to Malay on first launch`, plus any string fixes as `[strings] …` and `[strings] Regenerated`.
- [ ] **Step 5: Final verification.** Run `python3 -I tools/python/arah_ms_check.py data/strings/strings.txt data/strings/types_strings.txt data/strings/sound.txt data/categories.txt` (expected exit 0) and `ctest -j --test-dir build-claude --output-on-failure -R "platform_tests|indexer_tests|search_tests|routing_tests|style_tests"` (expected all pass). Show the owner the screenshots from Step 3.
