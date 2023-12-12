# Change Log

## v1.0.1 - 2023-12-12

([full changelog](https://github.com/executablebooks/sphinx-external-toc/compare/v1.0.0...21adcf94ca0e09e7fbce21bf87734435520169f2))

### Bugs fixed

- FIX: rework 104 to support e.g. PDFHTML [#105](https://github.com/executablebooks/sphinx-external-toc/pull/105) ([@agoose77](https://github.com/agoose77))
- FIX: exit if non-html builder [#104](https://github.com/executablebooks/sphinx-external-toc/pull/104) ([@agoose77](https://github.com/agoose77))
- FIX: simple grammatical error in `index.md` [#100](https://github.com/executablebooks/sphinx-external-toc/pull/100) ([@kallewesterling](https://github.com/kallewesterling))

### Maintenance and upkeep improvements

- MAINT: update changelog via github-activity [#102](https://github.com/executablebooks/sphinx-external-toc/pull/102) ([@agoose77](https://github.com/agoose77))

### Other merged PRs

- Bump actions/setup-python from 4 to 5 [#103](https://github.com/executablebooks/sphinx-external-toc/pull/103) ([@dependabot](https://github.com/dependabot))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/executablebooks/sphinx-external-toc/graphs/contributors?from=2023-11-08&to=2023-12-12&type=c))

[@agoose77](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Aagoose77+updated%3A2023-11-08..2023-12-12&type=Issues) | [@codecov](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Acodecov+updated%3A2023-11-08..2023-12-12&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Adependabot+updated%3A2023-11-08..2023-12-12&type=Issues) | [@kallewesterling](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Akallewesterling+updated%3A2023-11-08..2023-12-12&type=Issues) | [@welcome](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Awelcome+updated%3A2023-11-08..2023-12-12&type=Issues)



## 1.0.0 - 2023-11-08

([full changelog](https://github.com/executablebooks/sphinx-external-toc/compare/v0.3.1...9e8cc1f92d84fed6eb9602371709b6a88e47f688))

### Merged PRs

- maint: add ruff [#101](https://github.com/executablebooks/sphinx-external-toc/pull/101) ([@agoose77](https://github.com/agoose77))
- Bump actions/checkout from 3 to 4 [#98](https://github.com/executablebooks/sphinx-external-toc/pull/98) ([@dependabot](https://github.com/dependabot))
- chore: update versioning [#97](https://github.com/executablebooks/sphinx-external-toc/pull/97) ([@agoose77](https://github.com/agoose77))
- fixes https://github.com/executablebooks/jupyter-book/issues/1414 [#94](https://github.com/executablebooks/sphinx-external-toc/pull/94) ([@jdsalaro](https://github.com/jdsalaro))
- [pre-commit.ci] pre-commit autoupdate [#82](https://github.com/executablebooks/sphinx-external-toc/pull/82) ([@pre-commit-ci](https://github.com/pre-commit-ci))

### Contributors to this release

([GitHub contributors page for this release](https://github.com/executablebooks/sphinx-external-toc/graphs/contributors?from=2022-11-24&to=2023-12-04&type=c))

[@agoose77](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Aagoose77+updated%3A2022-11-24..2023-12-04&type=Issues) | [@codecov](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Acodecov+updated%3A2022-11-24..2023-12-04&type=Issues) | [@dependabot](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Adependabot+updated%3A2022-11-24..2023-12-04&type=Issues) | [@jdsalaro](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Ajdsalaro+updated%3A2022-11-24..2023-12-04&type=Issues) | [@mmcky](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Ammcky+updated%3A2022-11-24..2023-12-04&type=Issues) | [@pre-commit-ci](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Apre-commit-ci+updated%3A2022-11-24..2023-12-04&type=Issues) | [@welcome](https://github.com/search?q=repo%3Aexecutablebooks%2Fsphinx-external-toc+involves%3Awelcome+updated%3A2022-11-24..2023-12-04&type=Issues)

## 0.3.1 - 2022-11-25

- ⬆️ UPGRADE: Support `sphinx5` [#85](https://github.com/executablebooks/sphinx-external-toc/pull/85)

## 0.3.0 - 2022-04-16

- ⬆️ UPGRADE: Drop python 3.6 support (#75)
- ♻️ REFACTOR: Replace `attrs` with built-in `dataclasses` (#76)
- 🐛 FIX: gettext builder compatibility
- 🐛 FIX: Inserting toctree into empty document (#77)
- 🔧 MAINTAIN: Move from setuptools to flit, for PEP 621 packaging (#74)

## 0.2.4 - 2022-02-10

### What's Changed

- ⬆️ UPGRADE: allow click v8  by @lukasbindreiter in https://github.com/executablebooks/sphinx-external-toc/pull/69
- 📚: Fix ToC graphic link by @ZviBaratz in https://github.com/executablebooks/sphinx-external-toc/pull/63
- 🔧 MAINTAIN: Updated parser docstrings by @ZviBaratz in https://github.com/executablebooks/sphinx-external-toc/pull/61
- 🔧 MAINTAIN: Removed unused argument by @ZviBaratz in https://github.com/executablebooks/sphinx-external-toc/pull/66
- 🔧 MAINTAIN: Updated `api` docstrings by @ZviBaratz in https://github.com/executablebooks/sphinx-external-toc/pull/64
- 🔧: Docstring updates by @ZviBaratz in https://github.com/executablebooks/sphinx-external-toc/pull/67

### New Contributors

- @ZviBaratz made their first contribution in https://github.com/executablebooks/sphinx-external-toc/pull/61
- @lukasbindreiter made their first contribution in https://github.com/executablebooks/sphinx-external-toc/pull/69

**Full Changelog**: https://github.com/executablebooks/sphinx-external-toc/compare/v0.2.3...v0.2.4

## 0.2.3 - 2021-07-29

🔧 MAINTAIN: Update `attrs` minimum version to `20.3`, when `value_serializer` was introduced (required here).

👌 IMPROVE: Changed document identification.
The comparison of sitemaps and identification of changed documents to rebuild was improved and moved to `SiteMap.get_changed`.

## 0.2.2 - 2021-06-25

🐛 FIX: File extensions in ToC

Ensure files are still matched, if they are provided with file extensions.

## 0.2.1 - 2021-06-16

- ⬆️ UPDATE: Relax dependency pinning to allow Sphinx v4

## 0.2.0 - 2021-05-24

- ‼ BREAKING: the CLI command `to-site` is now `to-project`, and `from-site` is now `from-project`

## 0.1.0 - 2021-04-27

- ♻️ REFACTOR: key `items` -> `entries`
- 👌 IMPROVE: Add `--output` to `migrate` command

## 0.1.0a8 - 2021-04-19

- 👌 IMPROVE: validate URL: Ensure value of `url` keys match regex used by Sphinx to identify them
- 🐛 FIX: `external_toc_path` with absolute path

## 0.1.0a7 - 2021-04-18

- 👌 IMPROVE: Parsing `MalformedError` messages
- 👌 IMPROVE: jupyter-book migration
  - Better conversion validation
  - Move `options` key above `parts`/`chapters`/`sections` key

## 0.1.0a6 - 2021-04-18

- 👌 IMPROVE: Add `ensure_index_file` event on build completion
- ♻️ REFACTOR: Rename key: `parts` -> `subtrees`
- ♻️ REFACTOR: `sections` -> `items`, and add `format`
  - The `format` key adds key-mapping for jupyter-book support.
- ♻️ REFACTOR: API naming: renamed to be more general:
  - `DocItem` -> `Document`
  - `DocItem.parts` -> `Document.subtrees`
  - `TocItem` -> `TocTree`
  - `TocItem.sections` -> `TocTree.items`

## 0.1.0a5 - 2021-04-10

🐛 FIX: `numbered: true`, this was being equated to `numbered: 1` rather than `numbered: 999` (i.e. infinite depth).

## 0.1.0a4 - 2021-04-10

- ♻️ REFACTOR: Move parsing code to separate module
- ✨ NEW: Improve option parsing, add jupyter-book migration

## 0.1.0a3 - 2021-04-09

👌 IMPROVE: `toc.yml` validation

## 0.1.0a2 - 2021-04-08

🐛 FIX: for nested docnames in sub-folders

## 0.1.0a1 - 2021-04-08

Initial alpha release.
