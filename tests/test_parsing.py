from pathlib import Path

import pytest

from sphinx_external_toc.parsing import MalformedError, create_toc_dict, parse_toc_yaml

TOC_FILES = list(Path(__file__).parent.joinpath("_toc_files").glob("*.yml"))


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


TOC_FILES_BAD = list(Path(__file__).parent.joinpath("_bad_toc_files").glob("*.yml"))
ERROR_MESSAGES = {
    "bad_url.yml": "item validation @ '/items/0': 'url' must match regex",
    "empty.yml": "toc is not a mapping:",
    "file_and_glob_present.yml": "item contains incompatible keys .* @ '/items/0'",
    "list.yml": "toc is not a mapping:",
    "unknown_keys.yml": "Unknown keys found: .* @ '/'",
    "empty_items.yml": "'items' not a non-empty list @ '/'",
    "items_in_glob.yml": "item contains incompatible keys 'glob' and 'items' @ '/items/0'",
    "no_root.yml": "'root' key not found @ '/'",
    "unknown_keys_nested.yml": "Unknown keys found: {'unknown'}, allow.* @ '/subtrees/0/items/1/'",
    "empty_subtrees.yml": "'subtrees' not a non-empty list @ '/'",
    "items_in_url.yml": "item contains incompatible keys 'url' and 'items' @ '/items/0'",
    "subtree_with_no_items.yml": "item not a mapping containing 'items' key @ '/subtrees/0/'",
}


@pytest.mark.parametrize(
    "path", TOC_FILES_BAD, ids=[path.name.rsplit(".", 1)[0] for path in TOC_FILES_BAD]
)
def test_malformed_file_parse(path: Path):
    message = ERROR_MESSAGES[path.name]
    with pytest.raises(MalformedError, match=message):
        parse_toc_yaml(path)
