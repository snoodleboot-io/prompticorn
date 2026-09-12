"""What applying a profile would change (PRO-132).

Shown before anything is written. Overwriting somebody's manifest without
telling them what moved is the behaviour that makes people stop trusting a tool
with their configuration, so the diff exists to be read rather than to be
complete — top-level keys, in the terms the manifest uses.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import yaml


@dataclass(frozen=True)
class KeyChange:
    """One top-level manifest key that differs.

    Attributes:
        key: The manifest key.
        before: Its current value, or None when it is being added.
        after: The value the profile would set, or None when it is removed.
    """

    key: str
    before: Any | None
    after: Any | None

    @property
    def is_addition(self) -> bool:
        return self.before is None and self.after is not None

    @property
    def is_removal(self) -> bool:
        return self.after is None and self.before is not None

    def describe(self) -> str:
        """One line, with values rendered compactly enough to scan."""
        marker = "+" if self.is_addition else "-" if self.is_removal else "~"
        if self.is_addition:
            return f"  {marker} {self.key}: {_render(self.after)}"
        if self.is_removal:
            return f"  {marker} {self.key}: {_render(self.before)} (removed)"
        return f"  {marker} {self.key}: {_render(self.before)} → {_render(self.after)}"


@dataclass(frozen=True)
class ConfigDiff:
    """Every top-level key that applying a profile would change."""

    changes: tuple[KeyChange, ...] = ()

    @classmethod
    def between(cls, before: dict[str, Any], after: dict[str, Any]) -> ConfigDiff:
        """Compare two manifests, key by key, in sorted order.

        Sorted so the same pair always renders the same way; a diff whose order
        depends on dict construction is one people cannot compare between runs.
        """
        changes = [
            KeyChange(key=key, before=before.get(key), after=after.get(key))
            for key in sorted(set(before) | set(after))
            if before.get(key) != after.get(key)
        ]
        return cls(changes=tuple(changes))

    @property
    def is_empty(self) -> bool:
        """Whether applying would change nothing."""
        return not self.changes

    def render(self) -> str:
        if self.is_empty:
            return "No change: the project already matches this profile."
        lines = [f"{len(self.changes)} key(s) would change:"]
        lines.extend(change.describe() for change in self.changes)
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.render()


# Long values are truncated rather than wrapped: the diff is a summary, and the
# authority on what a profile contains is `profile show`.
_MAX_RENDERED = 60


def _render(value: Any) -> str:
    if value is None:
        return "—"
    text = yaml.safe_dump(value, default_flow_style=True, sort_keys=True, width=10_000).strip()
    text = text.removesuffix("...").strip()
    if len(text) > _MAX_RENDERED:
        return f"{text[:_MAX_RENDERED]}…"
    return text
