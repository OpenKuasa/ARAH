# Arah Plan 3: Core Rebrand on CoMaps — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Rewritten 2026-10-21 for CoMaps.** The Organic Maps version of this plan is in git history (`git log -- docs/superpowers/plans/2026-10-21-arah-plan3-core-rebrand.md`), and its partial work is in `~/Documents/arah-archive/files-feat-004/`.

**Goal:** Users see "Arah", not "CoMaps" (or "Organic Maps"), in the app text of every language, the shared core and on iPhone. Every value the owner still has to supply sits in clearly marked places, and a checker lists them.

**Architecture:**
- **Config:** Arah-specific values live in `libs/platform/arah_config.hpp` (C++) and `iphone/Maps/Arah/ArahConfig.swift` (iOS). Each value not yet supplied is marked `ARAH-PLACEHOLDER`.
- **Strings:** CoMaps has no Twine; Weblate edits the platform string files directly. So the rename is applied by a reviewed script to every language's Android `values*/` and iOS `*.lproj/` files.
- **Servers:** they stay CoMaps' until Plan 6 (spec amendment: "until the owner supplies them they stay as marked placeholders"). So map downloads and CoMaps' live map updates keep working, but Arah ignores the donate link the metaserver hands out.
- **Test:** `tools/python/arah_brand_check.py` is rewritten for CoMaps' files. It fails while user-visible CoMaps / Organic Maps branding remains, and lists the open placeholders.

**Tech Stack:** C++ (core), Swift/Objective-C++ (iOS), Android XML resources (values only), iOS `.strings`, Xcode project and entitlements, Python 3.

**Spec:** `docs/superpowers/specs/2026-10-21-arah-phase1-rebrand-design.md`. Read the Amendment first (attribution is now "Based on CoMaps"; servers stay placeholders), then §3 Rebrand, §5 Map hosting and the Constraints.

### Scope (rulings made while planning)
- **In Plan 5, not here:**
  - Android identity: `appId` (`app.comaps`, `android/app/build.gradle.kts`), app name, icons.
  - Android Java/Kotlin links: `Constants.java`, `Utils.java`, `HelpFragment.java`.
  - The Android About screen.

  The Android *string files* are renamed here: that is value-only and checkable without the Android SDK.
- **Icon and screen restyle:** Plans 4 and 5.
- **Store metadata** (`iphone/metadata/`, `android/app/src/*/play/`), hosting, signing key and repo: Plan 6. The checker skips store metadata until then.
- **Placeholders**, because the owner hasn't supplied the values yet:
  - **Servers:** `METASERVER_URL`, `DEFAULT_URLS_JSON`, `DEFAULT_CONNECTION_CHECK_IP`, `COUNTRIES_TXT_SIGNATURE_HEX` and `MAP_SERIES` keep CoMaps' values, marked as placeholders.
  - **OSM login:** OAuth client IDs and the `cm://oauth2/osm/callback` redirect keep CoMaps' values until the owner registers Arah on openstreetmap.org.
  - **iOS IDs:** bundle IDs become `my.arah.app` (+ `.debug`, `.tests`, `.widgetextension`) and the iCloud container `iCloud.my.arah.app` (+ `.debug`).
  - **Web:** website `https://github.com/ARAH-ORG/arah`, support email `support@arah.invalid`, privacy policy and terms URLs `https://github.com/ARAH-ORG/arah/blob/main/PRIVACY.md` and `…/TERMS.md`.
  - **Hidden until supplied:** the App Store review link, news page and social links. An empty value hides the row.
- **Kayak:** already removed in CoMaps. No task.
- **Malay place names on the map** (Plan M finding) are an open owner decision. Not part of this plan.

## Global Constraints

