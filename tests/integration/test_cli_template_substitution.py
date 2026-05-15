"""Integration test for template substitution through CLI workflow."""

import tempfile
from pathlib import Path

from prompticorn.prompt_builder import PromptBuilder


class TestCLITemplateSubstitution:
    """Test that template variables are substituted when using PromptBuilder (CLI path)."""

    def test_prompt_builder_passes_config_to_kilo_builder(self):
        """PromptBuilder should pass config to underlying builder for template substitution."""
        # Arrange
        builder = PromptBuilder("kilo")
        config = {"variant": "minimal", "spec": {"language": "python"}}

        # Act - Build to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            builder.build(output_path, config=config, dry_run=False)

            # Assert - Check that orchestrator was built
            orchestrator_file = output_path / ".kilo" / "agents" / "orchestrator.md"
            assert orchestrator_file.exists(), "Orchestrator agent file should be created"

            # Read the file
            content = orchestrator_file.read_text()

            # Template variable should be replaced
            assert "{{PRIMARY_AGENTS_LIST}}" not in content, (
                "Template variable should be substituted in generated file"
            )

            # Should contain actual agent entries
            assert "- **architect**" in content or "- **code**" in content, (
                "Should contain actual agent list entries"
            )

    def test_orchestrator_output_has_complete_agent_list(self):
        """Orchestrator should have a complete list of primary agents."""
        # Arrange
        builder = PromptBuilder("kilo")
        config = {"variant": "minimal", "spec": {}}

        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            builder.build(output_path, config=config, dry_run=False)

            orchestrator_file = output_path / ".kilo" / "agents" / "orchestrator.md"
            content = orchestrator_file.read_text()

            # Assert - Check for several expected agents
            expected_agents = ["architect", "ask", "orchestrator", "backend"]
            for agent in expected_agents:
                assert f"- **{agent}**" in content, f"Agent list should include {agent}"

    def test_config_none_does_not_crash(self):
        """Builder should handle config=None gracefully."""
        # Arrange
        builder = PromptBuilder("kilo")

        # Act - Should not crash
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            actions = builder.build(output_path, config=None, dry_run=False)

            # Assert - Should have created files
            assert len(actions) > 0

            orchestrator_file = output_path / ".kilo" / "agents" / "orchestrator.md"
            assert orchestrator_file.exists()
