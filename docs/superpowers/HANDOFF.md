# Arah: handoff (2026-10-21)

## Where things stand
Arah started on Organic Maps; that work is archived in `~/Documents/arah-archive/` (see its README). The owner then
moved the base to **CoMaps** (see the amendment at the top of the design doc).

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

## Next step
Run **Plan 3, core rebrand on CoMaps**: `docs/superpowers/plans/2026-10-21-arah-plan3-core-rebrand.md`
(rewritten for CoMaps; the brand is "CoMaps" and the attribution is "Based on CoMaps").

Then:
- Plan 4: iPhone screens and icon, including a Mapbox-like navigation view the owner showed: tilted 3D, big turn banner,
  arrival card, round floating buttons.
- Plan 5: Android screens, icon and identity, Malay by default via CoMaps' existing language screen. Needs the Android SDK.
- Plan 6: Arah GitHub repo, map hosting, signing key and metaserver (CoMaps has `docs/DEPLOY_OWN_MAP_SERVER.md`),
  store listings.

## Decision needed from the owner
- **Malay place names on the map.** CoMaps' map files carry no Malay names: its fixed 64-slot name-language table
  (`libs/i18n/localisation.hpp`) has no `ms`. So with the app in Malay, places show English names ("Royal Museum", not
  "Muzium Diraja"), unlike the Organic Maps-based Arah. Real fix: an `ms` slot plus Arah's own map generation
  (Phase 3 / Plan 6). Stopgap: on first launch, default the map language to local names (mostly Malay in Malaysia),
  which also affects English users. Not decided yet.

## Still needed from the owner
- **IDs:** iOS bundle ID and Android package name.
- **Map hosting:** server URLs, metaserver, and the key that signs `countries.txt`.
- **GitHub:** the account for Arah's repo.
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

## Build notes
- Run `./configure.sh` before the first build. It generates drules, symbols, strings and World maps; none are tracked.
  It needs `optipng` (installed via Homebrew).
- No CMakePresets: `cmake . -B build-<agent> -G Ninja -DCMAKE_BUILD_TYPE=Debug -DCMAKE_PREFIX_PATH=/opt/homebrew/opt/qt`.
- Tests run as `./build-<agent>/<suite> --data_path=data/ --user_resource_path=data/`.
- Known upstream test failures (excluded in CoMaps CI): three style_tests `Classificator_*Priority` and
  `Test_SymbolsConsistency`, three search_tests, routing_tests `RoadPenalty_*`.
- iOS: `xcode/CoMaps.xcworkspace`, scheme `CoMaps`. Simulator recipes (location permission, viewport, dark map,
  Malaysia map download) are in `~/Documents/arah-archive/plan-m/machine-notes.md`.
