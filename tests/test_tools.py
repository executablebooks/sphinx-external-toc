from pathlib import Path

import pytest

from sphinx_external_toc.parsing import parse_toc_data
from sphinx_external_toc.tools import (
    create_site_from_toc,
    create_site_map_from_path,
    migrate_jupyter_book,
)

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))
JB_TOC_FILES = list(
    Path(__file__).parent.joinpath("_jb_migrate_toc_files").glob("*.yml")
)


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_file_to_sitemap(path: Path, tmp_path: Path, data_regression):
    create_site_from_toc(path, root_path=tmp_path)
    file_list = [p.relative_to(tmp_path).as_posix() for p in tmp_path.glob("**/*")]
    data_regression.check(sorted(file_list))


def test_create_site_map_from_path(tmp_path: Path, data_regression):

    # create site files
    files = [
        "index.rst",
        "1_other.rst",
        "11_other.rst",
        ".hidden_file.rst",
        ".hidden_folder/index.rst",
        "subfolder1/index.rst",
        "subfolder2/index.rst",
        "subfolder2/other.rst",
        "subfolder3/no_index1.rst",
        "subfolder3/no_index2.rst",
        "subfolder14/index.rst",
        "subfolder14/subsubfolder/index.rst",
        "subfolder14/subsubfolder/other.rst",
    ]
    for posix in files:
        path = tmp_path.joinpath(*posix.split("/"))
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    site_map = create_site_map_from_path(tmp_path)
    data_regression.check(site_map.as_json())
    # data = create_toc_dict(site_map)
    # data_regression.check(data)


@pytest.mark.parametrize(
    "path", JB_TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in JB_TOC_FILES]
)
def test_migrate_jb(path, data_regression):
    toc = migrate_jupyter_book(Path(path))
    data_regression.check(toc)
    # check it is a valid toc
    parse_toc_data(toc)
