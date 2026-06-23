"""Coverage-focused tests for the error_recovery module.

These tests exercise the public surface of SafeAccessor, TemplateCache, and
ErrorContextBuilder, including edge and error paths, to raise module coverage.
"""

from prompticorn.builders.template_handlers.resolvers.error_recovery import (
    ErrorContextBuilder,
    SafeAccessor,
    TemplateCache,
)


class _Obj:
    """Simple object with attributes for object-access tests."""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestSafeAccessorGet:
    """Tests for SafeAccessor.get and nested access."""

    def test_get_simple_value(self):
        # Arrange
        accessor = SafeAccessor({"name": "Ada"})
        # Act
        result = accessor.get("name")
        # Assert
        assert result == "Ada"

    def test_get_nested_value(self):
        # Arrange
        accessor = SafeAccessor({"config": {"db": {"host": "localhost"}}})
        # Act
        result = accessor.get("config.db.host")
        # Assert
        assert result == "localhost"

    def test_get_default_when_root_context_missing(self):
        # Arrange
        accessor = SafeAccessor(None)
        # Act
        result = accessor.get("anything", default="fallback")
        # Assert
        assert result == "fallback"

    def test_get_missing_returns_default(self):
        # Arrange
        accessor = SafeAccessor({"name": "Ada"})
        # Act
        result = accessor.get("missing", default="N/A")
        # Assert
        assert result == "N/A"

    def test_get_uses_fallback_suggestion(self, caplog):
        # Arrange
        accessor = SafeAccessor({"alt_name": "Grace"})
        # Act
        with caplog.at_level("WARNING"):
            result = accessor.get("name", fallback_suggestions=["alt_name"])
        # Assert
        assert result == "Grace"
        assert any("using fallback 'alt_name'" in r.message for r in caplog.records)

    def test_get_fallback_all_missing_returns_default(self):
        # Arrange
        accessor = SafeAccessor({"name": "Ada"})
        # Act
        result = accessor.get("missing", default="def", fallback_suggestions=["also_missing"])
        # Assert
        assert result == "def"

    def test_get_logs_warning_when_missing(self, caplog):
        # Arrange
        accessor = SafeAccessor({})
        # Act
        with caplog.at_level("WARNING"):
            accessor.get("ghost", default=1)
        # Assert
        assert any("not found in template context" in r.message for r in caplog.records)

    def test_get_object_attribute_access(self):
        # Arrange
        accessor = SafeAccessor({"obj": _Obj(value=42)})
        # Act
        result = accessor.get("obj.value")
        # Assert
        assert result == 42

    def test_get_nested_stops_on_none(self):
        # Arrange: intermediate value is None
        accessor = SafeAccessor({"a": None})
        # Act
        result = accessor.get("a.b.c", default="d")
        # Assert
        assert result == "d"

    def test_get_nested_non_dict_non_attr_returns_none(self):
        # Arrange: scalar in the middle of a path
        accessor = SafeAccessor({"a": 5})
        # Act
        result = accessor.get("a.b", default="d")
        # Assert
        assert result == "d"


class TestSafeAccessorGetNested:
    """Direct tests for the _get_nested static helper."""

    def test_get_nested_dict(self):
        # Act / Assert
        assert SafeAccessor._get_nested({"x": {"y": 1}}, "x.y") == 1

    def test_get_nested_missing_key(self):
        # Act / Assert
        assert SafeAccessor._get_nested({"x": 1}, "z") is None

    def test_get_nested_object(self):
        # Act / Assert
        assert SafeAccessor._get_nested(_Obj(a=7), "a") == 7

    def test_get_nested_none_input(self):
        # Act / Assert
        assert SafeAccessor._get_nested(None, "a") is None


class TestSuggestSimilarProperties:
    """Tests for property-name suggestions via Levenshtein matching."""

    def test_suggests_close_match(self):
        # Arrange
        accessor = SafeAccessor({"username": "x", "password": "y"})
        # Act
        suggestions = accessor.suggest_similar_properties("usernam")
        # Assert
        assert "username" in suggestions

    def test_no_suggestions_when_far(self):
        # Arrange
        accessor = SafeAccessor({"completely_different": "x"})
        # Act
        suggestions = accessor.suggest_similar_properties("zzz")
        # Assert
        assert suggestions == []

    def test_respects_max_suggestions(self):
        # Arrange: several near-identical keys
        accessor = SafeAccessor({"name1": 1, "name2": 2, "name3": 3, "name4": 4})
        # Act
        suggestions = accessor.suggest_similar_properties("name", max_suggestions=2)
        # Assert
        assert len(suggestions) == 2

    def test_suggestions_sorted_by_distance(self):
        # Arrange
        accessor = SafeAccessor({"host": 1, "hostname": 2})
        # Act
        suggestions = accessor.suggest_similar_properties("host")
        # Assert: exact match should rank first
        assert suggestions[0] == "host"


class TestFlattenKeys:
    """Tests for the _flatten_keys static helper."""

    def test_flatten_nested_dict(self):
        # Act
        keys = SafeAccessor._flatten_keys({"a": {"b": 1}, "c": 2})
        # Assert
        assert "a" in keys
        assert "a.b" in keys
        assert "c" in keys

    def test_flatten_object_with_dict(self):
        # Arrange
        obj = _Obj(public=1, _private=2)
        # Act
        keys = SafeAccessor._flatten_keys(obj)
        # Assert
        assert "public" in keys
        assert "_private" not in keys

    def test_flatten_scalar_values_not_recursed(self):
        # Act
        keys = SafeAccessor._flatten_keys({"n": 1, "s": "str", "b": True})
        # Assert: scalars listed but not recursed into
        assert set(keys) == {"n", "s", "b"}


