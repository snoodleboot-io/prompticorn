"""Error recovery and safe access utilities for Jinja2 templates.

This module provides utilities for graceful error handling, fallback content,
and safe property access in templates to prevent runtime failures.

Features:
- Safe dictionary/object property access with fallbacks
- Missing template handling with fallback templates
- Graceful filter error handling
- Configuration property suggestions
- Logging integration for error tracking
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class SafeAccessor:
    """Safe accessor for template variables with fallback support."""

    def __init__(self, context: dict[str, Any] | None = None) -> None:
        """Initialize the safe accessor.

        Args:
            context: The template context dictionary
        """
        self.context = context or {}

    def get(
        self,
        path: str,
        default: Any = None,
        fallback_suggestions: list[str] | None = None,
    ) -> Any:
        """Safely get a value from context using dot notation.

        Supports nested access like 'config.database.host'.

        Args:
            path: The property path (supports dot notation)
            default: Default value if not found
            fallback_suggestions: Alternative property paths to try

        Returns:
            The value at path, a fallback value, or the default
        """
        # Try the primary path
        value = self._get_nested(self.context, path)
        if value is not None:
            return value

        # Try fallback suggestions
        if fallback_suggestions:
            for suggestion in fallback_suggestions:
                value = self._get_nested(self.context, suggestion)
                if value is not None:
                    logger.warning(
                        f"Property '{path}' not found in context; using fallback '{suggestion}'"
                    )
                    return value

        # Log warning about missing property
        logger.warning(
            f"Property '{path}' not found in template context; using default value: {default!r}"
        )
        return default

    @staticmethod
    def _get_nested(obj: Any, path: str) -> Any:
        """Get a nested value using dot notation.

        Args:
            obj: The object to access
            path: Dot-separated path (e.g., 'config.database.host')

        Returns:
            The value at the path, or None if not found
        """
        parts = path.split(".")
        current = obj

        for part in parts:
            if current is None:
                return None

            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                try:
                    # design-decision-override: Error recovery must handle dynamic attribute access
                    current = getattr(current, part)
                except AttributeError:
                    return None
            else:
                return None

        return current

    def suggest_similar_properties(self, requested: str, max_suggestions: int = 3) -> list[str]:
        """Suggest similar property names when one is not found.

        Uses simple Levenshtein distance for fuzzy matching.

        Args:
            requested: The property name that was requested
            max_suggestions: Maximum number of suggestions to return

        Returns:
            List of similar property names found in context
        """
        similar = []
        available = self._flatten_keys(self.context)

        for available_key in available:
            distance = self._levenshtein_distance(requested, available_key)
            # Accept suggestions with distance <= 3 (or 30% of length)
            threshold = max(3, len(requested) // 3)
            if distance <= threshold:
                similar.append((available_key, distance))

        # Sort by distance and return top suggestions
        similar.sort(key=lambda x: x[1])
        return [key for key, _ in similar[:max_suggestions]]

    @staticmethod
    def _flatten_keys(obj: Any, prefix: str = "") -> list[str]:
        """Flatten all keys in a nested dict/object.

        Args:
            obj: The object to flatten
            prefix: Current prefix for nested keys

        Returns:
            List of all property paths
        """
        keys = []

        if isinstance(obj, dict):
            for key, value in obj.items():
                full_key = f"{prefix}.{key}" if prefix else key
                keys.append(full_key)
                if isinstance(value, (dict, object)) and not isinstance(
                    value, (str, int, float, bool)
                ):
                    keys.extend(SafeAccessor._flatten_keys(value, full_key))
        elif hasattr(obj, "__dict__"):
            for key in obj.__dict__:
                if not key.startswith("_"):
                    full_key = f"{prefix}.{key}" if prefix else key
                    keys.append(full_key)

        return keys

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Edit distance between strings
        """
        if len(s1) < len(s2):
            return SafeAccessor._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


class TemplateCache:
    """Simple cache for frequently accessed templates with validation.

    Prevents repeated compilation of the same templates and provides
    hit/miss statistics for monitoring.
    """

    def __init__(self, max_size: int = 1000) -> None:
        """Initialize the template cache.

        Args:
            max_size: Maximum number of templates to cache
        """
        self.max_size = max_size
        self._cache: dict[str, Any] = {}
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        """Get a template from cache.

        Args:
            key: Cache key (usually template name or hash)

        Returns:
            Cached template or None if not found
        """
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Store a template in cache.

        Args:
            key: Cache key
            value: Template to cache
        """
        if len(self._cache) >= self.max_size:
            # Simple eviction: remove oldest entry
            self._cache.pop(next(iter(self._cache)))

        self._cache[key] = value

    def clear(self) -> None:
        """Clear the entire cache."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict[str, int]:
        """Get cache statistics.

        Returns:
            Dictionary with cache stats (hits, misses, hit_rate)
        """
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "total": total,
            "hit_rate_percent": int(hit_rate),
            "size": len(self._cache),
            "max_size": self.max_size,
        }


class ErrorContextBuilder:
    """Build detailed error context for better diagnostics."""

    @staticmethod
    def build_context(
        error_type: str,
        template_name: str | None = None,
        variables: dict[str, Any] | None = None,
        line_number: int | None = None,
        original_error: Exception | None = None,
    ) -> dict[str, Any]:
        """Build comprehensive error context.

        Args:
            error_type: Type of error (e.g., 'undefined_variable', 'missing_template')
            template_name: Name of template being rendered
            variables: Variables available in context
            line_number: Line number where error occurred
            original_error: Original exception

        Returns:
            Dictionary with complete error context
        """
        context = {
            "error_type": error_type,
            "template_name": template_name,
            "line_number": line_number,
        }

        if variables:
            context["available_variables"] = list(variables.keys())

        if original_error:
            context["original_error"] = {
                "type": type(original_error).__name__,
                "message": str(original_error),
            }

        return context

    @staticmethod
    def suggest_fix(error_type: str, context: dict[str, Any]) -> str:
        """Suggest a fix based on error type.

        Args:
            error_type: Type of error
            context: Error context

        Returns:
            Suggestion string
        """
        suggestions = {
            "undefined_variable": f"Check if '{context.get('variable_name')}' is passed to the template context",
            "missing_template": f"Verify template file exists: {context.get('template_name')}",
            "syntax_error": f"Check Jinja2 syntax around line {context.get('line_number', '?')}",
            "filter_error": "Verify filter arguments are correct",
            "circular_reference": "Check template inheritance chain for circular dependencies",
        }
        return suggestions.get(error_type, "Check template rendering logs for details")
