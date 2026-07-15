"""Coverage-focused tests for prompticorn.config_handler module."""

from pathlib import Path

from prompticorn.config_handler import (
    ConfigHandler,
    create_default_config,
    create_multi_language_config,
    detect_repository_type,
)


class TestEnsureConfigDir:
    """Tests for ConfigHandler.ensure_config_dir."""

    def test_creates_sessions_subdirectory(self, tmp_path):
        """Should create a sessions subdirectory inside the config dir."""
        # Arrange
        config_dir = tmp_path / ".prompticorn"

        # Act
        result = ConfigHandler.ensure_config_dir(config_dir)

        # Assert
        assert result == config_dir
        assert (config_dir / "sessions").is_dir()

    def test_idempotent_when_already_exists(self, tmp_path):
        """Should not fail when the directory already exists."""
        # Arrange
        config_dir = tmp_path / ".prompticorn"
        config_dir.mkdir()

        # Act
        ConfigHandler.ensure_config_dir(config_dir)
        result = ConfigHandler.ensure_config_dir(config_dir)

        # Assert
        assert result == config_dir
        assert (config_dir / "sessions").is_dir()

    def test_uses_default_dir_when_none(self, monkeypatch, tmp_path):
        """Should fall back to DEFAULT_CONFIG_DIR when no dir is provided."""
        # Arrange
        default_dir = tmp_path / "default-config"
        monkeypatch.setattr(ConfigHandler, "DEFAULT_CONFIG_DIR", default_dir)

        # Act
        result = ConfigHandler.ensure_config_dir(None)

        # Assert
        assert result == default_dir
        assert default_dir.is_dir()


class TestMigrateFromPromptosaurus:
    """Tests for the legacy directory migration behavior."""

    def test_renames_legacy_dir_when_target_missing(self, tmp_path):
        """Should rename .promptosaurus to the new config dir when target absent."""
        # Arrange
        legacy = tmp_path / ".promptosaurus"
        legacy.mkdir()
        (legacy / "marker.txt").write_text("legacy")
        config_dir = tmp_path / ".prompticorn"

        # Act
        ConfigHandler._migrate_from_promptosaurus(config_dir)

        # Assert
        assert config_dir.is_dir()
        assert (config_dir / "marker.txt").read_text() == "legacy"
        assert not legacy.exists()

    def test_no_migration_when_legacy_absent(self, tmp_path):
        """Should do nothing when there is no legacy directory."""
        # Arrange
        config_dir = tmp_path / ".prompticorn"

        # Act
        ConfigHandler._migrate_from_promptosaurus(config_dir)

        # Assert
        assert not config_dir.exists()

    def test_no_migration_when_target_already_exists(self, tmp_path):
        """Should not rename when the new config dir already exists."""
        # Arrange
        legacy = tmp_path / ".promptosaurus"
        legacy.mkdir()
        config_dir = tmp_path / ".prompticorn"
        config_dir.mkdir()

        # Act
        ConfigHandler._migrate_from_promptosaurus(config_dir)

        # Assert
        assert legacy.exists()
        assert config_dir.exists()

    def test_ensure_config_dir_triggers_migration(self, tmp_path):
        """ensure_config_dir should migrate a legacy directory before creating."""
        # Arrange
        legacy = tmp_path / ".promptosaurus"
        legacy.mkdir()
        (legacy / "old.yaml").write_text("x: 1")
        config_dir = tmp_path / ".prompticorn"

        # Act
        ConfigHandler.ensure_config_dir(config_dir)

        # Assert
        assert (config_dir / "old.yaml").exists()
        assert (config_dir / "sessions").is_dir()


class TestGetConfigPath:
    """Tests for ConfigHandler.get_config_path."""

    def test_default_path(self):
        """Should join the default dir with the default filename."""
        # Act
        path = ConfigHandler.get_config_path()

        # Assert
        assert path == Path(".prompticorn") / ".prompticorn.yaml"

    def test_custom_dir(self, tmp_path):
        """Should join a custom dir with the default filename."""
        # Act
        path = ConfigHandler.get_config_path(tmp_path)

        # Assert
        assert path == tmp_path / ".prompticorn.yaml"


