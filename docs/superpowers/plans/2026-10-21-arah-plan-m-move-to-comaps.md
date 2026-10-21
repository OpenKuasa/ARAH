# Arah Plan M: Move Arah onto CoMaps — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Repo note (2026-10-21):** this plan now runs in the clean CoMaps clone at `~/Documents/arah` (remote `comaps`).
> Branch `feat-002-move-to-comaps` from `feat-001-arah-setup` (which already holds Arah's docs, checkers and `CLAUDE.md`, so
> Task 1 Step 4 is done). Wherever this plan says "branch `feat-001-arah-phase1-design`" as a source, read
> `~/Documents/arah-archive/files/` (same paths) instead.

**Goal:** Rebuild Arah's finished Phase 1 work (the Tenang map palette and complete Malay) on top of CoMaps, so every later plan builds on CoMaps.

**Architecture:**
- **Branch:** a new branch from `comaps/main`, the CoMaps upstream (remote `comaps`, Codeberg), with Arah's docs and tools brought over.
- **Map palette:** ported by MapCSS variable name, plus Tenang values for CoMaps-only variables. Route and UI accent colours live in each style's `drape_colors.mapcss`.
- **Malay:** reused by key from Arah's Twine files on `feat-001-arah-phase1-design`, converted to CoMaps' formats:
  - Android `res/values-ms/*.xml`
  - iOS `ms.lproj/*`
  - JSON `data/translations/{sound,categories}-strings/ms.json/localize.json`

  CoMaps-only keys are translated with the same glossary.
- **Tests:** The Arah checkers are adapted to these formats and act as the tests, alongside the ported C++ tests.

**Tech Stack:** MapCSS + kothic, Android XML resources, iOS .strings/.stringsdict, JSON, C++ unit tests, Python 3.

**Spec:** `docs/superpowers/specs/2026-10-21-arah-phase1-rebrand-design.md`, read the "Amendment (2026-10-21)" first, then §2 and §4.

**Source of reusable work** (read-only): branch `feat-001-arah-phase1-design`:
- `data/styles/*/{light,dark}/colors.mapcss` and the `colors { }` blocks of `style.mapcss`
- `data/strings/{strings,types_strings,sound}.txt` and `data/categories*.txt` (`ms` values)
- `libs/map/style_tests/arah_palette_test.cpp`
- `tools/python/arah_ms_check.py`, `tools/python/arah_brand_check.py`
- `iphone/Maps/main.mm` (`ApplyArahDefaultLanguage`)
- Plan 2's glossary.

## Global Constraints

- **Branch** `feat-005-comaps-base` from `comaps/main` at its current tip, `a64450d0c7`. Don't push anywhere. Remote `origin` is Organic Maps and `comaps` is CoMaps; Arah's own remote comes in Plan 6.
- **Mergeability with CoMaps:** change values, not structure. Arah-only code goes in `arah_*` files.
- **Follow CoMaps' conventions on this branch.** Read its `docs/`, `CONTRIBUTING.md` and `.forgejo` CI for build, format and translation rules. Where they differ from Organic Maps' `CLAUDE.md`, CoMaps wins. Ledger each difference that matters.
- **Malay:** natural Malaysian Malay, Plan 2's glossary, the reviewed corrections from Plan 2's final review (e.g. Aktiviti Luar, jalan keluar for roundabouts, Kampung Kecil, Jalan Persekutuan for trunk), "…" not "...", and placeholders identical to the same platform's English.
- **Tenang palette values** are those on `feat-001-arah-phase1-design` after Plan 1's fixes, as pinned by that branch's `arah_palette_test.cpp`.
- **Commits:** generated files go in separate commits. Use CoMaps' commit-message style if it differs (check `git log comaps/main`). Sign off with `git commit -s` if CoMaps requires DCO.

## Review Focus

1. **Keys whose English changed in CoMaps.** About 100 of 525 Android app keys have different English from Organic Maps. Reusing the old Malay would then say something else. Pinned in Task 4: the checker flags any reused key whose CoMaps English differs from Arah's source English, and each flagged key gets retranslated.
2. **Platform placeholder styles differ** (`%1$s` on Android, `%@` on iOS). Malay copied across platforms must use each platform's own English placeholders. Pinned by the adapted checker comparing against the same file's English (Task 4).
3. **CoMaps-only map style variables left at old colours** make an odd patchwork map. Pinned by Task 2's check that every `@variable` in the four Tenang styles has a value from the Tenang table or a ledgered ruling, plus the before/after screenshots.
4. **Search with CoMaps' extra categories** (e.g. new types since the split) still finds everyday Malaysian words. Pinned by Task 3's `CategoriesHolder_MalaySynonyms` port.
5. **CoMaps' Android language screen lists Malay.** It must appear once the Malay resources exist. Pinned by checking `AppLanguagesFragment`'s language source (`locales_config.xml` and/or `supportedLocalizations`) in Task 4. Behaviour on device is checked in Plan 5.

