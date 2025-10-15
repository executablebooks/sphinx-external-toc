from sphinx.environment.collectors.toctree import TocTreeCollector
import gc
from sphinx.util import logging
from sphinx import addnodes as sphinxnodes

logger = logging.getLogger(__name__)

def disable_builtin_toctree_collector(app):
    for obj in gc.get_objects():
        if not isinstance(obj, TocTreeCollector):
            continue
        # When running sphinx-autobuild, this function might be called multiple
        # times. When the collector is already disabled `listener_ids` will be
        # `None`, and thus we don't need to disable it again.
        #
        # Note that disabling an already disabled collector will fail.
        if obj.listener_ids is None:
            continue
        obj.disable(app)
        logger.warning("[FORKED] Disabled built-in TocTreeCollector")

class TocTreeCollectorWithStyles(TocTreeCollector):
    def __init__(self, *args, **kwargs):
        logger.warning("[FORKED] Enabling new TocTreeCollectorWithStyles")
        super().__init__(*args, **kwargs)

    def assign_section_numbers(self, env):
        # First, call the original assign_section_numbers to get the default behavior
        logger.warning("[FORKED] Calling original TocTreeCollector.assign_section_numbers")
        result = super().assign_section_numbers(env)

        # Then, add any additional processing for styles here
        logger.warning("[FORKED] Processing styles")
        for docname in env.numbered_toctrees:
            logger.warning(f"[FORKED] Processing docname: {docname}")
            doctree = env.get_doctree(docname)
            for toctree in doctree.findall(sphinxnodes.toctree):
                style = toctree.get("style", "numerical")
                if style != "numerical":
                    logger.warning(f"[FORKED] Found toctree with non-numerical style: {style}")

        return result