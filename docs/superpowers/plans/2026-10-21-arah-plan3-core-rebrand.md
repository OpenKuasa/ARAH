# Arah Plan 3: Core Rebrand — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Users see "Arah", not "Organic Maps", in the shared core and on iPhone. Organic Maps' servers can no longer steer Arah. Every value the owner still has to supply sits in one clearly marked place.

**Architecture:** One new header, `arah_config.hpp`, holds every Arah-specific value: name, IDs, URLs, emails. Each value not yet supplied is marked `ARAH-PLACEHOLDER`. Shared C++ and `private.h` read from it. User-visible text changes through `data/strings/` (all languages) and is regenerated. iOS identity (name, bundle IDs, iCloud, associated domains) changes in the Xcode project and entitlements. A brand checker (`tools/python/arah_brand_check.py`) is the test: it fails while user-visible Organic Maps branding remains, and lists the open placeholders.

**Tech Stack:** C++ (core), Objective-C++/Swift (iOS), Twine strings, Xcode project files, Python 3 checker.

**Spec:** `docs/superpowers/specs/2026-10-21-arah-phase1-rebrand-design.md` §3 Rebrand throughout, §5 Map hosting, §6 Repository.

### Scope (rulings made while planning)
- **Android identity** (`appId`, app name, icons, Android-only links) goes to Plan 5, which needs the Android SDK to build and test. Shared strings and core changes here already reach Android.
- **The app icon** and visual restyle of the screens go to Plans 4 and 5. **Store metadata, hosting the mirror and metaserver, and the GitHub repo** go to Plan 6.
- **Placeholders, since the owner hasn't supplied the values yet:**
  - Map download servers **keep Organic Maps' CDN for now**, so the app stays testable. They are marked `ARAH-PLACEHOLDER`, and the brand checker lists them.
  - **The metaserver is switched off now** (`METASERVER_URL ""`). Downloads then use the built-in server list, and Organic Maps can no longer push donate prompts or settings into Arah. That is the spec §5 intent, available immediately.
  - Bundle ID `my.arah.app`, website `https://github.com/ARAH-ORG/arah` and support email `support@arah.invalid` are placeholders.
  - OSM OAuth keeps Organic Maps' credentials until the owner registers Arah on openstreetmap.org. The redirect scheme changes once that registration exists.

## Global Constraints

- **The brand name is "Arah"** in every language: a proper noun, never translated or declined.
- **Required attribution stays.** The About screen keeps "Based on Organic Maps" and the Apache-2.0 LICENSE/NOTICE. The map keeps "© OpenStreetMap" (spec Constraints). The map label changes from "Map data © OpenStreetMap © Organic Maps" to "Map data © OpenStreetMap".
- **Stay mergeable:** change values, not structure. Keep any new Arah logic in Arah-named files (`arah_config.hpp`, `arah_*.py`). Don't delete upstream code paths that a value can disable.
- **No visible Organic Maps leftovers** (spec anti-goal): "Organic Maps", organicmaps.app, omaps.app, Organic Maps social/donate/news links. The only exception is the attribution above.
- **Incoming `omaps.app`, `ge0` and `om://` links still open in Arah** (spec §3). Only outgoing links change.
- **Generated files** are committed separately as `[strings] Regenerated`. Commits use `[subsystem] Summary`, ≤80 chars, `git commit -s`.
- **Branch** `feat-004-core-rebrand` from `feat-001-arah-phase1-design`. Don't push.

## Review Focus

1. **Sharing a place with no domain:** the text must still be useful (name, address, coordinates, a standard map link) and must not contain omaps.app. Pinned by Task 4's share-text test.
2. **Map downloads still work after the metaserver is switched off:** the app falls back to the built-in server list. Pinned by Task 2's test that `MapFilesDownloader` uses `DefaultUrlsJSON` servers when `MetaServerUrl()` is empty (or by a check that `GetServersList` returns the default list), plus a manual download of Malaysia in the simulator in Task 6.
3. **Strings in all ~45 languages:** "Organic Maps" is replaced even when declined or quoted (e.g. «Organic Maps», "Organic Maps-ის"). Pinned by Task 3's brand checker, which runs over every language value.
4. **Deep links from old Organic Maps shares** (`https://omaps.app/…`, `om://`, `ge0://`) still open in Arah. Pinned by the existing ge0/mwm_url tests staying green (Task 4) and a manual check in Task 6.
5. **Placeholders must not ship silently:** the brand checker reports each `ARAH-PLACEHOLDER` occurrence, and `--release` turns them into failures. Pinned by Task 1's tests.

