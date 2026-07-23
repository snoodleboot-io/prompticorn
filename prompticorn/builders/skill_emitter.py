"""Canonical Agent Skills ``SKILL.md`` emitter (PRO-32 / E2).

The ``<base>/skills/<name>/SKILL.md`` folder shape is identical across every tool
that supports the Agent Skills spec (Codex, Zed, Roo, Junie) and is already what
prompticorn emits for Claude/Kilo/Cline/Cursor — only the base directory differs.
This module is the single, tool-agnostic writer for that shape so each generator
supplies just its base directory.

Every emitted file is guaranteed to carry YAML frontmatter with a ``name`` and a
``description`` (PRO-7 follow-up). Frontmatter is optional to the Claude Code
Agent Skills spec — a bare markdown file still loads — but the ``description`` is
what lets the model decide *when* to auto-invoke a skill. Skills authored in the
house format carry no frontmatter, so without this synthesis they would emit
without a description and silently become manual-only (``/skill-name``). The
writer restores the trigger uniformly rather than pushing frontmatter back into
every source file.
"""

import re
from pathlib import Path
from typing import Final

# Canonical Agent Skills base directory (used by Codex/Zed/Roo/Junie).
AGENTS_SKILLS_BASE: Final[str] = ".agents"

# Description is combined with when_to_use and capped at 1,536 chars by the spec;
# a Purpose sentence is far shorter, but bound it defensively.
_DESCRIPTION_MAX: Final[int] = 500


def skill_relative_path(base_dir: str, skill_name: str) -> str:
    """Return the SKILL.md path for a skill under ``base_dir``.

    Args:
        base_dir: Tool base directory, e.g. ``".claude"`` or ``".agents"``.
        skill_name: Skill identifier.

    Returns:
        Relative path, e.g. ``".claude/skills/feature-planning/SKILL.md"``.
    """
    return f"{base_dir}/skills/{skill_name}/SKILL.md"


def _title_from_name(skill_name: str) -> str:
    """A human display label derived from the skill's directory name."""
    return skill_name.replace("-", " ").replace("_", " ").strip().title()


def _extract_description(skill_name: str, body: str) -> str:
    """Derive a one-line description from a skill body.

    Prefers the first sentence of the ``## Purpose`` section (the house format).
    Falls back to the first non-heading prose line, then to the skill's title.
    """
    lines = body.splitlines()
    purpose: list[str] = []
    in_purpose = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## purpose"):
            in_purpose = True
            continue
        if in_purpose:
            if stripped.startswith("#"):  # next section — Purpose block ended
                break
            if stripped:
                purpose.append(stripped)
            elif purpose:  # blank line after collecting text ends the block
                break

    text = " ".join(purpose).strip()
    if not text:
        # Fall back to the first non-heading, non-blank, non-fence line.
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("```"):
                text = stripped
                break

    if not text:
        return f"{_title_from_name(skill_name)} skill."

    # Keep the first sentence, collapse whitespace, and bound the length.
    first_sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    first_sentence = re.sub(r"\s+", " ", first_sentence).strip()
    if len(first_sentence) > _DESCRIPTION_MAX:
        first_sentence = first_sentence[: _DESCRIPTION_MAX - 1].rstrip() + "…"
    return first_sentence


def _yaml_double_quote(value: str) -> str:
    """Escape a string for a YAML double-quoted scalar."""
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def ensure_frontmatter(skill_name: str, content: str) -> str:
    """Return ``content`` guaranteed to open with ``name``/``description`` frontmatter.

    Content that already begins with a ``---`` frontmatter block is returned
    unchanged. Otherwise a synthesized block is prepended, deriving ``name`` from
    the directory and ``description`` from the body's Purpose line.
    """
    if content.lstrip().startswith("---"):
        return content

    description = _extract_description(skill_name, content)
    frontmatter = (
        f"---\nname: {skill_name}\ndescription: {_yaml_double_quote(description)}\n---\n\n"
    )
    return frontmatter + content.lstrip("\n")


def write_skill(output_root: Path, base_dir: str, skill_name: str, content: str) -> str:
    """Write ``content`` to ``<output_root>/<base_dir>/skills/<skill_name>/SKILL.md``.

    Creates parent directories as needed and guarantees the emitted file carries
    ``name``/``description`` frontmatter.

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
    destination.write_text(ensure_frontmatter(skill_name, content), encoding="utf-8")
    return relative
