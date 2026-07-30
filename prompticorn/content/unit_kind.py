"""The kinds of content unit an ID can address, and their arity (PRO-103)."""

from __future__ import annotations

from enum import Enum


class UnitKind(Enum):
    """A category of addressable content, and the shape its ID must take.

    Arity is part of the grammar rather than a downstream check: ``agent/foo``
    without a variant addresses nothing, so it is rejected at parse time instead
    of failing later with a confusing miss.
    """

    AGENT = "agent"
    SUBAGENT = "subagent"
    SKILL = "skill"
    WORKFLOW = "workflow"
    CONVENTION = "convention"
    PERSONA = "persona"
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


_ARITIES: dict[UnitKind, tuple[int, ...]] = {
    UnitKind.AGENT: (2,),
    UnitKind.SUBAGENT: (3,),
    UnitKind.SKILL: (1,),
    UnitKind.WORKFLOW: (1, 2),
    UnitKind.CONVENTION: (2,),
    UnitKind.PERSONA: (1,),
    UnitKind.CONFIGURATION: (1,),
}

_DISCRIMINATORS: dict[UnitKind, tuple[str, ...]] = {
    UnitKind.CONVENTION: ("core", "language"),
}

_TEMPLATES: dict[UnitKind, str] = {
    UnitKind.AGENT: "agent/{agent}/{variant}",
    UnitKind.SUBAGENT: "subagent/{agent}/{subagent}/{variant}",
    UnitKind.SKILL: "skill/{skill}",
    UnitKind.WORKFLOW: "workflow/{workflow}[/{variant}]",
    UnitKind.CONVENTION: "convention/core/{name} or convention/language/{language}",
    UnitKind.PERSONA: "persona/{persona}",
    UnitKind.CONFIGURATION: "configuration/{name}",
}
