# Arah

**Offline maps and navigation for Malaysia, in Bahasa Melayu.**

Arah ("direction" in Malay) is a free, open-source map and navigation app for everyday drivers in Malaysia. It is built
on [CoMaps](https://codeberg.org/comaps/comaps), the community fork of Organic Maps, and uses map data from
[OpenStreetMap](https://www.openstreetmap.org/).

> [!NOTE]
> Arah is in early development. There is no release in the App Store or Play Store yet.

## What Arah adds to CoMaps

- **Malay first.** The app opens in Bahasa Melayu, with Malaysian Malay for the app, search categories and voice
  directions. English and all of CoMaps' other languages stay available.
- **The "Tenang" look.** A calm, light map style: teal, warm beige and amber warnings, on every map mode, day and night.
- **Arah's own name**, with CoMaps credited on the About screen.

Everything else comes from CoMaps: offline maps of the whole world, driving, cycling, walking and public transport
routes, search, bookmarks, map editing, and no ads or tracking.

## Plans

1. **The rebrand (now):** the Malay app, the Tenang map style, Arah's iPhone and Android screens and icon.
2. **Live alerts:** traffic jams, police, accidents and speed cameras, reported by drivers.
3. **Arah's own Malaysia map data.**

## Building

Arah builds exactly like CoMaps:

- **First set-up:** [docs/INSTALL.md](docs/INSTALL.md), including `./configure.sh`, which generates the map styles,
  strings and world maps.
- **Desktop (Qt) and tests:** [docs/INSTALL_DESKTOP.md](docs/INSTALL_DESKTOP.md) and [docs/TESTING.md](docs/TESTING.md).
- **iPhone:** open `xcode/CoMaps.xcworkspace` and run the `CoMaps` scheme. The app installs as "Arah".

Arah-only code lives in files named `arah_*`, so updates from CoMaps keep merging cleanly.

## Contributing

Bug reports, Malay wording, testing on real phones and code are all welcome. Start with
[CONTRIBUTING.md](CONTRIBUTING.md).

- **A place or road is wrong on the map?** Fix it on [OpenStreetMap](https://www.openstreetmap.org/). Arah's maps
  come from there.
- **Found a security problem?** See [SECURITY.md](SECURITY.md). Please do not open a public issue.

Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Credits and licence

Arah is licensed under the [Apache License 2.0](LICENSE), like CoMaps. See [NOTICE](NOTICE) and
[data/copyright.html](data/copyright.html) for the copyright of the code and libraries it includes.

- [CoMaps](https://codeberg.org/comaps/comaps), [Organic Maps](https://organicmaps.app/) and MAPS.ME, whose
  contributors wrote the app Arah is built on.
- Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), available under the Open
  Database License.

Arah is an independent community project. It is not affiliated with or endorsed by CoMaps, Organic Maps or
OpenStreetMap.
