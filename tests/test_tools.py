from pathlib import Path

import pytest

from sphinx_external_toc.tools import create_site_from_toc

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))


@pytest.mark.parametrize(
    "path", TOC_FILES, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES]
)
def test_file_to_sitemap(path: Path, tmp_path: Path, data_regression):
    create_site_from_toc(path, root_path=tmp_path)
    file_list = [p.relative_to(tmp_path).as_posix() for p in tmp_path.glob("**/*")]
    data_regression.check(sorted(file_list))
