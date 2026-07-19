"""Adversarial serialization tests for hand-formatted workflow outputs (PRO-88).

gemini `workflow_to_toml` and copilot-chat `workflow_to_prompt` build structured
formats (TOML / YAML frontmatter) from workflow content and names. Values with
special characters must not corrupt the output.
"""

import yaml

from prompticorn.builders.copilot_chat_builder import workflow_to_prompt
from prompticorn.builders.gemini_builder import workflow_to_toml


def _parse_toml(text: str):
    try:
        import tomllib
    except ModuleNotFoundError:  # py3.10
        import tomli as tomllib
    return tomllib.loads(text)


_ADVERSARIAL_BODY = "Line with ''' triple quote\nand a \" quote and a \\ backslash\n"


def test_gemini_toml_survives_adversarial_content():
    out = workflow_to_toml("weird-flow", _ADVERSARIAL_BODY)
    parsed = _parse_toml(out)  # must not raise
    assert parsed["prompt"] == _ADVERSARIAL_BODY
    assert parsed["description"] == "weird-flow workflow"


def test_copilot_chat_frontmatter_survives_colon_in_name():
    out = workflow_to_prompt("weird: colon", "# body\n")
    # Extract and parse the YAML frontmatter block.
    _, fm, _ = out.split("---", 2)
    data = yaml.safe_load(fm)  # must not raise
    assert data["description"] == "weird: colon workflow"
