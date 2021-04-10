"""Parse the ToC to a `SiteMap` object."""
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple, Union

import attr
import yaml

from .api import DocItem, FileItem, GlobItem, SiteMap, TocItem, UrlItem

FILE_KEY = "file"
GLOB_KEY = "glob"
URL_KEY = "url"

TOCTREE_OPTIONS = (
    "caption",
    "hidden",
    "maxdepth",
    "numbered",
    "reversed",
    "titlesonly",
)


class MalformedError(Exception):
    """Raised if toc file is malformed."""


def parse_toc_yaml(path: Union[str, Path], encoding: str = "utf8") -> SiteMap:
    """Parse the ToC file."""
    with Path(path).open(encoding=encoding) as handle:
        data = yaml.safe_load(handle)
    return parse_toc_data(data)


def parse_toc_data(data: Dict[str, Any]) -> SiteMap:
    """Parse a dictionary of the ToC."""
    if not isinstance(data, Mapping):
        raise MalformedError(f"toc is not a mapping: {type(data)}")

    defaults: Dict[str, Any] = data.get("defaults", {})

    doc_item, docs_list = _parse_doc_item(data, defaults, "/", file_key="root")

    site_map = SiteMap(root=doc_item, meta=data.get("meta"))

    _parse_docs_list(docs_list, site_map, defaults, "/")

    return site_map


def _parse_doc_item(
    data: Dict[str, Any], defaults: Dict[str, Any], path: str, file_key: str = FILE_KEY
) -> Tuple[DocItem, Sequence[Dict[str, Any]]]:
    """Parse a single doc item."""
    if file_key not in data:
        raise MalformedError(f"'{file_key}' key not found: '{path}'")
    if "sections" in data:
        # this is a shorthand for defining a single part
        if "parts" in data:
            raise MalformedError(f"Both 'sections' and 'parts' found: '{path}'")
        parts_data = [{"sections": data["sections"], **data.get("options", {})}]
    elif "parts" in data:
        parts_data = data["parts"]
        if not (isinstance(parts_data, Sequence) and parts_data):
            raise MalformedError(f"parts not a non-empty list: '{path}'")
    else:
        parts_data = []

    _known_link_keys = {FILE_KEY, GLOB_KEY, URL_KEY}

    parts = []
    for part_idx, part in enumerate(parts_data):

        if not (isinstance(part, Mapping) and "sections" in part):
            raise MalformedError(
                f"part not a mapping containing 'sections' key: '{path}{part_idx}'"
            )

        section_data = part["sections"]

        if not (isinstance(section_data, Sequence) and section_data):
            raise MalformedError(f"sections not a non-empty list: '{path}{part_idx}'")

        # generate sections list
        sections: List[Union[GlobItem, FileItem, UrlItem]] = []
        for sect_idx, section in enumerate(section_data):

            if not isinstance(section, Mapping):
                raise MalformedError(
                    f"toctree section not a mapping type: '{path}{part_idx}/{sect_idx}'"
                )

            link_keys = _known_link_keys.intersection(section)
            if not link_keys:
                raise MalformedError(
                    "toctree section does not contain one of "
                    f"{_known_link_keys!r}: '{path}{part_idx}/{sect_idx}'"
                )
            if not len(link_keys) == 1:
                raise MalformedError(
                    "toctree section contains incompatible keys "
                    f"{link_keys!r}: {path}{part_idx}/{sect_idx}"
                )

            if link_keys == {FILE_KEY}:
                sections.append(FileItem(section[FILE_KEY]))
            elif link_keys == {GLOB_KEY}:
                if "sections" in section or "parts" in section:
                    raise MalformedError(
                        "toctree section contains incompatible keys "
                        f"{GLOB_KEY} and parts/sections: {path}{part_idx}/{sect_idx}"
                    )
                sections.append(GlobItem(section[GLOB_KEY]))
            elif link_keys == {URL_KEY}:
                if "sections" in section or "parts" in section:
                    raise MalformedError(
                        "toctree section contains incompatible keys "
                        f"{URL_KEY} and parts/sections: {path}{part_idx}/{sect_idx}"
                    )
                sections.append(UrlItem(section[URL_KEY], section.get("title")))

        # generate toc key-word arguments
        keywords = {k: part[k] for k in TOCTREE_OPTIONS if k in part}
        for key in defaults:
            if key not in keywords:
                keywords[key] = defaults[key]

        try:
            toc_item = TocItem(sections=sections, **keywords)
        except TypeError as exc:
            raise MalformedError(f"toctree validation: {path}{part_idx}") from exc
        parts.append(toc_item)

    try:
        doc_item = DocItem(docname=data[file_key], title=data.get("title"), parts=parts)
    except TypeError as exc:
        raise MalformedError(f"doc validation: {path}") from exc

    docs_data = [
        section
        for part in parts_data
        for section in part["sections"]
        if FILE_KEY in section
    ]

    return (
        doc_item,
        docs_data,
    )


