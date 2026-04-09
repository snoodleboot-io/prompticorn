"""CopilotBuilder for generating GitHub Copilot instructions files.

This module implements the CopilotBuilder class that translates Agent IR models
into GitHub Copilot instructions files with YAML frontmatter and markdown sections.
"""

from pathlib import Path
from typing import Any

from src.builders.base import AbstractBuilder, BuildOptions
from src.builders.component_selector import ComponentSelector, Variant
from src.builders.errors import BuilderValidationError
from src.ir.models import Agent


class CopilotBuilder(AbstractBuilder):
    """Builder for GitHub Copilot instructions files.

    Generates `.github/instructions/{mode}.md` files with YAML frontmatter
    containing applyTo metadata and markdown sections for system prompts,
    tools, skills, workflows, and subagents.

    Output Format:
        ---
        applyTo:
          - model: "code"
          - parentAgents: []
        ---

        # Copilot Code Agent Instructions

        [System prompt content]

        ## Tools

        - tool1
        - tool2

        ## Skills

        ### Skill: skill-name
        Description and activation instructions

        ## Workflows

        ### Workflow: workflow-name
        Workflow instructions

        ## Subagents

        ### Subagent: subagent-name
        Subagent description
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize CopilotBuilder.

        Args:
            agents_dir: Base directory for agent configurations (default: 'agents')
        """
        self.agents_dir = agents_dir
        self.selector = ComponentSelector(agents_dir=agents_dir)

    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Build a GitHub Copilot instructions file.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options

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

        # Select variant (minimal or verbose)
        variant = Variant.MINIMAL if options.variant == "minimal" else Variant.VERBOSE

        # Load components with variant selection
        bundle = self.selector.select(agent, variant=variant)

        # Prepare YAML frontmatter with applyTo
        frontmatter = self._build_frontmatter(agent)

        # Compose markdown output
        markdown_sections = []

        # 1. Header with agent name
        markdown_sections.append(self._format_header(agent))
        markdown_sections.append("")

        # 2. System prompt as prose
        markdown_sections.append(bundle.prompt)
        markdown_sections.append("")

        # 3. Tools (if requested)
        if options.include_tools and agent.tools:
            markdown_sections.append(self._format_tools_section(agent.tools))
            markdown_sections.append("")

        # 4. Skills (if requested)
        if options.include_skills and bundle.skills:
            markdown_sections.append(self._format_skills_section(bundle.skills, agent.skills or []))
            markdown_sections.append("")

        # 5. Workflows (if requested)
        if options.include_workflows and bundle.workflow:
            markdown_sections.append(self._format_workflows_section(bundle.workflow))
            markdown_sections.append("")

        # 6. Subagents (if requested)
        if options.include_subagents and agent.subagents:
            markdown_sections.append(self._format_subagents_section(agent.subagents))
            markdown_sections.append("")

        markdown_content = "\n".join(markdown_sections).strip()

        # Compose YAML frontmatter + markdown
        return self._compose_yaml_markdown(frontmatter, markdown_content)

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent IR model for Copilot.

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
            Description of Copilot format
        """
        return "GitHub Copilot Instructions File (YAML frontmatter + Markdown)"

    def get_tool_name(self) -> str:
        """Get the tool name.

        Returns:
            "copilot"
        """
        return "copilot"

    def _build_frontmatter(self, agent: Agent) -> dict[str, Any]:
        """Build YAML frontmatter with applyTo metadata.

        Args:
            agent: The Agent IR model

        Returns:
            Dictionary of frontmatter fields with applyTo context list
        """
        apply_to_list = self._build_apply_to_list(agent)

        return {
            "applyTo": apply_to_list,
        }

    def _build_apply_to_list(self, agent: Agent) -> list[dict[str, Any]]:
        """Build the applyTo list for Copilot instructions.

        The applyTo field specifies contexts where the instructions apply.
        For Copilot, this typically includes:
        - model: The agent/mode name
        - parentAgents: List of parent agents (empty for root agents)

        Args:
            agent: The Agent IR model

        Returns:
            List of context dictionaries for applyTo field
        """
        # Build base context with model name
        contexts = [
            {
                "model": agent.name,
            },
            {
                "parentAgents": [],
            },
        ]

        return contexts

    def _format_header(self, agent: Agent) -> str:
        """Format the header for Copilot instructions.

        Args:
            agent: The Agent IR model

        Returns:
            Formatted header string
        """
        # Capitalize agent name nicely (e.g., "code" -> "Code")
        agent_display = agent.name.capitalize()
        return f"# Copilot {agent_display} Agent Instructions"

    def _format_tools_section(self, tools: list[str]) -> str:
        """Format tools section for Copilot instructions.

        Args:
            tools: List of tool names

        Returns:
            Formatted tools section as markdown
        """
        lines = ["## Tools\n"]

        for tool in tools:
            lines.append(f"- {tool}")

        return "\n".join(lines)

    def _format_skills_section(self, skills_content: str, skill_names: list[str]) -> str:
        """Format skills section for Copilot instructions.

        Args:
            skills_content: Raw skills content from component
            skill_names: List of skill names for reference

        Returns:
            Formatted skills section as markdown
        """
        lines = ["## Skills\n"]
        lines.append(skills_content.strip())
        return "\n".join(lines)

    def _format_workflows_section(self, workflow_content: str) -> str:
        """Format workflows section for Copilot instructions.

        Args:
            workflow_content: Raw workflow content from component

        Returns:
            Formatted workflows section as markdown
        """
        lines = ["## Workflows\n"]
        lines.append(workflow_content.strip())
        return "\n".join(lines)

    def _format_subagents_section(self, subagent_names: list[str]) -> str:
        """Format subagents section for Copilot instructions.

        Args:
            subagent_names: List of subagent names

        Returns:
            Formatted subagents section as markdown
        """
        lines = ["## Subagents\n"]
        lines.append("You may delegate to specialized agents:\n")

        for subagent in subagent_names:
            # Format subagent name nicely (e.g., "code-test" -> "Code Test")
            display_name = " ".join(word.capitalize() for word in subagent.split("-"))
            lines.append(f"### Subagent: {subagent}")
            lines.append(f"Specializes in {subagent.replace('-', ' ')} tasks.\n")

        return "\n".join(lines)

    def _compose_yaml_markdown(self, frontmatter: dict[str, Any], markdown_content: str) -> str:
        """Compose YAML frontmatter and markdown content.

        The instructions field in the YAML frontmatter contains the full
        instructions text. The markdown sections follow after the frontmatter.

        Args:
            frontmatter: Dictionary of YAML frontmatter fields
            markdown_content: Markdown content string

        Returns:
            Complete file content with YAML frontmatter and markdown
        """
        yaml_lines = ["---"]

        # Add applyTo field
        if "applyTo" in frontmatter:
            yaml_lines.append("applyTo:")
            for apply_to_item in frontmatter["applyTo"]:
                for key, value in apply_to_item.items():
                    if isinstance(value, list):
                        if not value:  # Empty list
                            yaml_lines.append(f"  - {key}: []")
                        else:
                            yaml_lines.append(f"  - {key}:")
                            for item in value:
                                yaml_lines.append(f"      - {item}")
                    else:
                        yaml_lines.append(f"  - {key}: {value}")

        yaml_lines.append("---")
        yaml_frontmatter = "\n".join(yaml_lines)

        return f"{yaml_frontmatter}\n\n{markdown_content}"
