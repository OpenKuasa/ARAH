# Arah: handoff (2026-10-21)

## Where things stand
Arah started on Organic Maps; that work is archived in `~/Documents/arah-archive/` (see its README). The owner then
moved the base to **CoMaps** (see the amendment at the top of the design doc).

Arah is on GitHub at **github.com/OpenKuasa/ARAH** (remote `origin`). `main` has Plan M and Plan 3, plus Arah's
README, CONTRIBUTING, SECURITY, code of conduct and issue/PR templates. Work goes through `feat-###` branches and PRs.

**Plan M is done** (`docs/superpowers/plans/2026-10-21-arah-plan-m-move-to-comaps.md`), merged into `feat-001-arah-setup`
from `feat-002-move-to-comaps` (kept):
- **Tenang map palette** on CoMaps' default, vehicle and outdoors styles, and so on every map mode (walking, cycling,
  driving, public transport). CoMaps-only colours got Tenang values by rule; every value is listed in
  `docs/superpowers/plans/2026-10-21-arah-plan-m-palette-table.md`. Pinned by `libs/map/style_tests/arah_palette_test.cpp`.
- **Malay (`ms`) complete:** search categories and voice (`data/translations/*/ms.json`), Android `values-ms`,
  iOS `ms.lproj`, registered in Android `localeFilters` + `locales_config.xml` and the Xcode project.
  `tools/python/arah_ms_check.py` checks every Malay file against the same platform's English.
- **iPhone opens in Malay** on first launch (`iphone/Maps/main.mm`).
- Evidence (before/after screenshots, scripts, the full decision log): `~/Documents/arah-archive/plan-m/`.

**Plan 3 is done** (`docs/superpowers/plans/2026-10-21-arah-plan3-core-rebrand.md`), on branch `feat-003-core-rebrand`:
- "CoMaps" is "Arah" in the app text of every language (Android and iOS), checked by `tools/python/arah_brand_check.py`
  (0 leaks; each allowed upstream name carries its reason in the checker).
- The iPhone app is "Arah": placeholder IDs `my.arah.app` / `iCloud.my.arah.app`, an `arah://` scheme, and About credits
  "Based on CoMaps" and hides CoMaps' news, review and social links until Arah has its own.
- Places are shared as OpenStreetMap links (no Arah domain yet); old CoMaps/ge0 links still open.
- CoMaps' map servers stay in use (placeholders); Arah ignores the donate link CoMaps' metaserver hands out.
- `python3 -I tools/python/arah_brand_check.py --release` lists every value still to supply.

Notes from the Plan 3 review:
- iOS `.strings` have no per-key fallback to English: a key Arah adds must go into every `*.lproj` (the checker enforces
  this for `about_based_on`). The internal product/module name stays `CoMaps`; users see `CFBundleDisplayName` "Arah".
- `https://comaps.at/…` links open CoMaps' web page now (Arah can't claim that domain); `cm://`, `comaps://` and `ge0://`
  still open in Arah. The new `arah://` scheme opens the app but no parser handles it yet.
- The website placeholder is written with and without a trailing slash; Android's `HelpFragment` appends paths to it
  (normalise in Plan 5).
- `tools/python/arah_name_check.py` lists translations that may name upstream in their own script; rerun after renames.

## Next step
Plan 4: iPhone screens and icon. CoMaps logos remain: the home-screen icon, `Image("comaps")` in `AboutCoMapsView`, the
widget's `CoMapsWidgetExtension/LiveActivity/AppLogo.swift`, and the `"Logo"` asset in share link previews. Then:
- Plan 4 (next): iPhone screens and icon, including a Mapbox-like navigation view the owner showed: tilted 3D, big turn banner,
  arrival card, round floating buttons.
- Plan 5: Android screens, icon and identity (`appId`, app name, Java links in `Constants.java`/`Utils.java`/`HelpFragment.java`,
  About screen with "Based on CoMaps"), Malay by default via CoMaps' language screen. Needs the
  Android SDK.
- Plan 6: map hosting, signing key and metaserver (CoMaps has `docs/DEPLOY_OWN_MAP_SERVER.md`),
  store listings.

## CoMaps branding audit (feat-007)
`tools/python/arah_brand_check.py` now also scans the bundled FAQ/copyright/welcome pages, store listings, release
settings and the user-visible string literals in export, OSM-editing and app-name code (0 leaks). Still open:
- **Plan 4:** CoMaps logo art in `Logo.imageset` (share previews and the "update your maps" screen), `Image("comaps")`,
  the widget `AppLogo`, and the app icon.
- **Plan 5:** Android launcher, splash and notification art. No "Based on CoMaps" credit on Android's About screen yet.
  None of feat-007's Android changes were compiled.
