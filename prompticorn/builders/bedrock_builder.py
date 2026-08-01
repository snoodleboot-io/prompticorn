"""BedrockBuilder — carry a prompticorn agent's system prompt to AWS Bedrock (PRO-9).

Bedrock is not a repo-dotfile assistant like the other 16 targets — it is a
model/agent-hosting API. So "Bedrock support" means emitting artifacts that carry
each agent's **system prompt** into Bedrock, in two flavours:

* **Portable (core):** a per-agent ``bedrock/prompts/<slug>.system.md`` plus a
  ``bedrock/agents.json`` manifest and a runnable ``bedrock/invoke_example.py``
  using the Converse API (``system=[{"text": ...}]``). Zero provisioning — no IAM
  role, no model ARN — the documented home for a system prompt.
* **Deployable (optional):** ``bedrock/cloudformation/agents.yaml`` with one
  ``AWS::Bedrock::Agent`` per agent, ``Instruction`` = the system prompt, and
  ``FoundationModel`` / ``AgentResourceRoleArn`` as template **Parameters** (the
  generator cannot synthesize a real IAM role or model id).

Bedrock has no skill or workflow primitive, so those are not represented here;
the system prompt is the whole payload. The layout drops ``write_skill``.

Field constraints verified against the AWS docs:
* ``AgentName`` / Prompt ``Name`` pattern ``^([0-9a-zA-Z][_-]?){1,100}$`` — the
  Roo slug (lowercase, single hyphens) satisfies it.
* ``Instruction``: min 40 chars (always met), **max 4000** — prompts over the cap
  are emitted with a warning comment rather than silently truncated.
* ``Description``: max 200 chars — truncated.

Sources: AWS::Bedrock::Agent (CloudFormation), Bedrock Converse API /
SystemContentBlock. See the Bedrock research note in Linear (PRO-9).
"""

import json
from typing import Any

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.convention_generator import (
    generate_core_convention,
    generate_language_convention,
)
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.roo_builder import slugify
from prompticorn.ir.models import Agent

# A current Claude model id on Bedrock, used as the example/parameter default.
# Region availability and inference-profile requirements vary — documented in the
# generated README.
_DEFAULT_MODEL_ID = "anthropic.claude-3-5-sonnet-20241022-v2:0"

# Bedrock Agent Instruction hard limits.
_INSTRUCTION_MIN = 40
_INSTRUCTION_MAX = 4000
_DESCRIPTION_MAX = 200


def _collapse(text: str) -> str:
    """Collapse whitespace in a description to a single line."""
    return " ".join(text.split())


def _short_description(description: str) -> str:
    collapsed = _collapse(description)
    if len(collapsed) <= _DESCRIPTION_MAX:
        return collapsed
    return collapsed[: _DESCRIPTION_MAX - 1].rstrip() + "…"


def _logical_id(slug: str) -> str:
    """A CloudFormation-safe logical id (alphanumeric) from a slug."""
    parts = [p for p in slug.replace("_", "-").split("-") if p]
    return "".join(p[:1].upper() + p[1:] for p in parts) + "Agent"


class BedrockBuilder(Builder):
    """Builder for AWS Bedrock system-prompt bundles + optional CloudFormation."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> dict:
        """Return a manifest dict for one agent.

        The layout writes ``system_prompt`` to ``bedrock/prompts/<slug>.system.md``
        and collects every dict in ``finalize`` to emit the manifest, invoke
        example, and CloudFormation.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )
        return {
            "name": agent.name,
            "slug": slugify(agent.name),
            "description": _short_description(agent.description),
            "system_prompt": agent.system_prompt,
        }

    def validate(self, agent: Agent) -> list[str]:
        errors: list[str] = []
        if not agent.name or not agent.name.strip():
            errors.append("agent name is required")
        if not agent.description or not agent.description.strip():
            errors.append("agent description is required")
        if not agent.system_prompt or not agent.system_prompt.strip():
            errors.append("agent system_prompt is required")
        elif len(agent.system_prompt.strip()) < _INSTRUCTION_MIN:
            errors.append(
                f"system_prompt must be at least {_INSTRUCTION_MIN} chars for a "
                "Bedrock Agent Instruction"
            )
        return errors

    def get_output_format(self) -> str:
        return "bedrock"

    def get_tool_name(self) -> str:
        return "bedrock"


