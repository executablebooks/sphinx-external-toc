# sphinx-external-toc [IN-DEVELOPMENT]

[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]
[![Code style: black][black-badge]][black-link]
[![PyPI][pypi-badge]][pypi-link]

A sphinx extension that allows the documentation site-map (a.k.a Table of Contents) to be defined external to the documentation files.

In normal Sphinx documentation, the documentation site-map is defined *via* a bottom-up approach - adding [`toctree` directives](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents) within pages of the documentation.

This extension facilitates a **top-down** approach to defining the site-map structure, within a single YAML file.

## User Guide

### Sphinx Configuration

Add to your `conf.py`:

```python
extensions = ["sphinx_external_toc"]
external_toc_path = "_toc.yml"  # optional, default: _toc.yml
external_toc_exclude_missing = False  # optional, default: False
```

### Basic Structure

A minimal ToC defines the top level `root` key, for a single root document file:

```yaml
root: intro
```

The value of the `root` key will be a path to a file, in Unix format (folders split by `/`), relative to the source directory, and can be with or without the file extension.

:::{note}
This root file will be set as the [`master_doc`](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-master_doc).
:::

Document files can then have a `parts` key - denoting a list of individual toctrees for that document - and in-turn each part should have a `sections` key - denoting a list of children links, that are one of: `file`, `url` or `glob`:

