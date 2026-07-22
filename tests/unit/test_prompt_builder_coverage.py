"""Focused coverage tests for prompticorn.prompt_builder.

These tests target the pure/IO-helper surface of :class:`PromptBuilder`
(static config extractors, per-tool file writers, skill/workflow loading,
language filtering, and the module-level factory) using real inputs and
``tmp_path`` for filesystem operations. TUI/curses behavior is not exercised.
"""

import pytest

from prompticorn.ir.models.agent import Agent
from prompticorn.prompt_builder import MissingSkillWarning, PromptBuilder, get_prompt_builder


@pytest.fixture
def kilo_builder():
    """Real PromptBuilder configured for the kilo tool."""
    return PromptBuilder("kilo")


def make_agent(name="code", **overrides):
    """Build a real Agent IR model with sensible defaults."""
    fields = {
        "name": name,
        "description": f"Agent: {name}",
        "mode": "all",
        "system_prompt": "Do the thing.",
        "tools": ["read", "write"],
        "skills": [],
        "workflows": [],
        "subagents": [],
        "permissions": None,
    }
    fields.update(overrides)
    return Agent(**fields)


class TestExtractLanguageFromConfig:
    """Tests for _extract_language_from_config."""

    def test_none_config_returns_none(self):
        assert PromptBuilder._extract_language_from_config(None) is None

    def test_missing_spec_returns_none(self):
        assert PromptBuilder._extract_language_from_config({"variant": "minimal"}) is None

    def test_dict_spec_returns_language(self):
        config = {"spec": {"language": "python"}}
        assert PromptBuilder._extract_language_from_config(config) == "python"

    def test_list_spec_returns_first_language(self):
        config = {"spec": [{"language": "go"}, {"language": "rust"}]}
        assert PromptBuilder._extract_language_from_config(config) == "go"

    def test_empty_list_spec_returns_none(self):
        assert PromptBuilder._extract_language_from_config({"spec": []}) is None

    def test_unexpected_spec_type_returns_none(self):
        # spec is neither dict nor non-empty list (falls to else branch).
        assert PromptBuilder._extract_language_from_config({"spec": "python"}) is None


class TestExtractAllLanguagesFromConfig:
    """Tests for _extract_all_languages_from_config."""

    def test_none_config_returns_none(self):
        assert PromptBuilder._extract_all_languages_from_config(None) is None

    def test_missing_spec_returns_none(self):
        assert PromptBuilder._extract_all_languages_from_config({}) is None

    def test_dict_spec_returns_single_item_list(self):
        config = {"spec": {"language": "python"}}
        assert PromptBuilder._extract_all_languages_from_config(config) == ["python"]

    def test_dict_spec_without_language_returns_none(self):
        config = {"spec": {"runtime": "3.14"}}
        assert PromptBuilder._extract_all_languages_from_config(config) is None

    def test_list_spec_filters_out_missing_languages(self):
        config = {"spec": [{"language": "python"}, {"folder": "x"}, {"language": "go"}]}
        assert PromptBuilder._extract_all_languages_from_config(config) == ["python", "go"]

    def test_list_spec_all_missing_languages_returns_none(self):
        config = {"spec": [{"folder": "a"}, {"folder": "b"}]}
        assert PromptBuilder._extract_all_languages_from_config(config) is None

    def test_unexpected_spec_type_returns_none(self):
        assert PromptBuilder._extract_all_languages_from_config({"spec": 42}) is None


class TestExtractAllSpecsFromConfig:
    """Tests for _extract_all_specs_from_config."""

    def test_none_config_returns_none(self):
        assert PromptBuilder._extract_all_specs_from_config(None) is None

    def test_dict_spec_with_language_returns_wrapped_list(self):
        spec = {"language": "python", "runtime": "3.14"}
        assert PromptBuilder._extract_all_specs_from_config({"spec": spec}) == [spec]

    def test_dict_spec_without_language_returns_none(self):
        assert PromptBuilder._extract_all_specs_from_config({"spec": {"runtime": "x"}}) is None

    def test_list_spec_filters_invalid_entries(self):
        config = {"spec": [{"language": "python"}, "bad", {"folder": "no-lang"}]}
        result = PromptBuilder._extract_all_specs_from_config(config)
        assert result == [{"language": "python"}]

    def test_list_spec_no_valid_entries_returns_none(self):
        config = {"spec": [{"folder": "no-lang"}, "bad"]}
        assert PromptBuilder._extract_all_specs_from_config(config) is None

    def test_unexpected_spec_type_returns_none(self):
        assert PromptBuilder._extract_all_specs_from_config({"spec": 7}) is None


class TestGetPromptBuilder:
    """Tests for the module-level get_prompt_builder factory."""

    @pytest.mark.parametrize(
        "tool",
        ["kilo-cli", "kilo-ide", "cline", "cursor", "copilot", "claude"],
    )
    def test_known_tools_return_builder(self, tool):
        builder = get_prompt_builder(tool)
        assert isinstance(builder, PromptBuilder)

    def test_kilo_cli_maps_to_kilo_internal_name(self):
        assert get_prompt_builder("kilo-cli").tool_name == "kilo"

    def test_unknown_tool_raises_value_error(self):
        with pytest.raises(ValueError, match="Unknown tool"):
            get_prompt_builder("does-not-exist")