class TestLoadConfig:
    """Tests for ConfigHandler.load_config."""

    def test_missing_file_returns_empty_dict(self, tmp_path):
        """Should return an empty dict for a missing file."""
        # Act
        loaded = ConfigHandler.load_config(tmp_path / "nope.yaml")

        # Assert
        assert loaded == {}

    def test_empty_file_returns_empty_dict(self, tmp_path):
        """Should return an empty dict when the YAML file is empty."""
        # Arrange
        config_path = tmp_path / "empty.yaml"
        config_path.write_text("")

        # Act
        loaded = ConfigHandler.load_config(config_path)

        # Assert
        assert loaded == {}

    def test_loads_existing_yaml(self, tmp_path):
        """Should parse an existing YAML file into a dict."""
        # Arrange
        config_path = tmp_path / "config.yaml"
        config_path.write_text("version: '1.0'\nspec:\n  language: python\n")

        # Act
        loaded = ConfigHandler.load_config(config_path)

        # Assert
        assert loaded["version"] == "1.0"
        assert loaded["spec"]["language"] == "python"

    def test_uses_default_path_when_none(self, monkeypatch, tmp_path):
        """Should resolve the default path when none is provided."""
        # Arrange
        monkeypatch.setattr(ConfigHandler, "DEFAULT_CONFIG_DIR", tmp_path / "cfg")

        # Act
        loaded = ConfigHandler.load_config(None)

        # Assert
        assert loaded == {}


class TestSaveConfig:
    """Tests for ConfigHandler.save_config."""

    def test_round_trip(self, tmp_path):
        """Should write a config that can be read back identically."""
        # Arrange
        config_path = tmp_path / "sub" / "config.yaml"
        config = {"version": "1.0", "spec": {"language": "python"}}

        # Act
        ConfigHandler.save_config(config, config_path)
        loaded = ConfigHandler.load_config(config_path)

        # Assert
        assert loaded == config
        assert (tmp_path / "sub" / "sessions").is_dir()

    def test_uses_default_path_when_none(self, monkeypatch, tmp_path):
        """Should save to the default path when none is provided."""
        # Arrange
        config_dir = tmp_path / "cfg"
        monkeypatch.setattr(ConfigHandler, "DEFAULT_CONFIG_DIR", config_dir)

        # Act
        ConfigHandler.save_config({"version": "1.0"}, None)

        # Assert
        assert (config_dir / ".prompticorn.yaml").exists()


class TestConfigExists:
    """Tests for ConfigHandler.config_exists."""

    def test_false_when_missing(self, tmp_path):
        """Should return False for a missing config file."""
        # Act / Assert
        assert ConfigHandler.config_exists(tmp_path / "missing.yaml") is False

    def test_true_when_present(self, tmp_path):
        """Should return True for an existing config file."""
        # Arrange
        config_path = tmp_path / "config.yaml"
        config_path.write_text("version: '1.0'")

        # Act / Assert
        assert ConfigHandler.config_exists(config_path) is True

    def test_uses_default_path_when_none(self, monkeypatch, tmp_path):
        """Should check the default path when none is provided."""
        # Arrange
        monkeypatch.setattr(ConfigHandler, "DEFAULT_CONFIG_DIR", tmp_path / "cfg")

        # Act / Assert
        assert ConfigHandler.config_exists(None) is False


class TestGetYaml:
    """Tests for the cached YAML instance."""

    def test_returns_cached_instance(self):
        """Should return the same instance on repeated calls."""
        # Act
        first = ConfigHandler._get_yaml()
        second = ConfigHandler._get_yaml()

        # Assert
        assert first is second


class TestDefaultTemplates:
    """Tests for the default template factory methods."""

    def test_single_language_template_structure(self):
        """Single-language template should expose expected nested keys."""
        # Act
        template = ConfigHandler.get_default_single_language_template()

        # Assert
        assert template["version"] == "1.0"
        assert template["repository"]["type"] == "single-language"
        assert template["spec"]["abstract_class_style"] == "interface"
        assert template["spec"]["coverage"]["line"] == 80
        assert "project" in template

    def test_default_project_settings(self):
        """Project settings should contain language-agnostic defaults."""
        # Act
        settings = ConfigHandler.get_default_project_settings()

        # Assert — data-system and layout/error-handling moved to per-spec.
        assert settings["commit_style"] == ""
        assert set(settings) == {
            "commit_style",
            "pr_size",
            "deploy_target",
        }

    def test_multi_language_template_structure(self):
        """Multi-language template should use a list spec."""
        # Act
        template = ConfigHandler.get_default_multi_language_template()

        # Assert
        assert template["repository"]["type"] == "multi-language-monorepo"
        assert template["spec"] == []
        assert template["project"]["commit_style"] == ""


