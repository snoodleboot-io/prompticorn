"""Tests for promptosaurus.questions.base module."""

import pytest

from promptosaurus.questions.base.constants import RepositoryTypes, REPO_TYPES
from promptosaurus.questions.base.folder_mapping_question import FolderMappingQuestion
from promptosaurus.questions.base.question import Question
from promptosaurus.questions.base.repository_type_question import RepositoryTypeQuestion


class TestQuestion:
    """Tests for Question abstract base class."""

    def test_question_is_abstract(self):
        """Question should be an abstract base class."""
        # Cannot instantiate directly
        with pytest.raises(TypeError):
            Question()

    def test_question_has_abstract_properties(self):
        """Question should define abstract properties."""
        # Check that the abstract methods are defined
        assert hasattr(Question, "key")
        assert hasattr(Question, "question_text")
        assert hasattr(Question, "explanation")
        assert hasattr(Question, "options")


class TestRepositoryTypeQuestion:
    """Tests for RepositoryTypeQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = RepositoryTypeQuestion()

        assert q.key == "repository_type"
        assert q.question_text
        assert q.explanation
        assert q.options
        assert q.default

    def test_options_are_valid(self):
        """Options should include all valid repo types."""
        q = RepositoryTypeQuestion()

        assert RepositoryTypes.SINGLE in q.options
        assert RepositoryTypes.MULTI_MONOREPO in q.options
        assert RepositoryTypes.MIXED in q.options

    def test_default_is_single_language(self):
        """Default should be single-language."""
        q = RepositoryTypeQuestion()

        assert q.default == RepositoryTypes.SINGLE

    def test_option_explanations_exist(self):
        """Each option should have an explanation."""
        q = RepositoryTypeQuestion()

        for opt in q.options:
            assert opt in q.option_explanations
            assert q.option_explanations[opt]

    def test_explain_option_returns_explanation(self):
        """explain_option should return the explanation for an option."""
        q = RepositoryTypeQuestion()

        explanation = q.explain_option(RepositoryTypes.SINGLE)
        assert explanation == q.option_explanations[RepositoryTypes.SINGLE]

    def test_explain_option_unknown_returns_empty(self):
        """explain_option for unknown option should return empty string."""
        q = RepositoryTypeQuestion()

        assert q.explain_option("unknown") == ""


class TestFolderMappingQuestion:
    """Tests for FolderMappingQuestion."""

    def test_question_has_required_properties(self):
        """Question should have all required properties."""
        q = FolderMappingQuestion()

        assert q.key == "folder_mapping"
        assert q.question_text
        assert q.explanation

    def test_options_is_empty_list(self):
        """Options should be empty for dynamic folder mapping."""
        q = FolderMappingQuestion()

        assert q.options == []

    def test_default_is_empty_string(self):
        """Default should be empty string for folder mapping."""
        q = FolderMappingQuestion()

        assert q.default == ""

    def test_num_folders_parameter(self):
        """Should accept num_folders parameter."""
        q = FolderMappingQuestion(num_folders=3)

        assert q._num_folders == 3


class TestConstants:
    """Tests for base module constants."""

    def test_repo_type_constants(self):
        """REPO_TYPE constants should have correct values."""
        assert RepositoryTypes.SINGLE == "single-language"
        assert RepositoryTypes.MULTI_MONOREPO == "multi-language-monorepo"
        assert RepositoryTypes.MIXED == "mixed"

    def test_repo_types_list(self):
        """REPO_TYPES should include all repo types."""
        assert RepositoryTypes.SINGLE in REPO_TYPES
        assert RepositoryTypes.MULTI_MONOREPO in REPO_TYPES
        assert RepositoryTypes.MIXED in REPO_TYPES
        assert len(REPO_TYPES) == 3
