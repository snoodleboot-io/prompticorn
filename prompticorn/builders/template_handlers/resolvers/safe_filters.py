"""Safe filter implementations with error handling for Jinja2 templates.

These filters provide graceful error handling to prevent template rendering
failures due to bad data or invalid arguments.

Filters:
    safe_get: Get a value from a dict/object with fallback
    safe_filter: Apply a filter with error handling
    safe_list: Convert to list with fallback
    safe_int: Convert to int with fallback
    safe_str: Convert to string with fallback
    safe_json: Parse JSON with fallback
    safe_regex: Apply regex with fallback
"""

import json
import logging
import re
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


def safe_get(obj: Any, path: str, default: Any = None) -> Any:
    """Safely get a value from a dict/object using dot notation with fallback.

    Example:
        {{ config | safe_get('database.host', 'localhost') }}
        → Gets config.database.host, falls back to 'localhost' if not found

    Args:
        obj: Dictionary or object to access
        path: Dot-separated path (e.g., 'database.host')
        default: Fallback value if not found

    Returns:
        Value at path, or default if not found
    """
    if obj is None:
        logger.debug(f"safe_get: obj is None, returning default: {default!r}")
        return default

    parts = path.split(".")
    current = obj

    for i, part in enumerate(parts):
        if current is None:
            logger.debug(f"safe_get: path '{'.'.join(parts[:i])}' is None, returning default")
            return default

        try:
            if isinstance(current, dict):
                current = current.get(part)
            elif hasattr(current, part):
                # design-decision-override: Template framework must handle dynamic attribute access
                current = getattr(current, part)
            else:
                logger.debug(
                    f"safe_get: '{part}' not found in {type(current).__name__}, returning default"
                )
                return default
        except (AttributeError, TypeError) as e:
            logger.debug(f"safe_get: error accessing '{part}': {e}, returning default")
            return default

    return current if current is not None else default


def safe_filter(
    value: Any, filter_func: Callable[[Any], Any], default: Any = None, error_msg: str | None = None
) -> Any:
    """Apply a filter function with error handling.

    Example:
        {{ value | safe_filter(custom_filter, default='unknown') }}

    Args:
        value: Value to filter
        filter_func: Filter function to apply
        default: Fallback value if filter fails
        error_msg: Custom error message to log

    Returns:
        Filtered value, or default if filter raises exception
    """
    try:
        return filter_func(value)
    except Exception as e:
        msg = error_msg or f"Filter failed: {type(e).__name__}: {e}"
        logger.warning(f"safe_filter: {msg}, returning default: {default!r}")
        return default


def safe_list(value: Any, default: list | None = None) -> list:
    """Convert value to list with error handling.

    Example:
        {{ value | safe_list(default=[]) }}

    Args:
        value: Value to convert
        default: Fallback list if conversion fails

    Returns:
        List, or default empty list
    """
    if default is None:
        default = []

    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    if isinstance(value, dict):
        logger.warning("safe_list: converting dict to list of values")
        return list(value.values())

    if isinstance(value, str):
        if value.strip().startswith("["):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
            except json.JSONDecodeError:
                logger.warning("safe_list: failed to parse JSON list")

        # Try comma-separated values
        return [v.strip() for v in value.split(",") if v.strip()]

    logger.warning(f"safe_list: cannot convert {type(value).__name__} to list")
    return default


def safe_int(value: Any, default: int = 0, base: int = 10) -> int:
    """Convert value to int with error handling.

    Example:
        {{ value | safe_int(default=0) }}

    Args:
        value: Value to convert
        default: Fallback integer
        base: Base for integer conversion (default 10)

    Returns:
        Integer, or default if conversion fails
    """
    if isinstance(value, int):
        return value

    if isinstance(value, bool):
        # bool is subclass of int, handle separately
        logger.debug("safe_int: converting bool to int")
        return int(value)

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            # Remove whitespace and common suffixes
            cleaned = value.strip().lower()
            # Remove common number suffixes (ms, s, KB, MB, etc.)
            for suffix in ["ms", "s", "kb", "mb", "gb", "tb"]:
                if cleaned.endswith(suffix):
                    cleaned = cleaned[: -len(suffix)].strip()
                    break
            return int(cleaned, base)
        except ValueError:
            logger.debug(f"safe_int: failed to convert string '{value}' to int")

    logger.warning(f"safe_int: cannot convert {type(value).__name__} to int, using default")
    return default


def safe_str(value: Any, default: str = "") -> str:
    """Convert value to string with error handling.

    Example:
        {{ value | safe_str(default='unknown') }}

    Args:
        value: Value to convert
        default: Fallback string

    Returns:
        String, or default if conversion fails
    """
    if isinstance(value, str):
        return value

    if value is None:
        logger.debug("safe_str: value is None, using default")
        return default

    try:
        if isinstance(value, (list, dict)):
            # Use JSON representation for complex types
            return json.dumps(value)
        return str(value)
    except Exception as e:
        logger.warning(f"safe_str: failed to convert to string: {e}")
        return default


def safe_json(value: Any, default: Any | None = None) -> Any:
    """Parse JSON string with error handling.

    Example:
        {{ json_string | safe_json(default={}) }}

    Args:
        value: String to parse as JSON
        default: Fallback value if parsing fails

    Returns:
        Parsed JSON, or default if parsing fails
    """
    if default is None:
        default = {}

    if isinstance(value, (dict, list)):
        # Already parsed
        return value

    if not isinstance(value, str):
        logger.warning("safe_json: value is not string, using default")
        return default

    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        logger.warning(f"safe_json: failed to parse JSON: {e}")
        return default


def safe_regex(
    value: Any,
    pattern: str,
    replacement: str = "",
    default: str | None = None,
    flags: int = 0,
) -> str:
    """Apply regex substitution with error handling.

    Example:
        {{ value | safe_regex(pattern='[0-9]+', replacement='XXX') }}

    Args:
        value: String to process
        pattern: Regex pattern
        replacement: Replacement string
        default: Fallback if regex fails
        flags: Regex flags (re.IGNORECASE, re.MULTILINE, etc.)

    Returns:
        String with substitutions, or default if regex fails
    """
    if default is None:
        default = str(value)

    try:
        value_str = str(value)
        compiled = re.compile(pattern, flags)
        return compiled.sub(replacement, value_str)
    except re.error as e:
        logger.warning(f"safe_regex: invalid regex pattern '{pattern}': {e}")
        return default
    except Exception as e:
        logger.warning(f"safe_regex: regex substitution failed: {e}")
        return default


def register_safe_filters(environment: Any) -> None:
    """Register all safe filters with a Jinja2 environment.

    Args:
        environment: A Jinja2 Environment instance
    """
    environment.filters["safe_get"] = safe_get
    environment.filters["safe_filter"] = safe_filter
    environment.filters["safe_list"] = safe_list
    environment.filters["safe_int"] = safe_int
    environment.filters["safe_str"] = safe_str
    environment.filters["safe_json"] = safe_json
    environment.filters["safe_regex"] = safe_regex
