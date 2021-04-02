# Configuration file for the Sphinx documentation builder.

project = "Sphinx External ToC"
copyright = "2021, Executable Book Project"
author = "Executable Book Project"

extensions = ["myst_parser", "sphinx_external_toc"]

master_doc = "intro"
html_theme = "sphinx_book_theme"
html_theme_options = {
    "home_page_in_toc": True,
    "use_edit_page_button": True,
    "repository_url": "https://github.com/executablebooks/sphinx-external-toc",
    "repository_branch": "main",
    "path_to_docs": "docs",
}
