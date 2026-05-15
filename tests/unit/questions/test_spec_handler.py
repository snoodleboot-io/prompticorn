"""Tests for prompticorn.questions.base.spec_handler module."""

import pytest

from prompticorn.questions.base.spec_handler import (
    MultiLanguageSpecHandler,
    SingleLanguageSpecHandler,
    SpecHandler,
)


class TestSingleLanguageSpecHandler:
    """Tests for SingleLanguageSpecHandler."""

    def test_creates_spec_from_language(self):
        """Should create spec dict from language."""
        handler = SingleLanguageSpecHandler()
        spec = handler.create_spec("python")

        assert isinstance(spec, dict)
        assert spec["language"] == "python"
        assert spec["runtime"] == "3.14"
        assert spec["package_manager"] == "uv"

    def test_creates_spec_with_overrides(self):
        """Should create spec with custom overrides."""
        handler = SingleLanguageSpecHandler()
        spec = handler.create_spec("python", runtime="3.11", package_manager="pip")

        assert spec["language"] == "python"
        assert spec["runtime"] == "3.11"
        assert spec["package_manager"] == "pip"

    def test_get_language_from_spec(self):
        """Should get language from spec dict."""
        handler = SingleLanguageSpecHandler()
        spec = {
            "language": "typescript",
            "runtime": "5.4",
            "package_manager": "npm",
        }

        language = handler.get_language(spec)

        assert language == "typescript"

    def test_is_multi_language_returns_false(self):
        """Should return False for single language handler."""
        handler = SingleLanguageSpecHandler()
        assert handler.is_multi_language() is False


class TestMultiLanguageSpecHandler:
    """Tests for MultiLanguageSpecHandler."""

    def test_creates_empty_spec_list(self):
        """Should create empty spec list."""
        handler = MultiLanguageSpecHandler()
        spec = handler.create_spec()

        assert isinstance(spec, list)
        assert len(spec) == 0

    def test_adds_folder_spec(self):
        """Should add folder spec to list."""
        handler = MultiLanguageSpecHandler()
        handler.add_folder_spec("frontend", "frontend", "ui", "typescript")
        handler.add_folder_spec("backend", "backend", "api", "python")

        spec = handler.get_spec()

        assert isinstance(spec, list)
        assert len(spec) == 2
        assert spec[0]["folder"] == "frontend"
        assert spec[1]["folder"] == "backend"

    def test_get_language_returns_first(self):
        """Should get language from first folder."""
        handler = MultiLanguageSpecHandler()
        handler.add_folder_spec("frontend", "frontend", "ui", "typescript")
        handler.add_folder_spec("backend", "backend", "api", "python")

        language = handler.get_language({})

        assert language == "typescript"

    def test_is_multi_language_returns_true(self):
        """Should return True for multi language handler."""
        handler = MultiLanguageSpecHandler()
        assert handler.is_multi_language() is True

    def test_validates_folder_path_not_empty(self):
        """Should validate folder path is not empty."""
        handler = MultiLanguageSpecHandler()

        with pytest.raises(ValueError, match="Folder path cannot be empty"):
            handler.add_folder_spec("", "frontend", "ui", "typescript")

    def test_prevents_duplicate_folders(self):
        """Should prevent duplicate folder paths."""
        handler = MultiLanguageSpecHandler()
        handler.add_folder_spec("frontend", "frontend", "ui", "typescript")

        with pytest.raises(ValueError, match="Duplicate folder"):
            handler.add_folder_spec("frontend", "backend", "api", "python")


class TestSpecHandlerFactory:
    """Tests for SpecHandler factory function."""

    def test_returns_single_language_handler(self):
        """Should return SingleLanguageSpecHandler for single-language."""
        handler = SpecHandler.for_repository_type("single-language")

        assert isinstance(handler, SingleLanguageSpecHandler)
        assert handler.is_multi_language() is False

    def test_returns_multi_language_handler(self):
        """Should return MultiLanguageSpecHandler for multi-language-monorepo."""
        handler = SpecHandler.for_repository_type("multi-language-monorepo")

        assert isinstance(handler, MultiLanguageSpecHandler)
        assert handler.is_multi_language() is True

    def test_raises_for_unknown_type(self):
        """Should raise ValueError for unknown repository type."""
        with pytest.raises(ValueError, match="Unknown repository type"):
            SpecHandler.for_repository_type("unknown")
