"""Every language version question's default is one of its options (PRO-94).

PRO-94 extended the per-language version arrays and bumped each default to the
current release. This guard pins the invariant that made that safe: a question's
`default` must be a member of its `options`. Without it, bumping a default (or
trimming an array) can silently offer a default the picker can't show — the
go-default-1.26-with-options-topping-1.22 inconsistency PRO-94 fixed.

Discovers the version/runtime question classes from disk so a new language is
covered automatically.
"""

import importlib
from pathlib import Path

import pytest

from prompticorn.questions.base.question import Question

_QUESTIONS_DIR = Path(__file__).parent.parent.parent.parent / "prompticorn" / "questions"


def _version_question_classes():
    """Yield (module_name, class) for every *version*/*runtime* question on disk."""
    found = []
    for path in sorted(_QUESTIONS_DIR.rglob("*question.py")):
        if not ("version" in path.stem or "runtime" in path.stem):
            continue
        rel = path.relative_to(_QUESTIONS_DIR.parent.parent).with_suffix("")
        module = importlib.import_module(".".join(rel.parts))
        for attr in vars(module).values():
            if (
                isinstance(attr, type)
                and issubclass(attr, Question)
                and attr is not Question
                and attr.__module__ == module.__name__
            ):
                found.append((path.stem, attr))
    return found


_CLASSES = _version_question_classes()


@pytest.mark.unit
class TestVersionOptionCoverage:
    def test_discovers_the_version_questions(self):
        # Sanity: the discovery found the known set (guards against a silent zero).
        assert len(_CLASSES) >= 20, f"only found {len(_CLASSES)} version questions"

    @pytest.mark.parametrize("stem,cls", _CLASSES, ids=[s for s, _ in _CLASSES])
    def test_default_is_a_listed_option(self, stem, cls):
        q = cls()
        assert q.default in q.options, (
            f"{stem}: default {q.default!r} is not in options {q.options!r} — "
            "bumping a default must keep it selectable (PRO-94)"
        )

    def test_python_offers_free_threaded_build_with_gil_note(self):
        """Python must offer 3.14t (PEP 703, no-GIL) with a GIL explanation."""
        from prompticorn.questions.python.python_runtime_question import PythonRuntimeQuestion

        q = PythonRuntimeQuestion()
        assert "3.14t" in q.options, "python must offer the free-threaded 3.14t build"
        note = q.option_explanations.get("3.14t", "").lower()
        assert "gil" in note, "3.14t must carry a note about the GIL"