def _parse_docs_list(
    docs_list: Sequence[Dict[str, Any]],
    site_map: SiteMap,
    defaults: Dict[str, Any],
    path: str,
):
    """Parse a list of docs."""
    for doc_data in docs_list:
        docname = doc_data["file"]
        if docname in site_map:
            raise MalformedError(f"document file used multiple times: {docname}")
        child_path = f"{path}{docname}/"
        child_item, child_docs_list = _parse_doc_item(doc_data, defaults, child_path)
        site_map[docname] = child_item

        _parse_docs_list(child_docs_list, site_map, defaults, child_path)


def create_toc_dict(site_map: SiteMap, *, skip_defaults: bool = True) -> Dict[str, Any]:
    """Create the Toc dictionary from a site-map."""
    data = _docitem_to_dict(
        site_map.root, site_map, skip_defaults=skip_defaults, file_key="root"
    )
    if site_map.meta:
        data["meta"] = site_map.meta.copy()
    return data


def _docitem_to_dict(
    doc_item: DocItem,
    site_map: SiteMap,
    *,
    skip_defaults: bool = True,
    file_key: str = FILE_KEY,
    parsed_docnames: Optional[Set[str]] = None,
) -> Dict[str, Any]:

    # protect against infinite recursion
    parsed_docnames = parsed_docnames or set()
    if doc_item.docname in parsed_docnames:
        raise RecursionError(f"{doc_item.docname!r} in site-map multiple times")
    parsed_docnames.add(doc_item.docname)

    data: Dict[str, Any] = {}

    data[file_key] = doc_item.docname
    if doc_item.title is not None:
        data["title"] = doc_item.title

    if not doc_item.parts:
        return data

    def _parse_section(item):
        if isinstance(item, FileItem):
            if item in site_map:
                return _docitem_to_dict(
                    site_map[item],
                    site_map,
                    skip_defaults=skip_defaults,
                    parsed_docnames=parsed_docnames,
                )
            return {FILE_KEY: str(item)}
        if isinstance(item, GlobItem):
            return {GLOB_KEY: str(item)}
        if isinstance(item, UrlItem):
            if item.title is not None:
                return {URL_KEY: item.url, "title": item.title}
            return {URL_KEY: item.url}
        raise TypeError(item)

    data["parts"] = []
    fields = attr.fields_dict(TocItem)
    for part in doc_item.parts:
        # only add these keys if their value is not the default
        part_data = {
            key: getattr(part, key)
            for key in ("caption", "numbered", "reversed", "titlesonly")
            if (not skip_defaults) or getattr(part, key) != fields[key].default
        }
        part_data["sections"] = [_parse_section(s) for s in part.sections]
        data["parts"].append(part_data)

    # apply shorthand if possible
    if len(data["parts"]) == 1 and list(data["parts"][0]) == ["sections"]:
        data["sections"] = data.pop("parts")[0]["sections"]

    return data
