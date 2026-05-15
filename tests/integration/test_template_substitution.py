"""Integration tests for template variable substitution in KiloBuilder."""

from pathlib import Path

import pytest

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.kilo_builder import KiloBuilder
from prompticorn.ir.models import Agent


class TestTemplateSubstitution:
    """Test that template variables are correctly substituted during build."""

    def test_template_variable_is_substituted_when_config_provided(self):
        """Template variables should be replaced when config is provided."""
        # Arrange
        agent = Agent(
            name="test-agent",
            description="Test agent with template",
            system_prompt="Agents: {{PRIMARY_AGENTS_LIST}}",
        )
        builder = KiloBuilder()
        options = BuildOptions(variant="minimal")
        config = {"spec": {}}

        # Act
        result = builder.build(agent, options, config)

        # Assert
        assert "{{PRIMARY_AGENTS_LIST}}" not in result, (
            "Template variable should be substituted, not left as-is"
        )

    def test_template_variable_not_substituted_without_config(self):
        """Template variables should remain if no config is provided."""
        # Arrange
        agent = Agent(
            name="test-agent",
            description="Test agent",
            system_prompt="Agents: {{PRIMARY_AGENTS_LIST}}",
        )
        builder = KiloBuilder()
        options = BuildOptions(variant="minimal")

        # Act
        result = builder.build(agent, options, config=None)

        # Assert
        assert "{{PRIMARY_AGENTS_LIST}}" in result, (
            "Template variable should remain unchanged when config is None"
        )

    def test_primary_agents_list_contains_agent_entries(self):
        """PRIMARY_AGENTS_LIST should be replaced with actual agent list."""
        # Arrange
        agent = Agent(
            name="test-orchestrator",
            description="Test orchestrator",
            system_prompt="Available:\n{{PRIMARY_AGENTS_LIST}}\nEnd",
        )
        builder = KiloBuilder()
        options = BuildOptions(variant="minimal")
        config = {"spec": {}}

        # Act
        result = builder.build(agent, options, config)

        # Assert - should have markdown list items OR "No agents" message
        assert ("- **" in result) or ("No agents" in result), (
            "PRIMARY_AGENTS_LIST should be replaced with agent list or 'No agents' message"
        )

        # Should NOT have the template variable
        assert "{{PRIMARY_AGENTS_LIST}}" not in result

    def test_real_orchestrator_agent_gets_agent_list(self):
        """Real orchestrator agent should get populated agent list."""
        # Arrange
        from prompticorn.agent_registry.registry import Registry

        agents_dir = Path("prompticorn/agents")
        if not agents_dir.exists():
            pytest.skip("Agents directory not found")

        registry = Registry.from_discovery(agents_dir)
        orchestrator = registry.get_agent("orchestrator")

        # Verify source has template variable
        assert "{{PRIMARY_AGENTS_LIST}}" in orchestrator.system_prompt, (
            "Orchestrator source should contain PRIMARY_AGENTS_LIST template variable"
        )

        # Act - build the agent
        builder = KiloBuilder()
        options = BuildOptions(variant="minimal")
        config = {"spec": {}}
        result = builder.build(orchestrator, options, config)

        # Assert - template should be replaced
        assert "{{PRIMARY_AGENTS_LIST}}" not in result, (
            "Built orchestrator should NOT contain unreplaced template variable"
        )

        # Should have actual agent entries
        assert "- **architect**" in result or "- **code**" in result, (
            "Built orchestrator should contain actual agent list entries"
        )

    def test_template_substitution_works_in_system_prompt_section(self):
        """Substituted content should appear in System Prompt section."""
        # Arrange
        agent = Agent(
            name="test", description="Test", system_prompt="Before\n{{PRIMARY_AGENTS_LIST}}\nAfter"
        )
        builder = KiloBuilder()
        options = BuildOptions(variant="minimal")
        config = {"spec": {}}

        # Act
        result = builder.build(agent, options, config)

        # Assert
        lines = result.split("\n")
        in_system_prompt = False
        found_substitution = False

        for line in lines:
            if line.strip() == "# System Prompt":
                in_system_prompt = True
            elif line.strip().startswith("# ") and in_system_prompt:
                # Reached next section
                break
            elif in_system_prompt:
                if "Before" in line or "After" in line or "- **" in line or "No agents" in line:
                    found_substitution = True

        assert found_substitution, "Template substitution should appear in System Prompt section"
        assert "{{PRIMARY_AGENTS_LIST}}" not in result


class TestPrimaryAgentsHandler:
    """Test the PrimaryAgentsHandler template handler."""

    def test_handler_can_handle_primary_agents_list(self):
        """Handler should recognize PRIMARY_AGENTS_LIST variable."""
        from prompticorn.builders.template_handlers.primary_agents_handler import (
            PrimaryAgentsHandler,
        )

        handler = PrimaryAgentsHandler()
        assert handler.can_handle("PRIMARY_AGENTS_LIST") is True

    def test_handler_rejects_other_variables(self):
        """Handler should reject variables it doesn't handle."""
        from prompticorn.builders.template_handlers.primary_agents_handler import (
            PrimaryAgentsHandler,
        )

        handler = PrimaryAgentsHandler()
        assert handler.can_handle("LANGUAGE") is False
        assert handler.can_handle("RUNTIME") is False
        assert handler.can_handle("OTHER_VAR") is False

    def test_handler_returns_string(self):
        """Handler should return a string when called."""
        from prompticorn.builders.template_handlers.primary_agents_handler import (
            PrimaryAgentsHandler,
        )

        handler = PrimaryAgentsHandler()
        result = handler.handle("PRIMARY_AGENTS_LIST", {})

        assert isinstance(result, str)
        assert len(result) > 0

    def test_handler_formats_as_markdown_list(self):
        """Handler should return markdown-formatted list."""
        from prompticorn.builders.template_handlers.primary_agents_handler import (
            PrimaryAgentsHandler,
        )

        handler = PrimaryAgentsHandler()
        result = handler.handle("PRIMARY_AGENTS_LIST", {})

        # Should either be agent list or "No agents" message
        assert ("- **" in result) or ("No agents" in result)
