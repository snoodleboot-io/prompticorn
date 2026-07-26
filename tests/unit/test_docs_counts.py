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


@pytest.mark.unit
def test_quickstart_states_current_skill_count():
    """QUICKSTART cites the skill count; keep it in step with the library."""
    text = _QUICKSTART.read_text(encoding="utf-8")
    n = _live_skill_count()
    assert re.search(rf"\b{n}\b\s+(?:specialized )?skills", text), (
        f"docs/QUICKSTART.md does not state the current skill count ({n}). "
        "Skills changed — update the doc."
    )
