"""What a provider may know about the project it is providing for (PRO-117)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LayerContext:
    """The inputs every provider receives.

    Attributes:
        project_root: The project being built.
        config: Its loaded manifest, or empty when there is none yet.
        environment: Environment variables, passed in rather than read from
            ``os.environ`` inside providers — so a test can describe a machine
            without mutating the real process environment.
    """

    project_root: Path
    config: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, str] = field(default_factory=dict)
