# Arah — Phase 1: Restyle and Rebrand (Design)

Date: 2026-10-21
Status: Approved by owner (2026-10-21); amended the same day, see below

## Amendment (2026-10-21): base project is CoMaps, not Organic Maps

The owner switched Arah's upstream from Organic Maps to **CoMaps** (codeberg.org/comaps/comaps),
the community, not-for-profit fork of Organic Maps (split April 2025, Apache 2.0). Where this
document says "Organic Maps" as the upstream or base, read "CoMaps". The attribution Arah must keep is
now "Based on CoMaps" (CoMaps' own NOTICE also credits Organic Maps and Maps.me; keep LICENSE/NOTICE).

Why: CoMaps is community-governed (fits "open source, community project"), has more active
contributors (49 vs 23 in the last 90 days, measured), and already ships three things on Arah's roadmap:
an in-app language picker (Android), map data updates without an app update (signed remote
`countries.txt`, hot-applied), and lane guidance on iPhone/CarPlay.

What changes in this design:
- **Upstream remote** is `comaps` (Codeberg). Arah stays connected to it the same way (§6).
- **Translations:** CoMaps keeps app text in platform files edited through Weblate (Android
  `res/values-*/strings.xml`, iOS `*.lproj/*.strings`) and JSON under `data/translations/`
  (sound, categories, countries), not `data/strings/*.txt`. Malay (§4) is added in those formats.
  Arah's finished Malay work is reused by key; CoMaps-only keys still need translating.
- **Malay by default on Android** can use CoMaps' existing in-app language screen instead of a new one.
- **Map hosting (§5):** CoMaps already runs community map mirrors and a metaserver, and publishes a
  signed `countries.txt`. Arah's own servers and signing key replace them; until the owner supplies
  them they stay as marked placeholders. Live map updates make the "app release per map version"
  coupling go away.
- **Map style (§2):** CoMaps' styles have diverged from Organic Maps'; the Tenang palette is ported
  by variable name, and CoMaps-only variables get Tenang values.
- The Organic Maps-based branches (`feat-001`…`feat-004`) are kept for history; work continues on a
  branch made from `comaps/main`.

## Intent

Arah ("direction" in Malay) is a navigation app for everyday drivers in Malaysia,
built from this Organic Maps codebase. The long-term goal is a Waze alternative:
live jam warnings, police and accident alerts, and speed-trap warnings, on top of
Organic Maps' offline maps and routing.

Phase 1 ships the existing app under the Arah name with a new, calm look,
Malay-first, publicly on the App Store and Play Store. It adds no new features.
Shipping the restyle first gets a real, polished product in users' hands while
the live-alerts work (Phase 2) is built.

Arah is an **open-source, community project** in its own public GitHub repository
(under a separate GitHub account from the current one), and it **stays connected to
upstream Organic Maps**: Arah pulls upstream improvements and map-format changes when it
chooses to. Upstream has no say over Arah.

## Roadmap (for context; only Phase 1 is in scope here)

1. **Phase 1: Arah 1.0.** Restyle, full rebrand, Malay default, own map hosting. Public release.
2. **Phase 2: Live alerts.** User-reported jams, police, accidents (needs a backend);
   full Malaysian AWAS fixed speed-camera coverage; an "Arah voice" for alerts,
   pre-recorded with ElevenLabs (fixed phrases such as "Polis di hadapan", "Kamera AWAS").
3. **Phase 3: Malaysia map data.** Arah's own Malaysia map files with additional data.

## Goals

- Every screen users see looks like the "Tenang" design (below), on iPhone and Android equally.
- The map itself is restyled to the Tenang palette (light and dark).
- Nothing user-visible says "Organic Maps", except the legally required credit (see Constraints).
- The app is Malay by default (UI, search, voice directions); English is selectable in settings.
- Arah downloads maps for the whole world from Arah's own servers.
- Published on the App Store and Google Play under Arah's own developer accounts and app IDs.
- The codebase stays easy to merge with upstream Organic Maps.

## Non-goals (Phase 1)

- No new features: no live alerts, reports, accounts, AWAS data, new Malaysia data, or recorded voice.
- No changes to routing, search ranking, map data or offline behaviour. (Adding Malay as a search
  language is in scope; see §4. That is a new locale, not a ranking change.)
- Desktop (Qt) app is not a product. It is only used to preview map-style changes quickly.
- No Arah web domain / share-link page yet (deferred by owner; see §3).
- Android F-Droid, Huawei and web builds are not shipped.

## Anti-goals (a failure even if it "works")

- Any existing feature broken or behaving differently, apart from look and wording
  (and the explicit exceptions listed in §3).
- Malay that reads like Indonesian or stiff formal text. It must be natural everyday Malaysian Malay.
- Visible leftovers of Organic Maps branding (old icon, green accents, "Organic Maps" text,
  organicmaps.app / omaps.app links, Organic Maps donate/news screens).
- iPhone and Android looking like two different apps.
- Removing the attribution the licenses require.
- Restructuring upstream code so heavily that pulling upstream updates becomes painful.

## Constraints

- **Licenses.** Code is Apache 2.0: keep LICENSE/NOTICE and an attribution
  ("Based on Organic Maps") on the About screen. Map data is OpenStreetMap (ODbL):
  "© OpenStreetMap contributors" stays visible as it is today. Arah's own code is also open source.
- **Stay mergeable with upstream** (owner decision). Concretely:
  - Prefer changing *values* over changing *structure*: theme colours, assets, MapCSS, string
    values, config constants. Restyle existing screens; don't rewrite them from scratch.
  - Keep Arah-specific changes in as few places as possible and easy to find, so merge conflicts
    stay small. Where an Arah-only file or setting can hold the change, use that.
  - Upstream stays as a second git remote (`upstream`); the Arah repo becomes `origin`.
- **Repo conventions** (see `CLAUDE.md`): clang-format, swiftformat and ktlint style gates; strings go
  through `data/strings/` then regenerate (never hand-edit generated files); styles are edited in
  MapCSS under `data/styles/` then regenerated; generated files committed separately.
- **Two separate UI codebases:** iPhone in Swift/Obj-C (`iphone/`), Android in
  Java/Kotlin (`android/`). The shared C++ core and map styles are common.

## Decided by the owner

- Name: **Arah**. Audience: everyday people in Malaysia.
- Platforms: **iPhone and Android, equal priority**, one shared design.
- Visual direction: **"Tenang" (calm)**: light, airy, soft white floating cards, teal accent.
  (Mockup "A" from the brainstorm session.)
- Restyle **the map too**, not just the app chrome.
- **Malay default**, English available.
- **Icon: "Blend A, Pin Kompas"**: a teal map pin containing a folded two-tone white compass
  arrow, on a warm beige rounded-square background. Wordmark: lowercase "arah", heavy weight, teal.
- **Public release** on App Store and Google Play. Owner already has developer accounts, app IDs,
  privacy policy and hosting.
- **Launch the restyle first**, alerts later.
- **Voice:** phone's built-in voice (Malay) for turn-by-turn in Phase 1; ElevenLabs recordings for
  alerts in Phase 2.
- **Open source, stays connected to upstream**, repo under a separate GitHub account.
- **Map hosting: whole world** on Arah's servers, same coverage as Organic Maps today.
- **Malay translation:** done and reviewed by the builder (Claude); no dedicated native reviewer.
- **Share-link domain: skipped for now.**

## Design system: Tenang

Palette (starting values; builder may tune for contrast/accessibility):

| Role | Light | Notes |
|---|---|---|
| Primary (teal) | `#0f8b7e` | buttons, links, active states, route line candidate |
| Primary gradient | `#14a593` → `#0b6f65` | icon, hero elements |
| Background (beige) | `#f4f1ea` | map land, app background |
| Surface | `#ffffff` | floating cards, sheets, search bar |
| Tint surface | `#eef7f5` | teal-tinted quick-action tiles |
| Warning (amber) | `#e8a33a` | speed cameras, cautions |
| Map: park/green | `#cfe8d6` | |
| Map: water | `#bcdcf3` | |
| Map: major road | `#ffd98a` | warm yellow |
| Map: minor road | `#ffffff` | |

Character: rounded corners (~14 px cards, ~22 px sheets), soft shadows rather than borders,
generous spacing, system font (SF on iPhone, Roboto on Android), no emoji in the real UI
(emoji in mockups were placeholders for icons).

Main map screen (from the chosen mockup): floating white search bar at top with the Arah mark
and placeholder "Cari tempat…"; a row of quick category chips under it (Petrol, Makan, Surau,
Parking); floating round controls on the right; a bottom sheet with a greeting and quick
destinations (Rumah / Kerja).
*Builder note:* Organic Maps today has no "home/work" shortcuts or greeting. Where a mockup
element implies new behaviour, implement it only if it maps onto an existing feature (chips
→ existing category search; Rumah/Kerja → existing bookmarks); otherwise leave it out.

**Dark mode ("Tenang Malam").** A matching dark palette, because the app switches to dark
automatically at night while driving. Same teal accent, dark neutral surfaces. Designed
alongside light.

## Scope of work

### 1. Screens to restyle (both platforms), in priority order
1. Main map: search bar, buttons, bottom bar/menu
2. Search and results
3. Place page (place details)
4. Route planning
5. Turn-by-turn navigation
6. Bookmarks and tracks
7. Menu and settings
8. Map downloader
Plus: onboarding/first launch, splash/launch screen, permission prompt text, widgets, and
CarPlay/Android Auto surfaces where they show branding.

### 2. Map style
Restyle `data/styles/default/light` and `dark` (colours in `colors.mapcss` and the includes) to Tenang.
Vehicle and outdoors styles get matching colours where they share elements. Map icons (POI symbols)
keep their meaning; recolour only where they clash.

### 3. Rebrand "throughout"
- App name, icon (all sizes), launch screen, colours, About screen (with required attribution).
- **IDs** (owner supplies values at build time): iOS bundle IDs for app, widget extension and tests;
  App Group; iCloud container (today `iCloud.app.organicmaps`, used for bookmark sync); Android
  `appId` in `android/build.gradle` (today `app.organicmaps`); signing configs; URL scheme (`om://`).
- **Android flavors:** ship `google` only. Leave other flavors in the code untouched (mergeability)
  but don't build, brand-check or publish them.
- **Servers** (`private.h`): map download servers and connection-check IP → Arah servers;
  `METASERVER_URL` (today `meta.omaps.app`, which hands out the server list at runtime) → Arah's own
  metaserver, so upstream cannot redirect Arah's downloads.
- **Share links.** Today they are built on `omaps.app` (`libs/ge0/url_generator.cpp`, `libs/map/share.cpp`).
  With no Arah domain yet, sharing sends place name, address, coordinates and a standard
  `geo:`/map link as plain text. *Builder's call (accepted exception to "no behaviour change").*
  Incoming `omaps.app`/`ge0` links should still open in Arah.
- **OpenStreetMap editing** stays. The owner registers an "Arah" OAuth app on openstreetmap.org
  and supplies client ID/secret; redirect URI changes from `om://` to Arah's scheme.
- **Kayak hotel affiliate link** (`KAYAK_AFFILIATE_ID`): removed. *Builder's call; owner may override.*
- **Remove/neutralise:** donate, Organic Maps news/"what's new", rate-us/support/social links and
  emails pointing to Organic Maps → Arah equivalents or hidden.
- **Store metadata:** `iphone/metadata/` and `android/app/src/google/play/`. Malay and English
  listings only, with new screenshots. Other existing language folders are not published.
- **App languages:** keep all ~45 existing UI languages (removing them would break a feature).
  In every language, "Organic Maps" → "Arah" (a proper noun, so substitution is mechanical);
  strings about removed features need no rewording.

### 4. Malay language
Malay (`ms`) does not exist anywhere in the app today. Work items:
- **App strings:** ~780 in `data/strings/strings.txt`.
- **Map feature types:** ~1,390 in `data/strings/types_strings.txt`.
- **Search categories:** `data/categories.txt` has **no** Malay (0 `ms:` lines; Indonesian has ~476).
  Add ~550 Malay category entries, and add `ms` to `CategoriesHolder::kLocaleMapping` in
  `libs/indexer/categories_holder.hpp` so Malay search works.
- **Voice directions:** add `data/sound-strings/ms.json` and register `ms` in the TTS language list
  (`libs/platform/languages.hpp`). Uses the phone's built-in Malay voice. If a phone has no Malay
  voice installed, fall back the way the app already does for missing voices and prompt the user
  to install one.
- **Platform-only strings** on Android/iOS not generated from `data/strings/` also need `ms`.
- **Default behaviour:** the app UI, search and voice are Malay regardless of the phone's language
  until the user picks English (or another language) in settings. Map labels follow the app
  language as they do today.
- **Quality:** Indonesian (`id`) may be used as a draft, but every string is rewritten into natural
  Malaysian Malay (e.g. "kereta" not "mobil", "telefon" not "ponsel"). Optional but recommended:
  a short beta with a few native speakers before launch.

### 5. Map hosting
- Arah's servers mirror Organic Maps' published map files for **the whole world** (ODbL allows this).
- Arah runs its own metaserver returning the Arah server list.
- **Updates:** map data versions are tied to `countries.txt` in each app release. When Arah merges
  upstream and ships a release with new map data, the mirror must hold that data version first.
  The builder documents a simple sync step (mirror → then release). Arah's own Malaysia files
  replace the Malaysia entries in Phase 3.

### 6. Repository
- Create the Arah repo under the owner's separate GitHub account; push there as `origin`.
- Keep upstream Organic Maps as remote `upstream`. Nothing is pushed upstream.
- Pulling upstream is done on a branch, built and tested before release.

## Left to the builder
- Exact component specs, spacing, typography scale, icon redraws, dark palette values.
- How to structure theming code on each platform (reuse existing theme systems).
- Which upstream-only screens to hide vs. adapt, as long as no existing user feature is lost.
- Order between platforms (suggested: iPhone first since it already builds here, Android right
  after the Android SDK is installed).

## Testing / done means
- Both apps build and existing unit tests pass; style gates (clang-format, swiftformat, ktlint,
  detekt, Android lint) pass.
- A unit test covers Malay category search (new `ms` locale).
- Manual pass of all screens listed in §1, light and dark, Malay and English, on at least one
  small and one large phone per platform.
- Turn-by-turn voice speaks Malay on a device with a Malay voice.
- A text search of the built apps and store metadata finds no user-visible "Organic Maps",
  "organicmaps.app" or "omaps.app", apart from the About-screen attribution.
- Maps for several countries (including Malaysia) download successfully from the Arah servers.
- A trial upstream merge after the restyle completes with only small, easy conflicts.
