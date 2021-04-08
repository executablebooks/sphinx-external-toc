from pathlib import Path

import pytest

from sphinx_external_toc.api import MalformedError, create_toc_dict, parse_toc_yaml

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))
TOC_FILES_BAD = list(Path(__file__).parent.joinpath("_bad_toc_files").glob("*.yml"))


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_file_to_sitemap(path: Path, data_regression):
    site_map = parse_toc_yaml(path)
    data_regression.check(site_map.as_json())


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_create_toc_dict(path: Path, data_regression):
    site_map = parse_toc_yaml(path)
    data = create_toc_dict(site_map)
    data_regression.check(data)


@pytest.mark.parametrize(
    "path", TOC_FILES_BAD, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES_BAD]
)
def test_malformed_file_parse(path: Path):
    with pytest.raises(MalformedError):
        parse_toc_yaml(path)
