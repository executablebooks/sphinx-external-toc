import pytest
from unittest.mock import Mock, patch
from sphinx_external_toc.collectors import (
    TocTreeCollectorWithStyles,
    disable_builtin_toctree_collector,
)
from sphinx.environment.collectors.toctree import TocTreeCollector


class TestDisableBuiltinToctreeCollector:
    def test_disable_collector_when_enabled(self):
        """Test disabling an enabled collector."""
        mock_app = Mock()
        from sphinx.environment.collectors.toctree import TocTreeCollector

        mock_collector = Mock(spec=TocTreeCollector)
        mock_collector.listener_ids = ["id1", "id2"]

        with patch(
            "sphinx_external_toc.collectors.gc.get_objects",
            return_value=[mock_collector],
        ):
            disable_builtin_toctree_collector(mock_app)
            mock_collector.disable.assert_called_once_with(mock_app)

    def test_skip_disable_when_already_disabled(self):
        """Test that already disabled collectors are skipped."""
        mock_app = Mock()
        from sphinx.environment.collectors.toctree import TocTreeCollector

        mock_collector = Mock(spec=TocTreeCollector)
        mock_collector.listener_ids = None

        with patch(
            "sphinx_external_toc.collectors.gc.get_objects",
            return_value=[mock_collector],
        ):
            disable_builtin_toctree_collector(mock_app)
            mock_collector.disable.assert_not_called()

    def test_skip_non_toctree_collectors(self):
        """Test that non-TocTreeCollector objects are skipped."""
        mock_app = Mock()

        with patch(
            "sphinx_external_toc.collectors.gc.get_objects",
            return_value=["not a collector", 123],
        ):
            disable_builtin_toctree_collector(mock_app)
            # Should not raise any errors


