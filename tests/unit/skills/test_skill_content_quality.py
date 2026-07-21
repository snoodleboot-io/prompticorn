"""Content-quality gate for skills (PRO-7).

Two failure modes shipped to users for a long time without any test noticing:

1. **Unfilled template placeholders** — files containing literal
   ``Concept 1: [Explanation]`` and ``[Step 1 description]``, emitted verbatim
   into user builds.
2. **Generic boilerplate** — 26 files sharing identical filler
   (``Understand the fundamentals``, ``Apply to real scenarios``) that says
   nothing about the skill it purports to teach.

At the worst point 76 of the 96 skills were hollow, and 50 of the 59 that a
build could actually reach were unfilled templates. PRO-7 authored real content
for all of them, so this gate is now unconditional — there is no allowlist, and
a hollow skill fails the suite outright.
"""

import re
from pathlib import Path

import pytest

_VARIANTS = ("minimal", "verbose")

# Literal artifacts of an unfilled template.
_PLACEHOLDER_PATTERNS = (
    re.compile(r"\[Explanation\]"),
    re.compile(r"\[Step \d"),
    re.compile(r"\[Practice"),
    re.compile(r"\[What is it\]"),
    re.compile(r"\[Name\]"),
    re.compile(r"^#+ *Concept \d", re.MULTILINE),
    re.compile(r"^- *Concept \d:", re.MULTILINE),
    re.compile(r"^- *Practice \d *$", re.MULTILINE),
    re.compile(r"^- *Importance \d *$", re.MULTILINE),
)

# Filler shared verbatim across the bulk-generated skills.
_BOILERPLATE_PHRASES = (
    "Understand the fundamentals",
    "Apply to real scenarios",
    "Can explain concepts clearly",
    "Can mentor others",
)


def _defects(text: str) -> list[str]:
    """Return the hollow-content markers found in a skill file."""
    found = [p.pattern for p in _PLACEHOLDER_PATTERNS if p.search(text)]
    found += [f"boilerplate: {p!r}" for p in _BOILERPLATE_PHRASES if p in text]
    return found


def _skill_names(skills_dir: Path) -> list[str]:
    return sorted(path.name for path in skills_dir.iterdir() if path.is_dir())


@pytest.mark.unit
class TestSkillContentQuality:
    """No skill ships template placeholders or generic filler."""

    def test_no_skill_contains_placeholders_or_boilerplate(self, skills_dir):
        """Every skill, both variants, contains real content."""
        offenders: dict[str, list[str]] = {}
        for name in _skill_names(skills_dir):
            for variant in _VARIANTS:
                path = skills_dir / name / variant / "SKILL.md"
                defects = _defects(path.read_text(encoding="utf-8"))
                if defects:
                    offenders[f"{name}/{variant}"] = defects
        assert not offenders, (
            "These skills contain unfilled template placeholders or generic "
            "boilerplate and would ship as-is to users. Write real content — do "
            f"not add an exemption: {offenders}"
        )

    def test_minimal_variants_avoid_jinja_delimiters(self, skills_dir):
        """Minimal skills must not contain ``{{`` or ``{%``.

        ``test_value_coverage_matrix.test_output_has_no_unrendered_templates``
        greps the whole emitted tree for those delimiters to catch a template
        that never got rendered. It builds with ``variant="minimal"``, so a
        literal ``{{`` in a minimal skill trips it for *every* tool at once —
        47 failures pointing at the builder rather than at the skill file.

        Legitimate syntax does collide here: GitHub Actions ``${{ github.sha }}``,
        JSX ``value={{ ... }}``, Argo ``{{args.x}}``. Rewrite it — a hoisted
        variable is usually clearer anyway — or keep it to the verbose variant,
        which that matrix does not currently emit.
        """
        offenders = {}
        for name in _skill_names(skills_dir):
            text = (skills_dir / name / "minimal" / "SKILL.md").read_text(encoding="utf-8")
            hits = [d for d in ("{{", "{%") if d in text]
            if hits:
                offenders[name] = hits
        assert not offenders, (
            "Minimal skills contain Jinja delimiters and will be reported as "
            f"unrendered templates by the value-coverage matrix: {offenders}"
        )
