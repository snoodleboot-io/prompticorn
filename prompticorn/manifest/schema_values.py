"""Shared value checks for manifest parsing (PRO-109).

Function-only, like :mod:`prompticorn.content.digest` and
:mod:`prompticorn.artifact.naming`. Both declaration types validate the same
kinds of thing, and every message they produce has to place the fault at a key
path — having one of them own these and the other borrow them would let the two
drift into phrasing the same error differently.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from prompticorn.manifest.errors import ManifestSchemaError


def describe_kind(value: Any) -> str:
    """Name a value's type for an error message, in YAML's vocabulary.

    A manifest author writes YAML, not Python, so ``a mapping`` lands where
    ``a CommentedMap`` would not.
    """
    if value is None:
        return "nothing (null)"
    if isinstance(value, bool):
        return "a boolean"
    if isinstance(value, dict):
        return "a mapping"
    if isinstance(value, list):
        return "a list"
    if isinstance(value, str):
        return "a string"
    return f"a {type(value).__name__}"


def require_mapping(raw: Any, key_path: str, expected_keys: Iterable[str]) -> dict[str, Any]:
    """Assert a value is a mapping, or raise pointing at it.

    Raises:
        ManifestSchemaError: With the offending key path.
    """
    if not isinstance(raw, dict):
        readable = ", ".join(f"'{key}'" for key in sorted(expected_keys))
        raise ManifestSchemaError(
            key_path, f"expected a mapping with {readable}, got {describe_kind(raw)}"
        )
    return raw


def reject_unknown_keys(raw: dict[str, Any], key_path: str, known: Iterable[str]) -> None:
    """Reject keys outside the schema.

    Named rather than ignored: a mistyped key that is silently dropped looks
    exactly like a setting that does not work, and costs far more to diagnose
    than it does to reject here.

    Raises:
        ManifestSchemaError: With the offending key path.
    """
    known_keys = set(known)
    unknown = sorted(set(raw) - known_keys)
    if not unknown:
        return
    raise ManifestSchemaError(
        key_path,
        f"has unknown key(s) {', '.join(repr(key) for key in unknown)}; "
        f"expected only {', '.join(sorted(known_keys))}",
    )


def required_string(raw: dict[str, Any], key: str, key_path: str) -> str:
    """Fetch a required, non-blank string, or raise pointing at the key.

    Raises:
        ManifestSchemaError: With the offending key path.
    """
    if key not in raw:
        raise ManifestSchemaError(f"{key_path}.{key}", "is required but missing")
    return _as_string(raw[key], f"{key_path}.{key}")


def optional_string(raw: dict[str, Any], key: str, key_path: str) -> str | None:
    """Fetch an optional, non-blank string, or None when the key is absent.

    An explicit ``null`` is treated as absent — YAML users write it to mean
    "unset", and rejecting it would be pedantry rather than protection.

    Raises:
        ManifestSchemaError: With the offending key path.
    """
    if key not in raw or raw[key] is None:
        return None
    return _as_string(raw[key], f"{key_path}.{key}")


def _as_string(value: Any, key_path: str) -> str:
    if not isinstance(value, str):
        raise ManifestSchemaError(key_path, f"expected a string, got {describe_kind(value)}")
    if not value.strip():
        raise ManifestSchemaError(key_path, "is empty")
    return value