---

### Task 1: CoMaps branch, baseline builds, Arah docs and tools

**Files:**
- Branch `feat-005-comaps-base` from `comaps/main`.
- Bring over from `feat-001-arah-phase1-design`: `docs/superpowers/**`, `tools/python/arah_ms_check.py`, `tools/python/test_arah_ms_check.py`, `tools/python/arah_brand_check.py`, `tools/python/test_arah_brand_check.py`. Use `git checkout feat-001-arah-phase1-design -- <paths>`, committed as `[docs] Bring Arah design and plans` and `[tools] Bring Arah checkers`.

- [ ] **Step 1: Create the branch.** Run `git checkout -b feat-005-comaps-base comaps/main && git submodule update --init --recursive` (CoMaps' `.gitmodules` may differ). Expected: a clean tree.
- [ ] **Step 2: Baseline desktop build.** Run `cmake --preset debug -B build-comaps -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt` (check that CoMaps has `CMakePresets.json`; otherwise follow its `INSTALL.md`), then `cmake --build build-comaps --target style_tests indexer_tests i18n_tests desktop`. Expected: success. If the build fails, fix only what's needed to build on macOS 27 and ledger it.
- [ ] **Step 3: Baseline iOS build** for the iPhone 17 Pro simulator, with `CODE_SIGNING_ALLOWED=NO` and a separate `-derivedDataPath`. Expected: BUILD SUCCEEDED. Screenshot KL at the three zooms used in Plan 1. These are the CoMaps "before" shots.
- [ ] **Step 4: Bring over the docs and tools** and commit them. Expected: `python3 -I tools/python/test_arah_ms_check.py` runs; its RepoTest failures are expected until Tasks 3 and 4.

### Task 2: Tenang palette on CoMaps styles

**Files:**
- Modify: `data/styles/{default,vehicle}/{light,dark}/colors.mapcss`
- Modify: `data/styles/*/{light,dark}/drape_colors.mapcss` (named UI colours such as `Route`, `RouteOutline`, `Selection`, `Arrow3D`, `DefaultTrackColor`, `SearchmarkDefault`, `RatingNone`, `TrafficOutline`)
- Modify: outdoors files in the same way as Plan 1, i.e. accents only, unless outdoors imports the default palette as it does in Organic Maps.
- Create: `libs/map/style_tests/arah_palette_test.cpp` (port it, adapting to CoMaps' `drule` APIs), registered in that `CMakeLists.txt`.

- [ ] **Step 1: Port the test first.** The expectations are the same as on `feat-001`: route/background per style, traffic colours unchanged in every style (taken from CoMaps' current values), light secondary roads visible (contrast ≥ 1.3 vs background, ≥ 1.25 vs residential), dark rivers ≥ 2.5, and the night road hierarchy, parks/buildings and park-label thresholds. Run `style_tests`. Expected: FAIL on the Arah expectations.
- [ ] **Step 2: Port the values.** A script copies every `@variable` value that exists on both `feat-001` and CoMaps. It then lists the CoMaps-only variables, and each gets a Tenang value chosen by role (land / water / green / road / building / label / landuse), recorded in the ledger as one table.
- [ ] **Step 3: Regenerate** with CoMaps' `tools/unix/generate_drules.sh`, rebuild, and run `style_tests`. Expected: PASS, including CoMaps' own consistency tests.
- [ ] **Step 4: Rebuild iOS** and take the same KL screenshots, light and dark, side by side with the Task 1 baseline. Fix any patchwork colour, then regenerate and re-run the tests.
- [ ] **Step 5: Commit** `[styles] Apply Arah Tenang palette` and the regenerated files separately.

### Task 3: Malay search and voice (core and JSON)

**Files:**
- Modify: `libs/indexer/categories_holder.hpp`: append `{"ms", <next code>}`, growing the array size by 1 (CoMaps uses a sized `std::array`, not `to_array`).
- Modify: `libs/platform/languages.hpp`: add `{"ms", "Bahasa Melayu"}` after `id`.
- Create: `data/translations/sound-strings/ms.json/localize.json`, built from `feat-001`'s `sound.txt` `ms` values by key. Keys missing in Arah are translated; keys only Arah had are dropped.
- Create: `data/translations/categories-strings/ms.json/localize.json`, built from `feat-001`'s `data/categories.txt` and `categories_cuisines.txt` `ms:` lines, keyed by the category's first line. CoMaps-only category keys are translated. Then run CoMaps' `tools/unix/generate_categories.sh`.
- Test: port `CategoriesHolder_Malay` and `CategoriesHolder_MalaySynonyms` (indexer tests) and `GetTextByIdMalayTest` (CoMaps has it in `libs/i18n/i18n_tests/get_text_by_id_tests.cpp`).

- [ ] **Step 1: Port the three tests and the `ms` TTS entry.** Expected: FAIL (no `ms` locale, no `ms.json`).
- [ ] **Step 2: Build the JSON files** with a scratch converter that reports reused, missing and dropped keys. Translate the missing keys with the glossary.
- [ ] **Step 3: Regenerate** categories (and anything else CoMaps' tools need), then build and run the indexer, search, i18n and routing tests. Expected: PASS. Raise the trie bound only if CoMaps has the same guard and Malay exceeds it; ledger the change.
- [ ] **Step 4: Commit** `[search] Add Malay search categories`, `[routing] Add Malay voice directions` and the generated files.

### Task 4: Malay app text and place types (Android and iOS)

**Files:**
- Create: `android/{app,sdk,libs/*}/src/main/res/values-ms/*.xml`, mirroring which modules have `values-id` or `values-in` in CoMaps. This includes plurals and `types_strings.xml` if it exists.
- Create: `iphone/Maps/LocalizedStrings/ms.lproj/{Localizable.strings,Localizable.stringsdict,InfoPlist.strings,LocalizableTypes.strings}`.
- Modify: the iOS `.pbxproj` (`ms` in `knownRegions` and the variant groups, as in Plan 2), `android/app/src/main/res/xml/locales_config.xml` and `android/gradle.properties` `supportedLocalizations` (if CoMaps still filters).
- Modify: `tools/python/arah_ms_check.py`, adding Android XML and iOS `.strings`/`.stringsdict` checks. Each Malay file is compared with the same platform's English file: every English key has Malay, placeholders match, no "...", and plurals have an `other` form.

- [ ] **Step 1: Extend the checker, tests first.** Add unit tests for an Android XML missing key, an iOS placeholder mismatch and a stringsdict without `other`. Then add a `--changed-english` report: keys whose CoMaps English differs from `feat-001`'s `en`. Run them. Expected: FAIL, then implement, then PASS.
- [ ] **Step 2: Build the Malay files** with a scratch converter that reuses Malay by key where the English is unchanged. It writes a work list of missing keys plus keys with changed English, for each platform.
- [ ] **Step 3: Translate the work list** with parallel translator agents, using Plan 2's brief, the glossary and its corrections. Check every batch with the checker and spot-check the language.
- [ ] **Step 4: Register `ms`** in the pbxproj, `locales_config.xml` and gradle. Confirm CoMaps' `AppLanguagesFragment` reads its list from those (Review Focus 5).
- [ ] **Step 5: Verify.** Run the checker on all Android/iOS Malay files (expected: 0 problems), `plutil -lint` on the iOS files (expected: OK), `xmllint --noout` on the Android XML (expected: OK) and the iOS build (expected: BUILD SUCCEEDED, with `ms.lproj` bundled).
- [ ] **Step 6: Commit** `[android] Add Malay translation`, `[ios] Add Malay translation`, and `[tools] Check Malay in platform string files`.

### Task 5: Malay by default on iPhone, and check

**Files:** Modify `iphone/Maps/main.mm` (port `ApplyArahDefaultLanguage` unchanged).

- [ ] **Step 1: Failing check.** A fresh install on an English-only simulator shows English labels (KL screenshot, e.g. "Royal Museum").
- [ ] **Step 2: Port the function.** Rebuild, then do a fresh install. Expected: Malay labels ("Muzium Diraja"), the app's `AppleLanguages` is `ms`, and `UserDefaultsTTSLanguageBcp47` is `ms-MY` (verify that CoMaps' TTS code behaves the same).
- [ ] **Step 3: Switch check.** Set the app's language to `en` via `simctl spawn defaults write <container plist>`, relaunch twice. Expected: it stays English. Restore the simulator's global language list afterwards (record it before changing it).
- [ ] **Step 4: Commit** `[ios] Default Arah to Malay on first launch`. Run all ported tests, the checkers and the iOS build, and show the owner the before/after screenshots.
