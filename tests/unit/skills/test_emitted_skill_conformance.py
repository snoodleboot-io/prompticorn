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


@pytest.mark.unit
class TestDescriptionExtractionMutationCoverage:
    """Pin _extract_description / _yaml_double_quote / ensure_frontmatter behavior (PRO-135).

    The earlier tests used single-line Purpose bodies where the first-prose-line
    fallback happens to produce the same answer, so mutations to the Purpose-
    detection logic survived. These cases make the Purpose path observably
    different from the fallback.
    """

    def _desc(self, name, body):
        from prompticorn.builders.skill_emitter import _extract_description

        return _extract_description(name, body)

    def test_purpose_wins_over_earlier_prose(self):
        # Prose appears BEFORE Purpose; the Purpose sentence must be chosen, not
        # the earlier line — kills the case-fold / continue-vs-break mutants.
        body = "# Title\n\nIntro prose that is not the purpose.\n\n## Purpose\nThe real purpose sentence.\n\n## Next\n"
        assert self._desc("s", body) == "The real purpose sentence."

    def test_purpose_header_is_case_insensitive(self):
        body = "## PURPOSE\nUpper cased header body.\n"
        assert self._desc("s", body) == "Upper cased header body."

    def test_multiline_purpose_joined_with_single_space(self):
        # Two-line Purpose, single sentence spanning both — kills the join mutant.
        body = "## Purpose\nFirst part\nsecond part done.\n\n## Next\n"
        assert self._desc("s", body) == "First part second part done."

    def test_first_sentence_only(self):
        body = "## Purpose\nSentence one. Sentence two should be dropped.\n"
        assert self._desc("s", body) == "Sentence one."

    def test_purpose_ended_by_next_heading_still_used(self):
        # break-vs-return: after the heading ends Purpose, the collected text is used.
        body = "## Purpose\nKept sentence.\n## Other\nignored.\n"
        assert self._desc("s", body) == "Kept sentence."

    def test_falls_back_to_first_prose_when_no_purpose(self):
        body = "# Heading\n\nFirst prose line here.\n\n## Section\n"
        assert self._desc("s", body) == "First prose line here."

    def test_falls_back_to_title_when_no_text(self):
        # No Purpose and no prose line at all (only headings/blanks) -> title from name.
        body = "# H1\n\n## H2\n\n### H3\n"
        assert self._desc("my-skill-name", body) == "My Skill Name skill."

    def test_length_bounded_with_ellipsis(self):
        body = "## Purpose\n" + ("word " * 200).strip() + "\n"
        out = self._desc("s", body)
        assert out.endswith("…") and len(out) <= 500

    def test_yaml_double_quote_escapes_backslash_and_quote(self):
        from prompticorn.builders.skill_emitter import _yaml_double_quote

        assert _yaml_double_quote(r"a\b") == r'"a\\b"'
        assert _yaml_double_quote('say "hi"') == r'"say \"hi\""'

    def test_ensure_frontmatter_detects_leading_whitespace_frontmatter(self):
        # Leading newline before --- must still count as existing frontmatter.
        body = "\n---\nname: kept\ndescription: kept\n---\n\nbody\n"
        assert ensure_frontmatter("kept", body) == body

    def test_ensure_frontmatter_strips_leading_newlines_from_body(self):
        out = ensure_frontmatter("s", "\n\n# Body\n\n## Purpose\nX.\n")
        # No blank line between the closing --- and the body.
        assert "---\n\n# Body" in out

    def test_title_from_name_replaces_underscores(self):
        from prompticorn.builders.skill_emitter import _title_from_name

        assert _title_from_name("foo_bar_baz") == "Foo Bar Baz"

    def test_heading_ends_purpose_even_without_sentence_break(self):
        # No period in the Purpose line: if the following heading is NOT treated
        # as the section end, its text would extend the (single) sentence.
        body = "## Purpose\nKept\n## Other\nleaked text\n"
        assert self._desc("s", body) == "Kept"

    def test_fallback_skips_code_fence_lines(self):
        # No Purpose; a fence precedes the first real prose line, which must win.
        body = "# H\n\n```\n\nActual prose wins.\n"
        assert self._desc("s", body) == "Actual prose wins."
