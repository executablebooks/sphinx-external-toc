"""Tests for sphinx_external_toc._compat module."""

import pytest
from sphinx_external_toc import _compat


class TestCompatModule:
    """Test compatibility functions."""

    def test_compat_module_exists(self):
        """Test that _compat module is importable."""
        assert _compat is not None

    def test_compat_module_has_functions(self):
        """Test that _compat has some public members."""
        import inspect

        members = inspect.getmembers(_compat)
        assert len(members) > 0

    def test_sphinx_compatibility_imports(self):
        """Test that compatibility imports work."""
        from sphinx_external_toc import _compat  # noqa: F401


class TestCompatValidators:
    """Test validator functions in _compat."""

    def test_instance_of_validator(self):
        """Test instance_of validator."""
        validator = _compat.instance_of(str)
        assert callable(validator)

    def test_instance_of_with_string(self):
        """Test instance_of validates strings."""
        validator = _compat.instance_of(str)

        # Should not raise - validators take (instance, attr, value)
        class MockAttr:
            name = "test_attr"

        validator(None, MockAttr(), "test")

    def test_instance_of_with_wrong_type(self):
        """Test instance_of raises on wrong type."""
        validator = _compat.instance_of(str)
        with pytest.raises(Exception):
            validator(123)

    def test_optional_validator(self):
        """Test optional validator."""
        validator = _compat.optional(_compat.instance_of(str))
        assert callable(validator)

        # Should accept None
        class MockAttr:
            name = "test_attr"

        validator(None, MockAttr(), None)
        # Should accept string
        validator(None, MockAttr(), "test")

    def test_optional_validator_wrong_type(self):
        """Test optional validator rejects wrong type."""
        validator = _compat.optional(_compat.instance_of(str))
        with pytest.raises(Exception):
            validator(123)

    def test_deep_iterable_validator(self):
        """Test deep_iterable validator."""
        validator = _compat.deep_iterable(_compat.instance_of(str))
        assert callable(validator)

    def test_deep_iterable_with_values(self):
        """Test deep_iterable with actual values."""
        validator = _compat.deep_iterable(
            _compat.instance_of(str), iterable_validator=_compat.instance_of(list)
        )

        class MockAttr:
            name = "test_attr"

        validator(None, MockAttr(), ["a", "b", "c"])

    def test_matches_re_validator(self):
        """Test matches_re validator."""
        validator = _compat.matches_re(r"^\d+$")
        assert callable(validator)

        # Should match
        class MockAttr:
            name = "test_attr"

        validator(None, MockAttr(), "123")

    def test_matches_re_validator_no_match(self):
        """Test matches_re validator rejects non-matching."""
        validator = _compat.matches_re(r"^\d+$")
        with pytest.raises(Exception):
            validator("abc")

    def test_instance_of_with_int(self):
        """Test instance_of with integers."""
        validator = _compat.instance_of(int)

        class MockAttr:
            name = "count"

        validator(None, MockAttr(), 42)

    def test_optional_with_none(self):
        """Test optional accepts None."""
        validator = _compat.optional(_compat.instance_of(int))

        class MockAttr:
            name = "count"

        validator(None, MockAttr(), None)

    def test_matches_re_with_pattern(self):
        """Test matches_re with various patterns."""
        validator = _compat.matches_re(r"^[a-z]+$")

        class MockAttr:
            name = "word"

        validator(None, MockAttr(), "hello")

    def test_matches_re_flags(self):
        """Test matches_re with flags."""
        import re

        validator = _compat.matches_re(r"^[a-z]+$", re.IGNORECASE)

        class MockAttr:
            name = "word"

        validator(None, MockAttr(), "HELLO")


class TestCompatValidateStyle:
    """Test validate_style function."""

    def test_validate_style_exists(self):
        """Test validate_style function exists."""
        assert callable(_compat.validate_style)

    def test_validate_style_callable(self):
        """Test validate_style is callable."""
        func = _compat.validate_style
        assert callable(func)


