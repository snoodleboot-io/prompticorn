"""Tests for project-level settings capture and injection into core conventions."""

import pytest

from prompticorn.cli import _ask_project_questions
from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.questions.project import NOT_SPECIFIED, get_project_questions
from prompticorn.source_layouts import get_source_layout


class TestProjectQuestions:
    """The project-question pipeline and its value mapping."""

    def test_keys_map_to_project_fields(self):
        # Each question key is project_<field>; <field> is the config key.
        keys = [q.key for q in get_project_questions()]
        assert keys == [
            "project_database",
            "project_orm",
            "project_error_handling",
            "project_commit_style",
            "project_pr_size",
            "project_deploy_target",
        ]

    def test_not_specified_maps_to_empty(self):
        # Arrange — a selector that always takes the default (Not specified).
        def select_default(
            question, options, explanations, question_explanation, default_index, allow_multiple
        ):
            return options[default_index]

        # Act
        project = _ask_project_questions(select_default)
        # Assert
        assert project == {
            "database": "",
            "orm": "",
            "error_handling": "",
            "commit_style": "",
            "pr_size": "",
            "deploy_target": "",
        }
        assert NOT_SPECIFIED  # sentinel is importable

    def test_selected_values_are_captured(self):
        def select_first_real(
            question, options, explanations, question_explanation, default_index, allow_multiple
        ):
            # Pick the first non-"Not specified" option.
            return next(o for o in options if o != NOT_SPECIFIED)

        project = _ask_project_questions(select_first_real)
        assert project["database"] == "PostgreSQL"
        assert all(v != "" for v in project.values())


class TestProjectInjection:
    """Project settings render into the core convention."""

    @pytest.mark.parametrize("tool", ["claude", "copilot"])
    def test_project_values_render_in_core_convention(self, tool, tmp_path):
        # Arrange
        config = create_default_config("python")
        config["variant"] = "minimal"
        config["active_personas"] = ["software_engineer"]
        config["project"] = {
            "database": "PostgreSQL",
            "orm": "SQLAlchemy",
            "commit_style": "Conventional Commits",
            "pr_size": "400",
            "deploy_target": "AWS Lambda",
        }
        # Act
        get_prompt_builder(tool).build(tmp_path, config=config, dry_run=False)
        # Assert — values appear and no bare TODO fill-ins remain.
        blob = "\n".join(
            p.read_text(encoding="utf-8", errors="ignore")
            for p in tmp_path.rglob("*")
            if p.is_file()
        )
        assert "PostgreSQL" in blob
        assert "SQLAlchemy" in blob
        assert "AWS Lambda" in blob
        assert "Database:            TODO" not in blob


class TestSourceLayout:
    """Language-specific source-tree layout in the core convention."""

    def test_get_source_layout_is_language_specific(self):
        # Arrange / Act / Assert
        assert "index.ts" in get_source_layout("typescript")
        assert "__init__.py" in get_source_layout("python")
        assert "cmd/" in get_source_layout("golang")

    def test_get_source_layout_falls_back_to_default(self):
        # An unknown language gets the generic layout, never empty.
        layout = get_source_layout("nonexistent-lang")
        assert "src/" in layout

    def test_core_convention_renders_language_layout(self, tmp_path):
        # Arrange
        config = create_default_config("python")
        config["variant"] = "minimal"
        config["active_personas"] = ["software_engineer"]
        # Act
        get_prompt_builder("claude").build(tmp_path, config=config, dry_run=False)
        general = (tmp_path / ".claude" / "conventions" / "core" / "general.md").read_text(
            encoding="utf-8"
        )
        # Assert — the Python standard layout is rendered (not a generic stub).
        assert "__init__.py" in general
        assert "└── TODO" not in general
