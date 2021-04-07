# sphinx-external-toc [IN-DEVELOPMENT]

A sphinx extension that allows the documentation toctree to be defined in a single YAML file.

In normal Sphinx documentation, the documentation structure is defined *via* a bottom-up approach - adding [`toctree` directives](https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html#table-of-contents) within pages of the documentation.

This extension facilitates a **top-down** approach to defining the structure, within a single file that is external to the documentation.

```{tableofcontents}
```
