"""Tests for the AWS Bedrock builder + layout (PRO-9)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

import pytest
import yaml

from prompticorn.builders.base import BuildOptions
from prompticorn.builders.bedrock_builder import (
    BedrockBuilder,
    _logical_id,
    generate_cloudformation,
    generate_invoke_example,
    generate_manifest,
)
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.layouts import get_layout
from prompticorn.ir.models import Agent
from prompticorn.prompt_builder import get_prompt_builder

_SYSTEM = "You are a careful backend engineer. " * 3  # comfortably over the 40-char floor


def _agent(name="Backend Agent", description="Design scalable backend systems", prompt=_SYSTEM):
    return Agent(name=name, description=description, system_prompt=prompt)


@pytest.mark.unit
class TestBedrockBuilder:
    def test_build_returns_manifest_dict(self):
        out = BedrockBuilder().build(_agent(), BuildOptions())
        assert out == {
            "name": "Backend Agent",
            "slug": "backend-agent",
            "description": "Design scalable backend systems",
            "system_prompt": _SYSTEM,
        }

    def test_description_truncated_to_200(self):
        out = BedrockBuilder().build(_agent(description="x " * 300), BuildOptions())
        assert len(out["description"]) <= 200
        assert out["description"].endswith("…")

    @pytest.mark.parametrize(
        ("field", "name", "description", "prompt"),
        [
            ("name", "  ", "d", _SYSTEM),
            ("description", "X", "  ", _SYSTEM),
            ("system", "X", "d", "   "),
        ],
    )
    def test_validate_rejects_missing_fields(self, field, name, description, prompt):
        # The Agent model rejects empty description/system_prompt at construction,
        # so exercise validate() directly with a stand-in to cover its guards.
        stand_in = SimpleNamespace(name=name, description=description, system_prompt=prompt)
        errors = BedrockBuilder().validate(stand_in)
        assert any(field in e for e in errors)

    def test_validate_rejects_too_short_instruction(self):
        errors = BedrockBuilder().validate(_agent(prompt="too short"))
        assert any("at least" in e for e in errors)

    def test_build_raises_on_invalid_agent(self):
        # Non-empty but under the 40-char Instruction floor: Agent constructs, the
        # Bedrock builder rejects.
        with pytest.raises(BuilderValidationError):
            BedrockBuilder().build(_agent(prompt="short"), BuildOptions())


@pytest.mark.unit
class TestBedrockArtifacts:
    def test_logical_id_is_alphanumeric(self):
        assert _logical_id("backend-agent") == "BackendAgentAgent"
        assert _logical_id("kilo_cli") == "KiloCliAgent"

    def test_manifest_is_valid_json_sorted_by_slug(self):
        dicts = [BedrockBuilder().build(_agent(name=n), BuildOptions()) for n in ("Zed", "Ask")]
        data = json.loads(generate_manifest(dicts))
        assert [a["slug"] for a in data["agents"]] == ["ask", "zed"]
        assert data["defaultModelId"]
        assert data["agents"][0]["systemPromptFile"] == "prompts/ask.system.md"

    def test_invoke_example_is_valid_python(self):
        import ast

        ast.parse(generate_invoke_example())

    def test_cloudformation_is_valid_yaml_with_bedrock_agents(self):
        # Prompt with an injected list + quotes + newlines — the shape that broke
        # a hand-rolled literal block.
        tricky = "Delegate to:\n- **ask**: things\n- **code**: other things\n" + _SYSTEM
        dicts = [BedrockBuilder().build(_agent(prompt=tricky), BuildOptions())]
        doc = yaml.safe_load(generate_cloudformation(dicts))
        assert list(doc["Parameters"]) == ["FoundationModel", "AgentResourceRoleArn"]
        (res,) = doc["Resources"].values()
        assert res["Type"] == "AWS::Bedrock::Agent"
        props = res["Properties"]
        assert props["Instruction"] == tricky.rstrip("\n")
        assert props["FoundationModel"] == {"Ref": "FoundationModel"}
        assert props["AgentName"] == "backend-agent"

    def test_cloudformation_flags_over_cap_instruction(self):
        dicts = [BedrockBuilder().build(_agent(prompt="a" * 5000), BuildOptions())]
        cfn = generate_cloudformation(dicts)
        assert "over Bedrock's 4000-char cap" in cfn
        assert yaml.safe_load(cfn)  # still valid YAML


@pytest.mark.unit
class TestBedrockLayout:
    def test_write_agent_writes_prompt_file(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            content = BedrockBuilder().build(_agent(), BuildOptions())
            written = get_layout("bedrock").write_agent(root, "Backend Agent", content)
            assert written == ["bedrock/prompts/backend-agent.system.md"]
            assert (root / written[0]).read_text().strip() == _SYSTEM.strip()

    def test_skills_are_dropped(self):
        with TemporaryDirectory() as tmp:
            assert get_layout("bedrock").write_skill(Path(tmp), "any-skill", "body") == []

    def test_finalize_emits_bundle(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            dicts = [BedrockBuilder().build(_agent(), BuildOptions())]
            written = get_layout("bedrock").finalize(root, dicts, None)
            assert set(written) == {
                "bedrock/README.bedrock.md",
                "bedrock/agents.json",
                "bedrock/conventions.md",
                "bedrock/cloudformation/agents.yaml",
                "bedrock/invoke_example.py",
            }
            for rel in written:
                assert (root / rel).exists()

    def test_finalize_empty_when_no_agents(self):
        with TemporaryDirectory() as tmp:
            assert get_layout("bedrock").finalize(Path(tmp), [], None) == []


@pytest.mark.unit
class TestBedrockEndToEnd:
    def test_full_build_produces_valid_bundle(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            get_prompt_builder("bedrock").build(
                root,
                {
                    "spec": {"language": "python"},
                    "active_personas": ["software_engineer"],
                    "variant": "minimal",
                },
                dry_run=False,
            )
            base = root / "bedrock"
            manifest = json.loads((base / "agents.json").read_text())
            assert manifest["agents"], "expected agents in the manifest"
            # every manifest prompt file exists
            for a in manifest["agents"]:
                assert (base / a["systemPromptFile"]).exists()
            # the whole CloudFormation parses and is all Bedrock agents
            doc = yaml.safe_load((base / "cloudformation" / "agents.yaml").read_text())
            assert doc["Resources"]
            assert all(r["Type"] == "AWS::Bedrock::Agent" for r in doc["Resources"].values())
