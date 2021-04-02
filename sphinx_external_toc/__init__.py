"""A sphinx extension that allows the site toctree to be defined in a single file."""

__version__ = "0.0.1"


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def setup(app: "Sphinx") -> dict:
    """Initialize the Sphinx extension."""
    from .events import append_toctrees, parse_toc_to_env

    app.add_config_value("external_toc_path", "_toc.yml", "env")
    app.connect("builder-inited", parse_toc_to_env)
    # TODO add docs with changed toctrees to changed in event.env-get-outdated
    # Note, this needs to occur before `TocTreeCollector.process_doc` (default priority 500)
    app.connect("doctree-read", append_toctrees, priority=100)

    return {"version": __version__, "parallel_read_safe": True}