- `file`: path to a single document file in Unix format,  with or without the file extension (as for `root`)
- `glob`: path to one or more document files *via* Unix shell-style wildcards (similar to [`fnmatch`](https://docs.python.org/3/library/fnmatch.html), but single stars don't match slashes.)
- `url`: path for an external URL (starting e.g. `http` or `https`)

:::{important}
Each document file can only occur once in the ToC!
:::

This can proceed recursively to any depth.

```yaml
root: intro
parts:
- sections:
  - file: doc1
    parts:
    - sections:
      - file: doc2
        parts:
        - sections:
          - file: doc3
  - url: https://example.com
  - glob: subfolder/other*
```

This is equivalent to having a single `toctree` directive in `intro`, containing `doc1`,
and a single `toctree` directive in `doc1`, with the `:glob:` flag and containing `doc2`, `https://example.com` and `subfolder/other*`.

As a shorthand, the `sections` key can be at the same level as the `file`, which denotes a document with a single `part`.
For example, this file is exactly equivalent to the one above:

```yaml
root: intro
sections:
- file: doc1
  sections:
  - file: doc2
    sections:
    - file: doc3
- url: https://example.com
- glob: subfolder/other*
```

### Titles and Captions

By default, ToCs will use the initial header within a document as its title.

With the `title` key you can set an alternative title for a document or URL in the ToC.
Each part can also have a `caption`, e.g. for use in ToC side-bars:

```yaml
root: intro
parts:
- caption: Part Caption
  sections:
  - file: doc1
    title: Document 1
  - url: https://example.com
    title: Example Site
```

### Numbering

You can automatically add numbers to all docs with a part by adding the `numbered: true` flag to it:

```yaml
root: intro
parts:
- numbered: true
  sections:
  - file: doc1
  - file: doc2
```

You can also **limit the TOC numbering depth** by setting the `numbered` flag to an integer instead of `true`, e.g., `numbered: 3`.

:::{note}
By default, section numbering restarts for each `part`.
If you want want this numbering to be continuous, check-out the [sphinx-multitoc-numbering extension](https://github.com/executablebooks/sphinx-multitoc-numbering).
:::

### Defaults

To have e.g. `numbered` added to all toctrees, set it under a `defaults` top-level key:

```yaml
defaults:
  numbered: true
root: intro
sections:
- file: doc1
  sections:
  - file: doc2
  - url: https://example.com
```

Available keys: `numbered`, `titlesonly`, `reversed`

## Add a ToC to a page's content

By default, the `toctree` generated per document (one per `part`) are appended to the end of the document and hidden (then, for example, most HTML themes show them in a side-bar).
But if you would like them to be visible at a certain place within the document body, you may do so by using the `tableofcontents` directive:

ReStructuredText:

```restructuredtext
.. tableofcontents::
```

MyST Markdown:

````md
```{tableofcontents}
```
````

Currently, only one `tableofcontents` should be used per page (all `toctree` will be added here), and only if it is a page with child/descendant documents.

## Excluding files not in ToC

By default, Sphinx will build all document files, regardless of whether they are specified in the Table of Contents, if they:

1. Have a file extension relating to a loaded parser (e.g. `.rst` or `.md`)
2. Do not match a pattern in [`exclude_patterns`](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-exclude_patterns)

To automatically add any document files that do not match a `file` or `glob` in the ToC to the `exclude_patterns` list, add to your `conf.py`:

```python
external_toc_exclude_missing = True
```

Note that, for performance, files that are in *hidden folders* (e.g. in `.tox` or `.venv`) will not be added to `exclude_patterns` even if they are not specified in the ToC.
You should exclude these folders explicitly.

## Command-line

This package comes with the `sphinx-etoc` command-line program, with some additional tools.

To see all options:

```console
$ sphinx-etoc --help
```

To build a template site from only a ToC file:

```console
$ sphinx-etoc create-site -p path/to/site -e rst path/to/_toc.yml
```

Note, you can also add additional files in `meta`/`create_files` amd append text to the end of files with `meta`/`create_append`, e.g.

```yaml
root: intro
sections:
- glob: doc*
meta:
  create_append:
    intro: |
      This is some
      appended text
  create_files:
  - doc1
  - doc2
  - doc3
```

To build a ToC file from an existing site:

```console
$ sphinx-etoc create-toc path/to/folder
```

Some rules used:

- Files/folders will be skipped if they match a pattern added by `-s` (based on [fnmatch](https://docs.python.org/3/library/fnmatch.html) Unix shell-style wildcards)
- Sub-folders with no content files inside will be skipped
- File and folder names will be sorted by [natural order](https://en.wikipedia.org/wiki/Natural_sort_order)
- If there is a file called `index` (or the name set by `-i`) in any folder, it will be treated as the index file, otherwise the first file by ordering will be used.

The command can also guess a `title` for each file, based on its path:

- The folder name is used for index files, otherwise the file name
- Words are split by `_`
- The first "word" is removed if it is an integer

For example, for a site with files:

```
index.rst
1_a_title.rst
11_another_title.rst
.hidden_file.rst
.hidden_folder/index.rst
1_a_subfolder/index.rst
2_another_subfolder/index.rst
2_another_subfolder/other.rst
3_subfolder/1_no_index.rst
3_subfolder/2_no_index.rst
14_subfolder/index.rst
14_subfolder/subsubfolder/index.rst
14_subfolder/subsubfolder/other.rst
```

will create the ToC:

```console
$ sphinx-etoc create-toc path/to/folder -i index -s ".*" -e ".rst" -t
root: index
sections:
- file: 1_a_title
  title: A title
- file: 11_another_title
  title: Another title
- file: 1_a_subfolder/index
  title: A subfolder
- file: 2_another_subfolder/index
  title: Another subfolder
  sections:
  - file: 2_another_subfolder/other
    title: Other
- file: 3_subfolder/1_no_index
  title: No index
  sections:
  - file: 3_subfolder/2_no_index
    title: No index
- file: 14_subfolder/index
  title: Subfolder
  sections:
  - file: 14_subfolder/subsubfolder/index
    title: Subsubfolder
    sections:
    - file: 14_subfolder/subsubfolder/other
      title: Other
```

## API

The ToC file is parsed to a `SiteMap`, which is a `MutableMapping` subclass, with keys representing docnames mapping to a `DocItem` that stores information on the toctrees it should contain:

```python
import yaml
from sphinx_external_toc.api import parse_toc_yaml
path = "path/to/_toc.yml"
site_map = parse_toc_yaml(path)
yaml.dump(site_map.as_json())
```

Would produce e.g.

```yaml
_root: intro
doc1:
  docname: doc1
  parts: []
  title: null
intro:
  docname: intro
  parts:
  - caption: Part Caption
    numbered: true
    reversed: false
    sections:
    - doc1
    titlesonly: true
  title: null
```

## Development Notes

Questions / TODOs:

- add migration CLI command for old jupyter-book format
- Should `titlesonly` default to `True` (as in jupyter-book)?
- nested numbered toctree not allowed (logs warning), so should be handled if `numbered: true` is in defaults
- Add additional top-level keys, e.g. `appendices` (see https://github.com/sphinx-doc/sphinx/issues/2502) and `bibliography`
- Add tests for "bad" toc files
- Using `external_toc_exclude_missing` to exclude a certain file suffix:
  currently if you had files `doc.md` and `doc.rst`, and put `doc.md` in your ToC,
  it will add `doc.rst` to the excluded patterns but then, when looking for `doc.md`,
  will still select `doc.rst` (since it is first in `source_suffix`).
  Maybe open an issue on sphinx, that `doc2path` should respect exclude patterns.
- Integrate https://github.com/executablebooks/sphinx-multitoc-numbering into this extension? (or upstream PR)
- document suppressing warnings
- test against orphan file
- https://github.com/executablebooks/sphinx-book-theme/pull/304
- CLI command to generate toc from existing documentation `toctrees` (and then remove toctree directives)

[github-ci]: https://github.com/executablebooks/sphinx-external-toc/workflows/continuous-integration/badge.svg?branch=main
[github-link]: https://github.com/executablebooks/sphinx-external-toc
[codecov-badge]: https://codecov.io/gh/executablebooks/sphinx-external-toc/branch/main/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/sphinx-external-toc
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-link]: https://github.com/ambv/black
[pypi-badge]: https://img.shields.io/pypi/v/sphinx-external-toc.svg
[pypi-link]: https://pypi.org/project/sphinx-external-toc
