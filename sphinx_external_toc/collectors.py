from sphinx.environment.collectors.toctree import TocTreeCollector
from docutils.nodes import toctree, Node
import gc
from sphinx.util import logging

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

    def process_doc(self, app, doctree: Node):
        # First, call the original process_doc to get the default behavior
        logger.warning("[FORKED] Calling original TocTreeCollector.process_doc")
        super().process_doc(app, doctree)

        # Then, add any additional processing for styles here
        logger.warning("[FORKED] Processing styles")