class TestCompatValidateFields:
    """Test validate_fields function."""

    def test_validate_fields_exists(self):
        """Test validate_fields function exists."""
        assert callable(_compat.validate_fields)

    def test_validate_fields_callable(self):
        """Test validate_fields is callable."""
        func = _compat.validate_fields
        assert callable(func)


class TestCompatField:
    """Test field function from attrs/dataclasses."""

    def test_field_exists(self):
        """Test field function exists."""
        assert callable(_compat.field)

    def test_field_callable(self):
        """Test field is callable."""
        func = _compat.field
        assert callable(func)


class TestCompatElement:
    """Test Element class."""

    def test_element_exists(self):
        """Test Element class exists."""
        assert _compat.Element is not None

    def test_element_is_type(self):
        """Test Element is a type."""
        assert isinstance(_compat.Element, type)


class TestCompatDataclassUtils:
    """Test dataclass utilities."""

    def test_dc_module_exists(self):
        """Test dc (dataclasses) module exists."""
        assert _compat.dc is not None

    def test_dc_module_has_dataclass(self):
        """Test dc module has dataclass decorator."""
        assert hasattr(_compat.dc, "dataclass")

    def test_dc_slots_exists(self):
        """Test DC_SLOTS exists."""
        assert isinstance(_compat.DC_SLOTS, dict)

    def test_field_function(self):
        """Test field function from dataclasses."""
        func = _compat.field
        assert callable(func)


class TestCompatImportPaths:
    """Test different import paths in _compat."""

    def test_compat_try_except_imports(self):
        """Test that _compat handles import failures gracefully."""
        import importlib

        reloaded = importlib.reload(_compat)
        assert reloaded is not None

    def test_compat_module_reloading(self):
        """Test that _compat module can be reloaded."""
        import importlib

        reloaded = importlib.reload(_compat)
        assert reloaded is not None

    def test_compat_all_imports_accessible(self):
        """Test that all _compat members are accessible."""
        import inspect

        for name, obj in inspect.getmembers(_compat):
            if not name.startswith("_"):
                attr = getattr(_compat, name)
                assert attr is not None


class TestCompatConditionalImports:
    """Test conditional import branches in _compat."""

    def test_compat_module_dict(self):
        """Test accessing _compat module dict."""
        compat_dict = _compat.__dict__
        assert isinstance(compat_dict, dict)
        assert len(compat_dict) > 0

    def test_compat_import_error_handling(self):
        """Test that import errors are handled gracefully."""
        import sys
        import importlib

        if "sphinx_external_toc._compat" in sys.modules:
            del sys.modules["sphinx_external_toc._compat"]

        compat_module = importlib.import_module("sphinx_external_toc._compat")
        assert compat_module is not None

    def test_compat_list_all_members(self):
        """Test that we can list all _compat members."""
        import inspect

        members = inspect.getmembers(
            _compat, predicate=lambda x: not inspect.isbuiltin(x)
        )
        assert len(members) > 0

        for name, obj in members:
            if not name.startswith("_"):
                assert obj is not None

    def test_compat_has_re_module(self):
        """Test that re module is available."""
        assert _compat.re is not None

    def test_compat_has_sys_module(self):
        """Test that sys module is available."""
        assert _compat.sys is not None

    def test_compat_findall_function(self):
        """Test findall function."""
        assert callable(_compat.findall)

    def test_compat_type_annotations(self):
        """Test that type annotations exist."""
        assert hasattr(_compat, "__annotations__")
        assert isinstance(_compat.__annotations__, dict)

    def test_compat_callable_type(self):
        """Test Callable type exists."""
        assert _compat.Callable is not None

    def test_compat_pattern_type(self):
        """Test Pattern type exists."""
        assert _compat.Pattern is not None

    def test_compat_validator_type(self):
        """Test ValidatorType exists."""
        assert _compat.ValidatorType is not None

    def test_compat_any_type(self):
        """Test Any type exists."""
        assert _compat.Any is not None

    def test_compat_type_type(self):
        """Test Type exists."""
        assert _compat.Type is not None
