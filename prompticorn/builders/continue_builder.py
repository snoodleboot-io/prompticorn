"""ContinueBuilder for generating Continue.dev configuration (PRO-55).

Continue has no agent-router primitive and full assistants pin a model/provider
we don't own, so the scope is **rules + prompts**. Each prompticorn agent is
flattened to a description-scoped rule (``.continue/rules/<slug>.md``);
conventions go to ``.continue/rules/`` (glob-scoped per language); workflows
become invokable prompts (``.continue/prompts/<slug>.md``). Continue does not
read ``AGENTS.md``, so the root doc is suppressed.

Verified against docs.continue.dev/customize/deep-dives/{rules,prompts}. See the
Continue design doc in Linear.
"""

from pathlib import Path

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.convention_generator import (
    generate_core_convention,
    generate_language_convention,
)
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.windsurf_builder import _LANG_EXT
from prompticorn.ir.models import Agent


def _rule(frontmatter: dict[str, object], body: str) -> str:
    """Compose a Continue rule/prompt file (YAML frontmatter + body)."""
    fm = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n\n{body}"


def _specs_from_config(config: dict | None) -> list[dict]:
    spec_cfg = config.get("spec") if config else None
    if isinstance(spec_cfg, list):
        return [s for s in spec_cfg if isinstance(s, dict)]
    if isinstance(spec_cfg, dict):
        return [spec_cfg]
    return []


class ContinueBuilder(Builder):
    """Builder for Continue.dev: agents-as-rules + conventions rules + prompts."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.continue/rules/<slug>.md`` persona rule for an agent.

        The rule is description-scoped (``alwaysApply: false``) so Continue pulls
        it in when the description matches the task.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )
        description = " ".join(agent.description.split())
        return _rule(
            {"name": agent.name, "description": description, "alwaysApply": False},
            agent.system_prompt,
        )

    def write_rules_files(self, output_dir: Path, config: dict | None = None) -> list[str]:
        """Write core + per-language conventions to ``.continue/rules/``."""
        rules_dir = output_dir / ".continue" / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)
        written: list[str] = []

        specs = _specs_from_config(config)
        primary_spec = specs[0] if specs else {}
        repository_type = (config.get("repository") or {}).get("type", "") if config else ""
        project = config.get("project") if config else None

        core = generate_core_convention(
            repository_type=repository_type,
            project=project,
            primary_language=primary_spec.get("language", ""),
            primary_spec=primary_spec,
        )
        (rules_dir / "conventions-core.md").write_text(
            _rule({"name": "Core project conventions", "alwaysApply": True}, core),
            encoding="utf-8",
        )
        written.append(".continue/rules/conventions-core.md")

        seen: set[str] = set()
        for spec in specs:
            language = spec.get("language")
            if not language or language in seen:
                continue
            seen.add(language)
            lang_content = generate_language_convention(language, spec)
            if not lang_content:
                continue
            fm: dict[str, object] = {
                "name": f"{language} conventions",
                "description": f"{language} coding conventions",
                "alwaysApply": False,
            }
            ext = _LANG_EXT.get(language)
            if ext:
                fm["globs"] = [f"**/*.{ext}"]
            (rules_dir / f"conventions-{language}.md").write_text(
                _rule(fm, lang_content), encoding="utf-8"
            )
            written.append(f".continue/rules/conventions-{language}.md")

        return written

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Continue (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Continue output format."""
        return "Continue.dev rules + prompts (.continue/)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "continue"


def workflow_to_continue_prompt(workflow_name: str, content: str) -> str:
    """Wrap a workflow's Markdown body into an invokable Continue prompt file."""
    return _rule(
        {
            "name": workflow_name,
            "description": f"{workflow_name} workflow",
            "invokable": True,
        },
        content,
    )
