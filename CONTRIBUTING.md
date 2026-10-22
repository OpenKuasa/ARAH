# Contributing to Arah

Arah is a community, open-source project. Thank you for helping.

You do not have to write code. Bug reports, better Malay wording, ideas, design and testing on real phones are all
useful.

## Ground rules

### Original work only

- **Do not copy from any proprietary app or service.** That means no source code, interface text, designs,
  screenshots, icons, images or map data. Building the same kind of feature as another navigation app is fine;
  reproducing its look or its implementation is not.
- **Do not copy map data from other maps** (Google Maps, Waze and so on). Their terms do not allow it. Map data comes
  from OpenStreetMap.
- **Do not use another company's names or branding** in the app, except to credit CoMaps, Organic Maps and
  OpenStreetMap, whose work Arah is built on.
- **Do not contribute anything you obtained under an agreement** with another company that restricts its use.
- **Do not make claims that are not true** in the app, the store listings or the docs.

### Licensing

Arah is licensed under the [Apache License 2.0](LICENSE), like CoMaps. By opening a pull request you agree that your
contribution is licensed under the same terms, and you confirm it is your own work or that you have the right to submit
it.

Everyone taking part follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## Where to report what

| What you found | Where it goes |
|---|---|
| A bug in Arah | A [bug report](https://github.com/OpenKuasa/ARAH/issues/new/choose) |
| An idea, or something you want to build | A [feature request](https://github.com/OpenKuasa/ARAH/issues/new/choose) |
| Awkward or wrong Malay | A bug report, with a screenshot and your suggested wording |
| A wrong place, road or name on the map | [OpenStreetMap](https://www.openstreetmap.org/), not here |
| A security problem | Privately, as the [security policy](SECURITY.md) explains |

Search the open issues first. If yours is already there, add to it.

## Issues

- **Small changes** such as a typo, a wording fix or an obvious bug can go straight to a pull request.
- **Anything bigger** starts as an issue: a new screen, a new setting, a change to how navigation behaves, or a new
  dependency. Agreeing the scope first saves you from building something that cannot be merged.
- **To take an issue,** comment on it and a maintainer will assign it to you. Please do not start on an issue
  assigned to someone else.

## Making a change

1. Fork the repository and create a branch from an up-to-date `main`.
2. Set up the build with [docs/INSTALL.md](docs/INSTALL.md). Run `./configure.sh` once before the first build.
3. Make your change in small, focused commits, and run the tests for the parts you touched
   ([docs/TESTING.md](docs/TESTING.md)).
4. Push to your fork and open a pull request against `main`.

### Branch names

Name your branch `type-description`, in lower case with hyphens, where the type is `feat` for a feature, `bug` for a
fix or `exp` for an experiment. If an issue tracks the work, put its number after the type, such as
`feat-41-speed-camera-alerts`. Maintainers' own branches carry a three-digit sequence number, such as
`feat-004-github-community-files`; please do not continue that sequence from a fork.

### Staying close to CoMaps

Arah regularly merges updates from CoMaps, so changes should keep that easy:

- **Change values, not structure.** Prefer changing a colour, a string or a setting over moving or rewriting CoMaps
  code.
- **Put Arah-only code in new files named `arah_*`**, and keep edits to CoMaps' own files small.
- **Follow CoMaps' conventions:** [docs/CPP_STYLE.md](docs/CPP_STYLE.md), [docs/OBJC_STYLE.md](docs/OBJC_STYLE.md),
  [docs/SWIFT_STYLE.md](docs/SWIFT_STYLE.md), [docs/JAVA_STYLE.md](docs/JAVA_STYLE.md) and
  [docs/FORMATTER.md](docs/FORMATTER.md).
- **Commit messages** follow CoMaps' style: `[subsystem] Summary`, such as `[ios] Default Arah to Malay on first launch`.
- **Generated files** (map styles, translations) are regenerated with the repository's tools, never edited by hand,
  and committed separately.
- **A fix that would help CoMaps too** is best sent to [CoMaps](https://codeberg.org/comaps/comaps) as well.

CoMaps' own guide, [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md), explains the code in more depth.

### Malay text

Use natural Malaysian Malay, not Indonesian (for example "kereta", not "mobil"; "telefon", not "ponsel"). Before
submitting Malay strings, run:

```bash
python3 tools/python/arah_ms_check.py
```

## Pull requests

- **One topic per pull request.** Unrelated fixes go in separate pull requests.
- **Link the issue.** If an issue tracks the work, write `Closes #41` in the description. If there is none, leave the
  line out; you do not need to create one.
- **Show interface changes** with before and after screenshots, on a phone-sized screen.
- **Say what you tested,** and on which devices.
- **Not finished?** Open it as a draft.

A maintainer will review your pull request and may ask for changes. Pull requests are squash-merged, so your commits
become one commit on `main` with you as the author.
