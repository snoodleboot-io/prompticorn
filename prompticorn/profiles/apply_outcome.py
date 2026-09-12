"""The result of applying a profile (PRO-132)."""

from __future__ import annotations

from dataclasses import dataclass

from prompticorn.profiles.config_diff import ConfigDiff
from prompticorn.profiles.profile import Profile


@dataclass(frozen=True)
class ApplyOutcome:
    """What applying a profile did, or would have done.

    Attributes:
        profile: The version applied.
        diff: What changed against the manifest that was there before.
        written: Whether anything was written. False for a dry run.
        had_existing: Whether the project already had a manifest — the
            difference between configuring a project and reconfiguring one.
    """

    profile: Profile
    diff: ConfigDiff
    written: bool
    had_existing: bool

    @property
    def changed_nothing(self) -> bool:
        """Whether the project already matched this profile."""
        return self.diff.is_empty

    def render(self) -> str:
        if self.changed_nothing:
            return f"{self.profile} — the project already matches it."
        verb = "Would apply" if not self.written else "Applied"
        return f"{verb} {self.profile}.\n\n{self.diff.render()}"

    def __str__(self) -> str:
        return self.render()