- **The brand name is "Arah"** in every language: a proper noun, never translated, declined or transliterated.
- **Required attribution stays.** iPhone About shows "Based on CoMaps" (Malay: "Berasaskan CoMaps"). LICENSE, NOTICE and `copyright.html` stay. The map keeps "Map data © OpenStreetMap" (already CoMaps' label).
- **Stay mergeable:** change values, not structure. New Arah logic goes in `arah_*` / `Arah*` files. Upstream code paths are disabled through a value (an empty URL hides a row; a constant turns a branch off), never deleted.
- **No visible leftovers** (spec anti-goal): "CoMaps", "Organic Maps", `comaps.app`, `comaps.at`, `comaps.tech`, `organicmaps.app`, `omaps.app`, or CoMaps social/donate/news links. The only exception is the attribution above.
- **Incoming links keep working:** `https://comaps.at/…`, `comaps://`, `cm://`, `ge0://`, `om://`, `https://omaps.app/…` (spec §3). Only outgoing links change.
- **Malay stays complete:** `tools/python/arah_ms_check.py` still reports 0 problems on all nine Malay files.
- **Commits and branch:**
  - Commit style is `[subsystem] Summary` (≤80 chars), always with `git commit -s`.
  - Work on branch `feat-003-core-rebrand` from `feat-001-arah-setup`. Don't push. Merge locally only when the owner says so.
  - Build dirs are `build-<agent-name>`.
- **Build machine:** follow `HANDOFF.md` "Build notes" and `~/Documents/arah-archive/plan-m/machine-notes.md` (simulator recipes, zsh quoting).

## Review Focus

1. **Translations where the name is inflected, quoted or transliterated** (e.g. «CoMaps», "CoMaps-ის", "CoMapsista", or the name in Cyrillic, Arabic, CJK or Thai script) must become "Arah" too.
   - Pinned in Task 3: the checker's brand pattern matches "CoMaps" as a substring, without word boundaries.
   - Also pinned in Task 3: a script-agnostic diff check. For every key whose `en` value contains "CoMaps", each other language's value must contain "Arah" after the rename, or be on a reviewed exception list.
2. **Sharing a place with no Arah domain** must still be useful (name, coordinates, a standard map link) and contain no comaps.at/comaps.app. Pinned by Task 4's share-text test.
3. **CoMaps' metaserver can't show a donate prompt in Arah**, while downloads still use its server list. Pinned by Task 2's `ParseMetaConfig` test.
4. **Old shared links** (`https://comaps.at/…`, `cm://`, `ge0://`, `om://`) still open a place. Pinned by Task 4's parser test plus the existing ge0/mwm_url tests staying green.
5. **Placeholders must not ship silently:** the checker lists each `ARAH-PLACEHOLDER`, and `--release` fails on them. Pinned by Task 1's tests.

---

### Task 1: Brand checker for CoMaps, and Arah config

**Files:**
- Modify: `tools/python/arah_brand_check.py`, `tools/python/test_arah_brand_check.py` (rewrite the scanned-file lists for CoMaps)
- Create: `libs/platform/arah_config.hpp`, listed in `libs/platform/CMakeLists.txt`
- Create: `iphone/Maps/Arah/ArahConfig.swift`, added to the CoMaps target in the pbxproj

**Interfaces:**
- **CLI:** `python3 -I tools/python/arah_brand_check.py [--release]`. It exits 1 on leaks, and with `--release` also on placeholders.
- **`find_brand_leaks(root) -> list[str]`**
  - Pattern: `re.compile(r"co ?maps|comaps\.(app|at|tech)|organic ?maps|omaps\.app", re.I)`.
  - Scans user-visible sources:
    - Android `android/{app,sdk}/src/main/res/values*/*.xml` (string values only; skip `translatable="false"`).
    - iOS `iphone/Maps/LocalizedStrings/*.lproj/*.strings` and `*.stringsdict`.
    - `data/translations/sound-strings/*.json/localize.json`.
    - `iphone/Maps/CoMaps.plist` and `iphone/Maps/*.entitlements`.
    - The `PRODUCT_NAME`, `INFOPLIST_KEY_CFBundleDisplayName` and `PRODUCT_BUNDLE_IDENTIFIER` lines of the pbxproj.
    - Outgoing-link code: `libs/ge0/url_generator.cpp`, `iphone/Maps/Classes/Share/*.mm`, `iphone/Maps/UI/Information/*.swift`, `iphone/Maps/Model/Social Media.swift`, `iphone/Maps/UI/Settings/CustomMapServerView.swift`.
  - Reports `path:line: [key] text`.
  - `ALLOWED` is an explicit list of `(path glob, key-or-substring, reason)`. Entries:
    - the `about_based_on` key (attribution);
    - `CoMaps.plist`'s own file name;
    - comment lines.
- **`find_placeholders(root) -> list[str]`:** unchanged from the current checker.
- **`arah_config.hpp`**, namespace `arah`, `inline constexpr std::string_view`:
  - `kAppName = "Arah"`
  - `kWebsiteUrl`, `kSupportEmail`, `kPrivacyUrl`, `kTermsUrl`: the placeholder values in Scope, each with `// ARAH-PLACEHOLDER: …`
  - `kShareLinkBase = ""` (no domain yet)
  - `inline constexpr bool kAcceptMetaserverDonateUrl = false;`
  - Port the header from `~/Documents/arah-archive/files-feat-004/libs/platform/arah_config.hpp` and extend it.
- **`ArahConfig.swift`**, `enum ArahConfig` with `static let`:
  - `appName = "Arah"`
  - `websiteURL`, `privacyURL`, `termsURL`, `supportEmail`: same values as the C++ header, each with an `// ARAH-PLACEHOLDER` comment.
  - `appStoreReviewURL: URL? = nil`, `newsURL: URL? = nil`, `socialMediaEnabled = false`.

- [ ] **Step 1: Write the failing tests** in `test_arah_brand_check.py` (temp-dir repos):
  - `test_android_leak_found`: `values-ru/strings.xml` with `<string name="k">О «CoMaps»</string>` gives 1 leak naming `k`.
  - `test_untranslatable_skipped`: `<string name="project_name" translatable="false">CoMaps</string>` gives 0 leaks.
  - `test_ios_leak_found`: `ms.lproj/Localizable.strings` with `"k" = "Versi CoMaps: %@";` gives 1 leak.
  - `test_url_leak_found`: `https://www.comaps.app/news/` in `InformationView.swift` gives 1 leak.
  - `test_attribution_allowed`: `"about_based_on" = "Based on CoMaps";` gives 0 leaks.
  - `test_release_fails_on_placeholder`: `main(["--release"])` returns 1 with a placeholder present. `main([])` returns 0 when there are only placeholders.
- [ ] **Step 2: Run** `python3 -I tools/python/test_arah_brand_check.py`. Expected: FAIL (the old checker scans `data/strings`).
- [ ] **Step 3: Implement** the checker changes and create both config files.
- [ ] **Step 4: Run** the tests (expected: PASS). Then run the checker on the repo and record the leak count per file group in the ledger (expected: exit 1 with many leaks; this is the baseline for Tasks 2–5). Build `platform_tests` (expected: compiles, so the header is valid).
- [ ] **Step 5: Commit** `[tools] Check CoMaps branding in Arah` and `[platform] Add Arah config` (the latter includes `ArahConfig.swift` and the pbxproj reference).

### Task 2: Server placeholders, and no donate link from CoMaps' metaserver

**Files:**
- Modify: `private.h`: add `// ARAH-PLACEHOLDER: …` comments above:
  - `METASERVER_URL`, `DEFAULT_URLS_JSON`, `DEFAULT_CONNECTION_CHECK_IP`, `COUNTRIES_TXT_SIGNATURE_HEX`, `MAP_SERIES` ("Arah map hosting and signing key, spec §5 / Plan 6");
  - the OSM OAuth block ("register Arah on openstreetmap.org; replace client IDs and the cm:// redirect").

  The values themselves don't change.
- Modify: `libs/platform/servers_list.cpp`: skip `settings::kDonateUrl` when `!arah::kAcceptMetaserverDonateUrl` (a one-condition change inside the existing `if`).
- Test: `libs/platform/platform_tests/arah_config_tests.cpp` (new; port the archive's file of that name), registered in that `CMakeLists.txt`.

**Interfaces:**
- Consumes: `arah::kAcceptMetaserverDonateUrl` (Task 1), `downloader::ParseMetaConfig(std::string const &) -> std::optional<MetaConfig>`.

- [ ] **Step 1: Write the failing test** `UNIT_TEST(Arah_MetaserverDonateIgnored)`. Parse `{"servers":["https://a.example/"],"settings":{"DonateUrl":"https://comaps.app/donate/","NY":"1"}}` and assert:
  - the result has a value;
  - `m_serversList == {"https://a.example/"}`;
  - `m_settings` has no `DonateUrl` key;
  - `m_settings` still has `NY`.

  Add `UNIT_TEST(Arah_DefaultServersStillParse)`: `ParseMetaConfig(GetPlatform().DefaultUrlsJSON())` has a non-empty server list.
- [ ] **Step 2: Run** `./build-<agent>/platform_tests --data_path=data/ --user_resource_path=data/ --filter=Arah`. Expected: `Arah_MetaserverDonateIgnored` FAILs and the other passes.
- [ ] **Step 3: Implement** the `servers_list.cpp` condition and the `private.h` comments.
- [ ] **Step 4: Run** `platform_tests` and `storage_tests`. Expected: the Arah tests pass, and storage_tests is unchanged from its baseline (run it on the branch base first, and ledger any upstream failures).
- [ ] **Step 5: Commit** `[platform] Ignore the CoMaps donate link in Arah and mark server placeholders`.

### Task 3: "Arah" in all app text (every language, Android and iOS)

**Files:**
- Modify:
  - `android/app/src/main/res/values*/strings.xml` and `android/sdk/src/main/res/values*/strings.xml` (all languages);
  - `iphone/Maps/LocalizedStrings/*.lproj/{Localizable,InfoPlist}.strings` and `Localizable.stringsdict`;
  - `data/translations/sound-strings/*.json/localize.json`, only if any voice string names the brand.
- Add the key `about_based_on` to iOS only: `en.lproj` "Based on CoMaps" and `ms.lproj` "Berasaskan CoMaps". Other languages fall back to English. Android gets it in Plan 5.

**Rules:**
- **Name:** replace "CoMaps" (and any leftover "Organic Maps") with "Arah", keeping punctuation and grammar. Transliterated forms in non-Latin scripts are found with Review Focus 1's diff check and replaced too.
- **URLs:**
  - Website, help and FAQ links on `comaps.app`, plus `translated_om_site_url` in every language, become `kWebsiteUrl`'s value (`https://github.com/ARAH-ORG/arah`).
  - Privacy and terms are built from `translated_om_site_url` in `InformationView.swift`; Task 5 switches them to `ArahConfig`.
  - Download links (`…/download/`) become `kWebsiteUrl`.
- **Support emails:** `*@comaps.app` becomes `support@arah.invalid`.
- **Donate, news and social strings stay** (their UI is hidden by values in Tasks 2 and 5; deleting keys hurts mergeability).

- [ ] **Step 1: Run the failing checks:**
  - `python3 -I tools/python/arah_brand_check.py | grep -cE "values|lproj"`. Expected: many leaks.
  - The Review Focus 1 diff check (a scratch script) prints every key whose `en` contains "CoMaps", and every language value that doesn't contain "CoMaps"/"Arah" after the rename. Expected: the list of transliterations to handle.
- [ ] **Step 2: Apply the replacements** with a scratch script:
  - Android XML: edit text in place, without re-serialising the file, so diffs stay one-line.
  - iOS `.strings`: line-based edit.
  - Print every changed value. Spot-check 30 across scripts: Latin, Cyrillic, Arabic, CJK, Thai, and Malay.
  - Add the two `about_based_on` lines.
- [ ] **Step 3: Check:**
  - brand checker over strings: 0 leaks;
  - the diff check: 0 unexplained values;
  - `python3 -I tools/python/arah_ms_check.py` on the nine Malay files: 0 problems;
  - `python3 -I tools/python/test_arah_ms_check.py`: OK;
  - `xmllint --noout` on every changed Android file, and `plutil -lint` on every changed iOS file: all OK.
- [ ] **Step 4: Commit** `[android] Rename CoMaps to Arah in app text` and `[ios] Rename CoMaps to Arah in app text`.

### Task 4: Outgoing share links without a domain

**Files:**
- Create: `libs/map/arah_share.hpp`, `libs/map/arah_share.cpp` (listed in `libs/map/CMakeLists.txt`)
- Modify: `iphone/Maps/Classes/Share/MWMShareActivityItem.mm`: when `arah::kShareLinkBase` is empty, use `arah::ShareLink` instead of rewriting `comaps://` to `https://comaps.at/`.
- Modify: `iphone/Maps/Classes/Share/MWMEditorViralActivityItem.mm`: replace the `comaps.app/get` / `fb-editor-v1` links with `arah::kWebsiteUrl`.
- Test: `libs/map/map_tests/arah_share_tests.cpp` (registered in that `CMakeLists.txt`); `libs/ge0/ge0_tests/` (existing parser tests).

**Interfaces:**
- Produces: `namespace arah { std::string ShareLink(double lat, double lon, int zoom); }`. It returns `https://www.openstreetmap.org/?mlat=<lat>&mlon=<lon>#map=<zoom>/<lat>/<lon>`, with coordinates to 5 decimals.
- Produces: `std::string ShareText(std::string_view name, std::string_view address, double lat, double lon, int zoom)`. It returns the lines below, joined by `\n`, skipping empty name or address lines:
  - `name`
  - `address`
  - `<lat>, <lon>` (5 decimals)
  - `ShareLink(...)`
- `GenerateShortShowMapUrl` and the ge0 parser stay unchanged, so incoming links keep working.

- [ ] **Step 1: Write the failing tests:**
  - `UNIT_TEST(Arah_ShareTextHasNoCoMapsLink)`: `ShareText("Masjid Jamek", "Jalan Tun Perak, Kuala Lumpur", 3.14893, 101.69585, 17)` contains:
    - `"Masjid Jamek"`
    - `"3.14893, 101.69585"`
    - `"https://www.openstreetmap.org/?mlat=3.14893&mlon=101.69585#map=17/3.14893/101.69585"`

    It contains none of `"comaps"`, `"omaps"` or `"ge0"` (case-insensitive).
  - `UNIT_TEST(Arah_ShareTextSkipsEmptyAddress)`: with an empty address, there's no blank line.
  - `UNIT_TEST(Arah_OldLinksStillParse)` in `ge0_tests`: `ge0::Ge0Parser` parses a `https://comaps.at/…`, a `cm://…` and a `ge0://…` URL to the same lat/lon. Take the URLs from an existing parser test case.
- [ ] **Step 2: Run** `map_tests` and `ge0_tests` with `--filter=Arah`. Expected: the share tests FAIL (no such functions); `Arah_OldLinksStillParse` passes.
- [ ] **Step 3: Implement** `arah_share.cpp` and switch the two iOS share items to it. For the HTML/email share variant, use `ShareLink` as the anchor.
- [ ] **Step 4: Run** `map_tests`, `ge0_tests` and the brand checker on the share files. Expected: the Arah tests pass, and the checker shows 0 leaks in `Classes/Share`.
- [ ] **Step 5: Commit** `[map] Share Arah places as OpenStreetMap links`.

### Task 5: iPhone identity and About screen

**Files:**
- Modify: `iphone/Maps/Maps.xcodeproj/project.pbxproj`:
  - `PRODUCT_NAME` becomes `Arah` / `Arah (Debug)`.
  - The widget's `INFOPLIST_KEY_CFBundleDisplayName` becomes `Arah`.
  - Every `app.comaps*` bundle ID becomes `my.arah.app*`, keeping the suffixes. Also set the `${BUNDLE_IDENTIFIER}` setting's source; find it with `grep -rn "BUNDLE_IDENTIFIER" xcode iphone`.
- Modify: `iphone/Maps/CoMaps-Debug.entitlements`, `iphone/Maps/CoMaps-Release.entitlements`:
  - iCloud containers become `iCloud.my.arah.app(.debug)`.
  - Remove `applinks:comaps.at` (no Arah domain).
- Modify: `iphone/Maps/CoMaps.plist`: add URL scheme `arah`, keeping `cm`, `ge0`, `geo` and the others.
- Modify: `iphone/Maps/UI/Information/InformationView.swift`:
  - News, volunteer, review and social rows show only when their `ArahConfig` value is set.
  - Privacy and terms open `ArahConfig.privacyURL` / `termsURL`.
  - Add a "Based on CoMaps" line (`about_based_on`) next to the copyright row.
- Modify: `iphone/Maps/Model/Social Media.swift` (email becomes `ArahConfig.supportEmail`) and `CustomMapServerView.swift` (example URL becomes `https://maps.example.org/`).
- Leave internal identifiers alone: file names (`CoMaps.plist`), error domains, Spotlight domains, log tags, and the incoming-link hosts in `DeepLinkHandler.swift`.

- [ ] **Step 1: Run the failing check:** `python3 -I tools/python/arah_brand_check.py | grep -E "pbxproj|entitlements|plist|Information|Social|CustomMap"`. Expected: leaks reported.
- [ ] **Step 2: Apply the edits.** The pbxproj can't hold comments next to build settings, so `arah_config.hpp` lists the placeholder bundle and iCloud IDs, already marked in Task 1.
- [ ] **Step 3: Check:**
  - `plutil -lint` on the pbxproj, both entitlements files and `CoMaps.plist`: OK.
  - Brand checker: 0 leaks for iOS files.
  - Build iOS for the iPhone 17 Pro simulator (`-destination 'id=0A66D354-92E6-4D43-83C4-D7C82FE5C6F9'`, `CODE_SIGNING_ALLOWED=NO`, `-derivedDataPath build-<agent>-ios`). Expected: BUILD SUCCEEDED, producing `Arah (Debug).app` with `CFBundleIdentifier` `my.arah.app.debug` and `CFBundleDisplayName` "Arah (Debug)" (read both with PlistBuddy).
- [ ] **Step 4: Commit** `[ios] Rename the iPhone app to Arah`.

### Task 6: Verify end to end

- [ ] **Step 1: Brand check:**
  - `python3 -I tools/python/arah_brand_check.py`: 0 leaks; the placeholder list printed.
  - `--release`: exit 1, listing exactly the Scope placeholders (servers, connection IP, signing key, map series, OSM OAuth, bundle and iCloud IDs, website, support email, privacy, terms).
- [ ] **Step 2: Test suite:** `platform_tests`, `storage_tests`, `ge0_tests`, `map_tests`, `indexer_tests`, `i18n_tests` and `style_tests --filter=Arah`, plus both Python checkers. Expected: all Arah tests pass; upstream suites unchanged from their branch-base baseline (ledgered).
- [ ] **Step 3: Simulator pass** (Review Focus 2–4). Avoid `simctl openurl`: it shows an undismissable dialog.
  - Fresh install of `my.arah.app.debug`. The home-screen label reads "Arah (Debug)" (screenshot via `simctl io`).
  - The app opens in Malay, as before, and the main map renders with the Malaysia map placed under `Documents/<version>/`.
  - The core log shows the metaserver servers list was used (`Requesting metaserver`) and no `DonateUrl` was stored. Check with `defaults read`/`settings.ini`.
  - Screenshot each check for the owner.
- [ ] **Step 4: Update `HANDOFF.md`:** Plan 3 is done and the placeholder list is current. Commit `[docs] Update Arah handoff after Plan 3`.
