"""What a manifest declares: an artifact plus an acceptable version range.

The manifest counterpart to :class:`~prompticorn.artifact.artifact_id.ArtifactId`
(PRO-107). A requirement says "some 2.x of the ACME security agent"; an id says
"exactly 2.1.0 of it".

They are separate types rather than one type with a ``SemanticVersion |
VersionRange`` field so that "is this pinned?" is answered by pyright rather than
at runtime. Resolution then reads as a type change — ``ArtifactRequirement`` in,
``ArtifactId`` out — and a manifest entry cannot reach a lock writer unpinned.
"""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.errors import InvalidArtifactIdError, InvalidVersionRangeError
from prompticorn.artifact.naming import (
    DEFAULT_NAMESPACE,
    VERSION_SEPARATOR,
    render_coordinate,
    split_identity,
    validate_name,
    validate_namespace,
)
from prompticorn.artifact.version_range import VersionRange


@dataclass(frozen=True)
class ArtifactRequirement:
    """A declared dependency on some acceptable version of an artifact.

    Attributes:
        namespace: Publishing namespace, defaulted to ``local`` at parse time.
        name: The artifact's name within its namespace.
        version_range: The versions this requirement will accept.
    """

    namespace: str
    name: str
    version_range: VersionRange

    @classmethod
    def parse(cls, raw_requirement: str) -> ArtifactRequirement:
        """Parse ``[namespace/]name@range``, e.g. ``acme/security-agent@>=2.1,<3``.

        Args:
            raw_requirement: The candidate requirement.

        Returns:
            The parsed value object.

        Raises:
            InvalidArtifactIdError: With a reason naming what to fix, including
                when the range half does not parse.
        """
        namespace, name, range_text = split_identity(raw_requirement)
        try:
            version_range = VersionRange.parse(range_text)
        except InvalidVersionRangeError as exc:
            raise InvalidArtifactIdError(
                raw_requirement, f"range {range_text!r} {exc.reason}"
            ) from exc
        return cls(namespace=namespace, name=name, version_range=version_range)

    @classmethod
    def local(cls, name: str, version_range: VersionRange) -> ArtifactRequirement:
        """Build a requirement in the default ``local`` namespace."""
        rendered = f"{name}{VERSION_SEPARATOR}{version_range.render()}"
        validate_name(rendered, name)
        return cls(namespace=DEFAULT_NAMESPACE, name=name, version_range=version_range)

    def __post_init__(self) -> None:
        """Validate coordinates supplied by direct construction."""
        rendered = f"{self.namespace}/{self.name}{VERSION_SEPARATOR}{self.version_range.render()}"
        validate_namespace(rendered, self.namespace)
        validate_name(rendered, self.name)

    @property
    def coordinate(self) -> str:
        """The ``namespace/name`` half, without the range."""
        return render_coordinate(self.namespace, self.name)

    def matches(self, candidate: ArtifactId) -> bool:
        """Whether ``candidate`` satisfies this requirement.

        The coordinate must match exactly before the version is considered: two
        artifacts sharing a name across namespaces are different artifacts, and
        comparing only versions would let one silently satisfy a requirement on
        the other.
        """
        if candidate.coordinate != self.coordinate:
            return False
        return self.version_range.contains(candidate.version)

    def render(self) -> str:
        """The canonical string form. ``parse(render())`` round-trips."""
        return f"{self.coordinate}{VERSION_SEPARATOR}{self.version_range.render()}"

    def __str__(self) -> str:
        return self.render()
