"""ClineBuilder for generating Cline IDE configuration files.

This module implements the ClineBuilder class that translates Agent IR models
into Cline IDE `.clinerules` files with skill activation via `use_skill` pattern.

Cline format:
- Single concatenated markdown file (`.clinerules`)
- YAML-free (pure markdown)
- Skills section includes activation instructions
- Uses `use_skill {skill_name}` invocation pattern
- Subagent delegation with skill context
"""

from pathlib import Path
from typing import Any

from src.builders.base import AbstractBuilder, BuildOptions
from src.builders.component_selector import ComponentSelector, Variant
from src.builders.errors import BuilderValidationError
from src.ir.models import Agent


class ClineBuilder(AbstractBuilder):
    """Builder for Cline IDE configurations.

    Generates `.clinerules` files (single concatenated markdown) with
    YAML-free format and Cline-specific `use_skill` activation pattern.

    Output Format:
        # System Prompt
        [System prompt content]

        # Tools
        - tool1
        - tool2

        # Skills
        The following skills are available...
        ## Skill: {skill_name}
        **When to use:** ...
        **How to invoke:** use_skill {skill_name}

        # Workflows
        [Workflows content]

        # Subagents
        You may delegate to these specialists...
        ### Subagent: {subagent_name}
        ...
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize ClineBuilder.

        Args:
            agents_dir: Base directory for agent configurations (default: 'agents')
        """
        self.agents_dir = agents_dir
        self.selector = ComponentSelector(agents_dir=agents_dir)

    def build(self, agent: Agent, options: BuildOptions) -> str:
        """Build a Cline configuration file.

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

        # Select variant (minimal or verbose)
        variant = Variant.MINIMAL if options.variant == "minimal" else Variant.VERBOSE

        # Load components with variant selection
        bundle = self.selector.select(agent, variant=variant)

        # Compose markdown sections (no YAML frontmatter for Cline)
        markdown_sections = []

        # 1. System Prompt
        markdown_sections.append("# System Prompt\n")
        markdown_sections.append(bundle.prompt)
        markdown_sections.append("")

        # 2. Tools (if requested)
        if options.include_tools and agent.tools:
            markdown_sections.append("# Tools\n")
            markdown_sections.append(self._format_tools(agent.tools))
            markdown_sections.append("")

        # 3. Skills (if requested) - with activation instructions
        if options.include_skills and bundle.skills:
            markdown_sections.append("# Skills\n")
            markdown_sections.append(self._format_skills_with_activation(bundle.skills, agent.skills))
            markdown_sections.append("")

        # 4. Workflows (if requested)
        if options.include_workflows and bundle.workflow:
            markdown_sections.append("# Workflows\n")
            markdown_sections.append(self._format_workflows(bundle.workflow))
            markdown_sections.append("")

        # 5. Subagents (if requested) - with skill context
        if options.include_subagents and agent.subagents:
            markdown_sections.append("# Subagents\n")
            markdown_sections.append(self._format_subagents_with_skills(agent.subagents, agent.skills))
            markdown_sections.append("")

        markdown_content = "\n".join(markdown_sections).strip()

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
        return "Cline IDE Rules File (.clinerules - Markdown)"

    def get_tool_name(self) -> str:
        """Get the tool name.

        Returns:
            "cline"
        """
        return "cline"

    def _format_tools(self, tools: list[str]) -> str:
        """Format tools list for display.

        Args:
            tools: List of tool names

        Returns:
            Formatted tools section
        """
        if not tools:
            return ""

        tool_lines = [f"- {tool}" for tool in tools]
        return "\n".join(tool_lines)

    def _format_workflows(self, workflow_content: str) -> str:
        """Format workflows section.

        Args:
            workflow_content: Raw workflow content from component

        Returns:
            Formatted workflow content (stripped whitespace)
        """
        return workflow_content.strip()

    def _format_skills_with_activation(self, skills_content: str, agent_skills: list[str]) -> str:
        """Format skills section with activation instructions.

        Generates skill descriptions with `use_skill` invocation syntax and
        information about when and why to use each skill.

        Args:
            skills_content: Raw skills content from component file
            agent_skills: List of skill names for this agent

        Returns:
            Formatted skills section with activation instructions
        """
        if not skills_content.strip():
            return ""

        sections = []

        # Add header explaining how to use skills
        sections.append("The following skills are available. Activate them explicitly via `use_skill` tool:\n")

        # Generate activation instructions for each skill
        for skill_name in agent_skills:
            activation_instructions = self._build_skill_activation_instructions(skill_name)
            sections.append(activation_instructions)
            sections.append("")

        # Add the raw skills content
        if skills_content.strip():
            sections.append(skills_content.strip())

        return "\n".join(sections)

    def _build_skill_activation_instructions(self, skill_name: str) -> str:
        """Generate activation instructions for a single skill.

        Creates formatted instructions including:
        - Skill name and description
        - When/why to use this skill
        - Invocation syntax: use_skill {skill_name}
        - Location reference

        Args:
            skill_name: Name of the skill to generate instructions for

        Returns:
            Formatted activation instructions for the skill
        """
        # Normalize skill name for display
        display_name = skill_name.replace("-", " ").replace("_", " ").title()

        instructions = f"""## Skill: {display_name}

