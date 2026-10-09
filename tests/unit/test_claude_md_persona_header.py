"""The CLAUDE.md persona header must reflect what was actually selected.

`prompt_builder` read `config.get("persona")` — singular — but the CLI only
ever writes `active_personas`, a list. The key never existed, so the default
fired on every build and every generated CLAUDE.md was stamped
"Persona: Software Engineer" regardless of what the user picked.

Reference: PRO-160
"""

import pytest

from prompticorn.builders.claude_md import NO_PERSONA_LABEL, generate_claude_md
from prompticorn.prompt_builder import _describe_personas


@pytest.mark.parametrize("config", [None, {}, {"active_personas": []}, {"active_personas": None}])
def test_no_selection_does_not_claim_a_persona(config):
    """With nothing selected the honest header is 'none', not a real persona."""
    label = _describe_personas(config)
    assert label == NO_PERSONA_LABEL
    assert "Software Engineer" not in label


def test_reads_active_personas_not_the_singular_key():
    """The exact bug: a `persona` key is not what the CLI writes."""
    assert _describe_personas({"persona": "qa_tester"}) == NO_PERSONA_LABEL
    assert _describe_personas({"active_personas": ["qa_tester"]}) == "QA / Tester"


def test_multiple_personas_are_all_named():
    label = _describe_personas({"active_personas": ["qa_tester", "devops_engineer"]})
    assert label == "QA / Tester, DevOps Engineer"


def test_display_names_are_not_title_cased():
    """`.title()` turned "QA / Tester" into "Qa / Tester" and "SRE" into "Sre"."""
    assert _describe_personas({"active_personas": ["qa_tester"]}) == "QA / Tester"


def test_unknown_persona_falls_back_to_its_id_rather_than_failing():
    """A cosmetic header must never break a build."""
    assert _describe_personas({"active_personas": ["not_a_persona"]}) == "not_a_persona"


def test_label_reaches_the_rendered_document_verbatim():
    rendered = generate_claude_md(
        [{"name": "test", "description": "Write tests"}],
        "QA / Tester, DevOps Engineer",
    )
    assert "**Persona:** QA / Tester, DevOps Engineer" in rendered


def test_default_rendered_header_claims_nothing():
    rendered = generate_claude_md([{"name": "test", "description": "Write tests"}])
    assert f"**Persona:** {NO_PERSONA_LABEL}" in rendered
