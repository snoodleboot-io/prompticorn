"""Coverage-focused unit tests for prompticorn.personas.registry.

These tests use inline persona data and tmp_path fixtures to exercise every
public method, default-value branch, and error path of PersonaRegistry and
PersonaFilter without relying on the shipped personas.yaml.
"""

import textwrap
from pathlib import Path

import pytest
import yaml

from prompticorn.personas.registry import PersonaFilter, PersonaRegistry


@pytest.fixture
def sample_data():
    """A fully-populated persona dataset covering all queried fields."""
    return {
        "version": "2.0",
        "universal_agents": ["ask", "debug"],
        "personas": {
            "engineer": {
                "display_name": "Engineer",
                "description": "Builds things.",
                "focus": "implementation",
                "primary_agents": ["code", "test"],
                "secondary_agents": ["review"],
                "workflows": ["code", "test"],
                "skills": ["aaa", "mocking"],
            },
            "tester": {
                "display_name": "Tester",
                "description": "Tests things.",
                "focus": "quality",
                "primary_agents": ["test"],
                "secondary_agents": [],
                "workflows": ["test"],
                "skills": ["coverage"],
            },
        },
    }


@pytest.fixture
def registry(sample_data):
    """Registry built directly from sample data."""
    return PersonaRegistry(sample_data)


def _write_yaml(directory: Path, data: dict) -> Path:
    """Arrange helper: persist a dict to a yaml file and return its path."""
    path = directory / "personas.yaml"
    path.write_text(yaml.safe_dump(data))
    return path


class TestPersonaRegistryConstruction:
    """Construction and default-value handling."""

    def test_init_populates_fields(self, sample_data):
        # Arrange / Act
        reg = PersonaRegistry(sample_data)

        # Assert
        assert reg.list_personas() == ["engineer", "tester"]
        assert reg.get_universal_agents() == ["ask", "debug"]

    def test_init_uses_defaults_for_empty_data(self):
        # Arrange / Act: empty dict triggers all .get() defaults
        reg = PersonaRegistry({})

        # Assert
        assert reg.list_personas() == []
        assert reg.get_universal_agents() == []
        assert reg._version == "unknown"

    def test_init_reads_version(self, registry):
        # Assert
        assert registry._version == "2.0"

    def test_from_yaml_with_path_object(self, tmp_path, sample_data):
        # Arrange
        path = _write_yaml(tmp_path, sample_data)

        # Act
        reg = PersonaRegistry.from_yaml(path)

        # Assert
        assert reg.list_personas() == ["engineer", "tester"]

    def test_from_yaml_with_string_path(self, tmp_path, sample_data):
        # Arrange
        path = _write_yaml(tmp_path, sample_data)

        # Act: pass a str to exercise Path() coercion branch
        reg = PersonaRegistry.from_yaml(str(path))

        # Assert
        assert reg.get_display_name("engineer") == "Engineer"

    def test_from_yaml_missing_file_raises(self, tmp_path):
        # Arrange
        missing = tmp_path / "does_not_exist.yaml"

        # Act / Assert
        with pytest.raises(FileNotFoundError, match="Personas file not found"):
            PersonaRegistry.from_yaml(missing)

    def test_from_yaml_malformed_raises(self, tmp_path):
        # Arrange: invalid yaml content
        path = tmp_path / "bad.yaml"
        path.write_text(textwrap.dedent("foo: [unclosed"))

        # Act / Assert
        with pytest.raises(yaml.YAMLError):
            PersonaRegistry.from_yaml(path)