def _sorted_entries(built_agents: list[Any]) -> list[dict]:
    """Deterministic, deduplicated agent dicts sorted by slug (CI-stable)."""
    entries = {
        a["slug"]: a
        for a in built_agents
        if isinstance(a, dict) and {"name", "slug", "description", "system_prompt"} <= a.keys()
    }
    return [entries[slug] for slug in sorted(entries)]


def generate_manifest(built_agents: list[Any]) -> str:
    """Portable JSON manifest of every agent's system prompt + inference hint."""
    agents = [
        {
            "name": a["name"],
            "slug": a["slug"],
            "description": a["description"],
            "systemPromptFile": f"prompts/{a['slug']}.system.md",
            "suggestedInferenceConfig": {"temperature": 0.7, "maxTokens": 2048, "topP": 0.9},
        }
        for a in _sorted_entries(built_agents)
    ]
    return json.dumps({"defaultModelId": _DEFAULT_MODEL_ID, "agents": agents}, indent=2) + "\n"


def generate_invoke_example() -> str:
    """A runnable boto3 Converse example — the zero-provisioning system-prompt path."""
    return '''\
"""Invoke a prompticorn-generated system prompt against AWS Bedrock (Converse API).

    python invoke_example.py <agent-slug> "your user message"

Requires boto3 and AWS credentials with bedrock:InvokeModel. Some models require
an inference-profile id rather than the base model id — see README.bedrock.md.
"""

import json
import pathlib
import sys

import boto3

HERE = pathlib.Path(__file__).parent
MANIFEST = json.loads((HERE / "agents.json").read_text(encoding="utf-8"))


def main() -> None:
    if len(sys.argv) < 3:
        slugs = ", ".join(a["slug"] for a in MANIFEST["agents"])
        sys.exit(f"usage: python invoke_example.py <agent-slug> <message>\\nagents: {slugs}")

    slug, message = sys.argv[1], sys.argv[2]
    entry = next((a for a in MANIFEST["agents"] if a["slug"] == slug), None)
    if entry is None:
        sys.exit(f"unknown agent: {slug}")

    system_prompt = (HERE / entry["systemPromptFile"]).read_text(encoding="utf-8")
    cfg = entry["suggestedInferenceConfig"]

    client = boto3.client("bedrock-runtime")
    response = client.converse(
        modelId=MANIFEST["defaultModelId"],
        system=[{"text": system_prompt}],
        messages=[{"role": "user", "content": [{"text": message}]}],
        inferenceConfig={
            "temperature": cfg["temperature"],
            "maxTokens": cfg["maxTokens"],
            "topP": cfg["topP"],
        },
    )
    print(response["output"]["message"]["content"][0]["text"])


if __name__ == "__main__":
    main()
'''


def generate_cloudformation(built_agents: list[Any]) -> str:
    """One ``AWS::Bedrock::Agent`` per agent; model + role are Parameters."""
    header = (
        "# AWS::Bedrock::Agent scaffold generated by prompticorn (optional path).\n"
        "#\n"
        "# Instruction = the agent's system prompt. Bedrock caps Instruction at\n"
        f"# {_INSTRUCTION_MAX} chars (min {_INSTRUCTION_MIN}); over-cap agents are flagged below and\n"
        "# need trimming or Bedrock Prompt Management. FoundationModel and\n"
        "# AgentResourceRoleArn cannot be synthesized — supply them as parameters.\n"
        'AWSTemplateFormatVersion: "2010-09-09"\n'
        "Description: prompticorn-generated Amazon Bedrock agents\n"
        "Parameters:\n"
        "  FoundationModel:\n"
        "    Type: String\n"
        f'    Default: "{_DEFAULT_MODEL_ID}"\n'
        "  AgentResourceRoleArn:\n"
        "    Type: String\n"
        "    Description: IAM role ARN the Bedrock agent assumes at runtime.\n"
        "Resources:\n"
    )
    blocks = [header]
    for a in _sorted_entries(built_agents):
        prompt = a["system_prompt"].rstrip("\n")
        over = len(prompt) > _INSTRUCTION_MAX
        warn = (
            f"    # WARNING: Instruction is {len(prompt)} chars, over Bedrock's "
            f"{_INSTRUCTION_MAX}-char cap; trim before deploying.\n"
            if over
            else ""
        )
        # YAML is a JSON superset, so JSON-encoded scalars are always valid YAML
        # and safely carry newlines, quotes, and the injected agent lists that a
        # hand-rolled literal block mis-indents. !Ref uses flow mapping form.
        blocks.append(
            f"  {_logical_id(a['slug'])}:\n"
            f"    Type: AWS::Bedrock::Agent\n"
            f"{warn}"
            f"    Properties:\n"
            f"      AgentName: {json.dumps(a['slug'])}\n"
            f'      FoundationModel: {{"Ref": "FoundationModel"}}\n'
            f'      AgentResourceRoleArn: {{"Ref": "AgentResourceRoleArn"}}\n'
            f"      Description: {json.dumps(a['description'])}\n"
            f"      Instruction: {json.dumps(prompt)}\n"
        )
    return "\n".join(blocks)


