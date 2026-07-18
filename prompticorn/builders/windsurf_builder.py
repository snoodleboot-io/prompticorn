"""WindsurfBuilder for generating Windsurf / Cascade configuration (PRO-52).

Windsurf has no agent primitive and a hard ~12k-character budget on rules, so
each prompticorn agent is emitted as a **skill** (``.windsurf/skills/<slug>/
SKILL.md``) — skills are progressively disclosed and escape the rules budget.
Conventions go to ``.windsurf/rules/`` with Cascade ``trigger`` frontmatter
(core = ``always_on`` when it fits Windsurf's ~12k budget, else ``model_decision``;
per-language = ``glob``); the fat root ``AGENTS.md`` is
suppressed to stay within the 12k budget. Workflows become
``.windsurf/workflows/<slug>.md``.

Verified against docs.devin.ai/desktop/cascade/*. See the Windsurf design doc in
Linear.
"""

import warnings
from pathlib import Path

import yaml

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.convention_generator import (
    generate_core_convention,
    generate_language_convention,
)
from prompticorn.builders.errors import BuilderValidationError
from prompticorn.builders.junie_builder import slugify
from prompticorn.ir.models import Agent

# Language -> file extension for glob-scoped convention rules. Languages absent
# here fall back to a description-triggered (model_decision) rule.
_LANG_EXT = {
    "python": "py",
    "typescript": "ts",
    "javascript": "js",
    "go": "go",
    "rust": "rs",
    "java": "java",
    "kotlin": "kt",
    "csharp": "cs",
    "ruby": "rb",
    "php": "php",
    "swift": "swift",
    "scala": "scala",
    "elixir": "ex",
    "fsharp": "fs",
}


# Windsurf caps rule files at ~12,000 characters (per file, and the always-on
# aggregate). Rules over this are silently truncated by Windsurf.
_RULE_CHAR_LIMIT = 12000


class WindsurfRuleBudgetWarning(UserWarning):
    """Raised when an emitted Windsurf rule exceeds the ~12k character cap."""


def _warn_if_over_budget(rel_path: str, content: str) -> None:
    if len(content) > _RULE_CHAR_LIMIT:
        warnings.warn(
            f"{rel_path} is {len(content)} chars, over Windsurf's "
            f"{_RULE_CHAR_LIMIT}-char rule cap; Windsurf will truncate it. "
            "Consider trimming conventions or moving detail into skills.",
            WindsurfRuleBudgetWarning,
            stacklevel=2,
        )


def _rule(frontmatter: dict[str, object], body: str) -> str:
    """Compose a Windsurf rule file (trigger frontmatter + body)."""
    fm = yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{fm}\n---\n\n{body}"


def _specs_from_config(config: dict | None) -> list[dict]:
    spec_cfg = config.get("spec") if config else None
    if isinstance(spec_cfg, list):
        return [s for s in spec_cfg if isinstance(s, dict)]
    if isinstance(spec_cfg, dict):
        return [spec_cfg]
    return []


class WindsurfBuilder(Builder):
    """Builder for Windsurf: agents-as-skills + Cascade rule conventions."""

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build one ``.windsurf/skills/<slug>/SKILL.md`` body for an agent."""
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )
        description = " ".join(agent.description.split())
        frontmatter = yaml.safe_dump(
            {"name": slugify(agent.name), "description": description},
            sort_keys=False,
            allow_unicode=True,
        ).strip()
        return f"---\n{frontmatter}\n---\n\n{agent.system_prompt}\n"

    def write_rules_files(self, output_dir: Path, config: dict | None = None) -> list[str]:
        """Write core + per-language conventions to ``.windsurf/rules/``.

        Core is ``always_on`` only when it fits Windsurf's ~12k budget; a larger
        core is emitted ``model_decision`` (pulled on demand by description) so it
        does not consume the always-on budget. Each language is a ``glob`` rule
        scoped to its file extension (``model_decision`` when the extension is
        unknown). Any rule still over the per-file cap raises a build warning.
        """
        rules_dir = output_dir / ".windsurf" / "rules"
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
        # A large always-on core would blow the 12k always-on budget; keep it
        # always-on only when it fits, otherwise make it description-triggered.
        core_trigger = "always_on" if len(core) <= _RULE_CHAR_LIMIT else "model_decision"
        core_rule = _rule(
            {"trigger": core_trigger, "description": "Core project conventions"}, core
        )
        (rules_dir / "conventions-core.md").write_text(core_rule, encoding="utf-8")
        _warn_if_over_budget(".windsurf/rules/conventions-core.md", core_rule)
        written.append(".windsurf/rules/conventions-core.md")

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
            if ext:
                fm: dict[str, object] = {
                    "trigger": "glob",
                    "globs": f"**/*.{ext}",
                    "description": f"{language} conventions",
                }
            else:
                fm = {"trigger": "model_decision", "description": f"{language} conventions"}
            rel = f".windsurf/rules/conventions-{language}.md"
            lang_rule = _rule(fm, lang_content)
            (rules_dir / f"conventions-{language}.md").write_text(lang_rule, encoding="utf-8")
            _warn_if_over_budget(rel, lang_rule)
            written.append(rel)

        return written

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent for Windsurf (name, description, system prompt required)."""
        errors = []
        if not agent.name:
            errors.append("Agent name is required and must not be empty")
        if not agent.description:
            errors.append("Agent description is required and must not be empty")
        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")
        return errors

    def get_output_format(self) -> str:
        """Return a description of the Windsurf output format."""
        return "Windsurf agent-as-skill + .windsurf/rules conventions"

    def get_tool_name(self) -> str:
        """Return the internal tool name."""
        return "windsurf"


def workflow_to_windsurf(workflow_name: str, content: str) -> str:
    """Wrap a workflow's Markdown body into a Windsurf workflow file.

    Emits only the ``description`` frontmatter (the safe, documented field);
    ``auto_execution_mode`` is intentionally omitted (under-documented).
    """
    return _rule({"description": f"{workflow_name} workflow"}, content)