class TestInitLoaders:
    """Tests for loader initialization behavior in __init__."""

    def test_loaders_present_for_real_package(self, kilo_builder):
        # Bundled configuration files exist, so loaders should initialize.
        assert kilo_builder.agent_skill_loader is not None
        assert kilo_builder.language_skill_loader is not None

    def test_registry_discovers_agents(self, kilo_builder):
        agents = kilo_builder.registry.get_all_agents()
        assert isinstance(agents, dict)
        assert len(agents) > 0


class TestWriteOutput:
    """Tests for the per-tool _write_output dispatcher."""

    def test_kilo_writes_agent_markdown(self, tmp_path):
        builder = PromptBuilder("kilo")
        written = builder._write_output(tmp_path, "code", "# Code agent")
        assert written == [".kilo/agents/code.md"]
        assert (tmp_path / ".kilo" / "agents" / "code.md").read_text() == "# Code agent"

    def test_cline_creates_then_appends(self, tmp_path):
        builder = PromptBuilder("cline")
        builder._write_output(tmp_path, "code", "first")
        builder._write_output(tmp_path, "code", "second")
        content = (tmp_path / ".clinerules").read_text()
        assert "first" in content
        assert "second" in content

    def test_claude_dict_content_writes_files(self, tmp_path):
        builder = PromptBuilder("claude")
        content = {".claude/agents/code.md": "body"}
        written = builder._write_output(tmp_path, "code", content)
        assert written == [".claude/agents/code.md"]
        assert (tmp_path / ".claude" / "agents" / "code.md").read_text() == "body"

    def test_claude_non_string_dict_falls_back_to_json(self, tmp_path):
        builder = PromptBuilder("claude")
        # Values are not strings -> old JSON fallback path.
        content = {"settings": {"nested": True}}
        written = builder._write_output(tmp_path, "code", content)
        assert written == ["custom_instructions/code.json"]
        json_path = tmp_path / "custom_instructions" / "code.json"
        assert '"nested": true' in json_path.read_text()

    def test_copilot_creates_then_appends(self, tmp_path):
        builder = PromptBuilder("copilot")
        builder._write_output(tmp_path, "code", "alpha")
        builder._write_output(tmp_path, "code", "beta")
        text = (tmp_path / ".github" / "copilot-instructions.md").read_text()
        assert "alpha" in text
        assert "beta" in text

    def test_cursor_creates_then_appends(self, tmp_path):
        builder = PromptBuilder("cursor")
        builder._write_output(tmp_path, "code", "one")
        builder._write_output(tmp_path, "code", "two")
        text = (tmp_path / ".cursorrules").read_text()
        assert "one" in text
        assert "two" in text


class TestWriteSubagentOutput:
    """Tests for _write_subagent_output."""

    def test_writes_nested_subagent_file(self, tmp_path):
        builder = PromptBuilder("kilo")
        written = builder._write_subagent_output(tmp_path, "code", "feature", "content")
        expected_path = tmp_path / ".kilo" / "agents" / "code" / "feature.md"
        assert expected_path.read_text() == "content"
        assert written == [".kilo/agents/code/feature.md"]


class TestWriteSingleSkill:
    """Tests for the per-tool _write_single_skill dispatcher."""

    @pytest.mark.parametrize(
        ("tool", "expected"),
        [
            ("kilo", ".kilo/skills/my-skill/SKILL.md"),
            ("cline", ".cline/skills/my-skill/SKILL.md"),
            ("claude", ".claude/skills/my-skill/SKILL.md"),
            ("copilot", ".github/skills/my-skill.md"),
            ("cursor", ".cursor/skills/my-skill/SKILL.md"),
        ],
    )
    def test_writes_skill_for_each_tool(self, tmp_path, tool, expected):
        builder = PromptBuilder(tool)
        skill = {"name": "my-skill", "full_content": "skill body"}
        written = builder._write_single_skill(tmp_path, skill)
        assert written == [expected]
        # The emitter synthesizes name/description frontmatter when the body has
        # none (PRO-7 follow-up); the original body is preserved after it.
        assert (tmp_path / expected).read_text().endswith("skill body")


class TestParseSkillsFile:
    """Tests for _parse_skills_file."""

    def test_parses_multiple_skills(self, kilo_builder):
        content = "---\nname: first\n---\nbody one\n---\nname: second\n---\nbody two\n"
        skills = kilo_builder._parse_skills_file(content)
        names = [s["name"] for s in skills]
        assert names == ["first", "second"]
        assert "body one" in skills[0]["body"]
        assert skills[1]["full_content"].startswith("---")

    def test_empty_content_returns_empty_list(self, kilo_builder):
        assert kilo_builder._parse_skills_file("") == []

    def test_frontmatter_without_name_is_skipped(self, kilo_builder):
        content = "---\ntitle: nope\n---\nbody\n"
        assert kilo_builder._parse_skills_file(content) == []


