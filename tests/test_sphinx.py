import os
from pathlib import Path

import pytest
from sphinx.testing.util import SphinxTestApp
from sphinx.testing.path import path as sphinx_path

from sphinx_external_toc.tools import create_site_from_toc

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))


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
        app = make_app(srcdir=sphinx_path(os.path.abspath(str(src_path))), **kwargs)
        return SphinxBuild(app, src_path)

    yield _func


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_success(path: Path, tmp_path: Path, sphinx_build_factory):
    """Test successful builds."""
    src_dir = tmp_path / "srcdir"
    # write document files
    create_site_from_toc(path, root_path=src_dir)
    # write conf.py
    src_dir.joinpath("conf.py").write_text(CONF_CONTENT, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build()


def test_contains_toctree(tmp_path: Path, sphinx_build_factory):
    """Test for warning if ``toctree`` directive in file."""
    path = Path(__file__).parent.joinpath("_bad_toc_files", "contains_toctree.yml")
    src_dir = tmp_path / "srcdir"
    # write document files
    sitemap = create_site_from_toc(path, root_path=src_dir)
    # write conf.py
    src_dir.joinpath("conf.py").write_text(CONF_CONTENT, encoding="utf8")
    # run sphinx
    builder = sphinx_build_factory(src_dir)
    builder.build(assert_pass=False)
    assert sitemap.meta["expected_warning"] in builder.warnings
