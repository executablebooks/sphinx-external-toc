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
        result = super().assign_section_numbers(env) # only needed to maintain functionality

        # Processing styles
        logger.warning("[FORKED] Processing styles")
        for docname in env.numbered_toctrees:
            logger.warning(f"[FORKED] Processing docname: {docname}")
            doctree = env.get_doctree(docname)
            for toctree in doctree.findall(sphinxnodes.toctree):
                style = toctree.get("style", "numerical")
                if style != "numerical":
                    logger.warning(f"[FORKED] Found toctree {toctree.get('caption','NAMELESS')} with non-numerical style {style}")
                    # convert the section numbers to the new style
                    for _, ref in toctree["entries"]:
                        logger.warning(f"[FORKED] Current section number: {env.titles[ref]['secnumber']}")
                        env.titles[ref]["secnumber"] = self.__renumber(env.titles[ref]["secnumber"],style)
                        logger.warning(f"[FORKED] New section number: {env.titles[ref]['secnumber']}")

        return result

    def __renumber(self, number,style):
        if not number or not style or style == "numerical":
            return number
        
        if not isinstance(style, str):
            style = style[0]  # if multiple styles are given, use only the first one, the other are used in another method
        # only convert the first number to the new style
        first = number[0]
        if style == "romanupper":
            number[0] = self.__to_roman(first).upper()
        elif style == "romanlower":
            number[0] = self.__to_roman(first).lower()
        else:
            pass

        return number
    
    def __to_roman(self, n):
        """Convert an integer to a Roman numeral."""
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syms = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ''
        i = 0
        while n > 0:
            for _ in range(n // val[i]):
                roman_num += syms[i]
                n -= val[i]
            i += 1
        return roman_num