"""Edge/error-branch coverage for RegistryDiscovery."""

import pytest

from prompticorn.agent_registry.discovery import RegistryDiscovery
from prompticorn.agent_registry.errors import RegistryLoadError


class TestDiscoverErrors:
    def test_discover_agents_missing_dir_raises(self, tmp_path):
        disc = RegistryDiscovery(tmp_path / "does-not-exist")
        with pytest.raises(RegistryLoadError):
            disc.discover_agents()

    def test_discover_wraps_failure(self, tmp_path):
        disc = RegistryDiscovery(tmp_path / "missing")
        with pytest.raises(RegistryLoadError):
            disc.discover()

    def test_malformed_agent_is_skipped_not_fatal(self, tmp_path):
        # Agent dir with no prompt.md / variants -> load fails, is skipped.
        (tmp_path / "broken").mkdir()
        (tmp_path / "core").mkdir()  # non-agent dir, must be ignored
        result = RegistryDiscovery(tmp_path).discover_agents()
        assert "broken" not in result
        assert "core" not in result


class TestDiscoverSubagents:
    def test_no_subagents_dir_returns_empty(self, tmp_path):
        (tmp_path / "agentx").mkdir()
        assert RegistryDiscovery(tmp_path).discover_subagents("agentx") == {}

    def test_subagent_skips_files_and_hidden(self, tmp_path):
        sub = tmp_path / "agentx" / "subagents"
        sub.mkdir(parents=True)
        (sub / "afile.txt").write_text("x")  # non-dir -> skipped
        (sub / ".hidden").mkdir()  # dot dir -> skipped
        (sub / "broken").mkdir()  # malformed subagent -> skipped, not fatal
        result = RegistryDiscovery(tmp_path).discover_subagents("agentx")
        assert result == {}


class TestValidateStructure:
    def test_missing_agents_dir(self, tmp_path):
        issues = RegistryDiscovery(tmp_path / "nope").validate_structure()
        assert any("not found" in i for i in issues)

    def test_agent_without_prompt_or_variants(self, tmp_path):
        (tmp_path / "lonely").mkdir()
        issues = RegistryDiscovery(tmp_path).validate_structure()
        assert any("lonely" in i and "neither" in i for i in issues)

    def test_variant_missing_prompt(self, tmp_path):
        (tmp_path / "ag" / "minimal").mkdir(parents=True)  # variant dir, no prompt.md
        issues = RegistryDiscovery(tmp_path).validate_structure()
        assert any("ag" in i and "minimal" in i for i in issues)

    def test_subagent_without_variants(self, tmp_path):
        agent = tmp_path / "ag"
        agent.mkdir()
        (agent / "prompt.md").write_text("---\nname: ag\n---\nbody")
        (agent / "subagents" / "subx").mkdir(parents=True)  # no minimal/verbose
        issues = RegistryDiscovery(tmp_path).validate_structure()
        assert any("subx" in i for i in issues)

    def test_clean_top_level_agent_no_issue(self, tmp_path):
        agent = tmp_path / "ag"
        agent.mkdir()
        (agent / "prompt.md").write_text("---\nname: ag\n---\nbody")
        issues = RegistryDiscovery(tmp_path).validate_structure()
        assert not any("ag" in i for i in issues)
