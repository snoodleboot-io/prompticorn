"""Package emitted Agent Skills into claude.ai / Claude Desktop upload zips (PRO-10).

Claude Desktop (the native chat app) has no on-disk skill path — its only file
config is ``claude_desktop_config.json`` (MCP servers), which prompticorn does not
produce. The one way to get prompticorn's actual skill content into the desktop /
claude.ai experience is a **manual zip upload** via Settings > Features.

This packages each emitted ``<name>/SKILL.md`` folder into its own ``<name>.zip``
in the exact structure claude.ai accepts, verified against Anthropic's docs:

* one skill per zip;
* the archive's top-level entry is the skill **folder** — ``<name>/SKILL.md`` —
  not ``SKILL.md`` at the root (which fails discovery);
* the folder name must equal the skill's frontmatter ``name``;
* ``name`` must be lowercase ``[a-z0-9-]`` and must not contain the reserved
  words "anthropic" or "claude".

Sources: platform.claude.com Agent Skills overview; support.claude.com "How to
create custom Skills". See the zip-format research in Linear (PRO-10).
"""

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

# claude.ai skill `name` rule: lowercase letters, digits, hyphens; max 64 chars.
_NAME_RE = re.compile(r"^[a-z0-9-]{1,64}$")
_RESERVED = ("anthropic", "claude")


@dataclass(frozen=True)
class PackagedSkill:
    """One packaged skill zip (or a skipped skill with a reason)."""

    name: str
    zip_path: Path | None
    skipped_reason: str | None = None

    @property
    def ok(self) -> bool:
        return self.zip_path is not None


def _name_problem(name: str) -> str | None:
    """Return why ``name`` is unacceptable to claude.ai, or None if it is fine."""
    if not _NAME_RE.match(name):
        return "name must be 1-64 chars of lowercase letters, digits, or hyphens"
    lowered = name.lower()
    for reserved in _RESERVED:
        if reserved in lowered:
            return f"name may not contain the reserved word '{reserved}'"
    return None


def _skill_dirs(source_dir: Path) -> list[Path]:
    """Skill folders (each holding a SKILL.md) directly under ``source_dir``, sorted."""
    return sorted(
        (d for d in source_dir.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()),
        key=lambda d: d.name,
    )


def package_skills(source_dir: Path, output_dir: Path) -> list[PackagedSkill]:
    """Zip each ``<name>/SKILL.md`` folder under ``source_dir`` into ``<name>.zip``.

    Args:
        source_dir: A directory of emitted skills, e.g. ``.claude/skills`` — each
            child ``<name>/`` must contain a ``SKILL.md``.
        output_dir: Where the ``<name>.zip`` files are written (created if needed).

    Returns:
        One :class:`PackagedSkill` per skill folder, sorted by name; skills whose
        name violates claude.ai's rules are reported with ``skipped_reason`` and
        no zip rather than producing an archive that would fail to upload.

    Raises:
        FileNotFoundError: If ``source_dir`` does not exist or holds no skills.
    """
    if not source_dir.is_dir():
        raise FileNotFoundError(f"source directory does not exist: {source_dir}")

    skill_dirs = _skill_dirs(source_dir)
    if not skill_dirs:
        raise FileNotFoundError(f"no <name>/SKILL.md skills found under {source_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    results: list[PackagedSkill] = []

    for skill_dir in skill_dirs:
        name = skill_dir.name
        problem = _name_problem(name)
        if problem:
            results.append(PackagedSkill(name=name, zip_path=None, skipped_reason=problem))
            continue

        zip_path = output_dir / f"{name}.zip"
        # Deterministic archive: sorted members, each arced under the skill folder
        # so the zip's top-level entry is `<name>/...` (the accepted form).
        members = sorted(p for p in skill_dir.rglob("*") if p.is_file())
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for member in members:
                arcname = f"{name}/{member.relative_to(skill_dir).as_posix()}"
                zf.write(member, arcname)
        results.append(PackagedSkill(name=name, zip_path=zip_path))

    return results
