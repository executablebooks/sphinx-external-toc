from pathlib import Path
from typing import Optional

from docutils.nodes import document, compound as compound_node
from sphinx.addnodes import toctree as toctree_node
from sphinx.application import Sphinx
from sphinx.transforms import SphinxTransform
from sphinx.util.matching import Matcher

from .api import DocItem, SiteMap, UrlItem, parse_toc_file


def parse_toc_to_env(app: Sphinx) -> None:
    """Parse the external toc file and store it in the Sphinx environment."""
    # TODO convert exceptions to sphinx warnings (particularly MalformedError)
    site_map = parse_toc_file(Path(app.srcdir) / app.config["external_toc_path"])
    # TODO check if already external_site_map exists and compare to identify changed tocs/docs
    app.env.external_site_map = site_map
    # Update the master_doc to the root doc  # TODO warn if different?
    app.config["master_doc"] = site_map.root.docname


def append_toctrees(app: Sphinx, doctree: document) -> None:
    """Create the toctree nodes and add it to the document.

    Adapted from `sphinx/directives/other.py::TocTree`
    """
    site_map: SiteMap = app.env.external_site_map
    doc_item: Optional[DocItem] = site_map.get(app.env.docname)

    if doc_item is None or not doc_item.parts:
        return

    suffixes = app.config.source_suffix
    excluded = Matcher(app.config.exclude_patterns)

    for toctree in doc_item.parts:

        subnode = toctree_node()
        subnode["parent"] = app.env.docname
        subnode.source = doctree.source
        subnode["entries"] = []
        subnode["includefiles"] = []
        subnode["maxdepth"] = -1
        subnode["caption"] = toctree.caption
        subnode["glob"] = False
        subnode["hidden"] = True
        subnode["includehidden"] = False
        subnode["numbered"] = toctree.numbered
        subnode["titlesonly"] = toctree.titlesonly
        wrappernode = compound_node(classes=["toctree-wrapper"])
        wrappernode.append(subnode)

        node_list = []

        for entry in toctree.sections:

            if isinstance(entry, UrlItem):
                subnode["entries"].append((entry.title, entry.url))
                continue

            child_doc_item = site_map[entry]

            docname = child_doc_item.docname
            title = child_doc_item.title

            # remove any suffixes
            for suffix in suffixes:
                if docname.endswith(suffix):
                    docname = docname[: -len(suffix)]
                    break

            if docname not in app.env.found_docs:
                if excluded(app.env.doc2path(docname, None)):
                    message = (
                        f"toctree contains reference to excluded document {docname!r}"
                    )
                else:
                    message = f"toctree contains reference to nonexisting document {docname!r}"

                node_list.append(doctree.reporter.warning(message))
                app.env.note_reread()
            else:
                subnode["entries"].append((title, docname))
                subnode["includefiles"].append(docname)

        # reversing entries can be useful when globbing
        if toctree.reversed:
            subnode["entries"] = list(reversed(subnode["entries"]))
            subnode["includefiles"] = list(reversed(subnode["includefiles"]))

        node_list.append(wrappernode)

        # note here the toctree cannot not just be appended to the end of the document,
        # since `TocTreeCollector.process_doc` expects it in a section
        # TODO check if there is this is always ok
        doctree.children[-1].extend(node_list)


# other implementations that can eventually be deleted.


class _AppendToctrees(SphinxTransform):
    """This is not used and would be an alternate route,
    to using the 'doctree-read' event, via`app.add_transform(_AppendToctrees)`
    """

    default_priority = 100

    def apply(self, **kwargs) -> None:
        append_toctrees(self.app, self.document)


def _modify_source(app, docname, source):
    """This is not used, but would be the implementation if using:
    app.connect("source-read", _modify_source)
    """
    site_map = app.env.external_site_map
    doc_item = site_map.get(app.env.docname)

    if doc_item is None or not doc_item.parts:
        return

    for toctree in doc_item.parts:
        entries = "\n".join(
            entry for entry in toctree.sections if isinstance(entry, str)
        )
        source[0] += f"```{{toctree}}\n{entries}\n```\n"
