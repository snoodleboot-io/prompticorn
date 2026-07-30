"""The bundled tree, behind the ContentSource interface (PRO-104).

The only implementation in this milestone, so behaviour is unchanged by
construction: it reads exactly the files the loaders read today, from exactly
the same place.

The ID-to-path mapping is the whole substance of this class. It is declared once,
per kind, and used for both enumeration and reading — so a unit that enumerates
can always be read, and the two cannot drift.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

from prompticorn.content.content_source import ContentSource
from prompticorn.content.content_unit import BUILTIN_LAYER, ContentUnit
from prompticorn.content.errors import SourceUnavailableError, UnitNotFoundError
from prompticorn.content.unit_id import UnitId
from prompticorn.content.unit_kind import UnitKind

# Files under agents/core/ named `conventions-{language}.md` are language
# conventions; every other .md there is a core convention.
_LANGUAGE_CONVENTION_PREFIX = "conventions-"

# personas.yaml sits outside configurations/ but is configuration all the same,
# so it is addressed as one rather than inventing a kind for a single file.
_PERSONAS_UNIT_NAME = "personas"


class BuiltinContentSource(ContentSource):
    """Content shipped inside the installed package.

    Args:
        root: The package root to read from. Defaults to the directory
            containing ``prompticorn``, resolved from this module's own
            location — never from the current working directory, which is
            wrong whenever the process runs from outside the repo.
    """

    def __init__(self, root: Path | None = None) -> None:
        # `parent.parent` from prompticorn/content/ is the prompticorn package.
        self._root = (root or Path(__file__).resolve().parent.parent).resolve()

    @property
    def name(self) -> str:
        return BUILTIN_LAYER

    @property
    def root(self) -> Path:
        return self._root

    def units(self) -> Iterable[ContentUnit]:
        self._require_available()
        ids = sorted(self._discover(), key=lambda unit_id: unit_id.render())
        return [ContentUnit(id=unit_id, layer=BUILTIN_LAYER) for unit_id in ids]

    def read(self, unit_id: UnitId) -> str:
        self._require_available()
        path = self.path_for(unit_id)
        if path is None or not path.is_file():
            raise UnitNotFoundError(unit_id.render(), self.name)
        return path.read_text(encoding="utf-8")

    def has(self, unit_id: UnitId) -> bool:
        """Cheaper than scanning every unit: the mapping is total, so a single
        stat answers it."""
        path = self.path_for(unit_id)
        return path is not None and path.is_file()

    def path_for(self, unit_id: UnitId) -> Path | None:
        """The file backing a unit ID, or None if the kind has no mapping.

        Returning a path does not imply the file exists — callers stat it.
        """
        segments = unit_id.segments
        match unit_id.kind:
            case UnitKind.AGENT:
                return self._root / "agents" / segments[0] / "prompt.md"
            case UnitKind.SUBAGENT:
                agent, subagent, variant = segments
                return (
                    self._root / "agents" / agent / "subagents" / subagent / variant / "prompt.md"
                )
            case UnitKind.SKILL:
                skill, variant = segments
                return self._root / "skills" / skill / variant / "SKILL.md"
            case UnitKind.WORKFLOW:
                workflow, variant = segments
                return self._root / "workflows" / workflow / variant / "workflow.md"
            case UnitKind.CONVENTION:
                scope, name = segments
                if scope == "core":
                    return self._root / "agents" / "core" / f"{name}.md"
                return self._root / "agents" / "core" / f"{_LANGUAGE_CONVENTION_PREFIX}{name}.md"
            case UnitKind.CONFIGURATION:
                if segments[0] == _PERSONAS_UNIT_NAME:
                    return self._root / "personas" / "personas.yaml"
                return self._root / "configurations" / f"{segments[0]}.yaml"
        return None  # pragma: no cover - exhaustive over UnitKind

    # -- discovery -------------------------------------------------------

    def _discover(self) -> Iterator[UnitId]:
        yield from self._discover_agents_and_subagents()
        yield from self._discover_variant_tree("skills", UnitKind.SKILL, "SKILL.md")
        yield from self._discover_variant_tree("workflows", UnitKind.WORKFLOW, "workflow.md")
        yield from self._discover_conventions()
        yield from self._discover_configurations()

    def _discover_agents_and_subagents(self) -> Iterator[UnitId]:
        agents_dir = self._root / "agents"
        if not agents_dir.is_dir():
            return
        for agent_dir in sorted(agents_dir.iterdir()):
            # `core/` holds conventions, not an agent.
            if not agent_dir.is_dir() or agent_dir.name == "core":
                continue
            if (agent_dir / "prompt.md").is_file():
                yield UnitId.parse(f"agent/{agent_dir.name}")
            subagents_dir = agent_dir / "subagents"
            if not subagents_dir.is_dir():
                continue
            for subagent_dir in sorted(subagents_dir.iterdir()):
                if not subagent_dir.is_dir():
                    continue
                for variant_dir in sorted(subagent_dir.iterdir()):
                    if (variant_dir / "prompt.md").is_file():
                        yield UnitId.parse(
                            f"subagent/{agent_dir.name}/{subagent_dir.name}/{variant_dir.name}"
                        )

    def _discover_variant_tree(
        self, directory: str, kind: UnitKind, filename: str
    ) -> Iterator[UnitId]:
        base = self._root / directory
        if not base.is_dir():
            return
        for item_dir in sorted(base.iterdir()):
            if not item_dir.is_dir():
                continue
            for variant_dir in sorted(item_dir.iterdir()):
                if (variant_dir / filename).is_file():
                    yield UnitId.parse(f"{kind.value}/{item_dir.name}/{variant_dir.name}")

    def _discover_conventions(self) -> Iterator[UnitId]:
        core_dir = self._root / "agents" / "core"
        if not core_dir.is_dir():
            return
        for path in sorted(core_dir.glob("*.md")):
            stem = path.stem
            if stem.startswith(_LANGUAGE_CONVENTION_PREFIX):
                language = stem[len(_LANGUAGE_CONVENTION_PREFIX) :]
                yield UnitId.parse(f"convention/language/{language}")
            else:
                yield UnitId.parse(f"convention/core/{stem}")

    def _discover_configurations(self) -> Iterator[UnitId]:
        configurations_dir = self._root / "configurations"
        if configurations_dir.is_dir():
            for path in sorted(configurations_dir.glob("*.yaml")):
                yield UnitId.parse(f"configuration/{path.stem}")
        if (self._root / "personas" / "personas.yaml").is_file():
            yield UnitId.parse(f"configuration/{_PERSONAS_UNIT_NAME}")

    def _require_available(self) -> None:
        if not self._root.is_dir():
            raise SourceUnavailableError(
                self.name, f"bundled content root does not exist: {self._root}"
            )