class TestLevenshteinDistance:
    """Tests for the Levenshtein distance helper."""

    def test_identical_strings(self):
        assert SafeAccessor._levenshtein_distance("abc", "abc") == 0

    def test_empty_second_string(self):
        assert SafeAccessor._levenshtein_distance("abc", "") == 3

    def test_one_substitution(self):
        assert SafeAccessor._levenshtein_distance("cat", "bat") == 1

    def test_swaps_shorter_first(self):
        # Triggers the len(s1) < len(s2) branch
        assert SafeAccessor._levenshtein_distance("a", "abc") == 2


class TestTemplateCache:
    """Tests for TemplateCache get/set/clear/stats and eviction."""

    def test_get_miss_returns_none(self):
        # Arrange
        cache = TemplateCache()
        # Act
        result = cache.get("absent")
        # Assert
        assert result is None
        assert cache.stats()["misses"] == 1

    def test_set_and_get_hit(self):
        # Arrange
        cache = TemplateCache()
        cache.set("k", "v")
        # Act
        result = cache.get("k")
        # Assert
        assert result == "v"
        assert cache.stats()["hits"] == 1

    def test_eviction_when_full(self):
        # Arrange
        cache = TemplateCache(max_size=2)
        cache.set("a", 1)
        cache.set("b", 2)
        # Act: adding a third evicts the oldest ("a")
        cache.set("c", 3)
        # Assert
        assert cache.get("a") is None
        assert cache.get("c") == 3
        assert cache.stats()["size"] == 2

    def test_clear_resets_state(self):
        # Arrange
        cache = TemplateCache()
        cache.set("k", "v")
        cache.get("k")
        cache.get("missing")
        # Act
        cache.clear()
        # Assert
        stats = cache.stats()
        assert stats["hits"] == 0
        assert stats["misses"] == 0
        assert stats["size"] == 0

    def test_stats_hit_rate_zero_when_empty(self):
        # Arrange
        cache = TemplateCache()
        # Act
        stats = cache.stats()
        # Assert
        assert stats["hit_rate_percent"] == 0
        assert stats["total"] == 0

    def test_stats_hit_rate_computed(self):
        # Arrange
        cache = TemplateCache()
        cache.set("k", "v")
        cache.get("k")  # hit
        cache.get("x")  # miss
        # Act
        stats = cache.stats()
        # Assert
        assert stats["hit_rate_percent"] == 50
        assert stats["max_size"] == 1000


class TestErrorContextBuilder:
    """Tests for ErrorContextBuilder.build_context and suggest_fix."""

    def test_build_context_minimal(self):
        # Act
        ctx = ErrorContextBuilder.build_context("undefined_variable")
        # Assert
        assert ctx["error_type"] == "undefined_variable"
        assert ctx["template_name"] is None
        assert "available_variables" not in ctx
        assert "original_error" not in ctx

    def test_build_context_with_variables(self):
        # Act
        ctx = ErrorContextBuilder.build_context("undefined_variable", variables={"a": 1, "b": 2})
        # Assert
        assert set(ctx["available_variables"]) == {"a", "b"}

    def test_build_context_with_original_error(self):
        # Arrange
        err = ValueError("boom")
        # Act
        ctx = ErrorContextBuilder.build_context("syntax_error", original_error=err)
        # Assert
        assert ctx["original_error"]["type"] == "ValueError"
        assert ctx["original_error"]["message"] == "boom"

    def test_build_context_full(self):
        # Act
        ctx = ErrorContextBuilder.build_context(
            "missing_template",
            template_name="t.j2",
            line_number=12,
        )
        # Assert
        assert ctx["template_name"] == "t.j2"
        assert ctx["line_number"] == 12

    def test_suggest_fix_undefined_variable(self):
        # Act
        msg = ErrorContextBuilder.suggest_fix("undefined_variable", {"variable_name": "foo"})
        # Assert
        assert "foo" in msg

    def test_suggest_fix_missing_template(self):
        # Act
        msg = ErrorContextBuilder.suggest_fix("missing_template", {"template_name": "x.j2"})
        # Assert
        assert "x.j2" in msg

    def test_suggest_fix_syntax_error_with_line(self):
        # Act
        msg = ErrorContextBuilder.suggest_fix("syntax_error", {"line_number": 9})
        # Assert
        assert "9" in msg

    def test_suggest_fix_syntax_error_without_line(self):
        # Act
        msg = ErrorContextBuilder.suggest_fix("syntax_error", {})
        # Assert
        assert "?" in msg

    def test_suggest_fix_filter_error(self):
        # Act
        msg = ErrorContextBuilder.suggest_fix("filter_error", {})
        # Assert
        assert "filter" in msg.lower()

    def test_suggest_fix_circular_reference(self):
        # Act
        msg = ErrorContextBuilder.suggest_fix("circular_reference", {})
        # Assert
        assert "circular" in msg.lower()

    def test_suggest_fix_unknown_error_type(self):
        # Act
        msg = ErrorContextBuilder.suggest_fix("totally_unknown", {})
        # Assert
        assert "logs" in msg.lower()
