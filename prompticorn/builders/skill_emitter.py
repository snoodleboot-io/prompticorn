"""Canonical Agent Skills ``SKILL.md`` emitter (PRO-32 / E2).

The ``<base>/skills/<name>/SKILL.md`` folder shape is identical across every tool
that supports the Agent Skills spec (Codex, Zed, Roo, Junie) and is already what
prompticorn emits for Claude/Kilo/Cline/Cursor — only the base directory differs.
This module is the single, tool-agnostic writer for that shape so each generator
supplies just its base directory.
"""

from pathlib import Path
from typing import Final

# Canonical Agent Skills base directory (used by Codex/Zed/Roo/Junie).
AGENTS_SKILLS_BASE: Final[str] = ".agents"


def skill_relative_path(base_dir: str, skill_name: str) -> str:
    """Return the SKILL.md path for a skill under ``base_dir``.

    Args:
        base_dir: Tool base directory, e.g. ``".claude"`` or ``".agents"``.
        skill_name: Skill identifier.

    Returns:
        Relative path, e.g. ``".claude/skills/feature-planning/SKILL.md"``.
    """
    return f"{base_dir}/skills/{skill_name}/SKILL.md"


def write_skill(output_root: Path, base_dir: str, skill_name: str, content: str) -> str:
    """Write ``content`` to ``<output_root>/<base_dir>/skills/<skill_name>/SKILL.md``.

    Creates parent directories as needed.

    Args:
        output_root: Root output directory.
        base_dir: Tool base directory, e.g. ``".claude"`` or ``".agents"``.
        skill_name: Skill identifier.
        content: Full SKILL.md content.

    Returns:
        The written path relative to ``output_root``.
    """
    relative = skill_relative_path(base_dir, skill_name)
    destination = output_root / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content, encoding="utf-8")
    return relative
