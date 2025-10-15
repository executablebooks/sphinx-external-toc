import copy
from sphinx.environment.collectors.toctree import TocTreeCollector
import gc
from sphinx.util import logging
from sphinx import addnodes as sphinxnodes
from docutils import nodes

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

        self.__numerical_count = 0
        self.__romanupper_count = 0
        self.__romanlower_count = 0
        self.__alphaupper_count = 0
        self.__alphalower_count = 0
        self.__map_old_to_new = {}

    def assign_section_numbers(self, env):
        # First, call the original assign_section_numbers to get the default behavior
        logger.warning("[FORKED] Calling original TocTreeCollector.assign_section_numbers")
        result = super().assign_section_numbers(env) # only needed to maintain functionality
        logger.warning(f"[FORKED] Original TocTreeCollector.assign_section_numbers done.\nResult:\n{result}\nSection numbers:\n{env.toc_secnumbers}")

        # Processing styles
        logger.warning("[FORKED] Processing styles")
        for docname in env.numbered_toctrees:
            logger.warning(f"[FORKED] Processing docname: {docname}")
            doctree = env.get_doctree(docname)
            for toctree in doctree.findall(sphinxnodes.toctree):
                style = toctree.get("style", "numerical")
                if not isinstance(style, list):
                    style = [style]
                restart = toctree.get("restart_numbering", False)
                if restart:
                    logger.warning(f"[FORKED] Restarting numbering for style {style}")
                    if style[0] == "numerical":
                        self.__numerical_count = 0
                    elif style[0] == "romanupper":
                        self.__romanupper_count = 0
                    elif style[0] == "romanlower":
                        self.__romanlower_count = 0
                    elif style[0] == "alphaupper":
                        self.__alphaupper_count = 0
                    elif style[0] == "alphalower":
                        self.__alphalower_count = 0
                # convert the section numbers to the new style
                for _, ref in toctree["entries"]:
                    if style[0] == "numerical":
                        self.__numerical_count += 1
                    if style[0] == "romanupper":
                        self.__romanupper_count += 1
                    elif style[0] == "romanlower":
                        self.__romanlower_count += 1
                    elif style[0] == "alphaupper":
                        self.__alphaupper_count += 1
                    elif style[0] == "alphalower":
                        self.__alphalower_count += 1
                    else:
                        pass
                    old_secnumber = copy.deepcopy(env.titles[ref]["secnumber"])
                    logger.warning(f"[FORKED] Old section number of {ref}: {old_secnumber}")
                    new_secnumber = self.__renumber(env.titles[ref]["secnumber"],style)
                    logger.warning(f"[FORKED] New section number of {ref}: {new_secnumber}")
                    env.titles[ref]["secnumber"] = copy.deepcopy(new_secnumber)
                    if ref in env.tocs:
                        self.__replace_toc(env, ref, env.tocs[ref],style)

                    # STORE IN THE MAP
                    if isinstance(old_secnumber, list):
                        old_secnumber = old_secnumber[0]
                    if isinstance(new_secnumber, list):
                        new_secnumber = new_secnumber[0]
                    self.__map_old_to_new[old_secnumber] = new_secnumber

        logger.warning(f"[FORKED] Final map:\n{self.__map_old_to_new}")
        # Now, replace the section numbers in env.toc_secnumbers
        for docname in env.toc_secnumbers:
            logger.warning(f"[FORKED] Old section numbers in {docname}: {env.toc_secnumbers[docname]}")
            for anchorname, secnumber in env.toc_secnumbers[docname].items():
                logger.warning(f"[FORKED] Old secnumber: {secnumber}")
                first_number = secnumber[0]
                secnumber = (self.__map_old_to_new.get(first_number, first_number), *secnumber[1:])
                logger.warning(f"[FORKED] New secnumber: {secnumber}")
                env.toc_secnumbers[docname][anchorname] = copy.deepcopy(secnumber)
            logger.warning(f"[FORKED] New section numbers in {docname}: {env.toc_secnumbers[docname]}")


        return result

    def __renumber(self, number_set,style_set):
        if not number_set or not style_set:
            return number_set

        if not isinstance(style_set, list):
            style_set = [style_set]  # if not multiple styles are given, convert to list
        # for each style, convert the corresponding number, where only the first number 
        # is rebased, the rest are kept as is, but converted.
        # convert the first number to the new style
        if style_set[0] == "numerical":
            number_set[0] = self.__numerical_count
        if style_set[0] == "romanupper":
            number_set[0] = self.__to_roman(self.__romanupper_count).upper()
        elif style_set[0] == "romanlower":
            number_set[0] = self.__to_roman(self.__romanlower_count).lower()
        elif style_set[0] == "alphaupper":
            number_set[0] = self.__to_alpha(self.__alphaupper_count).upper()
        elif style_set[0] == "alphalower":
            number_set[0] = self.__to_alpha(self.__alphalower_count).lower()
        else:
            pass
        # convert the rest of the numbers to the corresponding styles
        for i in range(1, min(len(number_set), len(style_set))):
            if style_set[i] == "numerical":
                continue  # keep as is
            if style_set[i] == "romanupper":
                number_set[i] = self.__to_roman(int(number_set[i])).upper()
            elif style_set[i] == "romanlower":
                number_set[i] = self.__to_roman(int(number_set[i])).lower()
            elif style_set[i] == "alphaupper":
                number_set[i] = self.__to_alpha(int(number_set[i])).upper()
            elif style_set[i] == "alphalower":
                number_set[i] = self.__to_alpha(int(number_set[i])).lower()
            else:
                pass

        return number_set
    
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
    
    def __to_alpha(self, n):
        """Convert an integer to an alphabetical representation (A, B, ..., Z, AA, AB, ...)."""
        result = ""
        while n > 0:
            n -= 1
            result = chr(n % 26 + ord('A')) + result
            n //= 26
        return result
    
    def __replace_toc(self, env, ref, node,style):
        if isinstance(node, nodes.reference):
            fixed_number = self.__renumber(node["secnumber"],style)
            node["secnumber"] = fixed_number
            env.toc_secnumbers[ref][node["anchorname"]] = fixed_number

        elif isinstance(node, sphinxnodes.toctree):
            logger.warning(f"[FORKED] Found nested toctree in {ref}:\n{node.pformat()}")
            self.__fix_nested_toc(env, node, style)

        else:
            for child in node.children:
                logger.warning(f"[FORKED] Recursing into child of {type(node)}")
                self.__replace_toc(env, ref, child,style)

    def __fix_nested_toc(self, env, toctree, style):
        for _, ref in toctree["entries"]:
            old_secnumber = copy.deepcopy(env.titles[ref]["secnumber"])
            logger.warning(f"[FORKED-NESTED] Old section number of {ref}: {old_secnumber}")
            new_secnumber = self.__renumber(env.titles[ref]["secnumber"],style)
            logger.warning(f"[FORKED-NESTED] New section number of {ref}: {new_secnumber}")
            env.titles[ref]["secnumber"] = copy.deepcopy(new_secnumber)
            if ref in env.tocs:
                self.__replace_toc(env, ref, env.tocs[ref],style)