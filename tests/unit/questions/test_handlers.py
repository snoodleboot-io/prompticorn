"""Tests for promptosaurus.questions.handlers module."""

from unittest.mock import Mock

import pytest

from promptosaurus.questions.handlers.handle_single_language_questions import (
    HandleSingleLanguageQuestions,
)
from promptosaurus.questions.handlers.language_question_handler import LanguageQuestionHandler


class TestLanguageQuestionHandler:
    """Tests for LanguageQuestionHandler base class."""

    def test_handle_method_raises_not_implemented(self):
        """Base handle() method should raise NotImplementedError."""
        handler = LanguageQuestionHandler()

        with pytest.raises(NotImplementedError):
            handler.handle("single-language")


class TestHandleSingleLanguageQuestions:
    """Tests for HandleSingleLanguageQuestions handler."""

    def test_handler_initializes_with_selector(self):
        """Handler should initialize with a selector function."""
        mock_selector = Mock(return_value="python")
        handler = HandleSingleLanguageQuestions(mock_selector)

        assert handler.select_option == mock_selector

    def test_handle_returns_config_dict(self, monkeypatch):
        """Handle should return a configuration dictionary."""
        mock_selector = Mock(return_value="python")
        handler = HandleSingleLanguageQuestions(mock_selector)

        # Mock click.echo to avoid output during test
        monkeypatch.setattr("click.echo", lambda x: None)

        config = handler.handle("single-language")

        assert isinstance(config, dict)
        assert "defaults" in config

    def test_python_questions_in_config(self, monkeypatch):
        """Python questions should populate config defaults."""
        mock_selector = Mock(return_value="python")
        handler = HandleSingleLanguageQuestions(mock_selector)

        # Mock click.echo to avoid output during test
        monkeypatch.setattr("click.echo", lambda x: None)

        config = handler.handle("single-language")

        assert "defaults" in config
        # Config should have some defaults populated
        assert isinstance(config["defaults"], dict)

    def test_handler_with_mock_selector_returning_ruff(self, monkeypatch):
        """Handler should work with selector returning ruff for linter."""
        # First call returns "python" for language selection
        # Subsequent calls return answers for each question
        mock_selector = Mock(return_value="ruff")
        handler = HandleSingleLanguageQuestions(mock_selector)

        # Mock click.echo to avoid output during test
        monkeypatch.setattr("click.echo", lambda x: None)

        config = handler.handle("single-language")

        # Verify the config was created
        assert config is not None
        assert "defaults" in config
