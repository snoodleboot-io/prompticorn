"""Unit tests for PromptBuilder with empty personas list."""

import tempfile
from pathlib import Path

from promptosaurus.prompt_builder import PromptBuilder


class TestPromptBuilderEmptyPersonas:
    """Test that empty personas list generates only universal agents."""

    def test_empty_personas_generates_only_universal_agents(self):
        """When active_personas=[], should only generate universal agents."""
        # Arrange
        builder = PromptBuilder("kilo")
        config = {
            "variant": "minimal",
            "spec": {"language": "python"},
            "active_personas": [],  # Empty list - no personas selected
        }

        # Act - Build to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            builder.build(output_path, config=config, dry_run=False)

            # Get list of generated agent files
            agents_dir = output_path / ".kilo" / "agents"
            agent_files = []
            if agents_dir.exists():
                for item in agents_dir.iterdir():
                    if item.is_file() and item.suffix == ".md":
                        agent_files.append(item.stem)

            # Expected universal agents (from personas.yaml)
            expected_universal = {"ask", "debug", "explain", "plan", "orchestrator"}

            # Assert - Should only have universal agents
            actual_agents = set(agent_files)
            assert actual_agents == expected_universal, (
                f"Expected only universal agents {expected_universal}, but got {actual_agents}"
            )

            # Verify count
            assert len(actual_agents) == 5, (
                f"Expected 5 universal agents, but got {len(actual_agents)}"
            )

    def test_empty_personas_action_message(self):
        """Verify action message shows 0 personas selected."""
        # Arrange
        builder = PromptBuilder("kilo")
        config = {"variant": "minimal", "spec": {}, "active_personas": []}

        # Act
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir)
            actions = builder.build(output_path, config=config, dry_run=False)

            # Assert - Should show persona filtering with 0 personas
            persona_action = [a for a in actions if "Persona filtering" in a]
            assert len(persona_action) > 0, "Should have persona filtering action message"
            assert "0 persona(s) selected" in persona_action[0], (
                f"Should show 0 personas selected, got: {persona_action[0]}"
            )
