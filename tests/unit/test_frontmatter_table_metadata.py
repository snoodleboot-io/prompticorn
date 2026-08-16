"""Skill/subagent tables carry authored metadata, not placeholders (PRO-142).

The emitted agent file lists its skills and subagents in a table whose Purpose and
"When to Use" cells used to be synthesized from the name — "Capability for X",
"When workflow requires X". Those state no capability and no condition, so an agent
reading its own table learns nothing about when to load anything. The cells now come
from the authored frontmatter.
"""

import pytest

from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.text_utils import frontmatter_field, parse_frontmatter


class TestParseFrontmatter:
    def test_splits_metadata_from_body(self):
        metadata, body = parse_frontmatter("---\nname: thing\n---\n\n# Heading\n")
        assert metadata == {"name": "thing"}
        assert body == "\n# Heading\n"

    @pytest.mark.parametrize(
        ("text", "why"),
        [
            ("", "empty content"),
            ("# Heading\n", "no frontmatter block"),
            ("---\nname: [unclosed\n---\n", "malformed YAML"),
            ("---\njust a string\n---\n", "block is not a mapping"),
            ("body\n---\nname: late\n---\n", "block is not leading"),
        ],
    )
    def test_returns_content_unchanged_when_there_is_no_usable_block(self, text, why):
        """Authored metadata is best-effort: a build must not fail over it."""
        metadata, body = parse_frontmatter(text)
        assert metadata == {}, why
        assert body == text, why


class TestFrontmatterField:
    def test_reads_a_scalar(self):
        assert frontmatter_field("---\ndescription: Does a thing\n---\n", "description") == (
            "Does a thing"
        )

    def test_collapses_wrapped_values_to_one_line(self):
        """Table cells are single-line; a folded YAML scalar must not break the row."""
        text = "---\ndescription: >\n  first line\n  second line\n---\n"
        assert frontmatter_field(text, "description") == "first line second line"

    @pytest.mark.parametrize(
        ("text", "field"),
        [
            ("---\nname: thing\n---\n", "description"),
            ("---\ndescription: '   '\n---\n", "description"),
            ("---\ntools: [read, bash]\n---\n", "tools"),
        ],
    )
    def test_absent_blank_and_non_scalar_all_read_as_missing(self, text, field):
        assert frontmatter_field(text, field) is None


class TestEmittedTables:
    def test_skill_row_uses_the_authored_description(self):
        (row,) = ClaudeBuilder()._prepare_skills_data(["multiagent-orchestration"], "verbose")
        assert row["purpose"].startswith("Run a genuinely-parallel multiagent")
        assert "Capability for" not in row["purpose"]

    def test_skill_row_uses_the_authored_trigger_when_declared(self):
        (row,) = ClaudeBuilder()._prepare_skills_data(["multiagent-orchestration"], "verbose")
        assert "parallel" in row["when_to_use"].lower()
        assert row["when_to_use"] != "When workflow requires multiagent-orchestration"

    def test_body_derived_description_when_source_has_no_frontmatter(self):
        """PRO-145: only 9 of 119 authored skills declare frontmatter. Reading it
        alone left 79 referenced rows saying "Capability for <name>", which names
        the skill and says nothing else. The emitter already derives a description
        from the body when it writes each SKILL.md; the table reuses it."""
        (row,) = ClaudeBuilder()._prepare_skills_data(["api-security"], "verbose")
        assert row["purpose"] == "An API has no UI to hide things behind."
        assert "Capability for" not in row["purpose"]

    def test_no_referenced_skill_falls_back_to_the_placeholder(self):
        """The fallback should now be unreachable for real skills — every authored
        skill has either frontmatter or a body to derive from."""
        import pathlib as _pathlib

        names = sorted(p.name for p in _pathlib.Path("prompticorn/skills").iterdir() if p.is_dir())
        rows = ClaudeBuilder()._prepare_skills_data(names, "verbose")
        placeholders = [r["name"] for r in rows if r["purpose"].startswith("Capability for")]
        assert not placeholders

    def test_skill_row_falls_back_when_no_trigger_is_declared(self):
        """Most skills declare only a description; their rows keep the old cell
        rather than inventing a condition the author never stated."""
        (row,) = ClaudeBuilder()._prepare_skills_data(["feature-planning"], "verbose")
        assert row["when_to_use"] == "When workflow requires feature-planning"
        assert "Capability for" not in row["purpose"]

    def test_unknown_skill_falls_back_instead_of_failing(self):
        (row,) = ClaudeBuilder()._prepare_skills_data(["no-such-skill"], "verbose")
        assert row["purpose"] == "Capability for no-such-skill"
        assert row["when_to_use"] == "When workflow requires no-such-skill"

    def test_subagent_row_uses_the_authored_description(self):
        (row,) = ClaudeBuilder()._prepare_subagents_data(["devops"], "orchestrator", "verbose")
        assert "CI/CD" in row["purpose"]
        assert "Specialized for" not in row["purpose"]

    def test_subagent_row_resolves_against_its_parent_agent(self):
        """A bare subagent name is owned by the agent whose table it appears in;
        resolving it without that owner finds nothing and silently falls back."""
        (row,) = ClaudeBuilder()._prepare_subagents_data(
            ["environment-setup"], "orchestrator", "verbose"
        )
        assert "health-check" in row["purpose"]
        assert "before any" in row["when_to_use"].lower()

    def test_already_qualified_subagent_name_is_not_double_prefixed(self):
        (row,) = ClaudeBuilder()._prepare_subagents_data(
            ["orchestrator/devops"], "orchestrator", "verbose"
        )
        assert "CI/CD" in row["purpose"]

    def test_unknown_subagent_falls_back_instead_of_failing(self):
        (row,) = ClaudeBuilder()._prepare_subagents_data(["nope"], "orchestrator", "verbose")
        assert row["purpose"] == "Specialized for nope tasks"
