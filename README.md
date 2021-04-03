# sphinx-external-toc [IN-DEVELOPMENT]

A sphinx extension that allows the documentation toctree to be defined in a single file.

In normal Sphinx documentation, the documentation structure is defined *via* a bottom-up approach - adding [`toctree` directives](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents) within pages of the documentation.

This extension facilitates a **top-down** approach to defining the Table of Contents (ToC) structure, within a single file that is external to the documentation.

The path to the toc file can be defined with `external_toc_path` (default: `_toc.yml`).

## User Guide

### Sphinx Configuration

Add to your `conf.py`:

```python
extensions = ["sphinx_external_toc"]
external_toc_path = "_toc.yml"  # optional
```

### Basic Structure

A minimal ToC defines the top level `main` key, and a single root document page:

```yaml
main:
  doc: intro
```

The value of the `doc` key will be a path to a file (relative to the `conf.py`) with or without the file extension.

```{important}
Each document can only occur once in the ToC!
```

Documents can then have a `parts` key - denoting a list of individual toctrees for that document - and in-turn each part should have a `sections` key - denoting a list child documents/URLs.
This can proceed recursively to any depth.

```yaml
main:
  doc: intro
  parts:
  - sections:
    - doc: doc1
      parts:
      - sections:
        - doc: doc2
        - url: https://example.com
```

As a shorthand, the `sections` key can be at the same level as the `doc`, which denotes a document with a single `part`.
For example, this file is exactly equivalent to the one above:

```yaml
main:
  doc: intro
  sections:
  - doc: doc1
    sections:
    - doc: doc2
    - url: https://example.com
```

### Titles and Captions

By default, ToCs will use the initial header within a document as its title
With the `title` key you can set an alternative title for a document or URL.
Each part can also have a `caption`, e.g. for use in ToC side-bars:

```yaml
main:
  doc: intro
  title: Introduction
  parts:
  - caption: Part Caption
    sections:
    - doc: doc1
    - url: https://example.com
      title: Example Site
```

### Numbering

You can automatically add numbers to all docs with a part by adding the `numbered: true` flag to it:

```yaml
main:
  doc: intro
  parts:
  - numbered: true
    sections:
    - doc: doc1
    - doc: doc2
```

You can also **limit the TOC numbering depth** by setting the `numbered` flag to an integer instead of `true`, e.g., `numbered: 3`.

### Defaults

To have e.g. `numbered` added to all toctrees, set it in under a `defaults` top-level key:

```yaml
defaults:
  numbered: true
main:
  doc: intro
  sections:
  - doc: doc1
    sections:
    - doc: doc2
    - url: https://example.com
```

Available keys: `numbered`, `titlesonly`, `reversed`

## API

The ToC file is parsed to a `SiteMap`, which is a `MutableMapping` subclass, with keys representing docnames mapping to a `DocItem` that stores information on the toctrees it should contain:

```python
import yaml
from sphinx_external_toc.api import parse_toc_file
path = "path/to/_toc.yml"
site_map = parse_toc_file(path)
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
  title: Introduction
```

## Command-line

This package comes with the `sphinx-etoc` command-line program, with some additional tools.

To see all options:

```shell
$ sphinx-etoc --help
```

To build a template site from only a ToC file:

```shell
$ sphinx-etoc create-site -p path/to/site -e rst path/to/_toc.yml
```

## Development Notes

Want to have a built-in CLI including commands:

- generate toc from existing documentation toctrees (and remove toctree directives)
- generate toc from existing documentation, but just from its structure (i.e. `jupyter-book toc mybookpath/`)
- generate documentation skeleton from toc
- check toc (without running sphinx)

Process:

- Read toc ("builder-inited" event), error if toc not found
  - Note, in jupyter-book: if index page does not exist, works out first page from toc and creates an index page that just redirects to it)
- adds toctree node to page doctree after it is parsed ("doctree-read" event)
  - Note, in jupyter-book this was done by physically addingto the text before parsing ("source-read" event), but this is not as robust.

Questions / TODOs:

- What if toctree directive found in file? (raise incompatibility error/warnings)
- How to deal with changes in toctree, i.e. invalidating pages if there children change
- warn if `master_doc` specified and different to landing page.
- Should `titlesonly` default to `True` (as in jupyter-book)?
- nested numbered toctree not allowed (logs warning), so should be handled if `numbered: true` is in defaults
- Handle globbing in sections (separate `glob` key?), also deal with in `create_site_from_toc`
- Add additional top-level keys, e.g. `appendices` and `bibliography`
- testing against Windows
- option to add files not in toc to `ignore_paths` (including glob)
