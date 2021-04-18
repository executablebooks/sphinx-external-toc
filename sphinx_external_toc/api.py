"""Defines the `SiteMap` object, for storing the parsed ToC."""
from collections.abc import MutableMapping
from typing import Any, Dict, Iterator, List, Optional, Set, Union

import attr
from attr.validators import deep_iterable, instance_of, matches_re, optional


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

    # regex should match sphinx.util.url_re
    url: str = attr.ib(validator=[instance_of(str), matches_re(r".+://.*")])
    title: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))


@attr.s(slots=True)
class TocTree:
    """An individual toctree within a document."""

    # TODO validate uniqueness of docnames (at least one item)
    items: List[Union[GlobItem, FileItem, UrlItem]] = attr.ib(
        validator=deep_iterable(
            instance_of((GlobItem, FileItem, UrlItem)), instance_of(list)
        )
    )
    caption: Optional[str] = attr.ib(
        None, kw_only=True, validator=optional(instance_of(str))
    )
    hidden: bool = attr.ib(True, kw_only=True, validator=instance_of(bool))
    maxdepth: int = attr.ib(-1, kw_only=True, validator=instance_of(int))
    numbered: Union[bool, int] = attr.ib(
        False, kw_only=True, validator=instance_of((bool, int))
    )
    reversed: bool = attr.ib(False, kw_only=True, validator=instance_of(bool))
    titlesonly: bool = attr.ib(False, kw_only=True, validator=instance_of(bool))

    def files(self) -> List[str]:
        return [str(item) for item in self.items if isinstance(item, FileItem)]

    def globs(self) -> List[str]:
        return [str(item) for item in self.items if isinstance(item, GlobItem)]


@attr.s(slots=True)
class Document:
    """A document in the site map."""

    docname: str = attr.ib(validator=instance_of(str))
    title: Optional[str] = attr.ib(None, validator=optional(instance_of(str)))
    # TODO validate uniqueness of docnames across all parts (and none should be the docname)
    subtrees: List[TocTree] = attr.ib(
        factory=list, validator=deep_iterable(instance_of(TocTree), instance_of(list))
    )

    def child_files(self) -> List[str]:
        """Return all children files."""
        return [name for tree in self.subtrees for name in tree.files()]

    def child_globs(self) -> List[str]:
        """Return all children globs."""
        return [name for tree in self.subtrees for name in tree.globs()]


class SiteMap(MutableMapping):
    """A mapping of documents to their toctrees (or None if terminal)."""

    def __init__(
        self,
        root: Document,
        meta: Optional[Dict[str, Any]] = None,
        file_format: Optional[str] = None,
    ) -> None:
        self._docs: Dict[str, Document] = {}
        self[root.docname] = root
        self._root: Document = root
        self._meta: Dict[str, Any] = meta or {}
        self._file_format = file_format

    @property
    def root(self) -> Document:
        """Return the root document."""
        return self._root

    @property
    def meta(self) -> Dict[str, Any]:
        """Return the site-map metadata."""
        return self._meta

    @property
    def file_format(self) -> Optional[str]:
        """Return the format of the file to write to."""
        return self._file_format

    @file_format.setter
    def file_format(self, value: Optional[str]) -> None:
        """Set the format of the file to write to."""
        self._file_format = value

    def globs(self) -> Set[str]:
        """Return set of all globs present across all toctrees."""
        return {glob for item in self._docs.values() for glob in item.child_globs()}

    def __getitem__(self, docname: str) -> Document:
        return self._docs[docname]

    def __setitem__(self, docname: str, item: Document) -> None:
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

    def as_json(self) -> Dict[str, Any]:
        """Return JSON serialized site-map representation."""
        doc_dict = {
            k: attr.asdict(self._docs[k], value_serializer=self._serializer)
            if self._docs[k]
            else self._docs[k]
            for k in sorted(self._docs)
        }
        data = {"root": self.root.docname, "documents": doc_dict, "meta": self.meta}
        if self.file_format:
            data["file_format"] = self.file_format
        return data
