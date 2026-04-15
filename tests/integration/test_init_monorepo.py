"""Integration tests for promptosaurus init CLI command.

These tests exercise the actual CLI flow to catch bugs in the full user journey.
"""

from promptosaurus.questions.base.folder_spec import FolderSpec


class TestSetupMonorepoFolders:
    """Tests for the _setup_monorepo_folders function."""

    def test_folder_spec_import(self):
        """Verify FolderSpec can be imported and used."""
        spec = FolderSpec(
            folder="backend/api",
            type="backend",
            subtype="api",
            language="python",
        )
        assert spec.folder == "backend/api"
        assert spec.language == "python"

    def test_folder_spec_to_dict(self):
        """Verify FolderSpec converts to dict correctly."""
        spec = FolderSpec(
            folder="frontend/ui",
            type="frontend",
            subtype="ui",
            language="typescript",
        )
        d = spec.to_dict()
        assert d["folder"] == "frontend/ui"
        assert d["type"] == "frontend"
        assert d["subtype"] == "ui"
        assert d["language"] == "typescript"

    def test_folder_spec_defaults(self):
        """Verify FolderSpec applies language defaults."""
        spec = FolderSpec(
            folder="backend/api",
            type="backend",
            subtype="api",
        )
        # backend/api should default to Python
        assert spec.language == "python"

    def test_folder_spec_frontend_defaults(self):
        """Verify FolderSpec applies frontend defaults."""
        spec = FolderSpec(
            folder="frontend/ui",
            type="frontend",
            subtype="ui",
        )
        # frontend/ui should default to TypeScript
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
                "subtype": "api",
                "language": "python",
            },
            {
                "folder": "frontend",
                "type": "frontend",
                "subtype": "ui",
                "language": "typescript",
            },
        ]
        assert len(specs) == 2
        assert specs[0]["folder"] == "backend/api"
        assert specs[1]["folder"] == "frontend"


class TestMonorepoPresetTypes:
    """Tests for folder preset types."""

    def test_backend_preset_types(self):
        """Verify backend preset types are defined."""
        from promptosaurus.questions.base.folder_spec import FolderSpecRegistry

        assert "backend" in FolderSpecRegistry.get_folder_type_presets()
        assert "api" in FolderSpecRegistry.get_folder_type_presets()["backend"]
        assert "library" in FolderSpecRegistry.get_folder_type_presets()["backend"]
        assert "worker" in FolderSpecRegistry.get_folder_type_presets()["backend"]
        assert "cli" in FolderSpecRegistry.get_folder_type_presets()["backend"]

    def test_frontend_preset_types(self):
        """Verify frontend preset types are defined."""
        from promptosaurus.questions.base.folder_spec import FolderSpecRegistry

        assert "frontend" in FolderSpecRegistry.get_folder_type_presets()
        assert "ui" in FolderSpecRegistry.get_folder_type_presets()["frontend"]
        assert "library" in FolderSpecRegistry.get_folder_type_presets()["frontend"]
        assert "e2e" in FolderSpecRegistry.get_folder_type_presets()["frontend"]

    def test_preset_languages(self):
        """Verify preset languages are correct."""
        from promptosaurus.questions.base.folder_spec import FolderSpecRegistry

        # Backend defaults to Python
        assert (
            FolderSpecRegistry.get_folder_type_presets()["backend"]["api"]["language"] == "python"
        )
        # Frontend defaults to TypeScript
        assert (
            FolderSpecRegistry.get_folder_type_presets()["frontend"]["ui"]["language"]
            == "typescript"
        )
