"""Guard the library counts quoted in the entry-point docs (PRO-12).

README.md and docs/QUICKSTART.md advertise how many assistants and skills
prompticorn ships. Those numbers drifted badly — the docs claimed 5 assistants
and ~95 skills while the library had grown to 16 and 96 — and nothing caught it,
because prose counts aren't tested. These tests tie the headline numbers to the
live library, so adding a tool or skill fails here until the entry-point docs are
updated to match.

Scope is deliberately narrow: only the two documents a new user reads first, and
only the two counts that are unambiguous. (Language count is intentionally
excluded — there are 26 selectable languages but 29 conventions-*.md files, and
different docs legitimately cite either, so it is not a single canonical number.)
"""

import pathlib
import re

import pytest

from prompticorn.tools import MENU_ORDER

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_README = _ROOT / "README.md"
_QUICKSTART = _ROOT / "docs" / "QUICKSTART.md"


def _live_tool_count() -> int:
    """Selectable assistant targets = entries in the CLI menu order."""
    return len(MENU_ORDER)


def _live_skill_count() -> int:
    return len([d for d in (_ROOT / "prompticorn" / "skills").iterdir() if d.is_dir()])


@pytest.mark.unit
@pytest.mark.parametrize("doc", [_README, _QUICKSTART], ids=lambda p: p.name)
def test_doc_states_current_tool_count(doc):
    """The entry-point docs must cite the real number of supported assistants."""
    text = doc.read_text(encoding="utf-8")
    n = _live_tool_count()
    assert re.search(rf"\b{n}\b\s+(?:assistants|tools|supported assistants)", text), (
        f"{doc.name} does not state the current assistant count ({n}). "
        "A tool was likely added/removed — update the doc to match."
    )


@pytest.mark.unit
@pytest.mark.parametrize("doc", [_README, _QUICKSTART], ids=lambda p: p.name)
def test_doc_has_no_stale_assistant_count(doc):
    """Known-stale phrasings must never reappear."""
    text = doc.read_text(encoding="utf-8")
    for stale in ("5 assistants", "five assistants"):
        assert stale not in text, f"{doc.name} contains stale '{stale}'"


def _live_workflow_count() -> int:
    return len([d for d in (_ROOT / "prompticorn" / "workflows").iterdir() if d.is_dir()])


@pytest.mark.unit
@pytest.mark.parametrize("doc", [_README, _QUICKSTART], ids=lambda p: p.name)
def test_doc_states_current_skill_count(doc):
    """Both entry-point docs cite the skill count; keep them in step.

    Guarding only QUICKSTART let README drift to "~95 specialized skills"
    against a library of 127 — the exact drift this module exists to catch,
    in the other one of the two documents it names. (PRO-156)
    """
    text = doc.read_text(encoding="utf-8")
    n = _live_skill_count()
    assert re.search(rf"\b{n}\b\s+(?:specialized )?skills", text), (
        f"{doc.name} does not state the current skill count ({n}). "
        "Skills changed — update the doc."
    )


@pytest.mark.unit
@pytest.mark.parametrize("doc", [_README, _QUICKSTART], ids=lambda p: p.name)
def test_doc_has_no_approximate_library_counts(doc):
    """A "~" count is how these drift: it reads as current long after it is not.

    The live numbers are exact and cheap to assert, so the docs should state
    them exactly.
    """
    text = doc.read_text(encoding="utf-8")
    approximate = re.findall(r"~\s*\d+\s+(?:specialized skills|skills|workflows)", text)
    assert not approximate, (
        f"{doc.name} states approximate library counts {approximate}; "
        "use the exact number so this test can keep it honest."
    )


@pytest.mark.unit
@pytest.mark.parametrize("doc", [_README, _QUICKSTART], ids=lambda p: p.name)
def test_doc_states_current_workflow_count(doc):
    """Workflow counts drifted the same way the skill count did."""
    text = doc.read_text(encoding="utf-8")
    n = _live_workflow_count()
    assert re.search(rf"\b{n}\b\s+workflows", text), (
        f"{doc.name} does not state the current workflow count ({n}). "
        "Workflows changed — update the doc."
    )
