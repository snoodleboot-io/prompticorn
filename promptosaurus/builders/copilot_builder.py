"""CopilotBuilder for generating GitHub Copilot instructions files.

This module implements the CopilotBuilder class that translates Agent IR models
into GitHub Copilot instructions files with YAML frontmatter and markdown sections.
"""

from pathlib import Path
from typing import Any, Optional

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.loaders import CoreFilesLoader
from promptosaurus.ir.models import Agent


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
        self.core_loader = CoreFilesLoader()

    def build(self, agent: Agent, options: BuildOptions, config: Optional[dict] = None) -> str:
        """Build a GitHub Copilot instructions file.

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

        # Prepare YAML frontmatter with applyTo
        frontmatter = self._build_frontmatter(agent)

        # Compose markdown output
        markdown_sections = []

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
                        markdown_sections.append(f"## {key.capitalize()}\n")
                        markdown_sections.append(core_files[key])
                        markdown_sections.append("")

                # Add language conventions if available
                lang_key = f"conventions_{language}"
                if lang_key in core_files:
                    markdown_sections.append(f"## {language.capitalize()} Conventions\n")
                    markdown_sections.append(core_files[lang_key])
                    markdown_sections.append("")

        # 1. Header with agent name
        markdown_sections.append(self._format_header(agent))
        markdown_sections.append("")

        # 2. System prompt as prose - use variant content or agent model
        markdown_sections.append(system_prompt)
        markdown_sections.append("")

        # 3. Tools (if requested)
        if options.include_tools and agent.tools:
            markdown_sections.append(self._format_tools_section(agent.tools))
            markdown_sections.append("")

        # 4. Skills (if requested)
        if options.include_skills and agent.skills:
            markdown_sections.append(self._format_skills_section(agent.skills))
            markdown_sections.append("")

        # 5. Workflows (if requested)
        if options.include_workflows and agent.workflows:
            markdown_sections.append(
                self._format_workflows_section(agent.workflows, options.variant)
            )
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

    def _format_skills_section(self, skill_names: list[str]) -> str:
        """Format skills section for Copilot instructions.

        Args:
            skill_names: List of skill names from agent

        Returns:
            Formatted skills section as markdown
        """
        lines = ["## Skills\n"]

        for skill in skill_names:
            lines.append(f"- {skill}")

        return "\n".join(lines)

    def _format_workflows_section(self, workflow_names: list[str], variant: str = "minimal") -> str:
        """Format workflows section for Copilot instructions.

        Args:
            workflow_names: List of workflow names from agent
            variant: Variant to load (minimal/verbose)

        Returns:
            Formatted workflows section with full content
        """
        from promptosaurus.builders.workflow_loader import WorkflowLoader

        lines = ["## Workflows\n"]

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
        """Format subagents section for Copilot instructions.

        Args:
            subagent_names: List of subagent names

        Returns:
            Formatted subagents section as markdown
        """
        lines = ["## Subagents\n"]
        lines.append("You may delegate to specialized agents:\n")

        for subagent in subagent_names:
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
