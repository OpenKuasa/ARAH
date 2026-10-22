# Arah Plan 1: Tenang Map Style — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Recolour the map (all styles, light and dark) to Arah's "Tenang" palette, so the map matches the chosen design.

**Architecture:** Map colours are MapCSS variables in `data/styles/<family>/<variant>/colors.mapcss` plus a `colors { … }` block of named UI colours (route line, selection, arrow…) at the top of each `style.mapcss`. Change **values only**, never structure or names, so upstream merges stay easy. `tools/unix/generate_drules.sh` compiles them into `data/drules_*.bin/.txt`, which ship with the apps.

**Tech Stack:** MapCSS, kothic generator (Python 3), C++ unit tests (`style_tests`), Qt desktop app for visual checks.

**Spec:** `docs/superpowers/specs/2026-10-21-arah-phase1-rebrand-design.md` (sections "Design system: Tenang", "Scope §2 Map style").

### Phase 1 plan series (this is Plan 1)
1. **Tenang map style** (this plan). Needs nothing from the owner.
2. Malay language: strings, types, categories + `ms` search locale, voice, Malay default.
3. Core rebrand: IDs, `private.h` servers + metaserver, share links, Kayak, OSM OAuth, name/links. Needs owner values.
4. iPhone UI restyle + icon.
5. Android UI restyle + icon (after Android SDK install).
6. Repo, hosting mirror + metaserver, store metadata, release.

## Global Constraints

- Edit only colour **values** in `colors.mapcss` files and in the `colors { }` block of `style.mapcss` files. Don't rename, add or remove variables or named colours (`Test_NamedColorsConsistency` requires identical names across styles).
- Never hand-edit generated files (`data/drules_*`, `data/colors.txt`, `data/patterns.txt`, `data/visibility.txt`, `data/classificator.txt`, `data/types.txt`, `data/transit_colors.txt`). Regenerate with `tools/unix/generate_drules.sh`.
- Commit source edits and regenerated files **separately**; the generated commit's title is `[styles] Regenerated`.
- Commit format: `[styles] Summary in imperative mood`, ≤80 chars, `git commit -s`.
- Spec palette (light): primary teal `#0f8b7e`, gradient dark `#0b6f65`, gradient light `#14a593`, background beige `#f4f1ea`, park `#cfe8d6`, water `#bcdcf3`, major road `#ffd98a`, minor road `#ffffff`, warning amber `#e8a33a`.
- Keep the *meaning* colours unchanged: traffic (`Traffic*`, `RouteTraffic*`), bookmark colours (`Bookmark*`), road shields (`RoadShield*`), piste difficulty, military, transit line colours.
- Work on branch `feat-002-tenang-map-style`, created from `feat-001-arah-phase1-design`. Don't push (no Arah remote yet).

## Palette decisions (the builder's call per spec, pinned here)

**Tenang (light)**: used by `default/light` and `vehicle/light`.

| Variable(s) | Value |
|---|---|
| `@background`, `@label_halo_medium`, `@bridge_background` | `#F4F1EA` |
| `@water` / `@water_intermittent` / `@river` / `@water_label` | `#BCDCF3` / `#D6E9F7` / `#8EC3E8` / `#3F7FAF` |
| `@green0`…`@green5`, `@forest`, `@park`, `@natpark`, `@sport*` | soft greens from `#DCEBDD` (lightest) to `#B7D9BF` (forest); `@green2`/`@park` = `#CFE8D6`; keep the existing lightest→darkest order |
| `@green6` / `@park_label` | `#7FA88A` / `#3E7D5A` |
| `@trunk0`, `@trunk1` | `#F4B860`, `#F6C070` |
| `@primary0`, `@primary1`, `@primary2` | `#FFD98A`, `#FFDE98`, `#FFE3A6` |
| `@secondary0`, `@secondary1` | `#FFEBC0`, `#FFF0CF` |
| `@tertiary`, `@residential`, `@unclassified`, `@pedestrian`, `@footway` | `#FFFFFF` |
| `@building0` / `@building1` / borders | `#E6E1D6` / `#DFD9CC` / `#CFC8B9`, `#C8C1B1` |
| other landuse (`@leisure`, `@university`, `@hospital`, `@industrial`, `@parking*`, `@farmland`, `@farmyard`, `@pedestrian_area*`, `@platform`) | same hue as today, nudged warmer/lighter to sit on `#F4F1EA`; builder's call |

Named colours (`style.mapcss` `colors { }`), light styles:
`Route` `#0F8B7E`, `RouteOutline` `#0B6F65`, `Selection` `#0F8B7E`, `Arrow3D` `#14A593`, `DefaultTrackColor` `#0F8B7E`, `SearchmarkDefault` `#0F8B7E`, `RatingNone` `#0F8B7E`, `TrafficOutline` `#F4F1EA`.