---

### Task 1: Brand checker and Arah config

**Files:**
- Create: `tools/python/arah_brand_check.py`, `tools/python/test_arah_brand_check.py`
- Create: `libs/platform/arah_config.hpp`
- Modify: `libs/platform/CMakeLists.txt` (list the header)

**Interfaces:**
- Produces: CLI `python3 tools/python/arah_brand_check.py [--release]`, which exits 1 if it finds problems. Functions:
  - `find_brand_leaks(repo_root) -> list[str]`: scans the user-visible sources, i.e. `data/strings/*.txt` (every language value), `iphone/Maps/OMaps.plist`, the `PRODUCT_NAME` and `INFOPLIST_KEY_CFBundleDisplayName` lines in `iphone/Maps/Maps.xcodeproj/project.pbxproj`, `iphone/Maps/*.entitlements`, `libs/drape_frontend/gui/copyright_label.cpp`, `libs/map/share.cpp` and `libs/ge0/url_generator.cpp` (outgoing link generation only). Each line containing `Organic Maps`, `organicmaps.app` or `omaps.app` is reported, unless it is in `ALLOWED`, an explicit list of `(path, substring)` pairs such as the About attribution key.
  - `find_placeholders(repo_root) -> list[str]`: every line containing `ARAH-PLACEHOLDER` in tracked text files.
- Produces: `libs/platform/arah_config.hpp`, namespace `arah`, with `inline constexpr std::string_view`:
  - `kAppName = "Arah"`
  - `kWebsiteUrl = "https://github.com/ARAH-ORG/arah"` (placeholder)
  - `kSupportEmail = "support@arah.invalid"` (placeholder)
  - `kShareLinkBase = ""` (no domain yet; empty means "share a geo: link")

  Each placeholder line carries a `// ARAH-PLACEHOLDER: <what the owner must supply>` comment.

- [ ] **Step 1: Write the failing tests** (`unittest`, temp dirs):
  - `test_leak_found`: a fake `data/strings/strings.txt` with `ru = «Organic Maps»` produces one leak naming the file and key line.
  - `test_allowed_not_reported`: a line matching an `ALLOWED` entry is not reported.
  - `test_placeholder_listed`: a file containing `// ARAH-PLACEHOLDER: x` is listed.
  - `test_release_fails_on_placeholder`: `main(["--release"])` returns 1 when a placeholder exists; `main([])` returns 0 when only placeholders exist and there are no leaks.
- [ ] **Step 2: Run** `python3 -I tools/python/test_arah_brand_check.py`. Expected: ImportError/FAIL.
- [ ] **Step 3: Implement** the checker and create `arah_config.hpp`.
- [ ] **Step 4: Run** the tests (expected: PASS). Then run `python3 -I tools/python/arah_brand_check.py | tail -1`. Expected: exit 1, with many leaks reported. That is the baseline for Tasks 2–5.
- [ ] **Step 5: Commit** `[tools] Add Arah brand checker and config header`.

### Task 2: Servers, metaserver, Kayak, OSM placeholders

**Files:**
- Modify: `private.h`
- Test: `libs/storage/storage_tests/` (find the downloader/servers test with `grep -rn DefaultUrlsJSON libs/storage libs/platform`)

- [ ] **Step 1: Write the failing test** `UNIT_TEST(Arah_NoMetaserver)` in `libs/platform/platform_tests/` (new file `arah_config_tests.cpp`, registered in that `CMakeLists.txt`). It asserts:
  - `GetPlatform().MetaServerUrl()` is empty.
  - `downloader::ParseMetaConfig(GetPlatform().DefaultUrlsJSON())->servers` is non-empty.
  - `std::string_view(KAYAK_AFFILIATE_ID).empty()` holds.
- [ ] **Step 2: Run** `cmake --build build-claude --target platform_tests && ctest --test-dir build-claude --output-on-failure -R platform_tests`. Expected: FAIL (metaserver set, Kayak set).
- [ ] **Step 3: Edit `private.h`.**
  - Set `METASERVER_URL ""`.
  - Set `KAYAK_AFFILIATE_ID ""`.
  - Keep `DEFAULT_URLS_JSON` and `DEFAULT_CONNECTION_CHECK_IP`, each with a `// ARAH-PLACEHOLDER: Arah map server URLs (spec §5)` comment.
  - Add `// ARAH-PLACEHOLDER: register Arah on openstreetmap.org, then replace client id/secret and redirect scheme` above the OSM OAuth block.
  - `storage_tests/downloader_tests.cpp` skips when `METASERVER_URL` is empty, so check nothing else assumes it.
