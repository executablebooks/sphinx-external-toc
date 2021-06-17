# Command-line

This package comes with the `sphinx-etoc` command-line program, with some additional tools.

To see all options:

```console
$ sphinx-etoc --help
Usage: sphinx-etoc [OPTIONS] COMMAND [ARGS]...

  Command-line for sphinx-external-toc.

Options:
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  from-project  Create a ToC file from a project directory.
  migrate    Migrate a ToC from a previous revision.
  parse      Parse a ToC file to a site-map YAML.
  to-project    Create a project directory from a ToC file.
```

To build a template project from only a ToC file:

```console
$ sphinx-etoc to-project -p path/to/site -e rst path/to/_toc.yml
```

Note, you can also add additional files in `meta`/`create_files` amd append text to the end of files with `meta`/`create_append`, e.g.

```yaml
root: intro
entries:
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
$ sphinx-etoc from-project path/to/folder
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

For example, for a project with files:

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
$ sphinx-etoc from-project path/to/folder -i index -s ".*" -e ".rst" -t
root: index
entries:
- file: 1_a_title
  title: A title
- file: 11_another_title
  title: Another title
- file: 1_a_subfolder/index
  title: A subfolder
- file: 2_another_subfolder/index
  title: Another subfolder
  entries:
  - file: 2_another_subfolder/other
    title: Other
- file: 3_subfolder/1_no_index
  title: No index
  entries:
  - file: 3_subfolder/2_no_index
    title: No index
- file: 14_subfolder/index
  title: Subfolder
  entries:
  - file: 14_subfolder/subsubfolder/index
    title: Subsubfolder
    entries:
    - file: 14_subfolder/subsubfolder/other
      title: Other
```
