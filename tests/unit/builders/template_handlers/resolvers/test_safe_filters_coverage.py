"""Coverage-focused tests for safe filter implementations.

This test module validates the graceful-fallback behavior of the safe_*
Jinja2 filters in ``safe_filters.py``:
- safe_get dot-notation access on dicts, objects, and error paths
- safe_filter exception swallowing
- safe_list conversion across container/string types
- safe_int conversion including suffixes and bases
- safe_str conversion including complex types
- safe_json parsing and passthrough
- safe_regex substitution and invalid-pattern handling
- register_safe_filters environment wiring
"""

import re

from prompticorn.builders.template_handlers.resolvers.safe_filters import (
    register_safe_filters,
    safe_filter,
    safe_get,
    safe_int,
    safe_json,
    safe_list,
    safe_regex,
    safe_str,
)


class TestSafeGet:
    """Test dot-notation lookup with fallbacks."""

    def test_none_obj_returns_default(self):
        # Arrange / Act
        result = safe_get(None, "a.b", default="fallback")
        # Assert
        assert result == "fallback"

    def test_nested_dict_access(self):
        obj = {"database": {"host": "localhost"}}
        assert safe_get(obj, "database.host") == "localhost"

    def test_missing_key_returns_default(self):
        obj = {"database": {}}
        assert safe_get(obj, "database.host", default="def") == "def"

    def test_intermediate_none_returns_default(self):
        obj = {"database": None}
        assert safe_get(obj, "database.host", default="def") == "def"

    def test_object_attribute_access(self):
        class Cfg:
            def __init__(self):
                self.host = "h1"

        assert safe_get(Cfg(), "host") == "h1"

    def test_attribute_not_found_returns_default(self):
        class Cfg:
            pass

        assert safe_get(Cfg(), "missing", default="d") == "d"

    def test_exception_during_access_returns_default(self):
        class Boom:
            @property
            def trap(self):
                raise TypeError("boom")

        # hasattr returns False when the property raises, so it falls to the
        # not-found branch and returns default.
        assert safe_get(Boom(), "trap", default="d") == "d"

    def test_final_value_none_returns_default(self):
        obj = {"key": None}
        assert safe_get(obj, "key", default="d") == "d"

    def test_single_level_value(self):
        assert safe_get({"a": 1}, "a") == 1


class TestSafeFilter:
    """Test filter application with exception handling."""

    def test_successful_filter(self):
        assert safe_filter("abc", str.upper) == "ABC"

    def test_filter_raises_returns_default(self):
        def boom(_):
            raise ValueError("nope")

        assert safe_filter("x", boom, default="d") == "d"

    def test_filter_custom_error_msg(self, caplog):
        def boom(_):
            raise RuntimeError("bad")

        with caplog.at_level("WARNING"):
            result = safe_filter("x", boom, default=None, error_msg="custom message")
        assert result is None
        assert "custom message" in caplog.text


class TestSafeList:
    """Test list conversion across types."""

    def test_list_passthrough(self):
        data = [1, 2, 3]
        assert safe_list(data) is data

    def test_tuple_to_list(self):
        assert safe_list((1, 2)) == [1, 2]

    def test_set_to_list(self):
        assert sorted(safe_list({1, 2})) == [1, 2]

    def test_dict_to_values(self):
        assert sorted(safe_list({"a": 1, "b": 2})) == [1, 2]

    def test_json_string_list(self):
        assert safe_list('["a", "b"]') == ["a", "b"]

    def test_json_string_non_list_falls_through_to_csv(self):
        # JSON parses to a dict, not a list, so it falls to CSV splitting.
        result = safe_list('{"a": 1}')
        assert result == ['{"a": 1}']

    def test_invalid_json_list_falls_back_to_csv(self):
        # Starts with '[' but invalid JSON -> warns, then CSV split.
        result = safe_list("[not json")
        assert result == ["[not json"]

    def test_comma_separated_string(self):
        assert safe_list("a, b ,c") == ["a", "b", "c"]

    def test_comma_separated_skips_empty(self):
        assert safe_list("a,,b,") == ["a", "b"]

    def test_unconvertible_returns_default(self):
        assert safe_list(42, default=["fallback"]) == ["fallback"]

    def test_unconvertible_default_none_becomes_empty(self):
        assert safe_list(42) == []


