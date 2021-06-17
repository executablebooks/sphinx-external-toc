# Change Log

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
