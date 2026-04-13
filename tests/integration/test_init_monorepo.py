"""Integration tests for monorepo configuration initialization."""

from pathlib import Path

import pytest

from promptosaurus.config_handler import ConfigHandler
from promptosaurus.questions.base.spec_handler import FolderSpec


class TestMonorepoFolderDetection:
    """Tests for folder-level type detection in monorepo."""

    def test_frontend_folder_defaults_to_typescript(self):
        """Test that frontend folders default to TypeScript."""
        spec = FolderSpec(
            folder="frontend",
            type="frontend",
        )
        assert spec.language == "typescript"

    def test_ui_folder_defaults_to_typescript(self):
        """Test that ui folders default to TypeScript."""
        spec = FolderSpec(
            folder="ui",
            type="frontend",
            subtype="ui",
        )
        assert spec.language == "typescript"

    def test_backend_folder_defaults_to_python(self):
        """Test that backend folders default to Python."""
        spec = FolderSpec(
            folder="backend",
            type="backend",
        )
        assert spec.language == "python"

    def test_frontend_ui_folder_defaults_to_typescript(self):
        """Test that frontend/ui folders default to TypeScript."""
        spec = FolderSpec(
            folder="frontend/ui",
            type="frontend",
            subtype="ui",
        )
        assert spec.language == "typescript"


class TestMonorepoConfig:
    """Tests for multi-language-monorepo configuration."""

    def test_multi_language_config_template(self):
        """Verify multi-language config template exists."""
        from promptosaurus.config_handler import ConfigHandler

        assert "repository" in ConfigHandler.get_default_multi_language_template()
        assert "spec" in ConfigHandler.get_default_multi_language_template()
        assert (
            ConfigHandler.get_default_multi_language_template()["repository"]["type"]
            == "multi-language-monorepo"
        )

    def test_spec_list_structure(self):
        """Verify spec can be a list of folder specs."""
        specs = [
            {
                "folder": "backend/api",
                "type": "backend",
                "language": "python",
            },
            {
                "folder": "frontend/ui",
                "type": "frontend",
                "language": "typescript",
            },
        ]
        config = ConfigHandler.get_default_multi_language_template()
        config["spec"] = specs
        assert len(config["spec"]) == 2
        assert config["spec"][0]["folder"] == "backend/api"
        assert config["spec"][1]["folder"] == "frontend/ui"

    def test_repository_type_setting(self):
        """Verify repository type can be set."""
        config = ConfigHandler.get_default_multi_language_template()
        assert config["repository"]["type"] == "multi-language-monorepo"


class TestMonorepoInit:
    """Tests for initializing multi-language monorepo."""

    @pytest.mark.skip(reason="Requires full user interaction")
    def test_monorepo_init_creates_config(self, tmp_path):
        """Test that monorepo initialization creates valid config."""
        # This would require full CLI interaction
        # Skipping for now as it's an end-to-end test
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