class TestCreateDefaultConfig:
    """Tests for create_default_config."""

    def test_single_language_default(self):
        """Should produce a single-language config with a dict spec."""
        # Act
        config = create_default_config("python")

        # Assert
        assert config["repository"]["type"] == "single-language"
        assert isinstance(config["spec"], dict)
        assert config["spec"]["language"] == "python"

    def test_multi_language_branch_returns_list_spec(self):
        """Multi-language repo_type should produce an empty list spec."""
        # Act
        config = create_default_config("python", repo_type="multi-language-monorepo")

        # Assert
        assert config["repository"]["type"] == "multi-language-monorepo"
        assert config["spec"] == []


class TestCreateMultiLanguageConfig:
    """Tests for create_multi_language_config."""

    def test_sets_folder_specs(self):
        """Should attach the provided folder specs to the config."""
        # Arrange
        specs = [{"folder": "api", "language": "python"}]

        # Act
        config = create_multi_language_config(specs)

        # Assert
        assert config["spec"] == specs
        assert config["repository"]["type"] == "multi-language-monorepo"

    def test_kwarg_applied_to_repository_key(self):
        """A kwarg matching a repository key should update that nested value."""
        # Act
        config = create_multi_language_config([], type="custom-type")

        # Assert
        assert config["repository"]["type"] == "custom-type"

    def test_kwarg_applied_to_top_level_key(self):
        """A kwarg not in repository should be set at the top level."""
        # Act
        config = create_multi_language_config([], version="2.0")

        # Assert
        assert config["version"] == "2.0"

    def test_falsy_kwargs_ignored(self):
        """Falsy kwarg values should be ignored, leaving defaults intact."""
        # Act
        config = create_multi_language_config([], version="", type=None)

        # Assert
        assert config["version"] == "1.0"
        assert config["repository"]["type"] == "multi-language-monorepo"


class TestDetectRepositoryType:
    """Tests for detect_repository_type covering all branches."""

    def test_empty_config_is_unknown(self):
        """An empty config should be reported as unknown."""
        # Act / Assert
        assert detect_repository_type({}) == "unknown"

    def test_explicit_single_language(self):
        """An explicit single-language type should be returned as-is."""
        # Act / Assert
        assert (
            detect_repository_type({"repository": {"type": "single-language"}}) == "single-language"
        )

    def test_explicit_multi_language(self):
        """An explicit multi-language-monorepo type should be returned as-is."""
        # Act / Assert
        assert (
            detect_repository_type({"repository": {"type": "multi-language-monorepo"}})
            == "multi-language-monorepo"
        )

    def test_explicit_mixed(self):
        """An explicit mixed type should be returned as-is."""
        # Act / Assert
        assert detect_repository_type({"repository": {"type": "mixed"}}) == "mixed"

    def test_detect_from_list_spec(self):
        """A list spec without explicit type should be multi-language."""
        # Act / Assert
        assert detect_repository_type({"spec": [{"folder": "api"}]}) == "multi-language-monorepo"

    def test_detect_from_dict_spec(self):
        """A dict spec without explicit type should be single-language."""
        # Act / Assert
        assert detect_repository_type({"spec": {"language": "python"}}) == "single-language"

    def test_missing_spec_is_unknown(self):
        """A config with no spec and no explicit type should be unknown."""
        # Act / Assert
        assert detect_repository_type({"repository": {"type": ""}}) == "unknown"

    def test_non_collection_spec_is_unknown(self):
        """A spec that is neither list nor dict should be unknown."""
        # Act / Assert
        assert detect_repository_type({"spec": "not-a-collection"}) == "unknown"


