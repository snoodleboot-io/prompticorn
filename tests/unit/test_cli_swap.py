"""Unit tests for swap command in CLI."""

from click.testing import CliRunner

from prompticorn.cli import cli


class TestSwapCommand:
    """Tests for the swap command."""

    def test_swap_command_is_registered(self):
        """Swap command should be registered in CLI."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "swap" in result.output, "Swap command should be in help output"

    def test_swap_command_requires_config(self):
        """Swap command should fail gracefully if no config exists."""
        runner = CliRunner()

        # Run in isolated filesystem to ensure no config exists
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["swap"])

            # Should fail with error message about missing config
            assert result.exit_code != 0
            assert "No configuration found" in result.output or "Error" in result.output

    def test_swap_command_has_correct_help_text(self):
        """Swap command should have descriptive help text."""
        runner = CliRunner()
        result = runner.invoke(cli, ["swap", "--help"])

        assert result.exit_code == 0
        assert "persona" in result.output.lower(), "Help should mention personas"
        assert "regenerate" in result.output.lower(), "Help should mention regeneration"