class TestSafeInt:
    """Test int conversion with fallbacks and suffixes."""

    def test_int_passthrough(self):
        assert safe_int(7) == 7

    def test_bool_converted(self):
        assert safe_int(True) == 1
        assert safe_int(False) == 0

    def test_float_truncated(self):
        assert safe_int(3.9) == 3

    def test_string_number(self):
        assert safe_int("42") == 42

    def test_string_with_suffix(self):
        assert safe_int("100ms") == 100
        assert safe_int("5kb") == 5

    def test_string_invalid_returns_default(self):
        assert safe_int("abc", default=-1) == -1

    def test_base_conversion(self):
        assert safe_int("ff", base=16) == 255

    def test_unconvertible_type_returns_default(self):
        assert safe_int(None, default=99) == 99


class TestSafeStr:
    """Test string conversion."""

    def test_str_passthrough(self):
        assert safe_str("hello") == "hello"

    def test_none_returns_default(self):
        assert safe_str(None, default="d") == "d"

    def test_list_to_json(self):
        assert safe_str([1, 2]) == "[1, 2]"

    def test_dict_to_json(self):
        assert safe_str({"a": 1}) == '{"a": 1}'

    def test_int_to_str(self):
        assert safe_str(123) == "123"

    def test_conversion_exception_returns_default(self):
        class Boom:
            def __str__(self):
                raise ValueError("no str")

        assert safe_str(Boom(), default="d") == "d"


class TestSafeJson:
    """Test JSON parsing with fallbacks."""

    def test_dict_passthrough(self):
        data = {"a": 1}
        assert safe_json(data) is data

    def test_list_passthrough(self):
        data = [1, 2]
        assert safe_json(data) is data

    def test_parse_valid_json(self):
        assert safe_json('{"a": 1}') == {"a": 1}

    def test_non_string_returns_default(self):
        assert safe_json(42, default="d") == "d"

    def test_non_string_default_none_becomes_empty_dict(self):
        assert safe_json(42) == {}

    def test_invalid_json_returns_default(self):
        assert safe_json("{not json", default={"x": 1}) == {"x": 1}


class TestSafeRegex:
    """Test regex substitution with fallbacks."""

    def test_simple_substitution(self):
        assert safe_regex("a1b2", pattern="[0-9]", replacement="#") == "a#b#"

    def test_non_string_value_coerced(self):
        assert safe_regex(123, pattern="2", replacement="X") == "1X3"

    def test_flags_applied(self):
        result = safe_regex("ABC", pattern="abc", replacement="x", flags=re.IGNORECASE)
        assert result == "x"

    def test_invalid_pattern_returns_default(self):
        result = safe_regex("value", pattern="[unclosed", default="fallback")
        assert result == "fallback"

    def test_invalid_pattern_default_none_uses_value_str(self):
        result = safe_regex("value", pattern="[unclosed")
        assert result == "value"

    def test_generic_exception_returns_default(self):
        # str(value) raises -> generic except branch returns default.
        class Boom:
            def __str__(self):
                raise ValueError("no str")

        result = safe_regex(Boom(), pattern="x", replacement="y", default="fallback")
        assert result == "fallback"


class TestRegisterSafeFilters:
    """Test environment registration of all filters."""

    def test_registers_all_filters(self):
        class FakeEnv:
            def __init__(self):
                self.filters = {}

        env = FakeEnv()
        register_safe_filters(env)

        expected = {
            "safe_get",
            "safe_filter",
            "safe_list",
            "safe_int",
            "safe_str",
            "safe_json",
            "safe_regex",
        }
        assert expected.issubset(env.filters.keys())
        assert env.filters["safe_get"] is safe_get
        assert env.filters["safe_regex"] is safe_regex