- [ ] **Step 4: Run** platform_tests and storage_tests. Expected: PASS.
- [ ] **Step 5: Commit** `[platform] Stop using Organic Maps metaserver and Kayak id in Arah`.

### Task 3: "Arah" in all user-visible text

**Files:**
- Modify: `data/strings/strings.txt`, `data/strings/types_strings.txt`, `data/strings/sound.txt` (all language values)
- Generated: Android `values-*/strings.xml`, iOS `*.lproj/*`

**Rules:**
- **Name:** replace `Organic Maps` with `Arah` in every language, keeping surrounding punctuation and grammar. Where a language transliterated the name (e.g. Cyrillic or Arabic script forms of "Organic Maps"), replace that form too: grep each language's values for the `en` key's position.
- **URLs:**
  - Website and help/FAQ links: `organicmaps.app`/`omaps.app` website URLs become `kWebsiteUrl`'s value.
  - Social-media keys (Instagram, Telegram, Mastodon, Facebook, X, LinkedIn, Matrix, Bluesky…): their URL values get an empty `en` only if the UI hides empty links. Check `SocialMedia.swift` and the Android about screen; otherwise point them to `kWebsiteUrl` and note it.
  - Support emails: `*@organicmaps.app` becomes `support@arah.invalid`, marked as a placeholder in the key's `comment`.
- **Donate** strings stay. The feature turns off with the metaserver (no `DonateUrl`). Don't delete the keys (mergeability).
- **Allowed:** one new key `about_based_on` with `en = Based on Organic Maps` and `ms = Berasaskan Organic Maps` (attribution), added to the checker's `ALLOWED`.

- [ ] **Step 1: Run the failing check** `python3 -I tools/python/arah_brand_check.py | grep data/strings | tail -1`. Expected: leaks reported.
- [ ] **Step 2: Apply the replacements** with a reviewed script in the session scratchpad. Print every changed value for a spot check of 30 across scripts (Latin, Cyrillic, Arabic, CJK, Thai).
- [ ] **Step 3: Check.** Run the brand checker restricted to `data/strings` (expected: 0 leaks), then `python3 -I tools/python/arah_ms_check.py data/strings/strings.txt` (expected: 0 problems; the Malay is still complete).
- [ ] **Step 4: Regenerate** with `tools/unix/generate_localizations.sh`, reverting the unrelated `cy.lproj` drift as in Plan 2. Expected: exit 0.
- [ ] **Step 5: Commit** `[strings] Rename Organic Maps to Arah in all languages`, then `[strings] Regenerated`.

### Task 4: Outgoing links and map attribution (core)

**Files:**
- Modify: `libs/ge0/url_generator.cpp`, `libs/map/share.cpp`, `libs/drape_frontend/gui/copyright_label.cpp`
- Test: `libs/ge0/ge0_tests/` and `libs/map/map_tests/` (find the share/url tests: `grep -rln "GenerateShortShowMapUrl\|share" libs/ge0/ge0_tests libs/map/map_tests`)

- [ ] **Step 1: Write the failing tests:**
  - `UNIT_TEST(Arah_ShareTextHasNoOmapsLink)`: build share text for a place named "Masjid Jamek" at 3.1489, 101.6958 with the existing share API (read `share.hpp`). Assert it contains `"Masjid Jamek"` and `"3.1489"`, contains `"geo:3.1489"` or `"https://www.openstreetmap.org/?mlat=3.1489"`, and does not contain `"omaps.app"`.
  - `UNIT_TEST(Arah_IncomingOmapsLinksStillParse)`: the existing ge0 parser accepts `https://omaps.app/o4B4pYZsRs/Zoo_Zürich` (copy a case from the existing parser tests).
