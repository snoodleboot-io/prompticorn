"""Tests for project-level settings capture and injection into core conventions."""

import re
from pathlib import Path

import pytest

from prompticorn.builders.convention_generator import (
    generate_all_conventions,
    get_all_languages,
)
from prompticorn.cli import _ask_project_questions
from prompticorn.config_handler import create_default_config
from prompticorn.prompt_builder import get_prompt_builder
from prompticorn.questions.project import NOT_SPECIFIED, get_project_questions
from prompticorn.source_layouts import get_source_layout

_JINJA = re.compile(r"\{\{|\{%")


class TestProjectQuestions:
    """The project-question pipeline and its value mapping."""

    def test_keys_map_to_project_fields(self):
        # Each question key is project_<field>; <field> is the config key.
        keys = [q.key for q in get_project_questions()]
        assert keys == [
            "project_layout_style",
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
        # Assert — "Not specified" maps to empty; layout_style defaults to flat.
        assert project == {
            "layout_style": "flat",
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

    def test_default_style_is_flat(self):
        # Python defaults to a flat package layout, not a src/ layout.
        assert not get_source_layout("python").startswith("src/")
        assert not get_source_layout("python", "flat").startswith("src/")

    def test_src_style_is_selectable(self):
        # Users can opt into a src/ layout.
        assert get_source_layout("python", "src").startswith("src/")
        assert get_source_layout("typescript", "src").startswith("src/")

    def test_config_default_layout_style_is_flat(self):
        from prompticorn.config_handler import ConfigHandler

        assert ConfigHandler.get_default_project_settings()["layout_style"] == "flat"

    def test_every_supported_language_has_a_layout(self):
        # Every language with a convention file must have its own source layout
        # (no silent fallback to the generic default).
        import yaml

        from prompticorn.builders.convention_generator import get_all_languages

        layouts_file = (
            Path(__file__).parent.parent.parent
            / "prompticorn"
            / "configurations"
            / "source_layouts.yaml"
        )
        defined = {k.lower() for k in yaml.safe_load(layouts_file.read_text()) if k != "default"}
        missing = sorted(set(get_all_languages()) - defined)
        assert not missing, f"languages without a source layout: {missing}"

    def test_get_source_layout_falls_back_to_default(self):
        # An unknown language gets the generic (flat) layout, never empty.
        layout = get_source_layout("nonexistent-lang")
        assert "tests/" in layout
        assert layout.strip()

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


class TestAllLanguagesRender:
    """End-to-end render check for every supported language."""

    @pytest.mark.parametrize("language", get_all_languages())
    def test_language_conventions_render_clean(self, language):
        # Arrange
        spec = {
            "language": language,
            "runtime": "",
            "package_manager": "",
            "test_framework": "",
            "linter": "",
            "formatter": "",
            "coverage": {},
        }
        # Act
        out = generate_all_conventions([spec], "single-language", {"layout_style": "flat"})
        general = out[".claude/conventions/core/general.md"]
        lang_conv = out.get(f".claude/conventions/languages/{language}.md", "")
        # Assert — language's source layout rendered into core convention, no leaks.
        assert get_source_layout(language).splitlines()[0] in general
        assert not _JINJA.search(general)
        assert "<!-- path" not in general
        assert lang_conv, f"no language convention generated for {language}"
        assert not _JINJA.search(lang_conv)
        assert "<!-- path" not in lang_conv

    @pytest.mark.parametrize("language", get_all_languages())
    def test_language_builds_end_to_end_strict(self, language, tmp_path):
        # Full build via a CoreFilesLoader-based tool (copilot) exercises the
        # StrictUndefined render path — a convention referencing an undefined
        # variable fails here even though the lenient Claude path would tolerate it.
        config = create_default_config(language)
        config["variant"] = "minimal"
        config["active_personas"] = ["software_engineer"]
        # Act
        actions = get_prompt_builder("copilot").build(tmp_path, config=config, dry_run=False)
        # Assert — no agent/file build failures and no leaked templates.
        failures = [a for a in actions if a.startswith("✗")]
        assert not failures, f"{language}: {failures}"
        for path in tmp_path.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8", errors="ignore")
                assert not _JINJA.search(text), f"{language}: jinja leak in {path.name}"
                assert "<!-- path" not in text, f"{language}: path leak in {path.name}"
