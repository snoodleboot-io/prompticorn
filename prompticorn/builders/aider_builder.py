"""AiderBuilder for generating Aider configuration (PRO-58).

Aider is the smallest target: it has no agent/skill/workflow primitive. Only
conventions map — emitted as a single root ``CONVENTIONS.md`` plus a
``.aider.conf.yml`` whose ``read:`` list makes aider always load it as read-only
context (aider does not auto-discover it). Agents, skills, and workflows are
dropped; the root ``AGENTS.md`` is suppressed.

Verified against aider.chat/docs/config/aider_conf.html. See the Aider design
doc in Linear.
"""

from pathlib import Path

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.convention_generator import (
    generate_core_convention,
    generate_language_convention,
)
from prompticorn.ir.models import Agent


def _specs_from_config(config: dict | None) -> list[dict]:
    spec_cfg = config.get("spec") if config else None
    if isinstance(spec_cfg, list):
        return [s for s in spec_cfg if isinstance(s, dict)]
    if isinstance(spec_cfg, dict):
        return [spec_cfg]
    return []


class AiderBuilder(Builder):
    """Builder for Aider: a single CONVENTIONS.md + .aider.conf.yml read wiring."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Aider has no per-agent config; agents are dropped (output discarded)."""
        return ""

    def write_rules_files(self, output_dir: Path, config: dict | None = None) -> list[str]:
        """Write CONVENTIONS.md (core + per-language) + .aider.conf.yml read wiring."""
        specs = _specs_from_config(config)
        primary_spec = specs[0] if specs else {}
        repository_type = (config.get("repository") or {}).get("type", "") if config else ""
        project = config.get("project") if config else None

        parts = [
            generate_core_convention(
                repository_type=repository_type,
                project=project,
                primary_language=primary_spec.get("language", ""),
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
                parts.append(lang_content)

        conventions = "\n\n---\n\n".join(part.strip() for part in parts) + "\n"
        (output_dir / "CONVENTIONS.md").write_text(conventions, encoding="utf-8")

        # aider does not auto-discover CONVENTIONS.md; the read: list loads it.
        conf = yaml.safe_dump({"read": ["CONVENTIONS.md"]}, sort_keys=False)
        (output_dir / ".aider.conf.yml").write_text(conf, encoding="utf-8")

        return ["CONVENTIONS.md", ".aider.conf.yml"]

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent (name/description/system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Aider output format."""
        return "Aider CONVENTIONS.md + .aider.conf.yml"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "aider"