**Activation:** `use_skill {skill_name}`
**Location:** `.kilo/skills/{skill_name}.md`

When to use: This skill provides specialized functionality for {display_name.lower()}.
Invoke it when you need to {display_name.lower()} or delegate to a specialist in this area.

How to invoke:
- Direct: Call the `use_skill` tool with skill name: `use_skill {skill_name}`
- Delegation: Request to delegate to the appropriate specialist for {skill_name}"""

        return instructions.strip()

    def _format_subagents_with_skills(self, subagent_names: list[str], agent_skills: list[str]) -> str:
        """Format subagents section with skill context.

        Includes information about which skills each subagent can access
        and hints for delegation using skill activation.

        Args:
            subagent_names: List of subagent names
            agent_skills: List of skill names available to the parent agent

        Returns:
            Formatted subagents section with delegation instructions
        """
        if not subagent_names:
            return ""

        sections = []

        # Add header
        sections.append("You may delegate to these specialists:\n")

        # Format each subagent with skill context
        for subagent_name in subagent_names:
            # Generate skill context for this subagent
            subagent_skills = self._get_subagent_skills(subagent_name, agent_skills)

            subagent_section = self._format_single_subagent_with_skills(
                subagent_name, subagent_skills
            )
            sections.append(subagent_section)
            sections.append("")

        return "\n".join(sections)

    def _get_subagent_skills(self, subagent_name: str, agent_skills: list[str]) -> list[str]:
        """Determine which skills are relevant for a subagent.

        Uses subagent name to infer relevant skills.
        In a full implementation, this would query a skill registry.

        Args:
            subagent_name: Name of the subagent
            agent_skills: List of available skills

        Returns:
            List of relevant skill names for this subagent
        """
        # Map common subagent names to skill patterns
        subagent_skill_map = {
            "test": ["test-first-implementation"],
            "code": ["test-first-implementation"],
            "refactor": ["refactor-code-module"],
            "review": ["code-review-audit"],
            "architect": ["architecture-design"],
            "document": ["documentation-generation"],
        }

        # Check for exact match or partial match
        for key, skills in subagent_skill_map.items():
            if key.lower() in subagent_name.lower():
                return [s for s in skills if s in agent_skills]

        # If no match, return empty list
        return []

    def _format_single_subagent_with_skills(self, subagent_name: str, skills: list[str]) -> str:
        """Format a single subagent entry with skill context.

        Args:
            subagent_name: Name of the subagent
            skills: List of skills this subagent specializes in

        Returns:
            Formatted subagent entry
        """
        # Normalize name for display
        display_name = subagent_name.replace("-", " ").replace("_", " ").title()

        lines = [f"### Subagent: {display_name}"]

        # Add skill context
        if skills:
            skill_names = [s.replace("-", " ").title() for s in skills]
            lines.append(f"Specializes in: {', '.join(skill_names)}")

        # Add invocation instructions
        lines.append(f"\nInvoke by: `use_skill {subagent_name}` or request \"use {subagent_name} subagent\"")

        # Add skill activation hints for each skill
        if skills:
            lines.append("\nAvailable skills:")
            for skill in skills:
                lines.append(f"  - `use_skill {skill}`")

        return "\n".join(lines).strip()
