"""AmazonQBuilder for generating Amazon Q Developer CLI configuration (PRO-49).

Amazon Q is the most divergent target: it does NOT read ``AGENTS.md``. Agents are
JSON files (``.amazonq/cli-agents/<name>.json``), conventions are auto-loaded
Markdown under ``.amazonq/rules/`` (via each agent's ``resources`` glob), and
workflows become saved prompts (``.amazonq/prompts/<name>.md``). There is no
skill primitive and no auto-routing (one active agent per session).

Verified against github.com/aws/amazon-q-developer-cli/docs. See the Amazon Q
design doc in Linear.
"""

import json
from pathlib import Path

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.convention_generator import (
    generate_core_convention,
    generate_language_convention,
)
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.junie_builder import slugify
from prompticorn.ir.models import Agent

# Glob that makes an agent load every convention file; a custom agent does NOT
# inherit the built-in default agent's resources, so each agent must list it.
_RULES_RESOURCE = "file://.amazonq/rules/**/*.md"


def _specs_from_config(config: dict | None) -> list[dict]:
    """Normalize config['spec'] into a list of spec dicts."""
    spec_cfg = config.get("spec") if config else None
    if isinstance(spec_cfg, list):
        return [s for s in spec_cfg if isinstance(s, dict)]
    if isinstance(spec_cfg, dict):
        return [spec_cfg]
    return []


class AmazonQBuilder(Builder):
    """Builder for Amazon Q CLI custom agents (JSON) + rules conventions."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.amazonq/cli-agents/<slug>.json`` agent definition.

        Returns:
            Pretty-printed JSON: name/description/prompt/tools/resources. The
            ``resources`` glob is required so conventions in .amazonq/rules load.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        definition = {
            "name": slugify(agent.name),
            "description": " ".join(agent.description.split()),
            "prompt": agent.system_prompt,
            "tools": ["*"],
            "resources": [_RULES_RESOURCE],
        }
        return json.dumps(definition, indent=2) + "\n"

    def write_rules_files(self, output_dir: Path, config: dict | None = None) -> list[str]:
        """Write core + per-language conventions to ``.amazonq/rules/``.

        Amazon Q auto-loads these via the agents' ``resources`` glob (Amazon Q
        does not read AGENTS.md), so this is where conventions must live.
        """
        rules_dir = output_dir / ".amazonq" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        written: list[str] = []

        specs = _specs_from_config(config)
        primary_spec = specs[0] if specs else {}
        primary_language = primary_spec.get("language", "")
        repository_type = (config.get("repository") or {}).get("type", "") if config else ""
        project = config.get("project") if config else None

        core = generate_core_convention(
            repository_type=repository_type,
            project=project,
            primary_language=primary_language,
            primary_spec=primary_spec,
        )
        (rules_dir / "conventions.md").write_text(core, encoding="utf-8")
        written.append(".amazonq/rules/conventions.md")

        seen: set[str] = set()
        for spec in specs:
            language = spec.get("language")
            if not language or language in seen:
                continue
            seen.add(language)
            lang_content = generate_language_convention(language, spec)
            if lang_content:
                (rules_dir / f"conventions-{language}.md").write_text(lang_content, encoding="utf-8")
                written.append(f".amazonq/rules/conventions-{language}.md")

        return written

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Amazon Q (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Amazon Q output format."""
        return "Amazon Q CLI agent (.amazonq/cli-agents/<name>.json)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "amazonq"
