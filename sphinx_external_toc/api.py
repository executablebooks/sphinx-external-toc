""" """
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence, Set, Tuple, Union

import attr
import yaml
from attr.validators import deep_iterable, instance_of, optional

FILE_KEY = "file"
GLOB_KEY = "glob"
URL_KEY = "url"


class FileItem(str):
    """A document path in a toctree list.

    This should be in Posix format (folders split by ``/``),
    relative to the source directory,
    and can be with or without extension.
    """


class GlobItem(str):
    """A document glob in a toctree list."""


@attr.s(slots=True)
class UrlItem:
    """A URL in a toctree."""

    url: str = attr.ib(validator=instance_of(str))
    title: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))


@attr.s(slots=True)
class TocItem:
    """An individual toctree within a document."""

    # TODO validate uniqueness of docnames (at least one item)
    sections: List[Union[GlobItem, FileItem, UrlItem]] = attr.ib(
        validator=deep_iterable(
            instance_of((GlobItem, FileItem, UrlItem)), instance_of(list)
        )
    )
    caption: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))
    numbered: Union[bool, int] = attr.ib(False, validator=instance_of((bool, int)))
    # TODO in jupyter-book titlesonly default is True, but why
    titlesonly: bool = attr.ib(True, validator=instance_of(bool))
    reversed: bool = attr.ib(False, validator=instance_of(bool))

    def files(self) -> List[str]:
        return [
            str(section) for section in self.sections if isinstance(section, FileItem)
        ]

    def globs(self) -> List[str]:
        return [
            str(section) for section in self.sections if isinstance(section, GlobItem)
        ]


@attr.s(slots=True)
class DocItem:
    """A document in the site map."""

    docname: str = attr.ib(validator=instance_of(str))
    title: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))
    # TODO validate uniqueness of docnames across all parts (and none should be the docname)
    parts: List[TocItem] = attr.ib(
        factory=list, validator=deep_iterable(instance_of(TocItem), instance_of(list))
    )

    def child_files(self) -> List[str]:
        """Return all children files."""
        return [name for part in self.parts for name in part.files()]

    def child_globs(self) -> List[str]:
        """Return all children globs."""
        return [name for part in self.parts for name in part.globs()]


class SiteMap(MutableMapping):
    """A mapping of documents to their toctrees (or None if terminal)."""

    def __init__(self, root: DocItem, meta: Optional[Dict[str, Any]] = None) -> None:
        self._docs: Dict[str, DocItem] = {}
        self[root.docname] = root
        self._root: DocItem = root
        self._meta: Dict[str, Any] = meta or {}

    @property
    def root(self) -> DocItem:
        """Return the root document."""
        return self._root

    @property
    def meta(self) -> Dict[str, Any]:
        """Return the site-map metadata."""
        return self._meta

    def globs(self) -> Set[str]:
        """Return set of all globs present across all toctrees."""
        return {glob for item in self._docs.values() for glob in item.child_globs()}

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

    @staticmethod
    def _serializer(inst: Any, field: attr.Attribute, value: Any) -> Any:
        """Serialize to JSON compatible value.

        (parsed to ``attr.asdict``)
        """
        if isinstance(value, (GlobItem, FileItem)):
            return str(value)
        return value

    def as_json(
        self, root_key: str = "_root", meta_key: str = "_meta"
    ) -> Dict[str, Any]:
        """Return JSON serialized site-map representation."""
        dct = {
            k: attr.asdict(v, value_serializer=self._serializer) if v else v
            for k, v in self._docs.items()
        }
        assert root_key not in dct
        dct[root_key] = self.root.docname
        if self.meta:
            assert meta_key not in dct
            dct[meta_key] = self.meta
        return dct


class MalformedError(Exception):
    """Raised if toc file is malformed."""


def parse_toc_yaml(path: Union[str, Path], encoding: str = "utf8") -> SiteMap:
    """Parse the ToC file."""
    with Path(path).open(encoding=encoding) as handle:
        data = yaml.safe_load(handle)
    return parse_toc_data(data)


def parse_toc_data(data: Dict[str, Any]) -> SiteMap:
    """Parse a dictionary of the ToC."""
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
        parts_data = [{"sections": data["sections"]}]
    else:
        parts_data = data.get("parts", [])

    if not isinstance(parts_data, Sequence):
        raise MalformedError(f"'parts' not a sequence: '{path}'")

    _known_link_keys = {FILE_KEY, GLOB_KEY, URL_KEY}

    parts = []
    for part_idx, part in enumerate(parts_data):

        # generate sections list
        sections: List[Union[GlobItem, FileItem, UrlItem]] = []
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
            if link_keys == {FILE_KEY}:
                sections.append(FileItem(section[FILE_KEY]))
            elif link_keys == {GLOB_KEY}:
                sections.append(GlobItem(section[GLOB_KEY]))
            elif link_keys == {URL_KEY}:
                sections.append(UrlItem(section[URL_KEY], section.get("title")))

        # generate toc key-word arguments
        keywords = {}
        for key in ("caption", "numbered", "titlesonly", "reversed"):
            if key in part:
                keywords[key] = part[key]
            elif key in defaults:
                keywords[key] = defaults[key]

        # TODO this is a hacky fix for the fact that sphinx logs a warning
        # for nested toctrees, see:
        # sphinx/environment/collectors/toctree.py::TocTreeCollector::assign_section_numbers::_walk_toctree
        if keywords.get("numbered") and path != "/":
            keywords.pop("numbered")

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
