"""A sphinx extension that allows the project toctree to be defined in a single file."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sphinx.application import Sphinx

__version__ = "1.1.0"


def setup(app: "Sphinx") -> dict:
    app.setup_extension("sphinx_multitoc_numbering")

    """Initialize the Sphinx extension."""
    from .collectors import (
        TocTreeCollectorWithStyles,
        disable_builtin_toctree_collector,
    )
    from .events import (
        InsertToctrees,
        TableofContents,
        add_changed_toctrees,
        ensure_index_file,
        parse_toc_to_env,
    )

    # collectors
    disable_builtin_toctree_collector(app)
    app.add_env_collector(TocTreeCollectorWithStyles)

    # variables
    app.add_config_value("external_toc_path", "_toc.yml", "env")
    app.add_config_value("external_toc_exclude_missing", False, "env")

    # Register use_multitoc_numbering if not already registered (e.g., by JupyterBook)
    try:
        app.add_config_value("use_multitoc_numbering", True, "env")
    except Exception:
        # Already registered, likely by JupyterBook
        pass

    # Note: this needs to occur after merge_source_suffix event (priority 800)
    # this cannot be a builder-inited event, since if we change the master_doc
    # it will always mark the config as changed in the env setup and re-build everything
    app.connect("config-inited", parse_toc_to_env, priority=900)
    app.connect("env-get-outdated", add_changed_toctrees)
    app.add_directive("tableofcontents", TableofContents)
    app.add_transform(InsertToctrees)
    app.connect("build-finished", ensure_index_file)

    return {"version": __version__, "parallel_read_safe": True}
