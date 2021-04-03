""" """
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Tuple, Union

import attr
from attr.validators import instance_of, deep_iterable, optional
import yaml


@attr.s(slots=True)
class UrlItem:
    """A URL in a toctree."""

    url: str = attr.ib(validator=instance_of(str))
    title: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))


@attr.s(slots=True)
class TocItem:
    """An individual toctree within a document."""

    # TODO validate uniqueness of docnames (at least one item)
    sections: List[Union[str, UrlItem]] = attr.ib(
        validator=deep_iterable(instance_of((str, UrlItem)), instance_of(list))
    )
    caption: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))
    numbered: Union[bool, int] = attr.ib(False, validator=instance_of((bool, int)))
    # TODO in jupyter-book titlesonly default is True, but why
    titlesonly: bool = attr.ib(True, validator=instance_of(bool))
    reversed: bool = attr.ib(False, validator=instance_of(bool))

    def docnames(self) -> List[str]:
        return [section for section in self.sections if isinstance(section, str)]


@attr.s(slots=True)
class DocItem:
    """A document in the site map."""

    docname: str = attr.ib(validator=instance_of(str))
    title: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))
    # TODO validate uniqueness of docnames across all parts (and none should be the docname)
    parts: List[TocItem] = attr.ib(
        factory=list, validator=deep_iterable(instance_of(TocItem), instance_of(list))
    )

    def children(self) -> List[str]:
        """Return all children docs."""
        return [name for part in self.parts for name in part.docnames()]


class SiteMap(MutableMapping):
    """A mapping of documents to their toctrees (or None if terminal)."""

    def __init__(self, root: DocItem) -> None:
        self._docs: Dict[str, DocItem] = {}
        self[root.docname] = root
        self._root: DocItem = root

    @property
    def root(self) -> DocItem:
        return self._root

    def __getitem__(self, docname: str) -> DocItem:
        return self._docs[docname]

    def __setitem__(self, docname: str, item: DocItem) -> None:
        assert item.docname == docname
        self._docs[docname] = item

    def __delitem__(self, docname: str):
        assert docname != self._root.docname, "cannot delete root doc item"
        del self._docs[docname]

    def __iter__(self) -> Iterator[str]:
        for docname in self._docs:
            yield docname

    def __len__(self) -> int:
        return len(self._docs)

    def as_json(self, root_key: str = "_root") -> Dict[str, Any]:
        dct = {k: attr.asdict(v) if v else v for k, v in self._docs.items()}
        assert root_key not in dct
        dct[root_key] = self.root.docname
        return dct


class MalformedError(Exception):
    """Raised if toc file is malformed."""


def parse_toc_file(path: Union[str, Path], encoding: str = "utf8") -> SiteMap:
    """Parse the ToC file."""
    with Path(path).open(encoding=encoding) as handle:
        data = yaml.safe_load(handle)
    return parse_toc_data(data)


def parse_toc_data(data: Dict[str, Any]) -> SiteMap:
    """Parse a dictionary of the ToC."""
    defaults: Dict[str, Any] = data.get("defaults", {})

    if "main" not in data:
        raise MalformedError("'main' key not present")

    doc_item, docs_list = _parse_doc_item(data["main"], defaults, "main/")

    site_map = SiteMap(root=doc_item)

    _parse_docs_list(docs_list, site_map, defaults, "main/")

    return site_map


def _parse_doc_item(
    data: Dict[str, Any], defaults: Dict[str, Any], path: str
) -> Tuple[DocItem, Sequence[Dict[str, Any]]]:
    """Parse a single doc item."""
    if "doc" not in data:
        raise MalformedError(f"'doc' key not found: '{path}'")
    if "sections" in data:
        # this is a shorthand for defining a single part
        if "parts" in data:
            raise MalformedError(f"Both 'sections' and 'parts' found: '{path}'")
        parts_data = [{"sections": data["sections"]}]
    else:
        parts_data = data.get("parts", [])

    if not isinstance(parts_data, Sequence):
        raise MalformedError(f"'parts' not a sequence: '{path}'")

    _known_link_keys = {"url", "doc"}

    parts = []
    for part_idx, part in enumerate(parts_data):

        # generate sections list
        sections: List[Union[str, UrlItem]] = []
        for sect_idx, section in enumerate(part["sections"]):
            link_keys = _known_link_keys.intersection(section)
            if not link_keys:
                raise MalformedError(
                    "toctree section does not contain one of "
                    f"{_known_link_keys!r}: {path}{part_idx}/{sect_idx}"
                )
            if not len(link_keys) == 1:
                raise MalformedError(
                    "toctree section contains incompatible keys "
                    f"{link_keys!r}: {path}{part_idx}/{sect_idx}"
                )
            if link_keys == {"url"}:
                sections.append(UrlItem(section["url"], section.get("title")))
            else:
                sections.append(section["doc"])

        # generate toc key-word arguments
        keywords = {}
        for key in ("caption", "numbered", "titlesonly", "reversed"):
            if key in part:
                keywords[key] = part[key]
            elif key in defaults:
                keywords[key] = defaults[key]

        try:
            toc_item = TocItem(sections=sections, **keywords)
        except TypeError as exc:
            raise MalformedError(f"toctree validation: {path}{part_idx}") from exc
        parts.append(toc_item)

    try:
        doc_item = DocItem(docname=data["doc"], title=data.get("title"), parts=parts)
    except TypeError as exc:
        raise MalformedError(f"doc validation: {path}") from exc

    docs_data = [
        section
        for part in parts_data
        for section in part["sections"]
        if "doc" in section
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
        docname = doc_data["doc"]
        if docname in site_map:
            raise MalformedError(f"document used multiple times: {docname}")
        child_path = f"{path}{docname}/"
        child_item, child_docs_list = _parse_doc_item(doc_data, defaults, child_path)
        site_map[docname] = child_item

        _parse_docs_list(child_docs_list, site_map, defaults, child_path)