class TestLoadWorkflowContent:
    """Tests for _load_workflow_content."""

    def test_missing_workflow_returns_none(self, kilo_builder):
        assert kilo_builder._load_workflow_content("definitely-not-a-workflow", "minimal") is None


class TestWriteSkillFiles:
    """Tests for _write_skill_files."""

    def test_agent_without_skills_returns_empty(self, kilo_builder, tmp_path):
        agent = make_agent(skills=[])
        assert kilo_builder._write_skill_files(tmp_path, "code", agent, "minimal") == []

    def test_real_skill_is_written(self, kilo_builder, tmp_path):
        # code-review-practices exists in the bundled skills directory.
        agent = make_agent(skills=["code-review-practices"])
        written = kilo_builder._write_skill_files(tmp_path, "review", agent, "minimal")
        assert written == [".kilo/skills/code-review-practices/SKILL.md"]
        assert (tmp_path / written[0]).exists()

    def test_unknown_skill_is_skipped_with_a_warning(self, kilo_builder, tmp_path):
        # PRO-89: an unresolvable skill still yields no file, but it must no
        # longer do so silently — the miss is what let 26 skills sit dead.
        agent = make_agent(skills=["totally-made-up-skill"])
        with pytest.warns(MissingSkillWarning, match="totally-made-up-skill"):
            written = kilo_builder._write_skill_files(tmp_path, "code", agent, "minimal")
        assert written == []


class TestWriteWorkflowFiles:
    """Tests for _write_workflow_files."""

    def test_agent_without_workflows_returns_empty(self, kilo_builder, tmp_path):
        agent = make_agent(workflows=[])
        assert kilo_builder._write_workflow_files(tmp_path, "code", agent, "minimal") == []

    def test_non_kilo_tool_returns_empty(self, tmp_path):
        builder = PromptBuilder("cline")
        agent = make_agent(workflows=["some-workflow"])
        assert builder._write_workflow_files(tmp_path, "code", agent, "minimal") == []

    def test_unknown_workflow_is_skipped(self, kilo_builder, tmp_path):
        agent = make_agent(workflows=["nonexistent-workflow"])
        assert kilo_builder._write_workflow_files(tmp_path, "code", agent, "minimal") == []


class TestFilterAgentForLanguage:
    """Tests for _filter_agent_for_language."""

    def test_returns_agent_instance(self, kilo_builder):
        agent = make_agent(name="code", skills=["s1"], workflows=["w1"])
        result = kilo_builder._filter_agent_for_language(agent, "python")
        assert isinstance(result, Agent)
        assert result.name == "code"
        # Tools are never filtered.
        assert result.tools == agent.tools

    def test_no_loaders_falls_back_to_original_skills(self, kilo_builder):
        # Disable loaders so the fallback path (original agent skills) executes.
        kilo_builder.agent_skill_loader = None
        kilo_builder.language_skill_loader = None
        agent = make_agent(skills=["orig-skill"], workflows=["orig-wf"])
        result = kilo_builder._filter_agent_for_language(agent, None)
        assert result.skills == ["orig-skill"]
        assert result.workflows == ["orig-wf"]

    def test_no_loaders_empty_agent_yields_empty_lists(self, kilo_builder):
        kilo_builder.agent_skill_loader = None
        kilo_builder.language_skill_loader = None
        agent = make_agent(skills=[], workflows=[])
        result = kilo_builder._filter_agent_for_language(agent, None)
        assert result.skills == []
        assert result.workflows == []


class TestBuild:
    """Tests for the high-level build orchestration on small persona sets."""

    def test_dry_run_returns_list_without_writing(self, kilo_builder, tmp_path):
        config = {"variant": "minimal", "spec": {"language": "python"}, "active_personas": []}
        actions = kilo_builder.build(tmp_path, config=config, dry_run=True)
        assert isinstance(actions, list)
        # No agent files written during dry run.
        assert not (tmp_path / ".kilo" / "agents").exists()

    def test_persona_filtering_failure_is_logged(self, kilo_builder, tmp_path, monkeypatch):
        # Force persona filtering to raise so the warning branch executes.
        import prompticorn.prompt_builder as pb

        def boom(*args, **kwargs):
            raise RuntimeError("persona blew up")

        monkeypatch.setattr(pb.PersonaRegistry, "from_yaml", boom)
        config = {"variant": "minimal", "active_personas": ["software_engineer"]}
        actions = kilo_builder.build(tmp_path, config=config, dry_run=True)
        assert any("Persona filtering failed" in a for a in actions)

    def test_claude_build_writes_claude_md(self, tmp_path):
        builder = PromptBuilder("claude")
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": [],
        }
        actions = builder.build(tmp_path, config=config, dry_run=False)
        assert (tmp_path / "CLAUDE.md").exists()
        assert any("CLAUDE.md" in a for a in actions)

    def test_kilo_build_writes_agents_md(self, tmp_path):
        builder = PromptBuilder("kilo")
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": [],
        }
        actions = builder.build(tmp_path, config=config, dry_run=False)
        assert (tmp_path / "AGENTS.md").exists()
        assert any("AGENTS.md" in a for a in actions)
