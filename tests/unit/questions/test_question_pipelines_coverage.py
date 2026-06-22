"""Interface + load coverage for every question in every language pipeline.

Instantiates every Question class referenced by question_pipelines.yaml (core and
fungible) and validates its public interface. This both guards the contract and
exercises the many per-language question classes.
"""

from pathlib import Path

import pytest
import yaml

from prompticorn.questions.base.question import Question
from prompticorn.questions.language import get_core_questions, get_fungible_questions

_PIPELINES = yaml.safe_load(
    (
        Path(__file__).parent.parent.parent.parent
        / "prompticorn"
        / "questions"
        / "question_pipelines.yaml"
    ).read_text()
)
_LANGUAGES = sorted(_PIPELINES.keys())
_FOLDER_TYPES = ["backend/api", "backend/worker", "frontend/ui", "frontend/e2e"]


def _check_question(q: Question) -> None:
    assert isinstance(q, Question)
    assert isinstance(q.key, str) and q.key
    assert isinstance(q.question_text, str) and q.question_text
    assert isinstance(q.explanation, str)
    assert isinstance(q.options, list)
    assert isinstance(q.option_explanations, dict)
    # A non-multi default, when set, must be one of the options.
    if q.options and not q.allow_multiple and q.default:
        assert q.default in q.options


@pytest.mark.parametrize("language", _LANGUAGES)
def test_core_questions_load_and_validate(language):
    questions = get_core_questions(language)
    assert questions, f"{language}: no core questions"
    keys = [q.key for q in questions]
    assert len(keys) == len(set(keys)), f"{language}: duplicate question keys {keys}"
    for q in questions:
        _check_question(q)


@pytest.mark.parametrize("language", _LANGUAGES)
def test_fungible_questions_load_and_validate(language):
    for folder_type in _FOLDER_TYPES:
        for q in get_fungible_questions(language, folder_type):
            _check_question(q)
