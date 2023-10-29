import os
from pathlib import Path

import pytest
from sphinx import version_info as sphinx_version_info
from sphinx.testing.util import SphinxTestApp

from sphinx_external_toc.tools import create_site_from_toc

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))
TOC_FILES_WARN = list(
    Path(__file__).parent.joinpath("_warning_toc_files").glob("*.yml")
)


CONF_CONTENT = """
extensions = ["sphinx_external_toc"]
external_toc_path = "_toc.yml"

"""


class SphinxBuild:
    def __init__(self, app: SphinxTestApp, src: Path):
        self.app = app
        self.src = src

    def build(self, assert_pass=True):
        self.app.build()
        if assert_pass:
            assert self.warnings == "", self.status
        return self

    @property
    def status(self):
        return self.app._status.getvalue()

    @property
    def warnings(self):
        return self.app._warning.getvalue()

    @property
    def outdir(self):
        return Path(self.app.outdir)


@pytest.fixture()
def sphinx_build_factory(make_app):
    def _func(src_path: Path, **kwargs) -> SphinxBuild:
        # For compatibility with multiple versions of sphinx, convert pathlib.Path to
        # sphinx.testing.path.path here.
        if sphinx_version_info >= (7, 2):
            app_srcdir = src_path
        else:
            from sphinx.testing.path import path

            app_srcdir = path(os.fspath(src_path))

        app = make_app(srcdir=app_srcdir, **kwargs)
        return SphinxBuild(app, src_path)

    yield _func


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_success(path: Path, tmp_path: Path, sphinx_build_factory, file_regression):
    """Test successful builds."""
    src_dir = tmp_path / "srcdir"
    # write document files
    site_map = create_site_from_toc(path, root_path=src_dir)
    # write conf.py
    src_dir.joinpath("conf.py").write_text(
        CONF_CONTENT
        + (
            "external_toc_exclude_missing = True"
            if site_map.meta.get("exclude_missing") is True
            else ""
        ),
        encoding="utf8",
    )
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build()
    # optionally check the doctree of a file
    if "regress" in site_map.meta:
        doctree = builder.app.env.get_doctree(site_map.meta["regress"])
        doctree["source"] = site_map.meta["regress"]
        file_regression.check(doctree.pformat(), extension=".xml", encoding="utf8")


def test_gettext(tmp_path: Path, sphinx_build_factory):
    """Test the gettext builder runs correctly."""
    src_dir = tmp_path / "srcdir"
    # write document files
    toc_path = Path(__file__).parent.joinpath("_toc_files", "basic.yml")
    create_site_from_toc(toc_path, root_path=src_dir, toc_name=None)
    # write conf.py
    content = f"""
extensions = ["sphinx_external_toc"]
external_toc_path = {Path(os.path.abspath(toc_path)).as_posix()!r}

"""
    src_dir.joinpath("conf.py").write_text(content, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir, buildername="gettext")
    builder.build()


@pytest.mark.parametrize(
    "path", TOC_FILES_WARN, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES_WARN]
)
def test_warning(path: Path, tmp_path: Path, sphinx_build_factory):
    src_dir = tmp_path / "srcdir"
    # write document files
    sitemap = create_site_from_toc(path, root_path=src_dir)
    # write conf.py
    src_dir.joinpath("conf.py").write_text(CONF_CONTENT, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build(assert_pass=False)
    assert sitemap.meta["expected_warning"] in builder.warnings


def test_absolute_path(tmp_path: Path, sphinx_build_factory):
    """Test if `external_toc_path` is supplied as an absolute path."""
    src_dir = tmp_path / "srcdir"
    # write document files
    toc_path = Path(__file__).parent.joinpath("_toc_files", "basic.yml")
    create_site_from_toc(toc_path, root_path=src_dir, toc_name=None)
    # write conf.py
    content = f"""
extensions = ["sphinx_external_toc"]
external_toc_path = {Path(os.path.abspath(toc_path)).as_posix()!r}

"""
    src_dir.joinpath("conf.py").write_text(content, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build()


def test_file_extensions(tmp_path: Path, sphinx_build_factory):
    """Test for tocs containing docnames with file extensions."""
    src_dir = tmp_path / "srcdir"
    src_dir.mkdir(exist_ok=True)
    # write documents
    src_dir.joinpath("intro.rst").write_text("Head\n====\n", encoding="utf8")
    src_dir.joinpath("markdown.rst").write_text("Head\n====\n", encoding="utf8")
    src_dir.joinpath("notebooks.rst").write_text("Head\n====\n", encoding="utf8")
    # write toc
    toc_path = tmp_path / "toc.yml"
    toc_path.write_text(
        """
format: jb-book
root: intro.rst
chapters:
- file: markdown.rst
  sections:
  - file: notebooks.rst
    """,
        encoding="utf8",
    )
    # write conf.py
    content = f"""
extensions = ["sphinx_external_toc"]
external_toc_path = {Path(os.path.abspath(toc_path)).as_posix()!r}

"""
    src_dir.joinpath("conf.py").write_text(content, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build()