class TestPersonaRegistryQueries:
    """Query methods over a known dataset."""

    def test_get_persona_info_returns_full_dict(self, registry):
        # Act
        info = registry.get_persona_info("engineer")

        # Assert
        assert info["focus"] == "implementation"
        assert info["primary_agents"] == ["code", "test"]

    def test_get_persona_info_unknown_raises_keyerror(self, registry):
        # Act / Assert
        with pytest.raises(KeyError, match="not found"):
            registry.get_persona_info("ghost")

    def test_get_agents_combines_primary_and_secondary(self, registry):
        # Act
        agents = registry.get_agents_for_persona("engineer")

        # Assert: order is primary then secondary
        assert agents == ["code", "test", "review"]

    def test_get_agents_with_empty_secondary(self, registry):
        # Act
        agents = registry.get_agents_for_persona("tester")

        # Assert
        assert agents == ["test"]

    def test_get_agents_defaults_when_keys_absent(self):
        # Arrange: persona lacking agent keys exercises .get([]) defaults
        reg = PersonaRegistry({"personas": {"bare": {}}})

        # Act
        agents = reg.get_agents_for_persona("bare")

        # Assert
        assert agents == []

    def test_get_workflows(self, registry):
        # Act / Assert
        assert registry.get_workflows_for_persona("engineer") == ["code", "test"]

    def test_get_workflows_default_when_absent(self):
        # Arrange
        reg = PersonaRegistry({"personas": {"bare": {}}})

        # Act / Assert
        assert reg.get_workflows_for_persona("bare") == []

    def test_get_skills(self, registry):
        # Act / Assert
        assert registry.get_skills_for_persona("engineer") == ["aaa", "mocking"]

    def test_get_skills_default_when_absent(self):
        # Arrange
        reg = PersonaRegistry({"personas": {"bare": {}}})

        # Act / Assert
        assert reg.get_skills_for_persona("bare") == []

    def test_get_display_name(self, registry):
        # Act / Assert
        assert registry.get_display_name("tester") == "Tester"

    def test_get_display_name_falls_back_to_key(self):
        # Arrange: no display_name -> returns persona_name
        reg = PersonaRegistry({"personas": {"bare": {}}})

        # Act / Assert
        assert reg.get_display_name("bare") == "bare"

    def test_get_description(self, registry):
        # Act / Assert
        assert registry.get_description("engineer") == "Builds things."

    def test_get_description_default_empty(self):
        # Arrange
        reg = PersonaRegistry({"personas": {"bare": {}}})

        # Act / Assert
        assert reg.get_description("bare") == ""


class TestPersonaFilter:
    """Filtering behavior across selected personas."""

    def test_init_validates_personas(self, registry):
        # Act / Assert: an unknown persona raises during construction
        with pytest.raises(KeyError, match="Invalid persona"):
            PersonaFilter(registry, ["engineer", "ghost"])

    def test_init_accepts_empty_selection(self, registry):
        # Act
        flt = PersonaFilter(registry, [])

        # Assert: only universal agents remain enabled
        assert flt.get_enabled_agents() == {"ask", "debug"}
        assert flt.get_enabled_workflows() == set()
        assert flt.get_enabled_skills() == set()

    def test_get_enabled_agents_includes_universal_and_persona(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["engineer"])

        # Act
        enabled = flt.get_enabled_agents()

        # Assert
        assert enabled == {"ask", "debug", "code", "test", "review"}

    def test_get_enabled_agents_unions_multiple_personas(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["engineer", "tester"])

        # Act
        enabled = flt.get_enabled_agents()

        # Assert: union of both personas + universal, deduplicated
        assert enabled == {"ask", "debug", "code", "test", "review"}

    def test_get_enabled_workflows(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["engineer", "tester"])

        # Act / Assert
        assert flt.get_enabled_workflows() == {"code", "test"}

    def test_get_enabled_skills(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["engineer", "tester"])

        # Act / Assert
        assert flt.get_enabled_skills() == {"aaa", "mocking", "coverage"}

    def test_is_agent_enabled_true_and_false(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["tester"])

        # Act / Assert
        assert flt.is_agent_enabled("test") is True
        assert flt.is_agent_enabled("ask") is True  # universal
        assert flt.is_agent_enabled("code") is False  # tester lacks code

    def test_is_workflow_enabled_true_and_false(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["tester"])

        # Act / Assert
        assert flt.is_workflow_enabled("test") is True
        assert flt.is_workflow_enabled("code") is False

    def test_is_skill_enabled_true_and_false(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["tester"])

        # Act / Assert
        assert flt.is_skill_enabled("coverage") is True
        assert flt.is_skill_enabled("aaa") is False

    def test_get_selected_personas(self, registry):
        # Arrange
        flt = PersonaFilter(registry, ["engineer"])

        # Act / Assert
        assert flt.get_selected_personas() == ["engineer"]
