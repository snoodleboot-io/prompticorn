"""Shared grammar for the ``namespace/name`` half of an artifact id (PRO-107).

Function-only, like :mod:`prompticorn.content.digest`: both
:class:`~prompticorn.artifact.artifact_id.ArtifactId` and
:class:`~prompticorn.artifact.artifact_requirement.ArtifactRequirement` write the
same coordinate and must agree on it byte for byte. Having one of them own the
grammar and the other borrow it would invite them to drift.
"""

from __future__ import annotations

import re

from prompticorn.artifact.errors import InvalidArtifactIdError

DEFAULT_NAMESPACE = "local"

NAMESPACE_SEPARATOR = "/"
VERSION_SEPARATOR = "@"

# Deliberately the same charset as `UnitId`'s segments, and lowercase for the
# same reason: `acme/Agent` and `acme/agent` are distinct dict keys but the same
# file on APFS and NTFS, so accepting both yields resolution that behaves
# differently on macOS than on Linux. Rejecting surfaces the ambiguity at
# authoring time instead of as a platform-specific bug later.
_TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def split_identity(raw_id: str) -> tuple[str, str, str]:
    """Split ``[namespace/]name@version`` into its three parts.

    The version half is returned unparsed: an id pins an exact version while a
    requirement carries a range, and this grammar is common to both.

    Args:
        raw_id: The candidate id or requirement.

    Returns:
        ``(namespace, name, version_text)``, with ``namespace`` defaulted to
        ``local`` when the input omits it.

    Raises:
        InvalidArtifactIdError: With a reason naming what to fix.
    """
    if not isinstance(raw_id, str):
        raise InvalidArtifactIdError(str(raw_id), f"expected a string, got {type(raw_id).__name__}")
    if not raw_id:
        raise InvalidArtifactIdError(raw_id, "is empty")
    if raw_id != raw_id.strip():
        raise InvalidArtifactIdError(raw_id, "has leading or trailing whitespace")

    if VERSION_SEPARATOR not in raw_id:
        raise InvalidArtifactIdError(
            raw_id, f"is missing {VERSION_SEPARATOR!r}; expected namespace/name@version"
        )
    if raw_id.count(VERSION_SEPARATOR) > 1:
        raise InvalidArtifactIdError(raw_id, f"contains more than one {VERSION_SEPARATOR!r}")

    coordinate, version_text = raw_id.split(VERSION_SEPARATOR)
    if not version_text:
        raise InvalidArtifactIdError(raw_id, "has no version after '@'")

    namespace, name = _split_coordinate(raw_id, coordinate)
    return namespace, name, version_text


def _split_coordinate(raw_id: str, coordinate: str) -> tuple[str, str]:
    """Split the ``[namespace/]name`` half, applying the default namespace."""
    if not coordinate:
        raise InvalidArtifactIdError(raw_id, "has no name before '@'")
    if coordinate.count(NAMESPACE_SEPARATOR) > 1:
        raise InvalidArtifactIdError(
            raw_id,
            f"contains more than one {NAMESPACE_SEPARATOR!r}; expected at most namespace/name",
        )

    if NAMESPACE_SEPARATOR in coordinate:
        namespace, name = coordinate.split(NAMESPACE_SEPARATOR)
    else:
        namespace, name = DEFAULT_NAMESPACE, coordinate

    validate_namespace(raw_id, namespace)
    validate_name(raw_id, name)
    return namespace, name


def validate_namespace(raw_id: str, namespace: str) -> None:
    """Reject a namespace that is empty or outside the token charset.

    Raises:
        InvalidArtifactIdError: With a reason naming what to fix.
    """
    _validate_token(raw_id, namespace, "namespace")


def validate_name(raw_id: str, name: str) -> None:
    """Reject a name that is empty or outside the token charset.

    Raises:
        InvalidArtifactIdError: With a reason naming what to fix.
    """
    _validate_token(raw_id, name, "name")


def _validate_token(raw_id: str, token: str, label: str) -> None:
    if not token:
        raise InvalidArtifactIdError(raw_id, f"has an empty {label}")
    if _TOKEN_RE.match(token):
        return
    if token != token.lower():
        raise InvalidArtifactIdError(
            raw_id,
            f"{label} {token!r} contains uppercase; artifact ids are lowercase so that "
            "resolution does not depend on filesystem case sensitivity",
        )
    raise InvalidArtifactIdError(
        raw_id, f"{label} {token!r} is not of the form [a-z0-9][a-z0-9._-]*"
    )


def render_coordinate(namespace: str, name: str) -> str:
    """Render the ``namespace/name`` half.

    The namespace is always emitted, even when it is the default. That is the
    whole point of defaulting it at parse time rather than at render time: every
    serialised form already carries a namespace, so introducing real ones later
    changes what the field contains, never whether it is there.
    """
    return f"{namespace}{NAMESPACE_SEPARATOR}{name}"
