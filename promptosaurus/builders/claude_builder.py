"""ClaudeBuilder for generating Claude Markdown artifacts.

This module implements the ClaudeBuilder class that translates Agent IR models
into Markdown files for the .claude/ directory structure.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from promptosaurus.builders.base import Builder, BuildOptions
from promptosaurus.builders.errors import BuilderValidationError
from promptosaurus.builders.naming_utils import (
    agent_to_file_name,
    skill_to_directory_name,
    subagent_to_file_name,
    workflow_to_file_name,
)
from promptosaurus.builders.workflow_loader import WorkflowLoader
from promptosaurus.ir.loaders import CoreFilesLoader
from promptosaurus.ir.models import Agent


class ClaudeBuilder(Builder):
    """Builder for Claude Markdown artifacts.

    Generates Markdown files in .claude/ directory structure:
    - .claude/agents/{agent-name}.md
    - .claude/subagents/{subagent-name}.md
    - .claude/workflows/{workflow-name}.md
    - CLAUDE.md (routing file)

    Note: Convention files are generated separately by `generate_all_conventions()`
    called from `PromptBuilder`, not by `ClaudeBuilder.build()`.

    Output Format:
        Markdown files with Jinja2 template rendering
    """

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize ClaudeBuilder.

        Args:
            agents_dir: Base directory for agent configurations (default: 'agents')
        """
        self.agents_dir = agents_dir
        self.core_loader = CoreFilesLoader()

        # Setup Jinja2 template environment
        template_dir = Path(__file__).parent.parent / "templates" / "claude"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def build(
        self, agent: Agent, options: BuildOptions, config: dict | None = None
    ) -> dict[str, str]:
        """Build Claude Markdown artifacts from an Agent IR model.

        Args:
            agent: The Agent IR model to build from
            options: Build configuration options
            config: Optional configuration dict with 'spec' key containing language info

        Returns:
            Dictionary mapping file paths to Markdown content
            Example:
            {
                ".claude/agents/code-agent.md": "# Code Agent\n...",
                ".claude/subagents/code-reviewer.md": "# Code Reviewer\n...",
                ".claude/workflows/feature-implementation.md": "# Feature Implementation\n..."
            }

        Raises:
            BuilderValidationError: If the agent model is invalid
        """
        # Validate the agent
        errors = self.validate(agent)
        if errors:
            raise BuilderValidationError(
                errors=errors, message=f"Invalid agent '{agent.name}': {'; '.join(errors)}"
            )

        # Build output dictionary with all artifact files
        output: dict[str, str] = {}

        # 1. Render agent file
        agent_file_name = agent_to_file_name(agent.name)
        agent_content = self._render_agent_file(agent, options, config)
        output[f".claude/agents/{agent_file_name}.md"] = agent_content

        # 2. Render subagent files (if any)
        if options.include_subagents and agent.subagents:
            for subagent_name in agent.subagents:
                subagent_file_name = subagent_to_file_name(subagent_name)
                subagent_content = self._render_subagent_file(subagent_name, agent.name, options)
                output[f".claude/subagents/{subagent_file_name}.md"] = subagent_content

        # 3. Render workflow files (if any)
        if options.include_workflows and agent.workflows:
            for workflow_name in agent.workflows:
                workflow_file_name = workflow_to_file_name(workflow_name)
                workflow_content = self._render_workflow_file(workflow_name, options)
                output[f".claude/workflows/{workflow_file_name}.md"] = workflow_content

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
        return "Claude Markdown artifacts (dict[str, str])"

    def get_tool_name(self) -> str:
        """Get the tool name.

        Returns:
            "claude"
        """
        return "claude"

    def _render_agent_file(
        self, agent: Agent, options: BuildOptions, config: dict | None = None
    ) -> str:
        """Render agent Markdown file from template.

        Args:
            agent: Agent IR model
            options: Build options
            config: Optional configuration

        Returns:
            Rendered Markdown content
        """
        template = self.jinja_env.get_template("agent.md.j2")

        prepared_skills = self._prepare_skills_data(agent.skills) if agent.skills else []

        # Prepare template data
        template_data = {
            "agent": {
                "name": agent.name.title(),
                "description": agent.description,
                "system_prompt": agent.system_prompt,
            },
            "when_to_use": self._generate_when_to_use(agent),
            "workflow": agent.workflows[0] if agent.workflows else None,
            "workflow_steps": self._extract_workflow_steps(agent.workflows[0], options.variant)
            if agent.workflows
            else [],
            "subagents": self._prepare_subagents_data(agent.subagents) if agent.subagents else [],
            "skills": prepared_skills,
            "notes": self._generate_agent_notes(agent),
        }

        return template.render(**template_data)

    def _render_subagent_file(
        self, subagent_name: str, parent_agent: str, options: BuildOptions
    ) -> str:
        """Render subagent Markdown file from template.

        Args:
            subagent_name: Name of the subagent
            parent_agent: Name of the parent agent
            options: Build options

        Returns:
            Rendered Markdown content
        """
        # Load actual subagent content
        subagent_content = self._load_subagent_content(parent_agent, subagent_name, options.variant)

        if subagent_content:
            # Return the actual subagent content directly (it's already markdown)
            return subagent_content

        # Fallback to template if content not found
        template = self.jinja_env.get_template("subagent.md.j2")

        template_data = {
            "subagent": {
                "name": subagent_name.replace("-", " ").title(),
                "description": f"Specialized agent for {subagent_name} tasks",
                "instructions": f"Provide focused assistance for {subagent_name}.",
                "detailed_instructions": "Follow the parent agent's context and requirements.",
            },
            "parent_agent": parent_agent,
            "notes": None,
        }

        return template.render(**template_data)

    def _render_workflow_file(self, workflow_name: str, options: BuildOptions) -> str:
        """Render workflow Markdown file from template.

        Args:
            workflow_name: Name of the workflow
            options: Build options

        Returns:
            Rendered Markdown content
        """
        # Load actual workflow content
        workflow_content = WorkflowLoader.load_workflow(workflow_name, options.variant)

        if workflow_content:
            # Return the actual workflow content (already formatted)
            return WorkflowLoader.format_workflow_content(
                workflow_content, include_frontmatter=False
            )

        # Fallback to template if workflow not found
        template = self.jinja_env.get_template("workflow.md.j2")

        template_data = {
            "workflow": {
                "name": workflow_name.replace("-", " ").title(),
                "description": f"Execute {workflow_name} workflow",
                "duration": "Variable",
                "prerequisites": "None",
                "overview": f"This workflow guides you through {workflow_name}.",
                "steps": [
                    {
                        "name": "Example Step",
                        "description": "Perform the task",
                        "actions": ["Action 1", "Action 2"],
                        "resources": [],
                    }
                ],
                "completion_criteria": [
                    "Task completed successfully",
                    "All tests passing",
                ],
            },
            "notes": None,
        }

        return template.render(**template_data)

    def _load_subagent_content(
        self, parent_agent: str, subagent_name: str, variant: str = "minimal"
    ) -> str | None:
        """Load subagent content from agents directory.

        Args:
            parent_agent: Name of the parent agent
            subagent_name: Name of the subagent
            variant: Variant (minimal/verbose)

        Returns:
            Subagent content as string, or None if not found
        """
        # Subagents are stored in promptosaurus/agents/{agent}/subagents/{subagent}/{variant}/prompt.md
        agents_dir = Path(__file__).parent.parent / "agents"

        # Try exact path match first
        subagent_path = (
            agents_dir / parent_agent / "subagents" / subagent_name / variant / "prompt.md"
        )

        if not subagent_path.exists():
            # Try other variant as fallback
            other_variant = "verbose" if variant == "minimal" else "minimal"
            subagent_path = (
                agents_dir
                / parent_agent
                / "subagents"
                / subagent_name
                / other_variant
                / "prompt.md"
            )

        if subagent_path.exists():
            return subagent_path.read_text(encoding="utf-8")

        return None

    def _generate_when_to_use(self, agent: Agent) -> str:
        """Generate 'when to use' description for agent.

        Args:
            agent: Agent IR model

        Returns:
            Description of when to use this agent
        """
        # Map agent names to usage scenarios
        scenarios = {
            "code": "Implementing features, fixing bugs, refactoring existing code",
            "architect": "Designing system architecture, planning technical solutions",
            "debug": "Diagnosing issues, analyzing errors, fixing bugs",
            "review": "Reviewing code quality, checking for issues, auditing changes",
            "test": "Writing tests, improving coverage, testing strategies",
            "refactor": "Improving code structure, optimizing design patterns",
            "performance": "Optimizing performance, identifying bottlenecks",
            "frontend": "Building user interfaces, accessibility, responsive design",
            "backend": "Designing APIs, microservices, backend systems",
            "orchestrator": "Coordinating multi-step workflows, managing complex tasks",
            "plan": "Developing PRDs, working with architects on ARDs",
            "explain": "Code walkthroughs, documentation, onboarding",
            "ask": "Answering questions, providing explanations",
            "enforcement": "Reviewing code against coding standards",
            "migration": "Handling dependency upgrades, framework migrations",
        }
        return scenarios.get(agent.name, f"Working on {agent.name} tasks")

    def _extract_workflow_steps(self, workflow_name: str, variant: str = "minimal") -> list[str]:
        """Extract high-level workflow steps for display in agent file.

        Args:
            workflow_name: Name of the workflow
            variant: Workflow variant (minimal/verbose)

        Returns:
            List of workflow step descriptions
        """
        # Load actual workflow to extract steps
        workflow_content = WorkflowLoader.load_workflow(workflow_name, variant)

        if workflow_content:
            # Extract headers (## Step X: ...) from workflow
            steps = []
            for line in workflow_content.split("\n"):
                if line.startswith("## Step ") or line.startswith("## "):
                    # Extract step description
                    step_text = line.lstrip("#").strip()
                    if step_text and not step_text.startswith("---"):
                        # Remove "Step X:" prefix if present
                        if ":" in step_text:
                            step_text = step_text.split(":", 1)[1].strip()
                        steps.append(step_text)

            if steps:
                return steps[:5]  # Return first 5 steps

        # Default fallback steps
        return [
            "Understand requirements",
            "Plan implementation",
            "Execute incrementally",
            "Test as you go",
            "Review and complete",
        ]

    def _prepare_subagents_data(self, subagent_names: list[str]) -> list[dict[str, str]]:
        """Prepare subagent data for template rendering.

        Args:
            subagent_names: List of subagent names

        Returns:
            List of subagent dictionaries with metadata
        """
        subagents = []
        for name in subagent_names:
            file_name = subagent_to_file_name(name)
            # Clean up the name for display
            display_name = name.replace("-", " ").replace("/", " - ").title()
            subagents.append(
                {
                    "name": display_name,
                    "purpose": f"Specialized for {name.replace('/', ' ')} tasks",
                    "file_name": file_name,
                    "when_to_use": f"When you need focused {name.replace('/', ' ')} assistance",
                }
            )
        return subagents

    def _prepare_skills_data(self, skill_names: list[str]) -> list[dict[str, str]]:
        """Prepare skills data for template rendering.

        Args:
            skill_names: List of skill names

        Returns:
            List of skill dictionaries with metadata
        """
        skills = []
        for name in skill_names:
            dir_name = skill_to_directory_name(name)
            skills.append(
                {
                    "name": name.replace("-", " ").title(),
                    "purpose": f"Capability for {name}",
                    "directory": dir_name,
                    "when_to_use": f"When workflow requires {name}",
                }
            )
        return skills

    def _generate_agent_notes(self, agent: Agent) -> str | None:
        """Generate agent-specific notes.

        Args:
            agent: Agent IR model

        Returns:
            Notes string or None
        """
        # Agent-specific notes
        notes_map = {
            "code": "Always run tests before marking work complete. Follow project's feature branch naming convention.",
            "test": "Focus on coverage first, then edge cases. Use the project's test framework.",
            "debug": "Start with rubber duck debugging for complex issues. Check logs before diving deep.",
        }
        return notes_map.get(agent.name)
