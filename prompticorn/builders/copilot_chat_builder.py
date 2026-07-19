"""CopilotChatBuilder for GitHub Copilot Chat (VS Code) customization (PRO-8).

Unlike the basic ``copilot`` target (a single concatenated
``.github/copilot-instructions.md``), Copilot Chat has three first-class
customization primitives that map cleanly onto prompticorn's IR:

* **Custom agents** — ``.github/agents/<slug>.agent.md`` (YAML frontmatter +
  system-prompt body). One per primary agent.
* **Prompt files** — ``.github/prompts/<slug>.prompt.md``, invoked as ``/slug``
  slash commands. Workflows map here.
* **Instructions files** — ``.github/instructions/<name>.instructions.md`` with an
  ``applyTo`` glob. Core conventions apply to ``**``; per-language conventions
  apply to ``**/*.<ext>``.

Skills have no Copilot Chat equivalent (there is no on-demand "skill" primitive),
so they are not emitted as separate files in v1 — agents still reference them by
name in their prose. Artifacts are kept disjoint from the ``copilot`` target
(``.github/agents|prompts|instructions`` vs ``.github/copilot-instructions.md``)
so the two never collide.

Verified against code.visualstudio.com/docs/copilot/customization
({custom-instructions, custom-chat-modes → custom agents, prompt-files}).
"""

import math
from pathlib import Path

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.convention_generator import (
    generate_core_convention,
    generate_language_convention,
)
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.roo_builder import slugify
from prompticorn.builders.windsurf_builder import _LANG_EXT
from prompticorn.ir.models import Agent


def _specs_from_config(config: dict | None) -> list[dict]:
    """Normalize ``config['spec']`` into a list of spec dicts."""
    spec_cfg = config.get("spec") if config else None
    if isinstance(spec_cfg, list):
        return [s for s in spec_cfg if isinstance(s, dict)]
    if isinstance(spec_cfg, dict):
        return [spec_cfg]
    return []


def workflow_to_prompt(name: str, content: str) -> str:
    """Wrap a workflow's content as a Copilot Chat prompt file.

    Prompt files are invoked as ``/<name>`` slash commands; a ``description``
    frontmatter field is the only metadata needed for v1. The workflow's own
    internal frontmatter (name/languages/subagents) is stripped so the emitted
    file has a single, valid YAML frontmatter block.
    """
    from prompticorn.builders.workflow_loader import WorkflowLoader

    body = WorkflowLoader.format_workflow_content(content, include_frontmatter=False)
    description = f"{name.replace('-', ' ')} workflow"
    # Serialize the frontmatter via yaml.safe_dump (like the sibling builders)
    # so a name containing a colon/quote can't break the YAML block (PRO-88).
    frontmatter = yaml.safe_dump(
        {"description": description}, default_flow_style=False, sort_keys=False
    ).strip()
    return f"---\n{frontmatter}\n---\n\n{body}\n"


class CopilotChatBuilder(Builder):
    """Builder for GitHub Copilot Chat custom agents + instructions files."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.github/agents/<slug>.agent.md`` custom-agent definition.

        Returns:
            YAML frontmatter (name/description) followed by the agent's system
            prompt as the agent body.
        """
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        description = " ".join(agent.description.split())
        # width=inf keeps each field on one line (no YAML line-folding) while
        # still quoting descriptions that contain YAML-special characters.
        frontmatter = yaml.safe_dump(
            {"name": slugify(agent.name), "description": description},
            sort_keys=False,
            allow_unicode=True,
            width=math.inf,
        ).strip()
        return f"---\n{frontmatter}\n---\n\n{agent.system_prompt}\n"

    def write_rules_files(self, output_dir: Path, config: dict | None = None) -> list[str]:
        """Write core + per-language conventions to ``.github/instructions/``.

        Core conventions get ``applyTo: '**'`` (always applied); each language's
        conventions get ``applyTo: '**/*.<ext>'`` so Copilot Chat attaches them
        only when editing files of that language.
        """
        instructions_dir = output_dir / ".github" / "instructions"
        instructions_dir.mkdir(parents=True, exist_ok=True)
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
        (instructions_dir / "core.instructions.md").write_text(
            f"---\napplyTo: '**'\n---\n\n{core}", encoding="utf-8"
        )
        written.append(".github/instructions/core.instructions.md")

        seen: set[str] = set()
        for spec in specs:
            language = spec.get("language")
            if not language or language in seen:
                continue
            seen.add(language)
            lang_content = generate_language_convention(language, spec)
            if not lang_content:
                continue
            ext = _LANG_EXT.get(language)
            apply_to = f"**/*.{ext}" if ext else "**"
            (instructions_dir / f"conventions-{language}.instructions.md").write_text(
                f"---\napplyTo: '{apply_to}'\n---\n\n{lang_content}", encoding="utf-8"
            )
            written.append(f".github/instructions/conventions-{language}.instructions.md")

        return written

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Copilot Chat (name, description, prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Copilot Chat output format."""
        return "GitHub Copilot Chat custom agent (.github/agents/<name>.agent.md)"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "copilot_chat"