**Tenang Malam (dark)**: used by `default/dark` and `vehicle/dark`.

| Variable(s) | Value |
|---|---|
| `@background`, `@label_halo_medium`, `@bridge_background` | `#1B2023` |
| water / river / water label | `#1E3442` / `#2A4A5E` / `#7FB3D5` |
| greens (all vegetation/park) | `#1E2E26` (lightest variable) to `#18261F` (forest) |
| `@trunk*` / `@primary*` | `#7A6234` / `#6B5A33` |
| `@secondary*` | `#545041` |
| minor roads (`@tertiary`, `@residential`, …) | `#3A4044` |
| buildings | `#2A2F33`, border `#33393D` |

Named colours, dark styles: `Route` `#3DCFB6`, `RouteOutline` `#0F8B7E`, `Selection` `#3DCFB6`, `Arrow3D` `#3DCFB6`, `DefaultTrackColor` `#3DCFB6`, `SearchmarkDefault` `#3DCFB6`, `RatingNone` `#3DCFB6`, `TrafficOutline` `#1B2023`.

**Outdoors** (`outdoors/light`, `outdoors/dark`): change only the named colours above (light set / dark set). Leave its terrain colours alone: outdoors users rely on them.

## Review Focus

1. **Road hierarchy at every zoom**: trunk vs primary vs secondary must stay distinguishable on beige, in light and dark. Checked by screenshots in Task 4.
2. **Label legibility**: dark text on the new beige and light text on Tenang Malam, including halos. Task 4 screenshots at zoom 12, 15 and 17.
3. **Traffic colours keep their meaning**: jams stay red, slow stays yellow, free stays green. Pinned by the `TrafficG1` assertion in Task 1's test.
4. **Route visibility over parks and water**: a teal route on green or blue must still stand out (the darker outline handles this). Task 4 screenshot of a route through a park.
5. **Named colours stay identical across styles**: the existing `Test_NamedColorsConsistency` must keep passing in every task.

---

### Task 1: Tenang light, default style (with palette test)

**Files:**
- Create: `libs/map/style_tests/arah_palette_test.cpp`
- Modify: `libs/map/style_tests/CMakeLists.txt` (add the file to `SRC`)
- Modify: `data/styles/default/light/colors.mapcss`, `data/styles/default/light/style.mapcss` (`colors { }` block only)
- Regenerated: `data/drules_*`, `data/colors.txt`, `data/transit_colors.txt` (whatever the script rewrites)

**Interfaces:**
- Consumes: `styles::RunForEveryMapStyle` (`libs/map/style_tests/helpers.hpp`), `drule::GetCurrentRules().GetColor(std::string_view)` and `.GetBgColor(int scale)` (`libs/indexer/drawing_rules.hpp`), returning ARGB `uint32_t`.
- Produces: test `Arah_TenangPalette` with an expectations table that Tasks 2–3 extend.

- [ ] **Step 1: Branch**

```bash
git checkout feat-001-arah-phase1-design && git checkout -b feat-002-tenang-map-style
cmake --preset debug -B build-claude   # reuse existing dir
```

- [ ] **Step 2: Write the failing test.** In namespace `arah_palette_test`, `UNIT_TEST(Arah_TenangPalette)` calls `styles::RunForEveryMapStyle`. For each style that has an entry in a local table `{MapStyle, routeArgb, bgArgb (0 = don't check)}`, it asserts:

```cpp
TEST_EQUAL(rules.GetColor("Route"), e.route, (mapStyle));
if (e.bg != 0)
  TEST_EQUAL(rules.GetBgColor(17), e.bg, (mapStyle));
// Meaning colours must not change (Review Focus 3):
if (mapStyle == MapStyleDefaultLight)
  TEST_EQUAL(rules.GetColor("TrafficG1"), 0xFFE42300u, ());
```

Initial table: `{MapStyleDefaultLight, 0xFF0F8B7E, 0xFFF4F1EA}`.
Before writing the expectations, read `RulesHolder::GetColor` and `GetBgColor` in `libs/indexer/drawing_rules.cpp` to confirm the alpha byte is `0xFF` for opaque colours. If the stored format differs, adapt the constants, not the approach.

- [ ] **Step 3: Run it and confirm it fails.**
Run: `cmake --build build-claude --target style_tests && ctest --test-dir build-claude --output-on-failure -R style_tests`
Expected: FAIL in `Arah_TenangPalette`, Route `0xFF0087FF` != `0xFF0F8B7E`.

- [ ] **Step 4: Apply the Tenang light palette** to `default/light/colors.mapcss` and the named colours in `default/light/style.mapcss`, using the values in the table above.

