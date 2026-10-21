# Arah: handoff (2026-10-21)

## Where things stand
Arah started on Organic Maps. That work is finished and archived in `~/Documents/arah-archive/`:
- **Plan 1, Tenang map palette:** light, dark, driving and outdoors styles, with contrast tests. Reviewed, fixed and approved by the owner.
- **Plan 2, Malay:** voice, search categories (~580 terms), 785 app strings, 1,003 place types, plurals, and Malay by default on iPhone. Reviewed and fixed.
- **Plan 3, core rebrand:** only partly done (brand checker, `arah_config.hpp`, metaserver off, strings renamed), then paused when the base moved.

Then the owner switched the base to **CoMaps** (see the amendment at the top of the design doc). This repo is a clean CoMaps clone with Arah's docs and checkers added.

## Next step
Run **Plan M**: `docs/superpowers/plans/2026-10-21-arah-plan-m-move-to-comaps.md`.
- **Port sources:** read from `~/Documents/arah-archive/files/` (the plan's "Source of reusable work" branch `feat-001-arah-phase1-design` is no longer in this repo).
- **Known numbers:**
  - Malay reuse: 683 of 988 CoMaps app keys and 934 of 1,460 type keys already have Arah Malay, and about 100 Android keys changed their English.
  - Palette reuse: about 90% of variables have the same name.

After Plan M, rewrite Plan 3 (core rebrand) for CoMaps: the brand is now "CoMaps" and the attribution is "Based on CoMaps". Then:
- Plan 4: iPhone screens and icon, including a Mapbox-like navigation view the owner showed: tilted 3D, big turn banner, arrival card, round floating buttons.
- Plan 5: Android screens and icon, Malay by default via CoMaps' existing language screen. Needs the Android SDK.
- Plan 6: Arah GitHub repo, map hosting, signing key and metaserver (CoMaps has `docs/DEPLOY_OWN_MAP_SERVER.md`), store listings.

## Still needed from the owner
- **IDs:** iOS bundle ID and Android package name.
- **Map hosting:** server URLs.
- **GitHub:** the account for Arah's repo.
- **OpenStreetMap:** register Arah as an OAuth app on openstreetmap.org.
- **Device check:** a manual pass of the Malay UI on iPhone (screens that need taps, small-screen clipping).

## Deferred minors (from reviews)
- Night palette: road hierarchy differs mainly by brightness, and it is a little brighter than before.
- Malay phrasing polish: "Sembunyikan"/"Tunjukkan" imperatives, "Berhampiran saya", "Pilih satu pilihan".
- Malay search noise: "air", bare "kereta", "basikal lajak"; add "tapau"; consider brand terms (KTM, KLIA, Grab).
- iOS Settings menu paths written in Malay on English phones.
- Inconsistencies: Aiskrim vs Ais Krim, Terminal vs Stesen Bas, Rel transit vs MRT.