def _specs_from_config(config: dict | None) -> list[dict]:
    """Normalize ``config['spec']`` into a list of spec dicts."""
    spec_cfg = config.get("spec") if config else None
    if isinstance(spec_cfg, list):
        return [s for s in spec_cfg if isinstance(s, dict)]
    if isinstance(spec_cfg, dict):
        return [spec_cfg]
    return []


def generate_conventions(config: dict | None) -> str:
    """Render the project's core + per-language conventions as one markdown doc.

    Bedrock has no rules-file concept, so the user's spec choices (runtime, test
    framework, linter, …) would otherwise never reach a Bedrock agent. This
    bundles them into ``bedrock/conventions.md`` to prepend to a prompt as context.
    """
    specs = _specs_from_config(config)
    primary_spec = specs[0] if specs else {}
    primary_language = primary_spec.get("language", "")
    repository_type = (config.get("repository") or {}).get("type", "") if config else ""
    project = config.get("project") if config else None

    sections = [
        generate_core_convention(
            repository_type=repository_type,
            project=project,
            primary_language=primary_language,
            primary_spec=primary_spec,
        )
    ]
    seen: set[str] = set()
    for spec in specs:
        language = spec.get("language")
        if not language or language in seen:
            continue
        seen.add(language)
        lang_content = generate_language_convention(language, spec)
        if lang_content:
            sections.append(lang_content)
    return "\n\n".join(s.rstrip() for s in sections) + "\n"


def generate_readme() -> str:
    """Explain the two paths and their prerequisites."""
    return f"""\
# AWS Bedrock output

prompticorn cannot write a repo dotfile for Bedrock — it is a hosted model/agent
API. Instead it emits your agents' **system prompts** in two forms.

## 1. Portable prompts (recommended, no provisioning)

- `prompts/<slug>.system.md` — one agent's system prompt.
- `conventions.md` — your project's language + project conventions (runtime, test
  framework, linter, formatter, …). Bedrock has no rules-file concept, so prepend
  this to a prompt (or pass it as an extra system block) to give the agent your
  project's standards.
- `agents.json` — manifest: name, description, prompt file, suggested inference config.
- `invoke_example.py` — a runnable boto3 **Converse** call that loads a prompt and
  sends a message. No IAM role or agent provisioning needed:

  ```bash
  pip install boto3
  python invoke_example.py <agent-slug> "your message"
  ```

  Some Bedrock models require an **inference-profile id** rather than the base
  model id (`{_DEFAULT_MODEL_ID}`); adjust `defaultModelId` in `agents.json` if
  `converse` reports the model is not accessible.

## 2. Deployable Bedrock Agents (optional)

- `cloudformation/agents.yaml` — one `AWS::Bedrock::Agent` per agent, with the
  system prompt as the agent `Instruction`.

  It cannot be deployed as-is: supply `FoundationModel` and `AgentResourceRoleArn`
  (a real IAM role) as parameters, and note Bedrock caps `Instruction` at
  {_INSTRUCTION_MAX} characters — longer prompts are flagged in the template and
  must be trimmed or moved to Bedrock Prompt Management.

  ```bash
  aws cloudformation deploy --template-file cloudformation/agents.yaml \\
    --stack-name prompticorn-agents \\
    --parameter-overrides AgentResourceRoleArn=arn:aws:iam::<acct>:role/<role>
  ```

## Not represented

Bedrock has no skill or workflow primitive, so prompticorn skills and workflows
are not emitted here — the system prompt is the whole payload.
"""
