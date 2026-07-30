"""The kinds of content unit an ID can address, and their arity (PRO-103)."""

from __future__ import annotations

from enum import Enum


class UnitKind(Enum):
    """A category of addressable content, and the shape its ID must take.

    These address **authored source** — a file in the bundled tree — not rendered
    output. That is why an agent takes no variant (it is authored as one
    ``prompt.md``) while a skill does (it is authored per variant). Rendered
    artifacts, which do vary by variant for every kind, get their own identity in
    the artifact-model work.

    Arity is part of the grammar rather than a downstream check: an ID whose
    shape disagrees with the content addresses nothing, so it is rejected at
    parse time instead of failing later as a confusing miss.
    """

    AGENT = "agent"
    SUBAGENT = "subagent"
    SKILL = "skill"
    WORKFLOW = "workflow"
    CONVENTION = "convention"
    CONFIGURATION = "configuration"

    @property
    def arities(self) -> tuple[int, ...]:
        """Valid segment counts *after* the kind prefix.

        ``workflow`` accepts both because a workflow may be addressed whole or
        by variant; every other kind has exactly one legal shape.
        """
        return _ARITIES[self]

    @property
    def discriminators(self) -> tuple[str, ...]:
        """Literal values the first segment must take, or empty if unconstrained.

        Only ``convention`` uses this: ``convention/core/{name}`` and
        ``convention/language/{language}`` are different namespaces that happen
        to share a prefix, and an unconstrained first segment would let
        ``convention/typo/foo`` parse cleanly and resolve to nothing.
        """
        return _DISCRIMINATORS.get(self, ())

    @property
    def template(self) -> str:
        """The grammar for this kind, for use in error messages."""
        return _TEMPLATES[self]


# Arities follow the bundled tree, verified against it rather than assumed.
# An agent is authored as a single `prompt.md` with no variant; skills and
# workflows are authored per variant. Addressing that disagrees with the content
# produces IDs that resolve to nothing, which is the failure the arity rule
# exists to prevent. (Corrected in PRO-104.)
_ARITIES: dict[UnitKind, tuple[int, ...]] = {
    UnitKind.AGENT: (1,),
    UnitKind.SUBAGENT: (3,),
    UnitKind.SKILL: (2,),
    UnitKind.WORKFLOW: (2,),
    UnitKind.CONVENTION: (2,),
    UnitKind.CONFIGURATION: (1,),
}

_DISCRIMINATORS: dict[UnitKind, tuple[str, ...]] = {
    UnitKind.CONVENTION: ("core", "language"),
}

_TEMPLATES: dict[UnitKind, str] = {
    UnitKind.AGENT: "agent/{agent}",
    UnitKind.SUBAGENT: "subagent/{agent}/{subagent}/{variant}",
    UnitKind.SKILL: "skill/{skill}/{variant}",
    UnitKind.WORKFLOW: "workflow/{workflow}/{variant}",
    UnitKind.CONVENTION: "convention/core/{name} or convention/language/{language}",
    UnitKind.CONFIGURATION: "configuration/{name}",
}
