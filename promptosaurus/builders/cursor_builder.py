"""CursorBuilder for generating Cursor AI rules files.

This module implements the CursorBuilder class that translates Agent IR models
into Cursor AI configuration files (.cursorrules) with markdown formatting.
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
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

    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Build a Cursor AI configuration file.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options

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

        # Compose markdown output as prose (no YAML frontmatter)
        sections = []

        # 1. Header with agent name
        sections.append(self._format_header(agent))
        sections.append("")

        # 2. System prompt as prose (first paragraph) - use agent.system_prompt directly
        sections.append(self._format_system_prompt_prose(agent.system_prompt, agent.description))
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
            sections.append(self._format_workflows_section(agent.workflows))
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
            lines.append(f"Usage: Call with appropriate parameters")
            lines.append("")

        return "\n".join(lines).rstrip()

    def _format_workflows_section(self, workflow_names: list[str]) -> str:
        """Format workflows section with step-by-step instructions.

        Args:
            workflow_names: List of workflow names from agent

        Returns:
            Formatted markdown section
        """
        lines = ["## Workflows", ""]

        for workflow in workflow_names:
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
