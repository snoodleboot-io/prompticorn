"""Tests for promptosaurus.questions.language module."""
import pytest

from promptosaurus.questions.language import (
    LANGUAGE_KEYS,
    get_language_questions,
)


class TestGetLanguageQuestions:
    """Tests for get_language_questions function."""

    def test_get_python_questions(self):
        """Should return questions for Python."""
        questions = get_language_questions("python")

        assert len(questions) > 0
        keys = [q.key for q in questions]
        assert "python_runtime" in keys
        assert "python_package_manager" in keys

    def test_get_typescript_questions(self):
        """Should return questions for TypeScript."""
        questions = get_language_questions("typescript")

        assert len(questions) > 0
        keys = [q.key for q in questions]
        assert "typescript_version" in keys

    def test_get_javascript_questions(self):
        """Should return questions for JavaScript (same as TypeScript)."""
        questions = get_language_questions("javascript")

        assert len(questions) > 0

    def test_get_unknown_language_returns_empty(self):
        """Unknown language should raise ValueError."""
        with pytest.raises(ValueError):
            get_language_questions("unknown_language")


class TestLanguageKeys:
    """Tests for LANGUAGE_KEYS."""

    def test_language_keys_includes_common_languages(self):
        """LANGUAGE_KEYS should include common languages."""
        assert "python" in LANGUAGE_KEYS
        assert "typescript" in LANGUAGE_KEYS
        assert "javascript" in LANGUAGE_KEYS
        assert "go" in LANGUAGE_KEYS
        assert "rust" in LANGUAGE_KEYS