class TestTocTreeCollectorWithStyles:
    @pytest.fixture
    def collector(self):
        return TocTreeCollectorWithStyles()

    def test_to_roman_basic(self, collector):
        """Test Roman numeral conversion."""
        assert collector._TocTreeCollectorWithStyles__to_roman(1) == "I"
        assert collector._TocTreeCollectorWithStyles__to_roman(4) == "IV"
        assert collector._TocTreeCollectorWithStyles__to_roman(9) == "IX"
        assert collector._TocTreeCollectorWithStyles__to_roman(27) == "XXVII"
        assert collector._TocTreeCollectorWithStyles__to_roman(1994) == "MCMXCIV"

    def test_to_roman_edge_cases(self, collector):
        """Test Roman numeral edge cases."""
        assert collector._TocTreeCollectorWithStyles__to_roman(0) == ""
        assert collector._TocTreeCollectorWithStyles__to_roman(3999) == "MMMCMXCIX"
        assert collector._TocTreeCollectorWithStyles__to_roman(58) == "LVIII"

    def test_to_alpha_basic(self, collector):
        """Test alphabetical conversion."""
        assert collector._TocTreeCollectorWithStyles__to_alpha(1) == "A"
        assert collector._TocTreeCollectorWithStyles__to_alpha(26) == "Z"
        assert collector._TocTreeCollectorWithStyles__to_alpha(27) == "AA"
        assert collector._TocTreeCollectorWithStyles__to_alpha(52) == "AZ"

    def test_to_alpha_edge_cases(self, collector):
        """Test alphabetical conversion edge cases."""
        assert collector._TocTreeCollectorWithStyles__to_alpha(0) == ""
        assert collector._TocTreeCollectorWithStyles__to_alpha(702) == "ZZ"
        assert collector._TocTreeCollectorWithStyles__to_alpha(703) == "AAA"

    def test_renumber_numerical(self, collector):
        """Test renumbering with numerical style."""
        collector._TocTreeCollectorWithStyles__numerical_count = 5
        result = collector._TocTreeCollectorWithStyles__renumber(
            [1, 2, 3], ["numerical"]
        )
        assert result[0] == 5

    def test_renumber_romanupper(self, collector):
        """Test renumbering with Roman uppercase style."""
        collector._TocTreeCollectorWithStyles__romanupper_count = 3
        result = collector._TocTreeCollectorWithStyles__renumber([1, 2], ["romanupper"])
        assert result[0] == "III"

    def test_renumber_romanlower(self, collector):
        """Test renumbering with Roman lowercase style."""
        collector._TocTreeCollectorWithStyles__romanlower_count = 4
        result = collector._TocTreeCollectorWithStyles__renumber([1, 2], ["romanlower"])
        assert result[0] == "iv"

    def test_renumber_alphaupper(self, collector):
        """Test renumbering with alpha uppercase style."""
        collector._TocTreeCollectorWithStyles__alphaupper_count = 1
        result = collector._TocTreeCollectorWithStyles__renumber([1], ["alphaupper"])
        assert result[0] == "A"

    def test_renumber_alphalower(self, collector):
        """Test renumbering with alpha lowercase style."""
        collector._TocTreeCollectorWithStyles__alphalower_count = 2
        result = collector._TocTreeCollectorWithStyles__renumber([1], ["alphalower"])
        assert result[0] == "b"

    def test_renumber_empty_input(self, collector):
        """Test renumbering with empty inputs."""
        assert collector._TocTreeCollectorWithStyles__renumber([], []) == []
        assert collector._TocTreeCollectorWithStyles__renumber(None, None) is None

    def test_renumber_mixed_styles(self, collector):
        """Test renumbering with multiple styles."""
        collector._TocTreeCollectorWithStyles__numerical_count = 2
        collector._TocTreeCollectorWithStyles__romanupper_count = 5
        result = collector._TocTreeCollectorWithStyles__renumber(
            [1, 5, 10], ["numerical", "romanupper", "numerical"]
        )
        assert result[0] == 2
        assert result[1] == "V"
        assert result[2] == 10

    def test_renumber_converts_string_numbers(self, collector):
        """Test that string numbers are skipped."""
        collector._TocTreeCollectorWithStyles__numerical_count = 1
        result = collector._TocTreeCollectorWithStyles__renumber(
            [1, "ii", 3], ["numerical", "numerical"]
        )
        assert result[0] == 1
        assert result[1] == "ii"  # kept as-is

    def test_renumber_non_list_style(self, collector):
        """Test renumbering with non-list style."""
        collector._TocTreeCollectorWithStyles__numerical_count = 5
        result = collector._TocTreeCollectorWithStyles__renumber([1, 2], "numerical")
        assert result[0] == 5

    def test_init_counters(self, collector):
        """Test that counters are initialized correctly."""
        assert collector._TocTreeCollectorWithStyles__numerical_count == 0
        assert collector._TocTreeCollectorWithStyles__romanupper_count == 0
        assert collector._TocTreeCollectorWithStyles__romanlower_count == 0
        assert collector._TocTreeCollectorWithStyles__alphaupper_count == 0
        assert collector._TocTreeCollectorWithStyles__alphalower_count == 0

    def test_assign_section_numbers_basic(self, collector):
        """Test assign_section_numbers with mocked environment."""
        mock_env = Mock()
        mock_env.numbered_toctrees = {}
        mock_env.titles = {}
        mock_env.titles_old = {}
        mock_env.toc_secnumbers = {}
        mock_env.get_doctree = Mock(return_value=Mock(findall=Mock(return_value=[])))
        mock_env.tocs = {}

        with patch(
            "sphinx_external_toc.collectors.TocTreeCollector.assign_section_numbers",
            return_value=None,
        ):
            result = collector.assign_section_numbers(mock_env)
            assert result is None

    def test_assign_section_numbers_with_numbered_toctrees(self, collector):
        """Test assign_section_numbers with actual numbered toctrees."""
        from docutils import nodes

        mock_env = Mock()
        mock_env.numbered_toctrees = {"doc1": ["numerical"]}
        mock_env.titles = {"doc1": nodes.title(text="Title")}
        mock_env.titles_old = {}
        mock_env.toc_secnumbers = {}
        mock_env.tocs = {"doc1": nodes.bullet_list()}
        mock_env.app = Mock()
        mock_env.app.config = Mock()
        mock_env.app.config.use_multitoc_numbering = False

        mock_doctree = Mock()
        mock_toctree = Mock()
        mock_toctree.get = Mock(
            side_effect=lambda key, default=None: {
                "style": "numerical",
                "restart_numbering": True,
            }.get(key, default)
        )
        mock_toctree.__getitem__ = Mock(return_value=[("", "doc1")])  # Mock entries
        mock_toctree.traverse = Mock(return_value=[])
        mock_doctree.findall = Mock(return_value=[mock_toctree])
        mock_env.get_doctree = Mock(return_value=mock_doctree)

        with patch.object(
            TocTreeCollector, "assign_section_numbers", return_value=None
        ):
            collector.assign_section_numbers(mock_env)
            assert "doc1" in mock_env.titles_old

    def test_assign_section_numbers_preserves_old_titles(self, collector):
        """Test that assign_section_numbers preserves old titles."""
        from docutils import nodes

        mock_env = Mock()
        mock_env.numbered_toctrees = {}
        mock_env.titles = {"doc1": nodes.title(text="Old")}
        mock_env.titles_old = {}
        mock_env.toc_secnumbers = {}
        mock_env.tocs = {}
        mock_env.get_doctree = Mock(return_value=Mock(findall=Mock(return_value=[])))

        with patch.object(
            TocTreeCollector, "assign_section_numbers", return_value=None
        ):
            collector.assign_section_numbers(mock_env)
            assert "doc1" in mock_env.titles_old

    def test_replace_toc_updates_secnumber(self, collector):
        """Test that __replace_toc updates section numbers correctly."""
        from docutils import nodes

        mock_env = Mock()
        ref = "test_doc"
        collector._TocTreeCollectorWithStyles__numerical_count = 10

        ref_node = nodes.reference()
        ref_node["secnumber"] = [5, 2]
        ref_node["anchorname"] = "section"

        mock_env.toc_secnumbers = {ref: {"section": [5, 2]}}

        collector._TocTreeCollectorWithStyles__replace_toc(
            mock_env, ref, ref_node, ["numerical"]
        )

        # First number should be replaced with count
        assert ref_node["secnumber"][0] == 10

    def test_replace_toc_with_multiple_references(self, collector):
        """Test __replace_toc with multiple reference nodes."""
        from docutils import nodes

        mock_env = Mock()
        ref = "test_doc"
        collector._TocTreeCollectorWithStyles__numerical_count = 3

        # Create multiple reference nodes
        ref_nodes = [nodes.reference() for _ in range(3)]
        for i, node in enumerate(ref_nodes):
            node["secnumber"] = [i + 1]
            node["anchorname"] = f"section{i}"
            mock_env.toc_secnumbers = {ref: {f"section{i}": [i + 1]}}

            collector._TocTreeCollectorWithStyles__replace_toc(
                mock_env, ref, node, ["numerical"]
            )
            assert node["secnumber"][0] == 3

    def test_fix_nested_toc_with_nested_structure(self, collector):
        """Test __fix_nested_toc with nested TOC structure."""
        from docutils import nodes

        mock_env = Mock()
        nested_list = nodes.bullet_list()
        nested_item = nodes.list_item()
        nested_list += nested_item

        toctree = Mock()
        toctree.children = [nested_list]
        toctree.__getitem__ = Mock(return_value=[])  # Mock the ["entries"] access

        collector._TocTreeCollectorWithStyles__alphalower_count = 1
        collector._TocTreeCollectorWithStyles__fix_nested_toc(
            mock_env, toctree, ["alphalower"]
        )

    def test_fix_nested_toc_empty_toctree(self, collector):
        """Test __fix_nested_toc with empty toctree."""
        mock_env = Mock()
        toctree = Mock()
        toctree.children = []
        toctree.__getitem__ = Mock(return_value=[])  # Mock the ["entries"] access

        # Should not raise any errors
        collector._TocTreeCollectorWithStyles__fix_nested_toc(
            mock_env, toctree, ["numerical"]
        )

    def test_renumber_all_styles(self, collector):
        """Test renumbering with all available styles."""
        styles = [
            ("numerical", 5, 5),
            ("romanupper", 3, "III"),
            ("romanlower", 4, "iv"),
            ("alphaupper", 2, "B"),
            ("alphalower", 1, "a"),
        ]

        for style_name, count, expected in styles:
            collector = TocTreeCollectorWithStyles()  # Reset counters
            attr_name = f"_{TocTreeCollectorWithStyles.__name__}__{style_name}_count"
            setattr(collector, attr_name, count)

            result = collector._TocTreeCollectorWithStyles__renumber(
                [1, 2, 3], [style_name]
            )
            assert result[0] == expected, f"Failed for style {style_name}"

    def test_renumber_preserves_remaining_numbers(self, collector):
        """Test that renumber preserves numbers after first."""
        collector._TocTreeCollectorWithStyles__numerical_count = 10
        result = collector._TocTreeCollectorWithStyles__renumber(
            [1, 2, 3, 4], ["numerical", "numerical", "numerical", "numerical"]
        )
        assert result[0] == 10
        assert result[1] == 2
        assert result[2] == 3
        assert result[3] == 4

    def test_to_roman_comprehensive(self, collector):
        """Test Roman numeral conversion comprehensively."""
        test_cases = [
            (1, "I"),
            (2, "II"),
            (3, "III"),
            (5, "V"),
            (10, "X"),
            (15, "XV"),
            (40, "XL"),
            (50, "L"),
            (90, "XC"),
            (100, "C"),
            (400, "CD"),
            (500, "D"),
            (900, "CM"),
            (1000, "M"),
        ]
        for num, expected in test_cases:
            result = collector._TocTreeCollectorWithStyles__to_roman(num)
            assert (
                result == expected
            ), f"Failed for {num}: got {result}, expected {expected}"

    def test_to_alpha_comprehensive(self, collector):
        """Test alphabetical conversion comprehensively."""
        test_cases = [
            (1, "A"),
            (2, "B"),
            (25, "Y"),
            (26, "Z"),
            (27, "AA"),
            (28, "AB"),
            (51, "AY"),
            (52, "AZ"),
            (53, "BA"),
            (702, "ZZ"),
            (703, "AAA"),
        ]
        for num, expected in test_cases:
            result = collector._TocTreeCollectorWithStyles__to_alpha(num)
            assert (
                result == expected
            ), f"Failed for {num}: got {result}, expected {expected}"

    def test_disable_builtin_multiple_collectors(self):
        """Test disabling with multiple collectors in memory."""
        from sphinx.environment.collectors.toctree import TocTreeCollector

        mock_app = Mock()
        mock_collector1 = Mock(spec=TocTreeCollector)
        mock_collector1.listener_ids = ["id1"]
        mock_collector2 = Mock(spec=TocTreeCollector)
        mock_collector2.listener_ids = None

        with patch(
            "sphinx_external_toc.collectors.gc.get_objects",
            return_value=[mock_collector1, mock_collector2, "other"],
        ):
            disable_builtin_toctree_collector(mock_app)
            mock_collector1.disable.assert_called_once_with(mock_app)
            mock_collector2.disable.assert_not_called()

    def test_assign_section_numbers_with_all_styles(self, collector):
        """Test assign_section_numbers with different numbering styles."""
        from docutils import nodes
        from sphinx import addnodes as sphinxnodes

        for style in [
            "numerical",
            "romanupper",
            "romanlower",
            "alphaupper",
            "alphalower",
        ]:
            mock_env = Mock()
            mock_env.numbered_toctrees = {"doc1": [style]}
            mock_env.titles = {"doc1": nodes.title(text="Title")}
            mock_env.titles_old = {}
            mock_env.toc_secnumbers = {"doc1": {}}
            mock_env.app = Mock()
            mock_env.app.config = Mock()
            mock_env.app.config.use_multitoc_numbering = False

            mock_doctree = Mock()
            mock_toctree = Mock(spec=sphinxnodes.toctree)
            mock_toctree.get = Mock(
                side_effect=lambda key, default=None: {
                    "style": style,
                    "restart_numbering": True,
                }.get(key, default)
            )
            mock_toctree.__getitem__ = Mock(return_value=[("", "doc1")])
            mock_toctree.traverse = Mock(return_value=[])
            mock_doctree.findall = Mock(return_value=[mock_toctree])
            mock_env.get_doctree = Mock(return_value=mock_doctree)

            with patch.object(
                TocTreeCollector, "assign_section_numbers", return_value=None
            ):
                collector.assign_section_numbers(mock_env)
                assert "doc1" in mock_env.titles_old

    def test_assign_section_numbers_toc_secnumbers_processing(self, collector):
        """Test that toc_secnumbers are properly processed."""
        from sphinx import addnodes as sphinxnodes

        mock_env = Mock()
        mock_env.numbered_toctrees = {"doc1": ["numerical"]}
        mock_env.titles = {"doc1": {"secnumber": [1]}}
        mock_env.titles_old = {"doc1": {"secnumber": [1]}}
        mock_env.toc_secnumbers = {"doc1": {"anchor": [1]}}
        mock_env.app = Mock()
        mock_env.app.config = Mock()
        mock_env.app.config.use_multitoc_numbering = False

        mock_doctree = Mock()
        mock_toctree = Mock(spec=sphinxnodes.toctree)
        mock_toctree.get = Mock(
            side_effect=lambda key, default=None: {
                "style": "numerical",
                "restart_numbering": False,
            }.get(key, default)
        )
        mock_toctree.__getitem__ = Mock(return_value=[])
        mock_toctree.traverse = Mock(return_value=[])
        mock_doctree.findall = Mock(return_value=[mock_toctree])
        mock_env.get_doctree = Mock(return_value=mock_doctree)

        with patch.object(
            TocTreeCollector, "assign_section_numbers", return_value=None
        ):
            collector.assign_section_numbers(mock_env)
            assert "doc1" in mock_env.toc_secnumbers

    def test_renumber_style_romanupper(self, collector):
        """Test renumber with romanupper counter."""
        collector._TocTreeCollectorWithStyles__romanupper_count = 2
        result = collector._TocTreeCollectorWithStyles__renumber([1], ["romanupper"])
        assert result[0] == "II"
        # Note: __renumber doesn't increment counter, just uses current value

    def test_renumber_style_romanlower(self, collector):
        """Test renumber with romanlower counter."""
        collector._TocTreeCollectorWithStyles__romanlower_count = 5
        result = collector._TocTreeCollectorWithStyles__renumber([1], ["romanlower"])
        assert result[0] == "v"

    def test_renumber_style_alphaupper(self, collector):
        """Test renumber with alphaupper counter."""
        collector._TocTreeCollectorWithStyles__alphaupper_count = 3
        result = collector._TocTreeCollectorWithStyles__renumber([1], ["alphaupper"])
        assert result[0] == "C"

    def test_renumber_style_alphalower(self, collector):
        """Test renumber with alphalower counter."""
        collector._TocTreeCollectorWithStyles__alphalower_count = 25
        result = collector._TocTreeCollectorWithStyles__renumber([1], ["alphalower"])
        assert result[0] == "y"

    def test_renumber_numerical_increments_counter(self, collector):
        """Test that renumber uses numerical counter."""
        collector._TocTreeCollectorWithStyles__numerical_count = 3
        result = collector._TocTreeCollectorWithStyles__renumber([1], ["numerical"])
        assert result[0] == 3

    def test_fix_nested_toc_with_entries(self, collector):
        """Test __fix_nested_toc processes entries."""
        from docutils import nodes

        mock_env = Mock()
        mock_env.titles = {"ref1": {"secnumber": [1, 2]}}
        mock_env.tocs = {"ref1": nodes.bullet_list()}

        toctree = Mock()
        toctree.children = []
        toctree.__getitem__ = Mock(return_value=[("doc1", "ref1")])

        collector._TocTreeCollectorWithStyles__numerical_count = 1
        collector._TocTreeCollectorWithStyles__fix_nested_toc(
            mock_env, toctree, ["numerical"]
        )

        toctree.__getitem__.assert_called_with("entries")

    def test_assign_section_numbers_process_entries_with_secnumber(self, collector):
        """Test processing entries that have secnumber in titles."""
        from docutils import nodes
        from sphinx import addnodes as sphinxnodes

        mock_env = Mock()
        mock_env.numbered_toctrees = {"doc1": ["numerical"]}
        mock_env.titles = {
            "doc1": {"secnumber": [1]},
            "doc2": {"secnumber": [2]},
        }
        mock_env.titles_old = {
            "doc1": {"secnumber": [1]},
            "doc2": {"secnumber": [2]},
        }
        mock_env.toc_secnumbers = {"doc1": {}, "doc2": {}}
        mock_env.tocs = {"doc2": nodes.bullet_list()}
        mock_env.app = Mock()
        mock_env.app.config = Mock()
        mock_env.app.config.use_multitoc_numbering = False

        mock_doctree = Mock()
        mock_toctree = Mock(spec=sphinxnodes.toctree)
        mock_toctree.get = Mock(
            side_effect=lambda key, default=None: {
                "style": "numerical",
                "restart_numbering": True,
            }.get(key, default)
        )
        # Entry with doc2 that has secnumber
        mock_toctree.__getitem__ = Mock(return_value=[("", "doc2")])
        mock_toctree.traverse = Mock(return_value=[])
        mock_doctree.findall = Mock(return_value=[mock_toctree])
        mock_env.get_doctree = Mock(return_value=mock_doctree)

        with patch.object(
            TocTreeCollector, "assign_section_numbers", return_value=None
        ):
            collector.assign_section_numbers(mock_env)
            # Verify doc2 title was processed
            assert "doc2" in mock_env.titles

    def test_assign_section_numbers_skip_entries_without_titles(self, collector):
        """Test that entries not in titles are skipped."""
        from docutils import nodes
        from sphinx import addnodes as sphinxnodes

        mock_env = Mock()
        mock_env.numbered_toctrees = {"doc1": ["numerical"]}
        mock_env.titles = {"doc1": nodes.title(text="Title")}
        mock_env.titles_old = {}
        mock_env.toc_secnumbers = {}
        mock_env.app = Mock()
        mock_env.app.config = Mock()
        mock_env.app.config.use_multitoc_numbering = False

        mock_doctree = Mock()
        mock_toctree = Mock(spec=sphinxnodes.toctree)
        mock_toctree.get = Mock(
            side_effect=lambda key, default=None: {
                "style": "numerical",
                "restart_numbering": True,
            }.get(key, default)
        )
        # Entry with doc_not_exists which is not in titles
        mock_toctree.__getitem__ = Mock(return_value=[("", "doc_not_exists")])
        mock_toctree.traverse = Mock(return_value=[])
        mock_doctree.findall = Mock(return_value=[mock_toctree])
        mock_env.get_doctree = Mock(return_value=mock_doctree)

        with patch.object(
            TocTreeCollector, "assign_section_numbers", return_value=None
        ):
            # Should not raise error even though doc_not_exists not in titles
            collector.assign_section_numbers(mock_env)

    def test_renumber_with_different_styles_in_sequence(self, collector):
        """Test renumber with different styles in one call."""
        collector._TocTreeCollectorWithStyles__numerical_count = 5
        collector._TocTreeCollectorWithStyles__romanupper_count = 2
        collector._TocTreeCollectorWithStyles__alphaupper_count = 3

        result = collector._TocTreeCollectorWithStyles__renumber(
            [1, 2, 3], ["numerical", "romanupper", "alphaupper"]
        )
        assert result[0] == 5
        assert result[1] == "II"
        assert result[2] == "C"

    def test_assign_section_numbers_handles_restart_numbering_true(self, collector):
        """Test assign_section_numbers with restart_numbering True."""
        from sphinx import addnodes as sphinxnodes

        for style in [
            "numerical",
            "romanupper",
            "romanlower",
            "alphaupper",
            "alphalower",
        ]:
            fresh_collector = TocTreeCollectorWithStyles()  # Fresh collector
            fresh_collector._TocTreeCollectorWithStyles__numerical_count = 10
            fresh_collector._TocTreeCollectorWithStyles__romanupper_count = 10
            fresh_collector._TocTreeCollectorWithStyles__romanlower_count = 10
            fresh_collector._TocTreeCollectorWithStyles__alphaupper_count = 10
            fresh_collector._TocTreeCollectorWithStyles__alphalower_count = 10

            mock_env = Mock()
            mock_env.numbered_toctrees = {"doc1": [style]}
            mock_env.titles = {}
            mock_env.titles_old = {}
            mock_env.toc_secnumbers = {}
            mock_env.app = Mock()
            mock_env.app.config = Mock()
            mock_env.app.config.use_multitoc_numbering = False

            mock_doctree = Mock()
            mock_toctree = Mock(spec=sphinxnodes.toctree)
            mock_toctree.get = Mock(
                side_effect=lambda key, default=None: {
                    "style": style,
                    "restart_numbering": True,
                }.get(key, default)
            )
            mock_toctree.__getitem__ = Mock(return_value=[])
            mock_toctree.traverse = Mock(return_value=[])
            mock_doctree.findall = Mock(return_value=[mock_toctree])
            mock_env.get_doctree = Mock(return_value=mock_doctree)

            with patch.object(
                TocTreeCollector, "assign_section_numbers", return_value=None
            ):
                fresh_collector.assign_section_numbers(mock_env)
                # Verify only the matching style counter was reset to 0
                if style == "numerical":
                    assert (
                        fresh_collector._TocTreeCollectorWithStyles__numerical_count
                        == 0
                    )
                if style == "romanupper":
                    assert (
                        fresh_collector._TocTreeCollectorWithStyles__romanupper_count
                        == 0
                    )
                if style == "romanlower":
                    assert (
                        fresh_collector._TocTreeCollectorWithStyles__romanlower_count
                        == 0
                    )
                if style == "alphaupper":
                    assert (
                        fresh_collector._TocTreeCollectorWithStyles__alphaupper_count
                        == 0
                    )
                if style == "alphalower":
                    assert (
                        fresh_collector._TocTreeCollectorWithStyles__alphalower_count
                        == 0
                    )
