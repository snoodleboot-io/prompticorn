"""Component composer for assembling components into builder output formats.

This module provides utilities for composing loaded components into
structured output formats (markdown, JSON, YAML+markdown).
"""

from typing import Any

from promptosaurus.builders.component_selector import ComponentBundle
from promptosaurus.ir.models import Agent


class ComponentComposer:
    """Compose components into formatted output for builders."""

    @staticmethod
    def compose_markdown(
        bundle: ComponentBundle,
        agent: Agent,
        include_sections: list[str] | None = None,
    ) -> str:
        """Compose components into markdown format.

        Default order:
        1. System Prompt
        2. Tools (from agent.tools)
        3. Skills (from bundle.skills)
        4. Workflows (from bundle.workflow)
        5. Subagents (from agent.subagents)

        Args:
            bundle: ComponentBundle with loaded content
            agent: Agent IR model for context
            include_sections: List of sections to include (default: all).
                             Valid values: 'prompt', 'tools', 'skills',
                             'workflows', 'subagents'

        Returns:
            Formatted markdown string
        """
        if include_sections is None:
            include_sections = [
                "prompt",
                "tools",
                "skills",
                "workflows",
                "subagents",
            ]

        sections: list[str] = []

        # 1. System Prompt (always included if requested)
        if "prompt" in include_sections:
            sections.append("# System Prompt\n")
            sections.append(bundle.prompt)
            sections.append("")

        # 2. Tools
        if "tools" in include_sections and agent.tools:
            sections.append("# Tools\n")
            sections.append(ComponentComposer._format_tools_section(agent.tools))
            sections.append("")

        # 3. Skills
        if "skills" in include_sections and bundle.skills:
            sections.append("# Skills\n")
            sections.append(ComponentComposer._format_skills_section(bundle.skills))
            sections.append("")

        # 4. Workflows
        if "workflows" in include_sections and bundle.workflow:
            sections.append("# Workflows\n")
            sections.append(ComponentComposer._format_workflows_section(bundle.workflow))
            sections.append("")

        # 5. Subagents
        if "subagents" in include_sections and agent.subagents:
            sections.append("# Subagents\n")
            sections.append(ComponentComposer._format_subagents_section(agent.subagents))
            sections.append("")

        return "\n".join(sections).strip()

    @staticmethod
    def compose_yaml_markdown(
        bundle: ComponentBundle,
        agent: Agent,
        frontmatter: dict[str, Any] | None = None,
    ) -> str:
        """Compose into YAML frontmatter + markdown format.

        Format:
        ---
        yaml: content
        ---
        # Markdown content

        Args:
            bundle: ComponentBundle with loaded content
            agent: Agent IR model for context
            frontmatter: Dictionary of YAML frontmatter data (optional).
                        Default includes agent name and variant.

        Returns:
            Formatted string with YAML frontmatter and markdown content
        """
        if frontmatter is None:
            frontmatter = {}

        # Add default frontmatter fields if not present
        if "name" not in frontmatter:
            frontmatter["name"] = agent.name
        if "variant" not in frontmatter:
            frontmatter["variant"] = bundle.variant.value
        if "fallback_used" not in frontmatter:
            frontmatter["fallback_used"] = bundle.fallback_used

        # Build YAML frontmatter
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
            elif isinstance(value, list):
                yaml_lines.append(f"{key}:")
                for item in value:
                    yaml_lines.append(f"  - {item}")
            else:
                yaml_lines.append(f"{key}: {value}")

        yaml_lines.append("---")
        yaml_frontmatter = "\n".join(yaml_lines)

        # Get markdown content
        markdown_content = ComponentComposer.compose_markdown(bundle, agent)

        return f"{yaml_frontmatter}\n\n{markdown_content}"

    @staticmethod
    def compose_json(
        bundle: ComponentBundle,
        agent: Agent,
    ) -> dict[str, Any]:
        """Compose into JSON format for APIs.

        Args:
            bundle: ComponentBundle with loaded content
            agent: Agent IR model for context

        Returns:
            Dictionary with structured component data
        """
        return {
            "agent": {
                "name": agent.name,
                "description": agent.description,
                "tools": agent.tools,
                "skills": agent.skills,
                "workflows": agent.workflows,
                "subagents": agent.subagents,
            },
            "components": {
                "variant": bundle.variant.value,
                "fallback_used": bundle.fallback_used,
                "prompt": bundle.prompt,
                "skills": bundle.skills,
                "workflow": bundle.workflow,
            },
        }

    @staticmethod
    def _format_tools_section(tools: list[str]) -> str:
        """Format tools section as markdown.

        Args:
            tools: List of tool names

        Returns:
            Formatted markdown string
        """
        if not tools:
            return ""

        lines = []
        for tool in tools:
            lines.append(f"- {tool}")

        return "\n".join(lines)

    @staticmethod
    def _format_skills_section(skills_content: str) -> str:
        """Format skills section.

        Args:
            skills_content: Raw skills content

        Returns:
            Formatted markdown string
        """
        return skills_content.strip()

    @staticmethod
    def _format_workflows_section(workflow_content: str) -> str:
        """Format workflows section.

        Args:
            workflow_content: Raw workflow content

        Returns:
            Formatted markdown string
        """
        return workflow_content.strip()

    @staticmethod
    def _format_subagents_section(subagent_names: list[str]) -> str:
        """Format subagents section as markdown list.

        Args:
            subagent_names: List of subagent names

        Returns:
            Formatted markdown string
        """
        if not subagent_names:
            return ""

        lines = []
        for subagent in subagent_names:
            lines.append(f"- {subagent}")

        return "\n".join(lines)
