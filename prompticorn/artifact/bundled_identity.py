"""Artifact identities for bundled content (PRO-108).

Gives every unit the resolver carries an :class:`ArtifactId`, so identity is
present from day one rather than retrofitted once real versioning exists.

Why names are kind-qualified
----------------------------

The ticket describes bundled identity as ``local/<name>@<version>``. A bare name
does not survive contact with the bundled tree: **10 names are used by two kinds
at once** — ``code`` is both an agent and a workflow, ``threat-modeling`` is both
a skill and a workflow, and so on. Under a bare-name scheme those distinct
artifacts collapse onto one identity, which is the exact conflation the artifact
model exists to prevent.

So the name carries its kind: ``agent.code`` and ``workflow.code`` are different
artifacts, as they should be. The namespace stays ``local``.

Artifact, not unit
------------------

An artifact is the *named thing*; its units are the variants inside it. So
``skill/threat-modeling/minimal`` and ``skill/threat-modeling/verbose`` are two
units of the single artifact ``local/skill.threat-modeling@<version>``. This is
what lets an org release "the ACME security agent" as one versioned thing while
the resolver still addresses each variant — the premise PRO-107 was built on.
"""

from __future__ import annotations

from collections.abc import Sequence

from prompticorn.artifact.artifact_id import ArtifactId
from prompticorn.artifact.naming import DEFAULT_NAMESPACE, VERSION_SEPARATOR
from prompticorn.artifact.package_version import bundled_version
from prompticorn.artifact.semantic_version import SemanticVersion
from prompticorn.content.unit_id import SEPARATOR as UNIT_SEPARATOR
from prompticorn.content.unit_id import UnitId
from prompticorn.content.unit_kind import UnitKind

_NAME_SEPARATOR = "."

# The token a variant-addressed kind ends its template with. Deriving the set of
# such kinds from `UnitKind.template` rather than restating it here means adding
# a variant to a kind cannot leave this module silently wrong.
_VARIANT_TOKEN = "{variant}"


def _carries_variant(kind: UnitKind) -> bool:
    """Whether this kind's last ID segment is a variant rather than a name."""
    return kind.template.endswith(_VARIANT_TOKEN)


class BundledIdentity:
    """Assigns :class:`ArtifactId`s to bundled content.

    Stateless apart from the version, so one instance can serve a whole process.

    Example:
        >>> identity = BundledIdentity()
        >>> identity.for_unit(UnitId.parse("skill/threat-modeling/minimal")).name
        'skill.threat-modeling'
    """

    def __init__(self, version: SemanticVersion | None = None) -> None:
        """Initialise with the version bundled artifacts are published under.

        Args:
            version: Override for the package version. Defaults to the
                translated distribution version.
        """
        self._version = version if version is not None else bundled_version()

    @property
    def version(self) -> SemanticVersion:
        """The version every bundled artifact is published under."""
        return self._version

    @property
    def namespace(self) -> str:
        """Always ``local`` today. Real namespaces arrive without a format break."""
        return DEFAULT_NAMESPACE

    def for_unit(self, unit_id: UnitId) -> ArtifactId:
        """The identity of the artifact that ``unit_id`` belongs to.

        Every variant of one artifact maps to the same id — that is what makes
        the artifact, rather than the unit, the thing being versioned.
        """
        return self.for_parts(unit_id.kind, self._name_segments(unit_id))

    def for_parts(self, kind: UnitKind, names: Sequence[str]) -> ArtifactId:
        """The identity for a kind and its name segments, excluding any variant.

        For callers holding names rather than a parsed unit — notably the agent
        registry, whose subagent key has no variant in it at all.

        Args:
            kind: The kind of content.
            names: Name segments, variant excluded. ``("code",)`` for an agent,
                ``("code", "boilerplate")`` for a subagent.

        Returns:
            The artifact identity.

        Raises:
            InvalidArtifactIdError: If the resulting name is not a legal token.
        """
        return ArtifactId(
            namespace=DEFAULT_NAMESPACE,
            name=self.artifact_name(kind, names),
            version=self._version,
        )

    def for_registry_key(self, key: str) -> ArtifactId:
        """The identity behind an agent-registry key.

        The registry keys agents as ``"code"`` and subagents as
        ``"code/boilerplate"``. Translating that shape lives here, in the one
        module that owns identity, rather than being re-derived by the registry
        and by discovery separately.

        Args:
            key: A registry key, with at most one ``/``.

        Returns:
            The artifact identity.

        Raises:
            InvalidArtifactIdError: If the key does not yield a legal name.
        """
        agent_name, separator, subagent_name = key.partition(UNIT_SEPARATOR)
        if separator:
            return self.for_parts(UnitKind.SUBAGENT, (agent_name, subagent_name))
        return self.for_parts(UnitKind.AGENT, (agent_name,))

    def for_coordinate(self, coordinate: str) -> ArtifactId:
        """The identity of an already-qualified ``namespace/name``. (PRO-111)

        What a manifest declaration resolves to: the declaration names the
        coordinate and the range, and this supplies the exact version the
        bundled content is published at.

        Args:
            coordinate: ``namespace/name``, as produced by
                :attr:`ArtifactRequirement.coordinate`.

        Returns:
            The artifact identity at this instance's version.

        Raises:
            InvalidArtifactIdError: If the coordinate is not well-formed.
        """
        return ArtifactId.parse(f"{coordinate}{VERSION_SEPARATOR}{self._version.render()}")

    @staticmethod
    def artifact_name(kind: UnitKind, names: Sequence[str]) -> str:
        """The kind-qualified artifact name, e.g. ``subagent.code.boilerplate``.

        Dots rather than slashes because a slash separates namespace from name
        in the serialised form, and because ``.`` is already in the id charset —
        so the qualified name needs no widening of the grammar.
        """
        return _NAME_SEPARATOR.join((kind.value, *names))

    @staticmethod
    def _name_segments(unit_id: UnitId) -> tuple[str, ...]:
        """The segments that name the artifact, with any trailing variant removed."""
        if _carries_variant(unit_id.kind):
            return unit_id.segments[:-1]
        return unit_id.segments
