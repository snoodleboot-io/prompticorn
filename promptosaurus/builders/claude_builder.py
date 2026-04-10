"""ClaudeBuilder for generating Claude Messages API JSON output.

This module implements the ClaudeBuilder class that translates Agent IR models
into JSON output compatible with Claude's Messages API format.
"""

import json
from pathlib import Path
from typing import Any, Optional

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.ir.loaders import CoreFilesLoader
from promptosaurus.ir.models import Agent


class ClaudeBuilder(AbstractBuilder):
    """Builder for Claude Messages API JSON output.

    Generates JSON dictionary with system prompt, tools, and instructions
    suitable for use with Claude's Messages API.

    Output Format:
        {
          "system": "You are an expert software engineer...",
          "tools": [
            {
              "name": "read",
              "description": "Read files and directories",
              "input_schema": {
                "type": "object",
                "properties": {
                  "filePath": {"type": "string"}
                }
              }
            }
          ],
          "instructions": "Follow these principles:\n- Read code before writing\n- Match existing patterns"
        }
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize ClaudeBuilder.

        Args:
            agents_dir: Base directory for agent configurations (default: 'agents')
        """
        self.agents_dir = agents_dir
        self.core_loader = CoreFilesLoader()

    def build(
        self, agent: Agent, options: BuildOptions, config: Optional[dict] = None
    ) -> dict[str, Any]:
        """Build Claude Messages API JSON output from an Agent IR model.

        Includes core system, conventions, and language-specific conventions if
        language is specified in config.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options
            config: Optional configuration dict with 'spec' key containing language info

        Returns:
            Dictionary with system, tools, and instructions keys
            All values are JSON-serializable

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
        base_prompt = agent.system_prompt

        # Build system prompt with core files if language is available
        system_prompt = self._build_system_prompt_with_core(base_prompt, config)

        # Build tools list with schemas
        tools_list = self._build_tools_list(agent.tools) if options.include_tools else []

        # Build instructions string from all sections
        instructions = self._build_instructions(
            agent,
            options,
        )

        # Return JSON-serializable dict
        output: dict[str, Any] = {
            "system": system_prompt,
            "tools": tools_list,
            "instructions": instructions,
        }

        # Verify JSON serializability
        try:
            json.dumps(output)
        except (TypeError, ValueError) as e:
            raise BuilderValidationError(
                errors=[f"Output is not JSON serializable: {str(e)}"],
                message=f"Invalid output from Claude builder: {str(e)}",
            )

        return output

    def validate(self, agent: Agent) -> list[str]:
        """Validate an Agent IR model for Claude.

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
            Description of Claude format
        """
        return "Claude Messages API JSON (dict)"

    def get_tool_name(self) -> str:
        """Get the tool name.

        Returns:
            "claude"
        """
        return "claude"

    def _build_system_prompt(self, prompt: str) -> str:
        """Get system prompt string from component bundle.

        Args:
            prompt: System prompt from component bundle

        Returns:
            System prompt as string (stripped)
        """
        return prompt.strip()

    def _build_system_prompt_with_core(self, prompt: str, config: Optional[dict] = None) -> str:
        """Build system prompt with core files included if language is available.

        Args:
            prompt: System prompt from agent
            config: Optional configuration dict with 'spec' key containing language info

        Returns:
            System prompt with core files prepended, or original prompt if no language
        """
        sections = []

        # Load and include core files if language is available
        if config:
            language = config.get("spec", {}).get("language")
            if language:
                core_files = self.core_loader.get_core_files(language, config)
                # Order: system, conventions, session, language-specific
                for key in ["system", "conventions", "session"]:
                    if key in core_files:
                        sections.append(core_files[key])

                # Add language conventions if available
                lang_key = f"conventions_{language}"
                if lang_key in core_files:
                    sections.append(core_files[lang_key])

        # Add the agent's system prompt
        sections.append(prompt.strip())

        # Join all sections with double newlines
        return "\n\n".join(sections)

    def _build_tools_list(self, tool_names: list[str]) -> list[dict[str, Any]]:
        """Build tools list with JSON schemas.

        Each tool gets a name, description, and input_schema (JSON schema).

        Args:
            tool_names: List of tool names from agent

        Returns:
            List of tool dictionaries with schemas
        """
        tools = []

        for tool_name in tool_names:
            tool_dict = self._build_tool_schema(tool_name)
            tools.append(tool_dict)

        return tools

    def _build_tool_schema(self, tool_name: str) -> dict[str, Any]:
        """Build JSON schema for a single tool.

        Creates a basic schema structure with name, description, and input_schema.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool metadata and schema
        """
        # Build basic tool schema
        tool: dict[str, Any] = {
            "name": tool_name,
            "description": f"Tool: {tool_name}",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param": {"type": "string", "description": "Parameter for the tool"}
                },
                "required": ["param"],
            },
        }

        return tool

    def _build_instructions(
        self,
        agent: Agent,
        options: BuildOptions,
    ) -> str:
        """Build instructions string from all sections.

        Concatenates skills, workflows, subagents, and rules into prose text.

        Args:
            agent: Agent IR model
            options: Build configuration options

        Returns:
            Instructions as concatenated prose text
        """
        sections = []

        # Add skills section if requested
        if options.include_skills and agent.skills:
            sections.append(self._format_skills_section(agent.skills))

        # Add workflows section if requested
        if options.include_workflows and agent.workflows:
            sections.append(self._format_workflows_section(agent.workflows, options.variant))

        # Add subagents section if requested
        if options.include_subagents and agent.subagents:
            sections.append(self._format_subagents_section(agent.subagents))

        # Join all sections with double newlines
        instructions = "\n\n".join(sections)

        return instructions.strip()

    def _format_skills_section(self, skill_names: list[str]) -> str:
        """Format skills section as prose.

        Args:
            skill_names: List of skill names from agent

        Returns:
            Formatted skills section as prose
        """
        lines = ["Skills:", ""]

        # Add each skill with invocation info
        for skill in skill_names:
            skill_key = skill.lower().replace(" ", "_").replace("-", "_")
            lines.append(f"- {skill}: Invoke by use_skill {skill_key}")

        return "\n".join(lines)

    def _format_workflows_section(self, workflow_names: list[str], variant: str = "minimal") -> str:
        """Format workflows section as prose with full content.

        Args:
            workflow_names: List of workflow names from agent
            variant: Variant to load (minimal/verbose)

        Returns:
            Formatted workflows section with full content
        """
        from promptosaurus.builders.workflow_loader import WorkflowLoader

        lines = ["Workflows:", ""]

        # Load and embed each workflow with full content
        for workflow in workflow_names:
            workflow_content = WorkflowLoader.load_workflow(workflow, variant)

            if workflow_content:
                # Format workflow content (strip frontmatter)
                formatted_content = WorkflowLoader.format_workflow_content(
                    workflow_content, include_frontmatter=False
                )

                lines.append(f"**{workflow}:**")
                lines.append("")
                lines.append(formatted_content)
                lines.append("")
            else:
                # Fallback to just name if content not found
                lines.append(f"- {workflow}")

        return "\n".join(lines)

    def _format_subagents_section(self, subagent_names: list[str]) -> str:
        """Format subagents section as prose.

        Args:
            subagent_names: List of subagent names

        Returns:
            Formatted subagents section
        """
        lines = ["Subagents:", ""]

        for subagent in subagent_names:
            lines.append(f"- {subagent}: Specialized agent for {subagent} tasks")

        return "\n".join(lines)

    def _format_rules_section(self, rules_content: str) -> str:
        """Format rules section as prose.

        Args:
            rules_content: Raw rules content from component

        Returns:
            Formatted rules section
        """
        lines = ["Rules:", ""]
        lines.append(rules_content.strip())
        return "\n".join(lines)
