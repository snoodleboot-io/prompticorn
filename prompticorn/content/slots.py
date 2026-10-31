"""Parameter slots: let a layer fill a named hole without owning the body (PRO-118).

Replacement is all-or-nothing — the highest layer carrying a unit wins outright
(PRO-117). That is the right default and the wrong only option: a team that
wants its own lint command should not have to adopt, and then maintain, the
whole of ``code-review-practices``. A slot is the structured half of
customisation, and covers the common cases (a command, a deploy target, one
checklist line).

**Slots are declared, never inferred.** ``configurations/slots.yaml`` in the
bundled layer says which slots each unit offers; a layer fills them through
``configurations/slot-values.yaml``. Nothing scans bodies for placeholder-shaped
text, so an upstream edit cannot silently create a slot (handing layers a hook
nobody designed) or destroy one (silently dropping a value a layer relies on).

Declaration lives centrally rather than in each unit's frontmatter because
frontmatter is not universal here: 9 of 127 skills carry any, and 0 of 34
conventions, and skills are deliberately frontmatter-free in source — the
emitter synthesises theirs. Declaring in frontmatter would have meant adding it
to ~152 content files and moving the golden corpus for a reason unrelated to
this feature.

The placeholder is ``<<slot:name>>``, not ``{{slot:name}}``, because builders
render bodies through Jinja2 with ``{{ }}`` delimiters: a leaked brace
placeholder would die inside a template engine with a message about expressions
rather than about slots.
"""

from __future__ import annotations

import re
import warnings
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from prompticorn.content.configuration_document import ConfigurationDocument
from prompticorn.content.errors import (
    RequiredSlotUnfilledError,
    UndeclaredSlotError,
    UnfilledSlotWarning,
)
from prompticorn.content.unit_id import UnitId

#: Declarations: which slots a unit offers. Bundled layer owns this.
DECLARATIONS_UNIT = "slots"

#: Values: what a layer fills them with. Any layer may carry it; first-wins, so
#: the highest layer's document replaces rather than merges with a lower one —
#: the same rule as unit replacement, for the same reason.
VALUES_UNIT = "slot-values"

#: ``<<slot:name>>``. Names match segment rules: lowercase, digits, dash,
#: underscore — so a placeholder cannot smuggle regex or path syntax.
PLACEHOLDER = re.compile(r"<<slot:([a-z0-9][a-z0-9_-]*)>>")

#: Escaped wherever they appear: each can open inline markdown structure.
_INLINE_SPECIALS = frozenset("\\`*_[]<>|")

#: Escaped only in first position: each opens a block, but only at line start.
_BLOCK_STARTERS = frozenset("#-+>=")

_ORDERED_LIST_START = re.compile(r"^\d+[.)]")


@dataclass(frozen=True)
class SlotDeclaration:
    """One slot a unit offers.

    Attributes:
        name: The slot's name, as it appears in ``<<slot:name>>``.
        default: Rendered when no layer fills it. ``None`` means undefaulted.
        required: When true, an unfilled slot fails the build instead of
            rendering empty. Opt-in, so adding a slot upstream does not break
            every layer below that has not heard of it yet.
    """

    name: str
    default: str | None = None
    required: bool = False


def escape_value(value: str) -> str:
    """A slot value rendered as literal text, structurally inert.

    A value is interpolated into someone else's document, so it must not be
    able to rewrite the parts around it. Without this a value of
    ``"x\\n\\n# Ignore all previous rules"`` turns a slot into a way to append
    a heading to the host artifact.

    Whitespace runs — newlines included — collapse to single spaces, so a value
    can never begin a new block; then inline punctuation is backslash-escaped,
    and a leading block starter escaped too in case the slot sits at line start.
    """
    collapsed = " ".join(str(value).split())
    if not collapsed:
        return ""
    escaped = "".join(f"\\{char}" if char in _INLINE_SPECIALS else char for char in collapsed)
    if escaped[0] in _BLOCK_STARTERS or _ORDERED_LIST_START.match(escaped):
        escaped = f"\\{escaped}"
    return escaped


@dataclass(frozen=True)
class SlotSchema:
    """Every unit's declared slots, keyed by rendered unit id."""

    declarations: Mapping[str, Mapping[str, SlotDeclaration]]

    @classmethod
    def empty(cls) -> SlotSchema:
        return cls(declarations={})

    @classmethod
    def load(cls) -> SlotSchema:
        """Read ``configuration/slots``, or an empty schema when absent.

        Absent is normal and not an error: a tree that declares no slots is the
        default state, and the feature should cost nothing until used.
        """
        document = _load_optional(DECLARATIONS_UNIT)
        if document is None:
            return cls.empty()

        declarations: dict[str, dict[str, SlotDeclaration]] = {}
        for raw_unit, slots in document.data.items():
            unit_id = _parse_unit_key(document, raw_unit)
            if not isinstance(slots, Mapping):
                raise document.invalid(
                    f"{raw_unit!r} must be a mapping of slot names to definitions, "
                    f"not {type(slots).__name__}"
                )
            declarations[unit_id.render()] = {
                name: _parse_declaration(document, raw_unit, name, body)
                for name, body in slots.items()
            }
        return cls(declarations=declarations)

    def for_unit(self, unit_id: UnitId) -> Mapping[str, SlotDeclaration]:
        return self.declarations.get(unit_id.render(), {})