- [ ] **Step 5: Regenerate the style.**
Run: `tools/unix/generate_drules.sh`
Expected: exit 0, ending with "Merging styles...".

- [ ] **Step 6: Run the tests and confirm they pass.**
Run: `cmake --build build-claude --target style_tests && ctest --test-dir build-claude --output-on-failure -R style_tests`
Expected: PASS, including `Test_NamedColorsConsistency`.

- [ ] **Step 7: Commit (two commits).**

```bash
git add libs/map/style_tests/arah_palette_test.cpp libs/map/style_tests/CMakeLists.txt data/styles/default/light
git commit -s -m "[styles] Apply Arah Tenang palette to default light style"
git add data/ && git commit -s -m "[styles] Regenerated"
```

### Task 2: Tenang Malam, default dark style

**Files:** Modify `data/styles/default/dark/colors.mapcss`, `data/styles/default/dark/style.mapcss`, `libs/map/style_tests/arah_palette_test.cpp`; regenerated files.

**Interfaces:** Consumes the `Arah_TenangPalette` table from Task 1.

- [ ] **Step 1: Add the failing expectation** `{MapStyleDefaultDark, 0xFF3DCFB6, 0xFF1B2023}` to the table.
- [ ] **Step 2: Run** `ctest --test-dir build-claude --output-on-failure -R style_tests` (after building `style_tests`). Expected: FAIL for `MapStyleDefaultDark`.
- [ ] **Step 3: Apply the Tenang Malam palette** to both dark files, using the dark table above.
- [ ] **Step 4: Regenerate** with `tools/unix/generate_drules.sh` (exit 0), then rebuild and rerun `style_tests`. Expected: PASS.
- [ ] **Step 5: Commit**: `[styles] Apply Arah Tenang Malam palette to default dark style`, then `[styles] Regenerated`.

### Task 3: Vehicle (driving) and outdoors styles

Driving mode uses the `vehicle` style, so it must match. Outdoors only gets the accent colours.

**Files:** Modify `data/styles/vehicle/{light,dark}/colors.mapcss`, `data/styles/vehicle/{light,dark}/style.mapcss`, `data/styles/outdoors/{light,dark}/style.mapcss` (`colors { }` only), `libs/map/style_tests/arah_palette_test.cpp`; regenerated files.

- [ ] **Step 1: Add the failing expectations:**
`{MapStyleVehicleLight, 0xFF0F8B7E, 0xFFF4F1EA}`, `{MapStyleVehicleDark, 0xFF3DCFB6, 0xFF1B2023}`, `{MapStyleOutdoorsLight, 0xFF0F8B7E, 0}`, `{MapStyleOutdoorsDark, 0xFF3DCFB6, 0}`.
- [ ] **Step 2: Run** `style_tests`. Expected: FAIL for these four styles.
- [ ] **Step 3: Apply the palettes.** For the vehicle styles, use the light and dark tables, mapped onto vehicle's own variable names (it has `@casing_road`, `@unclassified`, `@parking_l`, etc.; use the nearest equivalent row). For outdoors, change the named colours only.
- [ ] **Step 4: Regenerate**, rebuild, rerun `style_tests`. Expected: PASS for all styles.
- [ ] **Step 5: Commit**: `[styles] Apply Arah Tenang palette to vehicle and outdoors styles`, then `[styles] Regenerated`.

### Task 4: Visual check on desktop and owner sign-off

No code. Produces the screenshots the owner approves the map look from (Review Focus 1, 2 and 4).

- [ ] **Step 1: Rebuild the desktop app** (it copies the new drules into the bundle): `cmake --build build-claude --target desktop`. Expected: exit 0.
- [ ] **Step 2: Capture screenshots** with `screencapture -l <windowid>` or `screencapture -R`, saved to the session scratchpad. Download the Malaysia map in-app first (it still comes from Organic Maps' servers at this stage). Capture:
  - Kuala Lumpur city centre at zoom 12, 15 and 17, in light and dark (switch with the `?light` / `?dark` debug commands in search).
  - A car route through a park, for example across Taman Tasik Titiwangsa.
  - Driving mode (vehicle style) on a highway, in light and dark.
  - Outdoors style once, light, to confirm only the accents changed.
- [ ] **Step 3: Check each screenshot against Review Focus 1, 2 and 4.** Fix any failing colour value in its source file, regenerate, recommit (source and `[styles] Regenerated`), and recapture.
- [ ] **Step 4: Show the owner** the screenshots next to the Tenang mockup. Their approval closes Plan 1. Adjust values if they ask; that follows the same edit → regenerate → test → commit loop.
- [ ] **Step 5: Final verification**
Run: `ctest -j --test-dir build-claude --output-on-failure -R "style_tests|indexer_tests"`
Expected: all pass. `git status` is clean.