- **feat-009 (not compiled yet):** Android shares places, bookmarks and "my position" as OpenStreetMap links in the
  iPhone's text, through `arah::ShareText`/`ShareLink` (`ArahShare.java` + `arah_share_jni.cpp`, called from
  `SharingUtils.java`). Build and try a share once the Android SDK is in. The "Check out" first line
  (`arah_sharing_call_action_look`) has English and Malay only; other languages show English.
- **Plan 6 / owner:** Apple team ID (`DEVELOPMENT_TEAM 534D2KJBUK` is CoMaps'), an Arah OSM OAuth app (`private.h`
  uses CoMaps' registration), Arah-hosted KML placemark icons (`libs/kml/serdes.cpp` links comaps.at).
- **Malay:** the FAQ has no Malay section; the Malay store listing (`iphone/metadata/ms`, Play `listings/ms`) needs a
  native read. Play's default language stays `en-US` because `check_store_metadata.py` requires it.
- Seven map_tests and two kml serdes tests fail before and after feat-007 (upstream).

## Decision needed from the owner
- **Malay place names on the map.** CoMaps' map files carry no Malay names: its fixed 64-slot name-language table
  (`libs/i18n/localisation.hpp`) has no `ms`. So with the app in Malay, places show English names ("Royal Museum", not
  "Muzium Diraja"), unlike the Organic Maps-based Arah. Real fix: an `ms` slot plus Arah's own map generation
  (Phase 3 / Plan 6). Stopgap: on first launch, default the map language to local names (mostly Malay in Malaysia),
  which also affects English users. Not decided yet.

## Still needed from the owner
- **IDs:** iOS bundle ID and Android package name.
- **Map hosting:** server URLs, metaserver, and the key that signs `countries.txt`.
- **OpenStreetMap:** register Arah as an OAuth app on openstreetmap.org.
- **Web:** website, privacy policy and terms URLs, support email.
- **Device check:** a manual pass of the Malay UI on iPhone (screens that need taps, small-screen clipping).

## Deferred minors
From the Plan 1 and 2 reviews:
- Night palette: road hierarchy differs mainly by brightness.
- Malay phrasing polish: "Sembunyikan"/"Tunjukkan" imperatives, "Berhampiran saya", "Pilih satu pilihan".
- Malay search noise: "air", bare "kereta", "basikal lajak"; add "tapau"; consider brand terms (KTM, KLIA, Grab).
- iOS Settings menu paths written in Malay on English phones.
- Inconsistencies: Aiskrim vs Ais Krim, Terminal vs Stesen Bas, Rel transit vs MRT.

From the Plan M review:
- Malay wording: `subway` button says "Subway" (reads as the sandwich chain); "Perhentian" vs "titik henti";
  `type.highway.path` "Laluan" clashes with laluan = route ("Denai"?); "rel transit"; "Mengikut terbaru digunakan";
  socket names "Combo Jenis 1" vs "Type 2 combo"; `capacity_disabled_no` "tempat" vs "petak".
- Translator-unsure terms: "Kiri/Kanan Kapal", "Suar", wetland names (Paya Gambut/Buluh/Masin), "Jalan Tanah", "Lorong".
- No `countries-strings/ms.json` (the downloader shows English country names).
- Tests: `CategoriesHolder_MalaySynonyms` covers no CoMaps-only categories; the checker doesn't flag Malay keys missing
  from English; the category-button check covers Android only.
- CoMaps opens in walking mode and picks feet on en-US phones; Arah may want driving and metric.

From the Plan 3 review:
- `UIKitCategories.m` `rateApp` (no callers) still opens CoMaps' App Store page.
- OSM changesets are tagged `created_by = "CoMaps iOS …"` (`MWMEditorHelper.mm`); use Arah's name (and on Android).
- The checker allows any URL in `Social Media.swift`; narrow it to the six current hosts.

## Build notes
- Run `./configure.sh` before the first build. It generates drules, symbols, strings and World maps; none are tracked.
  It needs `optipng` (installed via Homebrew).
- No CMakePresets: `cmake . -B build-<agent> -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt`.
- Tests run as `./build-<agent>/<suite> --data_path=data/ --user_resource_path=data/`.
- Known upstream test failures (excluded in CoMaps CI): three style_tests `Classificator_*Priority` and
  `Test_SymbolsConsistency`, three search_tests, routing_tests `RoadPenalty_*`.
- iOS: `xcode/CoMaps.xcworkspace`, scheme `CoMaps`. Simulator recipes (location permission, viewport, dark map,
  Malaysia map download) are in `~/Documents/arah-archive/plan-m/machine-notes.md`.
