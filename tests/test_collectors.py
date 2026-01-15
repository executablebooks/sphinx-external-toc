import pytest
from unittest.mock import Mock, MagicMock, patch
from sphinx_external_toc.collectors import (
    TocTreeCollectorWithStyles,
    disable_builtin_toctree_collector,
)


class TestDisableBuiltinToctreeCollector:
    def test_disable_collector_when_enabled(self):
        """Test disabling an enabled collector."""
        mock_app = Mock()
        from sphinx.environment.collectors.toctree import TocTreeCollector
        mock_collector = Mock(spec=TocTreeCollector)
        mock_collector.listener_ids = ["id1", "id2"]
        
        with patch("sphinx_external_toc.collectors.gc.get_objects", return_value=[mock_collector]):
            with patch("sphinx_external_toc.collectors.TocTreeCollector", TocTreeCollector):
                disable_builtin_toctree_collector(mock_app)
                mock_collector.disable.assert_called_once_with(mock_app)

    def test_skip_disable_when_already_disabled(self):
        """Test that already disabled collectors are skipped."""
        mock_app = Mock()
        from sphinx.environment.collectors.toctree import TocTreeCollector
        mock_collector = Mock(spec=TocTreeCollector)
        mock_collector.listener_ids = None
        
        with patch("sphinx_external_toc.collectors.gc.get_objects", return_value=[mock_collector]):
            disable_builtin_toctree_collector(mock_app)
            mock_collector.disable.assert_not_called()

    def test_skip_non_toctree_collectors(self):
        """Test that non-TocTreeCollector objects are skipped."""
        mock_app = Mock()
        
        with patch("sphinx_external_toc.collectors.gc.get_objects", return_value=["not a collector", 123]):
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

    def test_to_alpha_basic(self, collector):
        """Test alphabetical conversion."""
        assert collector._TocTreeCollectorWithStyles__to_alpha(1) == "A"
        assert collector._TocTreeCollectorWithStyles__to_alpha(26) == "Z"
        assert collector._TocTreeCollectorWithStyles__to_alpha(27) == "AA"
        assert collector._TocTreeCollectorWithStyles__to_alpha(52) == "AZ"

    def test_renumber_numerical(self, collector):
        """Test renumbering with numerical style."""
        collector._TocTreeCollectorWithStyles__numerical_count = 5
        result = collector._TocTreeCollectorWithStyles__renumber([1, 2, 3], ["numerical"])
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
        result = collector._TocTreeCollectorWithStyles__renumber(
            [1, 5, 10], ["numerical", "romanupper", "numerical"]
        )
        assert result[0] == 2
        assert isinstance(result[1], str)

    def test_renumber_converts_string_numbers(self, collector):
        """Test that string numbers in middle positions are skipped."""
        collector._TocTreeCollectorWithStyles__numerical_count = 1
        result = collector._TocTreeCollectorWithStyles__renumber(
            [1, "ii", 3], ["numerical", "numerical"]
        )
        assert result[1] == "ii"  # kept as-is

    def test_init_counters(self, collector):
        """Test that counters are initialized correctly."""
        assert collector._TocTreeCollectorWithStyles__numerical_count == 0
        assert collector._TocTreeCollectorWithStyles__romanupper_count == 0
        assert collector._TocTreeCollectorWithStyles__romanlower_count == 0
        assert collector._TocTreeCollectorWithStyles__alphaupper_count == 0
        assert collector._TocTreeCollectorWithStyles__alphalower_count == 0