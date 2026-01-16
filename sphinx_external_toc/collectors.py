import gc
import copy
from docutils import nodes
from sphinx import addnodes as sphinxnodes
from sphinx.environment.collectors.toctree import TocTreeCollector


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


class TocTreeCollectorWithStyles(TocTreeCollector):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__numerical_count = 0
        self.__romanupper_count = 0
        self.__romanlower_count = 0
        self.__alphaupper_count = 0
        self.__alphalower_count = 0

    def assign_section_numbers(self, env):
        # First, call the original assign_section_numbers to get the default behavior
        result = super().assign_section_numbers(env)  # needed to maintain functionality

        # store current titles for mapping
        env.titles_old = copy.deepcopy(env.titles)

        # Processing styles
        for docname in env.numbered_toctrees:
            doctree = env.get_doctree(docname)
            for toctree in doctree.findall(sphinxnodes.toctree):
                style = toctree.get("style", "numerical")
                if not isinstance(style, list):
                    style = [style]
                restart = toctree.get("restart_numbering", None)
                continuous = env.app.config.use_multitoc_numbering
                if restart is None:
                    restart = not continuous  # set default behavior
                if restart:
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
                    # Skip URLs and other refs that aren't documents
                    if ref not in env.titles:
                        continue
                    if "secnumber" in env.titles[ref]:
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
                        new_secnumber = self.__renumber(
                            env.titles[ref]["secnumber"], style
                        )
                        env.titles[ref]["secnumber"] = copy.deepcopy(new_secnumber)
                        if ref in env.tocs:
                            self.__replace_toc(env, ref, env.tocs[ref], style)

        # Extract old and new section numbers for mapping and store in toc_secnumbers
        for doc, title in env.titles_old.items():
            old_secnumber = title.get("secnumber", None)
            new_secnumber = env.titles[doc].get("secnumber", None)
            renumber_depth = len(new_secnumber) if new_secnumber else 0
            if old_secnumber == new_secnumber:
                continue  # skip unchanged
            # get sec_numbers for this doc
            doc_secnumbers = env.toc_secnumbers.get(doc, {})
            if doc_secnumbers:
                for anchor, secnumber in doc_secnumbers.items():
                    if secnumber is None:
                        continue  # no number, so skip
                    if secnumber[:renumber_depth] == new_secnumber:
                        continue  # skip already updated
                    if len(secnumber) == renumber_depth:
                        # same length, so probably same numbering depth, so compare one level up
                        if secnumber[:-1] == new_secnumber[:-1]:
                            continue  # skip already updated
                    # if this point is reached for any anchor,
                    # we need to update this anchors secnumber
                    # to the new secnumber for the overlapping part
                    update_secnumber = list(secnumber)  # make a copy
                    for i in range(renumber_depth):
                        if (
                            secnumber[i] == old_secnumber[i]
                        ):  # only if the old matches the current
                            update_secnumber[i] = new_secnumber[i]
                    env.toc_secnumbers[doc][anchor] = copy.deepcopy(update_secnumber)

        # now iterate over env.toc_secnumbers to ensure all secnumbers are updated
        # at the same time
        for docname in env.toc_secnumbers:
            # get the new and old secnumbers for this docname
            old_secnumber = env.titles_old.get(docname, {}).get("secnumber", None)
            new_secnumber = env.titles[docname].get("secnumber", None)
            renumber_depth = len(new_secnumber) if new_secnumber else 0
            # iterate over all anchors in this docname
            for anchorname, secnumber in env.toc_secnumbers[docname].items():
                if secnumber is None:
                    continue  # no number, so skip
                if secnumber[:renumber_depth] == new_secnumber:
                    continue  # skip already updated
                if len(secnumber) == renumber_depth:
                    # same length, so probably same numbering depth, so compare one level up
                    if secnumber[:-1] == new_secnumber[:-1]:
                        continue  # skip already updated
                # if this point is reached for any anchor, we need to update this anchors secnumber
                # to the new secnumber for the overlapping part
                update_secnumber = list(secnumber)  # make a copy
                for i in range(renumber_depth):
                    if (
                        secnumber[i] == old_secnumber[i]
                    ):  # only if the old matches the current
                        update_secnumber[i] = new_secnumber[i]
                env.toc_secnumbers[doc][anchor] = copy.deepcopy(update_secnumber)

        # Now, convert all secnumbers in toc_secnumbers to tuples
        # to avoid issues with other steps in the algorithm
        for docname in env.toc_secnumbers:
            for anchorname, secnumber in env.toc_secnumbers[docname].items():
                if not secnumber:
                    continue
                secnumber = (*secnumber,)  # convert to tuple
                env.toc_secnumbers[docname][anchorname] = copy.deepcopy(secnumber)
        return result

    def __renumber(self, number_set, style_set):
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
            if style_set[i] == "numerical" and isinstance(number_set[i], int):
                continue  # keep as is
            if isinstance(number_set[i], str):
                continue  # skip non-numeric values, assuming those are already converted
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
        val = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
        syms = [
            "M",
            "CM",
            "D",
            "CD",
            "C",
            "XC",
            "L",
            "XL",
            "X",
            "IX",
            "V",
            "IV",
            "I",
        ]
        roman_num = ""
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
            result = chr(n % 26 + ord("A")) + result
            n //= 26
        return result

    def __replace_toc(self, env, ref, node, style):
        if isinstance(node, nodes.reference):
            fixed_number = self.__renumber(node["secnumber"], style)
            node["secnumber"] = fixed_number
            env.toc_secnumbers[ref][node["anchorname"]] = fixed_number

        elif isinstance(node, sphinxnodes.toctree):
            self.__fix_nested_toc(env, node, style)

        else:
            for child in node.children:
                self.__replace_toc(env, ref, child, style)

    def __fix_nested_toc(self, env, toctree, style):
        for _, ref in toctree["entries"]:
            # Only process internal document references
            if ref not in env.titles:
                continue

            if "secnumber" not in env.titles[ref]:
                continue
            new_secnumber = self.__renumber(env.titles[ref]["secnumber"], style)
            env.titles[ref]["secnumber"] = copy.deepcopy(new_secnumber)
            if ref in env.tocs:
                self.__replace_toc(env, ref, env.tocs[ref], style)
