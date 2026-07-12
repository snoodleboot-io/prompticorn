"""Central registry of supported AI tools (PRO-30 / F2a).

Single source of truth for tool metadata and dispatch. Each tool is declared
once as a :class:`ToolSpec`; the CLI pickers, name normalization/validation,
builder dispatch, and artifact create-sets are all derived from this registry,
so registering a new tool for metadata/dispatch means adding one ToolSpec entry
(and, if its menu position matters, one id in ``MENU_ORDER``).

Note the two namespaces this reconciles:
  * ``id`` — the canonical CLI-facing tool id (6 of them, e.g. ``kilo-cli``).
  * ``builder_name`` — the internal builder key (5 of them; ``kilo-cli`` and
    ``kilo-ide`` both dispatch to the ``kilo`` builder).
"""

import re
from dataclasses import dataclass, field
from typing import Final


@dataclass(frozen=True)
class ToolSpec:
    """Declarative description of one supported AI tool.

    Attributes:
        id: Canonical CLI-facing tool id (e.g. ``"kilo-cli"``).
        display_label: Human-facing label shown in the CLI pickers.
        explanation: One-line explanation shown next to the label in pickers.
        builder_name: Internal builder key for dispatch (may be shared).
        create_artifacts: Files/directories this tool creates.
    """

    id: str
    display_label: str
    explanation: str
    builder_name: str
    create_artifacts: frozenset[str] = field(default_factory=frozenset)


# Registry order intentionally matches the historical ``artifacts`` ordering so
# that ArtifactManager.current_tool (first-match detection) is unchanged.
_TOOL_SPECS: Final[tuple[ToolSpec, ...]] = (
    ToolSpec(
        id="kilo-cli",
        display_label="Kilo CLI",
        explanation="Kilo Code (CLI) - .opencode/rules/ with collapsed mode files",
        builder_name="kilo",
        create_artifacts=frozenset({".opencode/"}),
    ),
    ToolSpec(
        id="kilo-ide",
        display_label="Kilo IDE",
        explanation="Kilo Code (IDE) - .kilo/agents/ individual agent files",
        builder_name="kilo",
        create_artifacts=frozenset({".kilo/"}),
    ),
    ToolSpec(
        id="cline",
        display_label="Cline",
        explanation="Cline - .clinerules file (concatenated rules)",
        builder_name="cline",
        create_artifacts=frozenset({".clinerules"}),
    ),
    ToolSpec(
        id="cursor",
        display_label="Cursor",
        explanation="Cursor - .cursor/rules/ directory + .cursorrules",
        builder_name="cursor",
        create_artifacts=frozenset({".cursor/", ".cursorrules"}),
    ),
    ToolSpec(
        id="copilot",
        display_label="Copilot",
        explanation="GitHub Copilot - .github/copilot-instructions.md",
        builder_name="copilot",
        create_artifacts=frozenset({".github/copilot-instructions.md"}),
    ),
    ToolSpec(
        id="claude",
        display_label="Claude",
        explanation="Claude - generates .claude/ directory with Markdown agent files and CLAUDE.md",
        builder_name="claude",
        create_artifacts=frozenset({".claude/", "CLAUDE.md"}),
    ),
    ToolSpec(
        id="roo",
        display_label="Roo Code",
        explanation="Roo Code - .roomodes custom modes + .roo/ rules, skills, and commands",
        builder_name="roo",
        create_artifacts=frozenset({".roomodes", ".roo/"}),
    ),
)

TOOLS: Final[dict[str, ToolSpec]] = {spec.id: spec for spec in _TOOL_SPECS}

# Display order for the CLI pickers (init + switch). Kept separate from the
# registry order because the menu historically lists Claude before Cline/Cursor/
# Copilot, whereas the artifact/detection order does not.
MENU_ORDER: Final[tuple[str, ...]] = (
    "kilo-cli",
    "kilo-ide",
    "claude",
    "cline",
    "cursor",
    "copilot",
    "roo",
)


def _normalize(name: str) -> str:
    """Strip non-alphanumerics and lowercase (matches cli_utils normalization)."""
    return re.sub(r"[^a-zA-Z0-9]", "", name).lower()


def supported_tool_ids() -> set[str]:
    """Return the set of canonical tool ids."""
    return set(TOOLS)


def name_mappings() -> dict[str, str]:
    """Return normalized-name -> canonical-id mappings for every tool.

    Covers both the id and the display label (which normalize identically for
    the current tools), so user input in either form resolves.
    """
    mappings: dict[str, str] = {}
    for spec in TOOLS.values():
        mappings[_normalize(spec.id)] = spec.id
        mappings[_normalize(spec.display_label)] = spec.id
    return mappings


def builder_dispatch() -> dict[str, str]:
    """Return canonical-id -> internal builder-name mappings."""
    return {spec.id: spec.builder_name for spec in TOOLS.values()}


def create_artifacts_by_tool() -> dict[str, set[str]]:
    """Return canonical-id -> mutable create-artifact set."""
    return {spec.id: set(spec.create_artifacts) for spec in TOOLS.values()}


def menu_options() -> list[str]:
    """Return picker display labels in menu order."""
    return [TOOLS[tool_id].display_label for tool_id in MENU_ORDER]


def menu_explanations() -> dict[str, str]:
    """Return picker {display_label: explanation} in menu order."""
    return {TOOLS[tool_id].display_label: TOOLS[tool_id].explanation for tool_id in MENU_ORDER}