class TestOrmDatabaseMigration:
    """Tests for the one-shot legacy orm/database migration on load."""

    def test_single_language_scalar_migrated_to_lists(self):
        """Old single-language scalars become per-spec lists; project keys dropped."""
        # Arrange
        config = {
            "spec": {"language": "python"},
            "project": {
                "database": "PostgreSQL",
                "orm": "SQLAlchemy",
                "layout_style": "src",
                "error_handling": "Exceptions",
                "commit_style": "Conventional Commits",
            },
        }
        # Act
        ConfigHandler._migrate_old_orm_database_to_fungible(config)
        # Assert
        assert config["spec"]["databases"] == ["PostgreSQL"]
        assert config["spec"]["data_access"] == ["SQLAlchemy"]
        assert config["spec"]["layout_style"] == "src"
        assert config["spec"]["error_handling"] == "Exceptions"
        assert "database" not in config["project"]
        assert "orm" not in config["project"]
        assert "layout_style" not in config["project"]
        assert "error_handling" not in config["project"]
        assert config["project"]["commit_style"] == "Conventional Commits"

    def test_monorepo_backend_seeded_frontend_empty(self):
        """Backend/custom folders inherit data-system; frontend folders get [] ."""
        # Arrange
        config = {
            "spec": [
                {"language": "python", "type": "backend", "subtype": "api"},
                {"language": "typescript", "type": "frontend", "subtype": "ui"},
            ],
            "project": {"database": "PostgreSQL", "orm": "Prisma"},
        }
        # Act
        ConfigHandler._migrate_old_orm_database_to_fungible(config)
        # Assert
        backend, frontend = config["spec"]
        assert backend["databases"] == ["PostgreSQL"]
        assert backend["data_access"] == ["Prisma"]
        assert frontend["databases"] == []
        assert frontend["data_access"] == []

    def test_frontend_inherits_layout_and_error_but_not_data_system(self):
        """PRO-3 decision: layout_style/error_handling are per-language core fields
        that apply to frontend languages too, so a frontend folder inherits the
        user's prior global choice on migration (dropping them would silently lose
        it). Only the data-system fields are backend-only."""
        # Arrange
        config = {
            "spec": [
                {"language": "typescript", "type": "frontend", "subtype": "ui"},
            ],
            "project": {
                "database": "PostgreSQL",
                "orm": "Prisma",
                "layout_style": "src",
                "error_handling": "Exceptions",
            },
        }
        # Act
        ConfigHandler._migrate_old_orm_database_to_fungible(config)
        # Assert — data-system stays empty (backend-only), but layout/error carry over.
        (frontend,) = config["spec"]
        assert frontend["databases"] == []
        assert frontend["data_access"] == []
        assert frontend["layout_style"] == "src"
        assert frontend["error_handling"] == "Exceptions"

    def test_migration_is_idempotent(self):
        """Running the migration twice must not corrupt or accumulate values."""
        # Arrange
        config = {
            "spec": {"language": "python"},
            "project": {"database": "PostgreSQL", "orm": "SQLAlchemy"},
        }
        # Act
        ConfigHandler._migrate_old_orm_database_to_fungible(config)
        first = {
            "databases": list(config["spec"]["databases"]),
            "data_access": list(config["spec"]["data_access"]),
        }
        ConfigHandler._migrate_old_orm_database_to_fungible(config)
        # Assert — second run is a no-op (legacy keys already removed).
        assert config["spec"]["databases"] == first["databases"]
        assert config["spec"]["data_access"] == first["data_access"]

    def test_new_shape_config_is_noop(self):
        """A config already in the new shape is left untouched."""
        # Arrange
        config = {
            "spec": {
                "language": "python",
                "databases": ["MySQL"],
                "data_access": ["Django ORM"],
            },
            "project": {"commit_style": ""},
        }
        # Act
        ConfigHandler._migrate_old_orm_database_to_fungible(config)
        # Assert
        assert config["spec"]["databases"] == ["MySQL"]
        assert config["spec"]["data_access"] == ["Django ORM"]
        assert "databases" not in config["project"]

    def test_empty_scalars_become_empty_lists(self):
        """Empty legacy scalars migrate to empty lists, not [''] ."""
        # Arrange
        config = {"spec": {"language": "python"}, "project": {"database": "", "orm": ""}}
        # Act
        ConfigHandler._migrate_old_orm_database_to_fungible(config)
        # Assert
        assert config["spec"]["databases"] == []
        assert config["spec"]["data_access"] == []
