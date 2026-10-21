# Agent Instructions for Arah

Arah ("direction" in Malay) is a Malaysian navigation and offline maps app for everyday drivers, built on
**CoMaps** (the community, not-for-profit fork of Organic Maps; C++ core, iOS, Android, Qt desktop,
OpenStreetMap data). The goal is a Waze alternative for Malaysia. It is an open-source, community project.

## Start here
- **Design (approved, with a CoMaps amendment at the top):** `docs/superpowers/specs/2026-10-21-arah-phase1-rebrand-design.md`
- **Plans:** `docs/superpowers/plans/`
  - **Plan M** (`2026-10-21-arah-plan-m-move-to-comaps.md`) is the next one to run.
  - Plans 1–3 were written for the old Organic Maps base and are kept for reference.
- **Handoff and status:** `docs/superpowers/HANDOFF.md`
- **Work done on the old Organic Maps base** (the source for Plan M): `~/Documents/arah-archive/` (see its README)

## Decisions already made by the owner (don't re-ask)
- **Name and audience:** Arah, for everyday people in Malaysia. Public release on the App Store and Play Store, iPhone and Android equally.
- **Look:** the "Tenang" (calm) style. Light, soft white cards, teal `#0f8b7e`, beige `#f4f1ea`, amber warnings. Map colours restyled too.
- **Icon:** "Pin Kompas", a teal map pin holding a folded two-tone white compass arrow, on beige.
- **Language:** Malay is the default, English available, and all existing languages kept. The voice uses the phone's built-in voice now; ElevenLabs alerts come later.
- **Order of work:** the restyle and rebrand launch first. Then Phase 2, live alerts (jams, police, accidents, AWAS speed cameras). Then Phase 3, Arah's own Malaysia map data.
- **Base and hosting:**
  - **Base:** CoMaps, staying connected to upstream (remote `comaps`, codeberg.org/comaps/comaps).
  - **Arah's repo:** goes under the owner's separate GitHub account (account not yet supplied).
  - **Hosting:** the whole world on Arah's own servers (details not yet supplied). Until then those values are marked `ARAH-PLACEHOLDER`.
- **Share links:** no domain yet; places are shared as geo:/OpenStreetMap links.

## Working rules
- **Stay mergeable with CoMaps:** change values, not structure. Put Arah-only code in `arah_*` files.
- **Follow CoMaps' conventions:** `docs/CONTRIBUTING.md`, `docs/PR_GUIDE.md`, `docs/CPP_STYLE.md`, `docs/OBJC_STYLE.md`, `docs/JAVA_STYLE.md`, `docs/FORMATTER.md` and `docs/INSTALL*.md`. Use the commit style seen in `git log`: `[subsystem] Summary`.
- **Generated files** (styles, translations) are regenerated with the repo's tools, never hand-edited, and committed separately.
- **Malay text:** natural Malaysian Malay, not Indonesian. Use the glossary in the Plan 2 document and run `tools/python/arah_ms_check.py`.
- **Branding:** `tools/python/arah_brand_check.py` finds upstream branding left in user-visible places, and lists placeholders.
- **Process:** the owner uses the superpowers workflow (brainstorm → spec → plan → execute with TDD → one final review). The owner's global git rules (branch names `feat-###-…`, PRs, never delete branches) apply once Arah has its own remote. Until then, work on local branches and merge locally only when the owner says so.
- **Build machine:**
  - **OS and tools:** macOS 27. Xcode 27 with the Metal Toolchain installed; the iOS simulator lives in Xcode's "Device Hub" app. Qt from Homebrew at `/opt/homebrew/opt/qt`.
  - **Build dirs:** use `build-<agent-name>`.
  - **Android:** the SDK is not installed yet.
