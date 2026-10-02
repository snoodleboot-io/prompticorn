"""docs/PERSONAS.md must agree with personas.yaml.

The persona table and the prose counts drifted three separate times while
personas.yaml was being changed: PRO-158 added `qa-tester` and `atdd` to
qa_tester, PRO-162 rebuilt engineering_manager on product+architect, and
PRO-155 took the persona count from 12 to 21 — each time the YAML moved and
the doc did not. Prose is not covered by any other test, so it drifts silently.

Reference: PRO-161
"""

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path("prompticorn")
DOC = Path("docs") / "PERSONAS.md"

#: `| **Display Name** _(optional note)_ | focus | agent, agent |`
ROW = re.compile(r"^\| \*\*(?P<display>.+?)\*\*(?: _.*?_)? \| (?P<focus>.+?) \| (?P<agents>.+?) \|\s*$")


@pytest.fixture(scope="module")
def personas():
    with (ROOT / "personas" / "personas.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)["personas"]


@pytest.fixture(scope="module")
def doc_text():
    return DOC.read_text(encoding="utf-8")


def _rows(doc_text):
    return [m.groupdict() for line in doc_text.splitlines() if (m := ROW.match(line))]


def test_every_persona_has_a_table_row(personas, doc_text):
    documented = {r["display"] for r in _rows(doc_text)}
    missing = sorted(
        f"{key} ({p['display_name']})"
        for key, p in personas.items()
        if p["display_name"] not in documented
    )
    assert not missing, f"personas with no row in {DOC}: {missing}"


def test_table_rows_list_the_real_primary_agents(personas, doc_text):
    by_display = {p["display_name"]: (key, p) for key, p in personas.items()}
    wrong = []
    for row in _rows(doc_text):
        entry = by_display.get(row["display"])
        if entry is None:
            wrong.append(f"{row['display']!r} is not a display_name in personas.yaml")
            continue
        key, persona = entry
        documented = [a.strip() for a in row["agents"].split(",")]
        actual = persona.get("primary_agents") or []
        if documented != actual:
            wrong.append(f"{key}: doc says {documented}, yaml says {actual}")
    assert not wrong, f"{DOC} disagrees with personas.yaml: {wrong}"


def test_the_stated_persona_count_is_the_real_one(personas, doc_text):
    n = len(personas)
    assert re.search(rf"\*\*{n} persona", doc_text), (
        f"{DOC} does not state the real persona count ({n}); it drifted from 12 to 21 once already"
    )


def test_the_stated_agent_count_is_the_real_one(doc_text):
    """`core/` holds conventions, not a selectable agent, so it is excluded."""
    n = len([p for p in (ROOT / "agents").iterdir() if p.is_dir() and p.name != "core"])
    stale = re.findall(r"(?:all|~)\s*(\d+)\s+primary agents", doc_text)
    wrong = sorted({s for s in stale if int(s) != n})
    assert not wrong, f"{DOC} cites {wrong} primary agents; there are {n}"
