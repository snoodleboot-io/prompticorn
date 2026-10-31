"""Collect patches from every layer and apply them in a defined order (PRO-119)."""

from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any

import yaml

from prompticorn.content.errors import (
    ConflictingPatchWarning,
    MalformedConfigurationError,
    PatchMatchedNothingError,
)
from prompticorn.content.patches.append_patch import AppendPatch
from prompticorn.content.patches.patch_operation import PatchOperation
from prompticorn.content.patches.prepend_patch import PrependPatch
from prompticorn.content.patches.replace_section_patch import ReplaceSectionPatch
from prompticorn.content.unit_id import UnitId

if TYPE_CHECKING:
    from prompticorn.content.content_resolver import ContentResolver

#: The per-layer document patches are declared in.
PATCHES_UNIT = "patches"

_OPERATIONS = {
    "append": AppendPatch,
    "prepend": PrependPatch,
    "replace_section": ReplaceSectionPatch,
}

_COMMON_KEYS = frozenset({"op", "units", "content", "allow_empty"})
_OPERATION_KEYS = {"replace_section": frozenset({"heading"})}


class PatchApplier:
    """Every layer's patches, in order, applied to a unit's resolved text.

    **Patches are collected from every layer, not just the winning one.** This
    is the rule the whole feature rests on: a project that replaces a unit must
    not thereby discard an org's policy patch, or "enforced by the org layer"
    would mean "enforced until someone overrides the file", which is not
    enforcement. It is also why patches cannot ride
    :class:`ConfigurationDocument`, whose first-wins load is exactly right for
    slot values and exactly wrong here.

    Order is ascending layer precedence, then document order within a layer. So
    a higher layer's patch applies *last* and therefore wins a conflict, which
    matches how every other precedence decision here resolves.
    """

    def __init__(self, patches: Sequence[PatchOperation] = ()) -> None:
        self._patches = tuple(patches)
        self._matched: set[int] = set()

    @property
    def patches(self) -> tuple[PatchOperation, ...]:
        return self._patches

    @classmethod
    def collect(cls, resolver: ContentResolver) -> PatchApplier:
        """Read ``configuration/patches`` from every source in the stack.

        The resolver holds sources highest-precedence first, so they are walked
        in reverse to get ascending precedence — lowest layer's patches apply
        first, highest last.
        """
        unit_id = UnitId.parse(f"configuration/{PATCHES_UNIT}")
        collected: list[PatchOperation] = []
        for source in reversed(resolver.sources):
            if not source.has(unit_id):
                continue
            collected.extend(_parse_document(source.name, source.read(unit_id)))
        return cls(collected)

    def for_unit(self, unit_id: UnitId) -> list[PatchOperation]:
        return [patch for patch in self._patches if patch.matches(unit_id)]

    def apply(self, unit_id: UnitId, text: str) -> str:
        """``text`` with every patch targeting this unit applied, in order."""
        applicable = self.for_unit(unit_id)
        if not applicable:
            return text

        self._warn_on_contested_headings(unit_id, applicable)
        for patch in applicable:
            self._matched.add(id(patch))
            text = patch.apply(unit_id, text)
        return text

    def verify_all_matched(self) -> None:
        """Fail for any patch whose glob matched no unit in the whole build.

        Called once a build has resolved everything, because "matched nothing"
        is only knowable after the last unit: a patch is not unused until there
        is nothing left for it to be used on.

        Raises:
            PatchMatchedNothingError: Naming the patch and its glob.
        """
        for patch in self._patches:
            if patch.allow_empty or id(patch) in self._matched:
                continue
            raise PatchMatchedNothingError(
                patch=patch.describe(), units=patch.units, layer=patch.layer
            )

    @staticmethod
    def _warn_on_contested_headings(unit_id: UnitId, applicable: Sequence[PatchOperation]) -> None:
        """Warn when two patches replace the same heading; the last one wins.

        A warning and not an error because two layers legitimately caring about
        one section is normal in a deep stack, and the precedence rule already
        decides it. Silence is what is not acceptable: the losing layer's author
        would otherwise have no way to learn their rule stopped applying.
        """
        by_heading: dict[str, list[PatchOperation]] = {}
        for patch in applicable:
            heading = getattr(patch, "heading", None)
            if heading:
                by_heading.setdefault(heading.strip(), []).append(patch)
        for heading, contenders in by_heading.items():
            if len(contenders) > 1:
                names = ", ".join(patch.describe() for patch in contenders)
                warnings.warn(
                    f"{unit_id.render()} has {len(contenders)} patches replacing {heading!r} "
                    f"({names}); the last applies and the earlier ones are discarded",
                    ConflictingPatchWarning,
                    stacklevel=2,
                )


