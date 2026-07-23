"""Every emitted SKILL.md is a spec-conformant Agent Skill (PRO-7 follow-up).

The golden test pins emitted bytes but says nothing about whether those bytes
form a *valid* Agent Skill — which is how 87 skills shipped without frontmatter
after the house format (deliberately frontmatter-free in source) went straight to
output. Frontmatter is optional to the Claude Code spec, but the ``description``
is the auto-invocation trigger; without it a skill silently becomes manual-only.

These tests assert the emitter's guarantee directly, at the unit level, so the
regression cannot recur regardless of what the source files look like.
"""

import pytest

from prompticorn.builders.skill_emitter import ensure_frontmatter


def _parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal ``key: value`` frontmatter parse; returns {} if none present."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    assert end != -1, "frontmatter opened with --- but never closed"
    fields: dict[str, str] = {}
    for line in text[3:end].splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


@pytest.mark.unit
class TestEmittedSkillConformance:
    """The emitter guarantees name + description on every skill it writes."""

    def test_frontmatterless_content_gains_name_and_description(self):
        body = "# Some Skill (Minimal)\n\n## Purpose\nDo the thing well.\n\n## Core Techniques\n"
        out = ensure_frontmatter("some-skill", body)
        fm = _parse_frontmatter(out)
        assert fm.get("name") == "some-skill"
        assert fm["description"].strip('"') == "Do the thing well."

    def test_description_comes_from_the_purpose_line(self):
        body = "# X (Minimal)\n\n## Purpose\nFirst sentence here. Second one ignored.\n\n## More\n"
        fm = _parse_frontmatter(ensure_frontmatter("x", body))
        assert fm["description"].strip('"') == "First sentence here."

    def test_existing_frontmatter_is_not_doubled(self):
        body = "---\nname: kept\ndescription: original\n---\n\n# Body\n"
        out = ensure_frontmatter("kept", body)
        assert out == body
        assert out.count("---") == 2

    def test_description_is_yaml_safe_when_it_contains_quotes(self):
        body = '# X (Minimal)\n\n## Purpose\nUse "OK" not [ OK ] as a label.\n'
        out = ensure_frontmatter("x", body)
        # The synthesized description must round-trip through a YAML parser.
        import yaml

        end = out.find("\n---", 3)
        parsed = yaml.safe_load(out[3:end])
        assert "OK" in parsed["description"]

    def test_falls_back_to_the_title_when_no_purpose(self):
        body = "# Whatever\n\nSome text with no purpose section.\n"
        fm = _parse_frontmatter(ensure_frontmatter("edge-case-skill", body))
        # First prose line is used; if nothing, the title. Either way, non-empty.
        assert fm["description"].strip('"')

    def test_every_bundled_skill_emits_with_a_description(self, skills_dir):
        """The real corpus: every skill, both variants, yields a description."""
        missing = []
        for skill in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
            for variant in ("minimal", "verbose"):
                content = (skill / variant / "SKILL.md").read_text(encoding="utf-8")
                fm = _parse_frontmatter(ensure_frontmatter(skill.name, content))
                if not fm.get("description", "").strip('"'):
                    missing.append(f"{skill.name}/{variant}")
        assert not missing, f"Skills that would emit without a description: {missing}"
