"""ClineBuilder for generating Cline AI rules files.

This module implements the ClineBuilder class that translates Agent IR models
into Cline AI configuration files (.clinerules) with markdown formatting.
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.models import Agent


class ClineBuilder(AbstractBuilder):
    """Builder for Cline AI configuration files.

    Generates `.clinerules` files (single markdown file) with system prompt,
    tools, skills, workflows, and subagents sections.

    Output Format:
        # {Agent Name} Rules

        [System prompt as prose - no markdown formatting]

        ## Tools

        - tool1: Description and usage
        - tool2: Description and usage

        ## Skills

        ### Skill: skill-name
        Description of when and how to use this skill.
        Invoke by: use_skill skill-name

        ## Workflows

        ### Workflow: workflow-name
        Step-by-step workflow instructions...

        ## Subagents

        ### Subagent: subagent-name
        Description of what this subagent does...
        Invoke by: use_skill workflow-name or @subagent-name
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize ClineBuilder.

        Args:
            agents_dir: Base directory for agent configurations (default: 'agents')
        """
        self.agents_dir = agents_dir

    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Build a Cline AI configuration file.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options

        Returns:
            String containing markdown content for .clinerules file

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
        sections.append(self._format_system_prompt_prose(agent.system_prompt))
        sections.append("")

        # 3. Tools section (if requested)
        if options.include_tools and agent.tools:
            sections.append(self._format_tools_section(agent.tools))
            sections.append("")

        # 4. Skills section (if requested)
        if options.include_skills and agent.skills:
            sections.append(self._format_skills_section(agent.skills))
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
        """Validate an Agent IR model for Cline.

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
            Description of Cline format
        """
        return "Cline AI Rules File (Markdown)"

    def get_tool_name(self) -> str:
        """Get the tool name.

        Returns:
            "cline"
        """
        return "cline"

    def _format_header(self, agent: Agent) -> str:
        """Format the .clinerules header with agent name.

        Args:
            agent: The Agent IR model

        Returns:
            Markdown header string
        """
        return f"# {agent.name} Rules"

    def _format_system_prompt_prose(self, prompt: str) -> str:
        """Format system prompt as prose narrative.

        The system prompt is the first prose section after the header,
        without any special markdown formatting.

        Args:
            prompt: The system prompt content

        Returns:
            System prompt as prose (stripped)
        """
        return prompt.strip()

    def _format_tools_section(self, tools: list[str]) -> str:
        """Format tools as markdown section with descriptions.

        Args:
            tools: List of tool names

        Returns:
            Formatted markdown section
        """
        lines = ["## Tools", ""]
        lines.append("Available tools:")
        lines.append("")

        for tool in tools:
            # Format as markdown list with tool name
            lines.append(f"- **{tool}**: [Tool description and usage]")

        return "\n".join(lines)

    def _format_skills_section(self, skill_names: list[str]) -> str:
        """Format skills section with use_skill invocation pattern.

        Args:
            skill_names: List of skill names from agent

        Returns:
            Formatted markdown section with use_skill instructions
        """
        lines = ["## Skills", ""]
        lines.append("The following skills are available. Use them by calling use_skill::")
        lines.append("")

        # Add each skill with use_skill invocation pattern
        if skill_names:
            for skill in skill_names:
                # Convert skill name to snake_case if needed
                skill_key = skill.lower().replace(" ", "_").replace("-", "_")
                lines.append(f"### Skill: {skill}")
                lines.append("")
                lines.append(f"Invoke by: `use_skill {skill_key}`")
                lines.append("")

        return "\n".join(lines)

    def _format_workflows_section(self, workflow_names: list[str]) -> str:
        """Format workflows section with step-by-step instructions.

        Args:
            workflow_names: List of workflow names from agent

        Returns:
            Formatted markdown section
        """
        lines = ["## Workflows", ""]

        # Add each workflow as a list
        for workflow in workflow_names:
            lines.append(f"- {workflow}")

        return "\n".join(lines)

    def _format_subagents_section(self, subagent_names: list[str]) -> str:
        """Format subagents section with delegation instructions.

        Args:
            subagent_names: List of subagent names

        Returns:
            Formatted markdown section
        """
        lines = ["## Subagents", ""]
        lines.append("You may delegate to these specialists:")
        lines.append("")

        for subagent in subagent_names:
            # Convert subagent name to key format
            subagent_key = subagent.lower().replace(" ", "_").replace("-", "_")
            lines.append(f"### Subagent: {subagent}")
            lines.append("")
            lines.append(f"Specializes in {subagent} tasks.")
            lines.append("")
            lines.append(f"Invoke by: `use_skill {subagent_key}` or request '{subagent} subagent'")
            lines.append("")

        return "\n".join(lines)
