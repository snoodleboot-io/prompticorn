"""ClineBuilder for generating Cline AI rules files.

This module implements the ClineBuilder class that translates Agent IR models
into Cline AI configuration files (.clinerules) with markdown formatting.
"""

from pathlib import Path

from promptosaurus.builders.base import Builder, BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.loaders import CoreFilesLoader
from promptosaurus.ir.models import Agent


class ClineBuilder(Builder):
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
        self.core_loader = CoreFilesLoader()

    def build(self, agent: Agent, options: BuildOptions, config: dict | None = None) -> str:
        """Build a Cline AI configuration file.

        Includes core system, conventions, and language-specific conventions files
        if language is specified in config.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options
            config: Optional configuration dict with 'spec' key containing language info

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
        sections.append(self._format_system_prompt_prose(system_prompt))
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

    def _format_workflows_section(self, workflow_names: list[str], variant: str = "minimal") -> str:
        """Format workflows section with step-by-step instructions.

        Args:
            workflow_names: List of workflow names from agent
            variant: Variant to load (minimal/verbose)

        Returns:
            Formatted markdown section with full workflow content
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
