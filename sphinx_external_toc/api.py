"""Defines the `SiteMap` object, for storing the parsed ToC."""
from collections.abc import MutableMapping
from typing import Any, Dict, Iterator, List, Optional, Set, Union

import attr
from attr.validators import deep_iterable, instance_of, optional


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
    caption: Optional[str] = attr.ib(
        None, kw_only=True, validator=optional(instance_of(str))
    )
    hidden: bool = attr.ib(True, kw_only=True, validator=instance_of(bool))
    maxdepth: int = attr.ib(-1, kw_only=True, validator=instance_of(int))
    numbered: Union[bool, int] = attr.ib(
        False, kw_only=True, validator=instance_of((bool, int))
    )
    reversed: bool = attr.ib(False, kw_only=True, validator=instance_of(bool))
    titlesonly: bool = attr.ib(True, kw_only=True, validator=instance_of(bool))

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
