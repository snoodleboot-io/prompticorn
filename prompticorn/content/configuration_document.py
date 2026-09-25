"""A configuration YAML resolved through the layer stack, and validated (PRO-165).

`read_configuration` returns text, and every consumer used to hand that text
straight to ``yaml.safe_load`` and index the result. That was sound while the
only possible source was a file in the package, valid by construction and
reviewed before release. A project layer can now supply ``personas/personas.yaml``
or ``configurations/agent_skill_mapping.yaml``, so the text is user input — and a
wrong-shaped document loaded without checks does not fail, it *succeeds* into an
empty mapping, and the build quietly emits every agent instead of the fifteen
that were asked for.

This is the boundary where that stops. It resolves the unit, parses it, and
insists it is a mapping; a caller adds whatever further structure its own
document requires. Failures name the file **and the layer it came from**, because
with a stack in play "personas.yaml is wrong" does not say which personas.yaml.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import yaml

from prompticorn.content.content_resolver import default_resolver
from prompticorn.content.errors import MalformedConfigurationError
from prompticorn.content.unit_id import UnitId

# Reported when nothing in the stack carries the unit. Reachable only for a
# genuinely absent configuration, which raises UnitNotFoundError first — kept so
# the location can never be rendered as None.
UNKNOWN_LOCATION = "<unresolved>"


@dataclass(frozen=True)
class ConfigurationDocument:
    """One parsed ``configuration/{name}`` unit, and where it came from.

    Attributes:
        name: The configuration's unit name, e.g. ``personas``.
        layer: The layer that supplied it.
        location: The file it was read from, for error messages.
        data: The parsed mapping.
    """

    name: str
    layer: str
    location: str
    data: dict[str, Any]

    @classmethod
    def load(cls, name: str) -> ConfigurationDocument:
        """Resolve, parse and shape-check ``configuration/{name}``.

        Args:
            name: The configuration's unit name.

        Returns:
            The parsed document, with the layer that supplied it.

        Raises:
            UnitNotFoundError: If no layer carries it. Absence is a different
                condition from being present and wrong, and consumers treat the
                two differently.
            MalformedConfigurationError: If it is not valid YAML, or not a
                mapping at the top level.
        """
        resolver = default_resolver()
        unit_id = UnitId.parse(f"configuration/{name}")
        source = resolver.owner_of(unit_id)
        layer = source.name if source is not None else "unknown"
        text = resolver.read(unit_id)

        document = cls(name=name, layer=layer, location=_locate(source, unit_id), data={})
        try:
            parsed = yaml.safe_load(text)
        except yaml.YAMLError as error:
            raise document.invalid(f"it is not valid YAML: {error}") from error

        # An empty document is a mapping with nothing in it, not a shape error:
        # a file that is all comments is a legitimate way to say "no entries".
        if parsed is None:
            parsed = {}
        if not isinstance(parsed, Mapping):
            raise document.invalid(
                f"the top level must be a mapping of keys to values, not {type(parsed).__name__}"
            )
        return cls(name=name, layer=layer, location=document.location, data=dict(parsed))

    def invalid(self, reason: str) -> MalformedConfigurationError:
        """The error to raise about this document, with its origin attached.

        Returned rather than raised so a caller's own structural checks read as
        ``raise document.invalid(...)`` at the point the check fails, and every
        message carries the same file and layer without restating them.
        """
        return MalformedConfigurationError(
            name=self.name, layer=self.layer, location=self.location, reason=reason
        )

    def require_mapping(self, key: str) -> dict[str, Any]:
        """The value at ``key``, insisting it is a non-empty mapping.

        Non-empty because the documents this is used for exist to hold entries.
        An empty ``personas:`` block parses, loads, and then filters nothing —
        which is indistinguishable at the output from having asked for every
        agent, and is the failure this whole boundary exists to catch.

        Raises:
            MalformedConfigurationError: If the key is missing, not a mapping,
                or empty.
        """
        if key not in self.data:
            raise self.invalid(f"it has no {key!r} section")
        value = self.data[key]
        if not isinstance(value, Mapping):
            raise self.invalid(
                f"{key!r} must be a mapping of names to definitions, not {type(value).__name__}"
            )
        if not value:
            raise self.invalid(f"{key!r} is empty, so it defines nothing")
        return dict(value)

    def require_mapping_values(self, key: str | None = None) -> None:
        """Insist every value in the document (or in one section) is a mapping.

        Raises:
            MalformedConfigurationError: Naming the first offending key, so the
                message points at a line rather than at the file.
        """
        section = self.data if key is None else self.data[key]
        where = "the top level" if key is None else repr(key)
        for name, value in section.items():
            if not isinstance(value, Mapping):
                raise self.invalid(
                    f"{name!r} under {where} must be a mapping, not {type(value).__name__}"
                )

    def require_string_list(self, key: str) -> None:
        """Insist ``key``, if present, is a list of strings.

        Raises:
            MalformedConfigurationError: If it is present and some other shape.
        """
        if key not in self.data:
            return
        value = self.data[key]
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise self.invalid(f"{key!r} must be a list of names")


def _locate(source: Any, unit_id: UnitId) -> str:
    """The file a source reads a unit from, when it can name one.

    Duck-typed on ``path_for`` rather than isinstance-checked, because a source
    that resolves from something other than a filesystem is entitled not to have
    a path, and the unit id is a usable location in that case.
    """
    path_for = getattr(source, "path_for", None)
    if path_for is None:
        return unit_id.render() if source is not None else UNKNOWN_LOCATION
    path = path_for(unit_id)
    return str(path) if path is not None else unit_id.render()
