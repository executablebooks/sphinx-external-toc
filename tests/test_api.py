from pathlib import Path

import pytest

from sphinx_external_toc.api import parse_toc_file

TOC_FILES = list(Path(__file__).parent.joinpath("toc_files").glob("*.yml"))


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_file_to_sitemap(path: Path, data_regression):
    site_map = parse_toc_file(path)
    data_regression.check(site_map.as_json())