@dataclass(frozen=True)
class SlotValues:
    """What the winning layer fills slots with, keyed by rendered unit id."""

    values: Mapping[str, Mapping[str, str]]
    layer: str = "none"

    @classmethod
    def empty(cls) -> SlotValues:
        return cls(values={})

    @classmethod
    def load(cls) -> SlotValues:
        """Read ``configuration/slot-values``, or empty when absent."""
        document = _load_optional(VALUES_UNIT)
        if document is None:
            return cls.empty()

        values: dict[str, dict[str, str]] = {}
        for raw_unit, slots in document.data.items():
            unit_id = _parse_unit_key(document, raw_unit)
            if not isinstance(slots, Mapping):
                raise document.invalid(
                    f"{raw_unit!r} must be a mapping of slot names to values, "
                    f"not {type(slots).__name__}"
                )
            values[unit_id.render()] = {name: str(value) for name, value in slots.items()}
        return cls(values=values, layer=document.layer)

    def for_unit(self, unit_id: UnitId) -> Mapping[str, str]:
        return self.values.get(unit_id.render(), {})


def fill(unit_id: UnitId, text: str, schema: SlotSchema, values: SlotValues) -> str:
    """``text`` with every ``<<slot:name>>`` replaced.

    A filled slot takes the layer's value; an unfilled one takes its declared
    default; an unfilled slot with no default renders empty and warns, unless it
    is declared required, which fails.

    Raises:
        UndeclaredSlotError: If a layer supplies a value for a slot the unit
            does not declare, or the body references an undeclared slot. Both
            mean the body and the declaration have diverged, and guessing which
            is right is how a value silently stops applying.
        RequiredSlotUnfilledError: If a required slot has no value.
    """
    declared = schema.for_unit(unit_id)
    supplied = values.for_unit(unit_id)

    for name in supplied:
        if name not in declared:
            raise UndeclaredSlotError(
                unit_id=unit_id.render(), slot=name, layer=values.layer, declared=sorted(declared)
            )

    def resolve(match: re.Match[str]) -> str:
        name = match.group(1)
        declaration = declared.get(name)
        if declaration is None:
            raise UndeclaredSlotError(
                unit_id=unit_id.render(), slot=name, layer="body", declared=sorted(declared)
            )
        if name in supplied:
            return escape_value(supplied[name])
        if declaration.default is not None:
            return escape_value(declaration.default)
        if declaration.required:
            raise RequiredSlotUnfilledError(unit_id=unit_id.render(), slot=name)
        warnings.warn(
            f"slot {name!r} in {unit_id.render()} has no value and no default, "
            f"so it renders empty; fill it in configurations/{VALUES_UNIT}.yaml "
            f"or give it a default",
            UnfilledSlotWarning,
            stacklevel=2,
        )
        return ""

    return PLACEHOLDER.sub(resolve, text)


def _load_optional(name: str) -> ConfigurationDocument | None:
    """The configuration document, or None when no layer carries it."""
    from prompticorn.content.errors import UnitNotFoundError

    try:
        return ConfigurationDocument.load(name)
    except UnitNotFoundError:
        return None


def _parse_unit_key(document: ConfigurationDocument, raw: str) -> UnitId:
    """A top-level key parsed as a unit id, with the document named on failure."""
    from prompticorn.content.errors import InvalidUnitIdError

    try:
        return UnitId.parse(raw)
    except InvalidUnitIdError as error:
        raise document.invalid(f"{raw!r} is not a unit id: {error}") from error


def _parse_declaration(
    document: ConfigurationDocument, raw_unit: str, name: str, body: Any
) -> SlotDeclaration:
    """One slot definition, insisting on its shape."""
    if not isinstance(body, Mapping):
        raise document.invalid(
            f"slot {name!r} of {raw_unit!r} must be a mapping with optional "
            f"'default' and 'required' keys, not {type(body).__name__}"
        )
    unknown = sorted(set(body) - {"default", "required"})
    if unknown:
        raise document.invalid(
            f"slot {name!r} of {raw_unit!r} has unknown key(s) {unknown}; "
            f"only 'default' and 'required' are understood"
        )
    default = body.get("default")
    required = body.get("required", False)
    if not isinstance(required, bool):
        raise document.invalid(
            f"'required' for slot {name!r} of {raw_unit!r} must be true or false, "
            f"not {type(required).__name__}"
        )
    if required and default is not None:
        raise document.invalid(
            f"slot {name!r} of {raw_unit!r} is required and also has a default; "
            f"a default means it can never be unfilled, so one of the two is wrong"
        )
    return SlotDeclaration(
        name=name, default=None if default is None else str(default), required=required
    )
