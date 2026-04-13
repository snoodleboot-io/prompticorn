"""KiloBuilder for generating Kilo IDE agent configuration files.

This module implements the KiloBuilder class that translates Agent IR models
into Kilo IDE agent files with YAML frontmatter and markdown sections.
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.builder import Builder
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.loaders import CoreFilesLoader
from promptosaurus.ir.models import Agent


class KiloBuilder(AbstractBuilder):
    """Builder for Kilo IDE agent configurations.

    Generates `.kilo/agents/{name}.md` files with YAML frontmatter and
    markdown sections for system prompts, tools, skills, workflows, and
    subagents.

    Output Format:
        ---
        name: "agent_name"
        description: "Agent description"
        state_management: ".promptosaurus/sessions/"
        ---

        # System Prompt

        [System prompt content]

        # Tools

        - tool1
        - tool2

        # Skills

        [Skills content]

        # Workflows

        [Workflows content]

        # Subagents

        - subagent1
        - subagent2
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize KiloBuilder.

        Args:
            agents_dir: Base directory for agent configurations (default: 'agents')
        """
        self.agents_dir = agents_dir
        self.core_loader = CoreFilesLoader()
        # Initialize Builder for template variable substitution
        self._builder = Builder()

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build a Kilo agent configuration file.

        Includes core system, conventions, and language-specific conventions files
        if language is specified in config.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options
            config: Optional configuration dict with 'spec' key containing language info

        Returns:
            String containing YAML frontmatter + markdown sections

        Raises:
            BuilderValidationError: If the agent model is invalid
        """
        # Validate the agent
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        # Use agent system prompt directly (no variants for top-level agents)
        system_prompt = agent.system_prompt

        # Apply template variable substitution if config is provided
        if config:
            system_prompt = self._builder._substitute_template_variables(system_prompt, config)

        # Prepare YAML frontmatter
        frontmatter = self._build_frontmatter(agent)

        # Compose markdown output
        markdown_sections = []

        # NOTE: Core files (system.md, conventions.md, etc.) are now written to
        # .kilo/rules/ directory and referenced via kilo.jsonc config file.
        # They are NOT embedded in agent files anymore.

        # 1. System Prompt - use variant content or agent model
        markdown_sections.append("# System Prompt\n")
        markdown_sections.append(system_prompt)
        markdown_sections.append("")

        # 2. Tools (if requested)
        if options.include_tools and agent.tools:
            markdown_sections.append("# Tools\n")
            markdown_sections.append(self._format_tools(agent.tools))
            markdown_sections.append("")

        # 3. Skills (if requested)
        if options.include_skills and agent.skills:
            markdown_sections.append("# Skills\n")
            markdown_sections.append(self._format_skills(agent.skills))
            markdown_sections.append("")

        # 4. Workflows (if requested)
        if options.include_workflows and agent.workflows:
            markdown_sections.append("# Workflows\n")
            markdown_sections.append(self._format_workflows(agent.workflows))
            markdown_sections.append("")

        # 5. Subagents (if requested)
        if options.include_subagents and agent.subagents:
            markdown_sections.append("# Subagents\n")
            markdown_sections.append(self._format_subagents(agent.subagents))
            markdown_sections.append("")

        markdown_content = "\n".join(markdown_sections).strip()

        # Compose YAML frontmatter + markdown
        return self._compose_yaml_markdown(frontmatter, markdown_content)
    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent IR model for Kilo.

        Checks that required fields are present and non-empty.

        Args:
            agent: The Agent IR model to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not agent.name:
            errors.append("Agent name is required and must not be empty")

        if not agent.description:
            errors.append("Agent description is required and must not be empty")

        if not agent.system_prompt:
            errors.append("System prompt is required and must not be empty")

        return errors

    def get_output_format(self) -> str:
        """Get the output format description.

        Returns:
            Description of Kilo format
        """
        return "Kilo IDE Agent File (YAML frontmatter + Markdown)"

    def get_tool_name(self) -> str:
        """Get the tool name.

        Returns:
            "kilo"
        """
        return "kilo"

    def build_subagents(self, agent: Agent, options: BuildOptions) -> dict[str, str]:
        """Build Kilo subagent configuration files.

        Generates subagent files in a nested directory structure:
        `.kilo/agents/{agent_name}/{subagent_name}.md`

        Args:
            agent: The parent Agent IR model
            options: Build configuration options

        Returns:
            Dictionary mapping subagent names to their file content

        Raises:
            BuilderValidationError: If agent or subagents are invalid
        """
        if not agent.subagents:
            return {}

        subagent_files = {}

        for subagent_name in agent.subagents:
            # Create a minimal Agent IR for the subagent
            # Subagents inherit some characteristics from parent
            subagent = Agent(
                name=subagent_name,
                description=f"Subagent of {agent.name}",
                system_prompt=f"You are a {subagent_name} subagent assisting {agent.name}.",
            )

            # Build subagent content
            subagent_content = self._build_subagent_file(subagent, agent.name, options)
            subagent_files[subagent_name] = subagent_content

        return subagent_files

    def _build_subagent_file(self, subagent: Agent, parent_name: str, options: BuildOptions) -> str:
        """Build a single subagent file with parent reference.

        Args:
            subagent: The subagent Agent IR model
            parent_name: Name of the parent agent
            options: Build configuration options

        Returns:
            String containing subagent file content with parent reference
        """
        # Validate the subagent
        errors = self.validate(subagent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid subagent '{subagent.name}': {'; '.join(errors)}"
            )

        # Build frontmatter with parent reference
        frontmatter = self._build_frontmatter(subagent)
        frontmatter["parent_agent"] = parent_name

        # Compose markdown with parent context
        markdown_sections = []

        # Add parent reference as intro
        markdown_sections.append("# Parent Agent\n")
        markdown_sections.append(f"{parent_name}\n")
        markdown_sections.append("")

        # System Prompt
        markdown_sections.append("# System Prompt\n")
        markdown_sections.append(subagent.system_prompt)
        markdown_sections.append("")

        # Tools (if present)
        if options.include_tools and subagent.tools:
            markdown_sections.append("# Tools\n")
            markdown_sections.append(self._format_tools(subagent.tools))
            markdown_sections.append("")

        # Skills (if present)
        if options.include_skills and subagent.skills:
            markdown_sections.append("# Skills\n")
            markdown_sections.append("; ".join(subagent.skills))
            markdown_sections.append("")

        markdown_content = "\n".join(markdown_sections).strip()

        # Compose YAML frontmatter + markdown
        return self._compose_yaml_markdown(frontmatter, markdown_content)

    def _build_frontmatter(self, agent: Agent) -> dict[str, Any]:
        """Build YAML frontmatter for Kilo agent file.

        Args:
            agent: The Agent IR model

        Returns:
            Dictionary of frontmatter fields
        """
        frontmatter: dict[str, Any] = {
            "name": agent.name,
            "description": agent.description,
        }

        # Add mode if present
        if hasattr(agent, "mode") and agent.mode:
            frontmatter["mode"] = agent.mode

        # Add state management
        frontmatter["state_management"] = ".promptosaurus/sessions/"

        # Add permissions if present
        if agent.permissions:
            frontmatter["permission"] = agent.permissions

        return frontmatter

    def _format_tools(self, tools: list[str]) -> str:
        """Format tools as markdown list.

        Args:
            tools: List of tool names

        Returns:
            Formatted markdown string
        """
        lines = []
        for tool in tools:
            lines.append(f"- {tool}")
        return "\n".join(lines)

    def _format_skills(self, skills: list[str]) -> str:
        """Format skills as markdown list.

        Args:
            skills: List of skill names

        Returns:
            Formatted markdown string
        """
        lines = []
        for skill in skills:
            lines.append(f"- {skill}")
        return "\n".join(lines)

    def _format_workflows(self, workflows: list[str]) -> str:
        """Format workflows as markdown list.

        Args:
            workflows: List of workflow names

        Returns:
            Formatted markdown string
        """
        lines = []
        for workflow in workflows:
            lines.append(f"- {workflow}")
        return "\n".join(lines)

    def _format_subagents(self, subagent_names: list[str]) -> str:
        """Format subagents as markdown list.

        Args:
            subagent_names: List of subagent names

        Returns:
            Formatted markdown string
        """
        lines = []
        for subagent in subagent_names:
            lines.append(f"- {subagent}")
        return "\n".join(lines)

    def _compose_yaml_markdown(self, frontmatter: dict[str, Any], markdown_content: str) -> str:
        """Compose YAML frontmatter and markdown content.

        Args:
            frontmatter: Dictionary of YAML frontmatter fields
            markdown_content: Markdown content string

        Returns:
            Complete file content with YAML frontmatter and markdown
        """
        yaml_lines = ["---"]

        for key, value in frontmatter.items():
            if isinstance(value, bool):
                yaml_lines.append(f"{key}: {str(value).lower()}")
            elif isinstance(value, str):
                # Quote strings that contain special characters
                if any(c in value for c in ['"', "'", ":", "\n"]):
                    yaml_lines.append(f'{key}: "{value}"')
                else:
                    yaml_lines.append(f"{key}: {value}")
            elif isinstance(value, (int, float)):
                yaml_lines.append(f"{key}: {value}")
            elif isinstance(value, dict):
                # Handle nested dictionaries (like permissions)
                yaml_lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    yaml_lines.append(f"  {sub_key}: {sub_value}")
            else:
                yaml_lines.append(f"{key}: {value}")

        yaml_lines.append("---")
        yaml_frontmatter = "\n".join(yaml_lines)

        return f"{yaml_frontmatter}\n\n{markdown_content}"

    def write_rules_files(self, output_dir: Path, config: dict | None = None) -> list[str]:
        """Write core convention files to .kilo/rules/ directory.

        Outputs static core files and language-specific conventions
        (if language is configured). Jinja2 templates are rendered
        with user's config values before writing.

        Args:
            output_dir: Project root directory (e.g., Path("."))
            config: Optional config dict with 'spec' key containing language, runtime, etc.

        Returns:
            List of file paths written relative to .kilo directory

        Example:
            >>> builder = KiloBuilder()
            >>> config = {"spec": {"language": "python", "runtime": "3.11"}}
            >>> files = builder.write_rules_files(Path("."), config)
            >>> files
            ['rules/system.md', 'rules/session.md', 'rules/conventions.md', 'rules/conventions-python.md']
        """
        # Create .kilo/rules/ directory
        kilo_dir = output_dir / ".kilo"
        rules_dir = kilo_dir / "rules"
        rules_dir.mkdir(parents=True, exist_ok=True)

        written_files = []

        # Static core files (no templating needed)
        static_files = [
            "system.md",
            "session.md",
            "session-troubleshooting.md",
            "decision-log-template.md",
        ]

        for filename in static_files:
            source_path = self.core_loader.core_dir / filename
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                output_path = rules_dir / filename
                output_path.write_text(content, encoding="utf-8")
                written_files.append(f"rules/{filename}")

        # Templated conventions.md (always include, render if config available)
        conventions_source = self.core_loader.core_dir / "conventions.md"
        if conventions_source.exists():
            content = conventions_source.read_text(encoding="utf-8")
            if config:
                content = self.core_loader._template_content(content, config)
            output_path = rules_dir / "conventions.md"
            output_path.write_text(content, encoding="utf-8")
            written_files.append("rules/conventions.md")

        # Language-specific conventions (only if language configured)
        if config:
            # Extract language (handles both single-language dict and multi-language-monorepo list)
            spec = config.get("spec")
            if isinstance(spec, dict):
                language = spec.get("language")
            elif isinstance(spec, list) and len(spec) > 0:
                language = spec[0].get("language")
            else:
                language = None
            if language:
                lang_source = self.core_loader.core_dir / f"conventions-{language}.md"
                if lang_source.exists():
                    content = lang_source.read_text(encoding="utf-8")
                    content = self.core_loader._template_content(content, config)
                    output_path = rules_dir / f"conventions-{language}.md"
                    output_path.write_text(content, encoding="utf-8")
                    written_files.append(f"rules/conventions-{language}.md")

        return written_files