def _parse_document(layer: str, text: str) -> list[PatchOperation]:
    """One layer's ``patches.yaml`` as operations, in document order."""
    document = _Document(layer)
    try:
        parsed = yaml.safe_load(text)
    except yaml.YAMLError as error:
        raise document.invalid(f"it is not valid YAML: {error}") from error
    if parsed is None:
        return []
    if not isinstance(parsed, Mapping):
        raise document.invalid(
            f"the top level must be a mapping with a {PATCHES_UNIT!r} key, "
            f"not {type(parsed).__name__}"
        )
    entries = parsed.get(PATCHES_UNIT)
    if entries is None:
        raise document.invalid(f"it has no {PATCHES_UNIT!r} section")
    if not isinstance(entries, Sequence) or isinstance(entries, str):
        raise document.invalid(
            f"{PATCHES_UNIT!r} must be a list of operations, not {type(entries).__name__}"
        )
    return [_parse_entry(document, index, entry) for index, entry in enumerate(entries)]


def _parse_entry(document: _Document, index: int, raw: Any) -> PatchOperation:
    """One list entry as an operation, insisting on its shape."""
    where = f"{PATCHES_UNIT}[{index}]"
    if not isinstance(raw, Mapping):
        raise document.invalid(f"{where} must be a mapping, not {type(raw).__name__}")

    op = raw.get("op")
    if op not in _OPERATIONS:
        known = ", ".join(sorted(_OPERATIONS))
        raise document.invalid(f"{where} has op {op!r}; expected one of {known}")

    allowed = _COMMON_KEYS | _OPERATION_KEYS.get(op, frozenset())
    unknown = sorted(set(raw) - allowed)
    if unknown:
        raise document.invalid(
            f"{where} has unknown key(s) {unknown}; a {op!r} patch understands {sorted(allowed)}"
        )
    for required in ("units", "content"):
        if not raw.get(required):
            raise document.invalid(f"{where} has no {required!r}, which every patch needs")
    if op == "replace_section" and not raw.get("heading"):
        raise document.invalid(f"{where} is a replace_section patch with no 'heading' to anchor to")

    allow_empty = raw.get("allow_empty", False)
    if not isinstance(allow_empty, bool):
        raise document.invalid(
            f"{where} has 'allow_empty' of {type(allow_empty).__name__}; expected true or false"
        )

    kwargs: dict[str, Any] = {
        "units": str(raw["units"]),
        "content": str(raw["content"]),
        "layer": document.layer,
        "index": index,
        "allow_empty": allow_empty,
    }
    if op == "replace_section":
        kwargs["heading"] = str(raw["heading"])
    return _OPERATIONS[op](**kwargs)


class _Document:
    """Just enough of ConfigurationDocument to report errors the same way.

    Patches cannot use ConfigurationDocument itself — that resolves one winning
    document, and patches are collected from every layer — but an author
    debugging a bad patch file should still be told which layer's file is wrong.
    """

    def __init__(self, layer: str) -> None:
        self.layer = layer

    def invalid(self, reason: str) -> MalformedConfigurationError:
        return MalformedConfigurationError(
            name=PATCHES_UNIT,
            layer=self.layer,
            location=f"configurations/{PATCHES_UNIT}.yaml",
            reason=reason,
        )
