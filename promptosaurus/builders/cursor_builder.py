"""CursorBuilder for generating Cursor AI rules files.

This module implements the CursorBuilder class that translates Agent IR models
into Cursor AI configuration files (.cursorrules) with markdown formatting.
"""

from pathlib import Path

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.loaders import CoreFilesLoader
from promptosaurus.ir.models import Agent


class CursorBuilder(AbstractBuilder):
    """Builder for Cursor AI configuration files.

    Generates `.cursorrules` files (single markdown file) with system prompt,
    constraints, tools, workflows, and subagents sections.

    Output Format:
        # {Agent Name} Rules

        You are an expert [description].

        Your responsibilities:
        - [responsibility 1]
        - [responsibility 2]

        ## Core Constraints

        - Type hints required on all public functions
        - [constraint 2]

        ## Available Tools

        ### read - Read files
        Purpose: [purpose]
        Usage: [usage]

        ### bash - Execute commands
        Purpose: [purpose]
        Usage: [usage]

        ## Workflows

        When implementing features:
        1. [step 1]
        2. [step 2]

        ## Subagents Available

        - architect: [description]
        - test: [description]
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize CursorBuilder.

        Args:
            agents_dir: Base directory for agent configurations (default: 'agents')
        """
        self.agents_dir = agents_dir
        self.core_loader = CoreFilesLoader()

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build a Cursor AI configuration file.

        Includes core system, conventions, and language-specific conventions files
        if language is specified in config.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options
            config: Optional configuration dict with 'spec' key containing language info

        Returns:
            String containing markdown content for .cursorrules file

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

        # Compose markdown output as prose (no YAML frontmatter)
        sections = []

        # Load and include core files if language is available
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
                core_files = self.core_loader.get_core_files(language, config)
                # Order: system, conventions, session, language-specific
                for key in ["system", "conventions", "session"]:
                    if key in core_files:
                        sections.append(f"## {key.capitalize()}\n")
                        sections.append(core_files[key])
                        sections.append("")

                # Add language conventions if available
                lang_key = f"conventions_{language}"
                if lang_key in core_files:
                    sections.append(f"## {language.capitalize()} Conventions\n")
                    sections.append(core_files[lang_key])
                    sections.append("")

        # 1. Header with agent name
        sections.append(self._format_header(agent))
        sections.append("")

        # 2. System prompt as prose (first paragraph) - use variant content or agent model
        sections.append(self._format_system_prompt_prose(system_prompt, agent.description))
        sections.append("")

        # 3. Core Constraints section
        if options.include_rules:
            sections.append(self._format_constraints_section(""))
            sections.append("")

        # 4. Tools section (if requested)
        if options.include_tools and agent.tools:
            sections.append(self._format_tools_section(agent.tools))
            sections.append("")

        # 5. Workflows section (if requested)
        if options.include_workflows and agent.workflows:
            sections.append(self._format_workflows_section(agent.workflows, options.variant))
            sections.append("")

        # 6. Subagents section (if requested)
        if options.include_subagents and agent.subagents:
            sections.append(self._format_subagents_section(agent.subagents))
            sections.append("")

        # Concatenate all sections
        markdown_content = "\n".join(sections).strip()
        return markdown_content

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent IR model for Cursor.

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
            Description of Cursor format
        """
        return "Cursor AI Rules File (Markdown)"

    def get_tool_name(self) -> str:
        """Get the tool name.

        Returns:
            "cursor"
        """
        return "cursor"

    def _format_header(self, agent: Agent) -> str:
        """Format the .cursorrules header with agent name.

        Args:
            agent: The Agent IR model

        Returns:
            Markdown header string
        """
        return f"# {agent.name} Rules"

    def _format_system_prompt_prose(self, prompt: str, description: str = "") -> str:
        """Format system prompt as prose narrative with responsibilities.

        The system prompt is rendered as prose with a responsibilities section
        extracted from the system prompt content.

        Args:
            prompt: The system prompt content
            description: Agent description for context

        Returns:
            System prompt as prose with responsibilities section
        """
        # Return the prompt as-is, stripped of whitespace
        return prompt.strip()

    def _format_constraints_section(self, rules: str) -> str:
        """Format constraints/rules as markdown section.

        Args:
            rules: Raw rules/constraints content

        Returns:
            Formatted markdown section
        """
        lines = ["## Core Constraints", ""]

        if rules:
            # If rules content exists, use it
            lines.append(rules.strip())
        else:
            # Provide default constraints for Cursor
            lines.append("- Type hints required on all public functions")
            lines.append("- No `any` types without explicit justification")
            lines.append("- Read code BEFORE writing code")
            lines.append("- Match existing patterns exactly")

        return "\n".join(lines)

    def _format_tools_section(self, tools: list[str]) -> str:
        """Format tools as markdown section with descriptions.

        Args:
            tools: List of tool names

        Returns:
            Formatted markdown section
        """
        lines = ["## Available Tools", ""]

        for tool in tools:
            # Format as markdown subsection with tool name
            lines.append(f"### {tool}")
            lines.append("")
            lines.append(f"Purpose: [Description of {tool}]")
            lines.append("Usage: Call with appropriate parameters")
            lines.append("")

        return "\n".join(lines).rstrip()

    def _format_workflows_section(self, workflow_names: list[str], variant: str = "minimal") -> str:
        """Format workflows section with step-by-step instructions.

        Args:
            workflow_names: List of workflow names from agent
            variant: Variant to load (minimal/verbose)

        Returns:
            Formatted workflows section with full content
        """
        from promptosaurus.builders.workflow_loader import WorkflowLoader

        lines = ["## Workflows", ""]

        # Load and embed each workflow with full content
        for workflow in workflow_names:
            workflow_content = WorkflowLoader.load_workflow(workflow, variant)

            if workflow_content:
                # Format workflow content (strip frontmatter)
                formatted_content = WorkflowLoader.format_workflow_content(
                    workflow_content, include_frontmatter=False
                )

                lines.append(f"### {workflow}")
                lines.append("")
                lines.append(formatted_content)
                lines.append("")
            else:
                # Fallback to just name if content not found
                lines.append(f"- {workflow}")

        return "\n".join(lines)

    def _format_subagents_section(self, subagent_names: list[str]) -> str:
        """Format subagents section with descriptions and roles.

        Args:
            subagent_names: List of subagent names

        Returns:
            Formatted markdown section
        """
        lines = ["## Subagents Available", ""]

        for subagent in subagent_names:
            # Convert subagent name to key format
            subagent_key = subagent.lower().replace(" ", "-").replace("_", "-")
            lines.append(f"- **{subagent}**: Specializes in {subagent_key} tasks")

        return "\n".join(lines)
