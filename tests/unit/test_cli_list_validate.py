"""Tests for the `list` and `validate` CLI commands (discovery-based)."""

from pathlib import Path

from click.testing import CliRunner

from prompticorn.cli import cli


class TestListCommand:
    """Tests for `prompticorn list`."""

    def test_list_succeeds_and_shows_discovered_agents(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["list"])
        # Assert
        assert result.exit_code == 0, result.output
        assert "AGENT REGISTRY" in result.output
        assert "code" in result.output  # a known bundled agent
        assert "subagents:" in result.output

    def test_list_output_has_no_attribution_term(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["list"])
        # Assert — user-facing output must not reference the assistant by name
        assert "Claude" not in result.output


class TestValidateCommand:
    """Tests for `prompticorn validate`."""

    def test_validate_passes_on_bundled_agents(self):
        # Arrange
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["validate"])
        # Assert
        assert result.exit_code == 0, result.output
        assert "Registry valid" in result.output

    def test_validate_fails_on_malformed_agent(self, tmp_path, monkeypatch):
        # Arrange — an agent directory with neither prompt.md nor variants
        broken_agents = tmp_path / "agents"
        (broken_agents / "broken").mkdir(parents=True)
        monkeypatch.setattr("prompticorn.cli._AGENTS_DIR", broken_agents)
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["validate"])
        # Assert
        assert result.exit_code == 1
        assert "broken" in result.output
        assert "issue(s) found" in result.output

    def test_validate_reports_missing_agents_dir(self, tmp_path, monkeypatch):
        # Arrange — point at a non-existent agents directory
        monkeypatch.setattr("prompticorn.cli._AGENTS_DIR", tmp_path / "does-not-exist")
        runner = CliRunner()
        # Act
        result = runner.invoke(cli, ["validate"])
        # Assert
        assert result.exit_code == 1
        assert "not found" in result.output.lower()


def test_agents_dir_constant_points_at_package_agents():
    # The CLI must discover from the bundled package agents/ directory.
    from prompticorn import cli as cli_module

    assert cli_module._AGENTS_DIR.name == "agents"
    assert (cli_module._AGENTS_DIR / "code" / "prompt.md").exists()
    assert isinstance(cli_module._AGENTS_DIR, Path)
