"""Coverage for cursor/copilot builder validate, accessors, and spec branches."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from prompticorn.agent_registry import Registry
from prompticorn.builders.base import BuildOptions
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.cursor_builder import CursorBuilder
from prompticorn.builders.errors import BuilderValidationError

_BUILDERS = [CursorBuilder, CopilotBuilder]
_AGENTS_DIR = Path(__file__).parent.parent.parent.parent / "prompticorn" / "agents"


@pytest.mark.parametrize("builder_cls", _BUILDERS)
def test_validate_reports_each_missing_field(builder_cls):
    builder = builder_cls()
    assert builder.validate(SimpleNamespace(name="", description="d", system_prompt="s"))
    assert builder.validate(SimpleNamespace(name="n", description="", system_prompt="s"))
    assert builder.validate(SimpleNamespace(name="n", description="d", system_prompt=""))
    assert builder.validate(SimpleNamespace(name="n", description="d", system_prompt="s")) == []


@pytest.mark.parametrize("builder_cls", _BUILDERS)
def test_tool_name_and_output_format(builder_cls):
    builder = builder_cls()
    assert builder.get_tool_name()
    assert builder.get_output_format()


@pytest.mark.parametrize("builder_cls", _BUILDERS)
def test_build_invalid_agent_raises(builder_cls):
    builder = builder_cls()
    invalid = SimpleNamespace(
        name="", description="", system_prompt="", subagents=[], skills=[], workflows=[]
    )
    with pytest.raises(BuilderValidationError):
        builder.build(invalid, BuildOptions(), {})


@pytest.mark.parametrize("builder_cls", _BUILDERS)
def test_build_multilanguage_extracts_primary_language(builder_cls, tmp_path):
    # Exercises the multi-language (list spec) language-extraction branch.
    agent = Registry.from_discovery(_AGENTS_DIR).get_agent("code")
    config = {"spec": [{"language": "python"}], "variant": "minimal"}
    result = builder_cls().build(agent, BuildOptions(variant="minimal"), config)
    assert result