- [ ] **Step 2: Run** `ge0_tests` and `map_tests`. Expected: the share test FAILs and the parser test PASSes (already supported).
- [ ] **Step 3: Implement.**
  - When `arah::kShareLinkBase` is empty, outgoing share URLs use `geo:<lat>,<lon>?q=<lat>,<lon>(<name>)` in text and an OpenStreetMap link (`https://www.openstreetmap.org/?mlat=…&mlon=…#map=<zoom>/<lat>/<lon>`) in HTML.
  - The "get the app" anchor in `share.cpp` points to `arah::kWebsiteUrl`.
  - The copyright label reads `"Map data © OpenStreetMap"`.
  - Keep each change a minimal branch on `arah::` constants.
- [ ] **Step 4: Run** `ge0_tests`, `map_tests` and `drape_frontend_tests` (offscreen, per `CLAUDE.md`). Expected: PASS. Update any upstream test that asserted the old omaps.app output; ledger each such change.
- [ ] **Step 5: Commit** `[map] Share Arah places without omaps.app links`.

### Task 5: iPhone identity

**Files:**
- Modify: `iphone/Maps/Maps.xcodeproj/project.pbxproj`:
  - `PRODUCT_NAME` becomes `"Arah"` / `"Arah (Debug)"`.
  - Widget `INFOPLIST_KEY_CFBundleDisplayName` becomes `Arah`.
  - Bundle IDs `app.organicmaps*` become `my.arah.app*` (placeholder; keep the `.debug`, `.tests` and `.widgetextension` suffixes).
- Modify: `iphone/Maps/OMaps-Debug.entitlements`, `iphone/Maps/OMaps-Release.entitlements`:
  - iCloud containers become `iCloud.my.arah.app` (+`.debug`).
  - Remove `applinks:omaps.app`.
- Modify: `iphone/Maps/OMaps.plist`: add URL scheme `arah` (keep `om`, `geo` and the others for incoming links).
- Modify: iOS Swift/ObjC files with hard-coded Organic Maps text or links (listed by `grep -rlnE "Organic Maps|organicmaps\.app|omaps\.app" iphone/Maps iphone/CoreApi --include='*.swift' --include='*.mm' --include='*.m'`).
  - User-visible text moves to `L("…")` keys, or uses `arah::kAppName`/`kWebsiteUrl` via a small `ArahConfig` ObjC wrapper.
  - Leave purely internal identifiers alone: file names, log tags, iCloud folder names (renaming those breaks sync), and `DeepLinkHandler` incoming hosts.
- Test: the brand checker covers `PRODUCT_NAME`, display name, entitlements and plist.

- [ ] **Step 1: Run the failing check:** `python3 -I tools/python/arah_brand_check.py | grep -E "pbxproj|entitlements|plist" | tail -3`. Expected: leaks reported.
- [ ] **Step 2: Apply the edits** above. Add `// ARAH-PLACEHOLDER` comments wherever the format allows (xcconfig/plist comments; for the pbxproj, list the placeholder bundle ID in `arah_config.hpp`'s comment instead).
- [ ] **Step 3: Check.** Run `plutil -lint` on the pbxproj, entitlements and plist (expected: OK). The brand checker should report 0 leaks for iOS files.
- [ ] **Step 4: Build** the iOS app for the iPhone 17 Pro simulator. Expected: BUILD SUCCEEDED, with the app at `Arah (Debug).app` and its home-screen name "Arah (Debug)".
- [ ] **Step 5: Commit** `[ios] Rename the iPhone app to Arah`.

### Task 6: Verify end to end

- [ ] **Step 1: Run the full brand check.** `python3 -I tools/python/arah_brand_check.py` should report 0 leaks and print the placeholder list. Then `python3 -I tools/python/arah_brand_check.py --release` should exit 1, listing exactly the placeholders: servers, connection IP, OSM OAuth, bundle ID, website, support email.
- [ ] **Step 2: Run the suite:** `ctest -j --test-dir build-claude --output-on-failure -R "platform_tests|storage_tests|ge0_tests|map_tests|indexer_tests|search_tests|routing_tests|style_tests"`. Expected: all pass.
- [ ] **Step 3: Simulator pass** (Review Focus 2, 4):
  - Fresh install. The home-screen name reads "Arah (Debug)".
  - Delete and re-download Malaysia_West in the app's downloader (or via file removal plus the in-app prompt). Download succeeds with the metaserver off.
  - Share a place: the text has no omaps.app.
  - `xcrun simctl openurl` an `https://omaps.app/…` link and an `om://map?ll=3.15,101.70` link: both open in Arah.
  - Screenshot each step for the owner.
- [ ] **Step 4: Commit** any fixes found, each with its test.
