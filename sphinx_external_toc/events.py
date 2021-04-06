"""Sphinx event functions."""
from pathlib import Path
from typing import List, Optional, Set

from docutils import nodes
from sphinx.addnodes import toctree as toctree_node
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.errors import ExtensionError
from sphinx.util import docname_join, logging
from sphinx.util.matching import Matcher, patfilter

from .api import DocItem, GlobItem, RefItem, SiteMap, UrlItem, parse_toc_file

logger = logging.getLogger(__name__)


def create_warning(
    app: Sphinx,
    doctree: nodes.document,
    category: str,
    message: str,
    *,
    line: Optional[int] = None,
    append_to: Optional[nodes.Element] = None,
    wtype: str = "etoc",
) -> Optional[nodes.system_message]:
    """Generate a warning, logging it if necessary.

    If the warning type is listed in the ``suppress_warnings`` configuration,
    then ``None`` will be returned and no warning logged.
    """
    message = f"{message} [{wtype}.{category}]"
    kwargs = {"line": line} if line is not None else {}

    if not logging.is_suppressed_warning(wtype, category, app.config.suppress_warnings):
        msg_node = doctree.reporter.warning(message, **kwargs)
        if append_to is not None:
            append_to.append(msg_node)
        return msg_node
    return None


def parse_toc_to_env(app: Sphinx, config: Config) -> None:
    """Parse the external toc file and store it in the Sphinx environment."""
    try:
        site_map = parse_toc_file(Path(app.srcdir) / app.config["external_toc_path"])
    except Exception as exc:
        raise ExtensionError(f"External ToC: {exc}") from exc
    config.external_site_map = site_map
    # Update the master_doc to the root doc of the site map
    if config["master_doc"] != site_map.root.docname:
        logger.info("External ToC: Changing master_doc to '%s'", site_map.root.docname)
    config["master_doc"] = site_map.root.docname


def add_changed_toctrees(
    app: Sphinx,
    env: BuildEnvironment,
    added: Set[str],
    changed: Set[str],
    removed: Set[str],
) -> Set[str]:
    """Add docs with new or changed toctrees to changed list."""
    previous_map = getattr(app.env, "external_site_map", None)
    # move external_site_map from config to env
    app.env.external_site_map = site_map = app.config.external_site_map
    # Compare to previous map, to record docnames with new or changed toctrees
    changed_docs = set()
    if previous_map:
        for docname in site_map:
            if (
                docname not in previous_map
                or site_map[docname] != previous_map[docname]
            ):
                changed_docs.add(docname)
    return changed_docs


def append_toctrees(app: Sphinx, doctree: nodes.document) -> None:
    """Create the toctree nodes and add it to the document.

    Adapted from `sphinx/directives/other.py::TocTree`
    """
    # check for existing toctrees and raise warning
    for node in doctree.traverse(toctree_node):
        create_warning(
            app,
            doctree,
            "toctree",
            "toctree directive not expected with external-toc",
            line=node.line,
        )

    site_map: SiteMap = app.env.external_site_map
    doc_item: Optional[DocItem] = site_map.get(app.env.docname)

    if doc_item is None or not doc_item.parts:
        return

    # initial variables
    suffixes = app.config.source_suffix
    all_docnames = app.env.found_docs.copy()
    all_docnames.remove(app.env.docname)  # remove current document
    excluded = Matcher(app.config.exclude_patterns)

    for toctree in doc_item.parts:

        subnode = toctree_node()
        subnode["parent"] = app.env.docname
        subnode.source = doctree.source
        subnode["entries"] = []
        subnode["includefiles"] = []
        subnode["maxdepth"] = -1
        subnode["caption"] = toctree.caption
        # TODO this wasn't in the original code,
        # but alabaster theme intermittently raised `KeyError('rawcaption')`
        subnode["rawcaption"] = toctree.caption or ""
        subnode["glob"] = any(isinstance(entry, GlobItem) for entry in toctree.sections)
        subnode["hidden"] = True
        subnode["includehidden"] = False
        subnode["numbered"] = toctree.numbered
        subnode["titlesonly"] = toctree.titlesonly
        wrappernode = nodes.compound(classes=["toctree-wrapper"])
        wrappernode.append(subnode)

        node_list: List[nodes.Element] = []

        for entry in toctree.sections:

            if isinstance(entry, UrlItem):

                subnode["entries"].append((entry.title, entry.url))

            elif isinstance(entry, RefItem):

                child_doc_item = site_map[entry]
                docname = docname_join(app.env.docname, str(entry))
                title = child_doc_item.title

                # remove any suffixes
                for suffix in suffixes:
                    if docname.endswith(suffix):
                        docname = docname[: -len(suffix)]
                        break

                if docname not in app.env.found_docs:
                    if excluded(app.env.doc2path(docname, None)):
                        message = f"toctree contains reference to excluded document {docname!r}"
                    else:
                        message = f"toctree contains reference to nonexisting document {docname!r}"

                    create_warning(app, doctree, "ref", message, append_to=node_list)
                    app.env.note_reread()
                else:
                    subnode["entries"].append((title, docname))
                    subnode["includefiles"].append(docname)

            elif isinstance(entry, GlobItem):
                patname = docname_join(app.env.docname, str(entry))
                docnames = sorted(patfilter(all_docnames, patname))
                for docname in docnames:
                    all_docnames.remove(docname)  # don't include it again
                    subnode["entries"].append((None, docname))
                    subnode["includefiles"].append(docname)
                if not docnames:
                    message = (
                        f"toctree glob pattern '{entry}' didn't match any documents"
                    )
                    create_warning(app, doctree, "glob", message, append_to=node_list)

        # reversing entries can be useful when globbing
        if toctree.reversed:
            subnode["entries"] = list(reversed(subnode["entries"]))
            subnode["includefiles"] = list(reversed(subnode["includefiles"]))

        node_list.append(wrappernode)

        # note here the toctree cannot not just be appended to the end of the document,
        # since `TocTreeCollector.process_doc` expects it in a section
        # TODO check if there is this is always ok
        doctree.children[-1].extend(node_list)
