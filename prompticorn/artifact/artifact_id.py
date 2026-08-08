"""The identity of one released artifact (PRO-107).

An ``ArtifactId`` names *what an org released* — "the ACME security agent
2.1.0". It is always pinned to an exact version, which is what a lock file
records.

Not to be confused with :class:`prompticorn.content.unit_id.UnitId`, which
addresses *where bytes live inside* an artifact (``agent/architect/minimal``).
An artifact contains one or more units. Keeping the two apart is what lets an
org version an artifact as a unit of release while the resolver still addresses
individual variants — so the two types share no base class and are accepted
nowhere interchangeably.

The content digest is deliberately **not** a field here; see
:class:`~prompticorn.artifact.pinned_artifact.PinnedArtifact`.
"""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.artifact.errors import InvalidArtifactIdError, InvalidSemanticVersionError
from prompticorn.artifact.naming import (
    DEFAULT_NAMESPACE,
    VERSION_SEPARATOR,
    render_coordinate,
    split_identity,
    validate_name,
    validate_namespace,
)
from prompticorn.artifact.semantic_version import SemanticVersion


@dataclass(frozen=True)
class ArtifactId:
    """A namespaced, versioned artifact identity.

    Immutable and hashable, so ids work as dict keys and set members — which is
    how a lock file indexes them.

    Attributes:
        namespace: Publishing namespace. Always ``local`` today; the field
            exists now so that adding real namespaces later is not a migration.
        name: The artifact's name within its namespace.
        version: The exact released version. Never a range — a range belongs to
            :class:`~prompticorn.artifact.artifact_requirement.ArtifactRequirement`.
    """

    namespace: str
    name: str
    version: SemanticVersion

    @classmethod
    def parse(cls, raw_id: str) -> ArtifactId:
        """Parse ``[namespace/]name@version``.

        The namespace defaults to ``local`` when omitted, so ``acme-sec@2.1.0``
        and ``local/acme-sec@2.1.0`` parse to the same value — but only the
        second form is ever rendered.

        Args:
            raw_id: The candidate id.

        Returns:
            The parsed value object.

        Raises:
            InvalidArtifactIdError: With a reason naming what to fix, including
                when the version half is not valid semver.
        """
        namespace, name, version_text = split_identity(raw_id)
        try:
            version = SemanticVersion.parse(version_text)
        except InvalidSemanticVersionError as exc:
            # Re-typed so a caller parsing ids catches one exception type, and
            # the message names the id the author actually wrote.
            raise InvalidArtifactIdError(raw_id, f"version {version_text!r} {exc.reason}") from exc
        return cls(namespace=namespace, name=name, version=version)

    @classmethod
    def local(cls, name: str, version: SemanticVersion) -> ArtifactId:
        """Build an id in the default ``local`` namespace.

        The convenience constructor for the only namespace that exists today.
        Validates ``name``, so it cannot be used to smuggle in a coordinate that
        :meth:`parse` would reject.
        """
        rendered = f"{name}{VERSION_SEPARATOR}{version.render()}"
        validate_name(rendered, name)
        return cls(namespace=DEFAULT_NAMESPACE, name=name, version=version)

    def __post_init__(self) -> None:
        """Validate coordinates supplied by direct construction.

        Without this, ``ArtifactId("ACME", "x", v)`` would bypass the grammar
        that :meth:`parse` enforces, and render an id that cannot be parsed back.
        """
        rendered = f"{self.namespace}/{self.name}{VERSION_SEPARATOR}{self.version.render()}"
        validate_namespace(rendered, self.namespace)
        validate_name(rendered, self.name)

    @property
    def coordinate(self) -> str:
        """The ``namespace/name`` half, without the version.

        This is what "the same artifact, different versions" compares on.
        """
        return render_coordinate(self.namespace, self.name)

    def render(self) -> str:
        """The canonical string form. ``parse(render())`` round-trips.

        The namespace is always present, even when it is the default.
        """
        return f"{self.coordinate}{VERSION_SEPARATOR}{self.version.render()}"

    def __str__(self) -> str:
        return self.render()
