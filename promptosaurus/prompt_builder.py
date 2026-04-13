"""Builder wrapper to generate tool-specific configs from bundled IR agents."""

from pathlib import Path
from typing import Any, Optional

from promptosaurus.agent_registry.registry import Registry
from promptosaurus.builders.factory import BuilderFactory
from promptosaurus.builders.base import BuildOptions
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.ir.models.agent import Agent
from promptosaurus.ir.loaders.language_skill_mapping_loader import LanguageSkillMappingLoader
from promptosaurus.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader


class PromptBuilder:
    """Builder that uses bundled IR-format agents with Phase 2A builders.

    Supports language-based filtering of skills and workflows via the
    language_skill_mapping.yaml registry. Skills and workflows are filtered
    based on the project's language and the agent/subagent combination.
    """

    def __init__(self, tool_name: str):
        """Initialize builder for a specific tool.

        Args:
            tool_name: Tool name ('kilo', 'cline', 'claude', 'copilot', 'cursor')
        """
        self.tool_name = tool_name
        self.builder = BuilderFactory.get_builder(tool_name)

        # Load agents from bundled IR directory
        agents_dir = Path(__file__).parent / "agents"
        self.registry = Registry.from_discovery(agents_dir)

        # Initialize language skill mapping loader
        language_mapping_file = (
            Path(__file__).parent / "configurations" / "language_skill_mapping.yaml"
        )
        try:
            self.language_skill_loader = LanguageSkillMappingLoader(language_mapping_file)
        except FileNotFoundError:
            self.language_skill_loader = None

        # Initialize agent skill mapping loader (language-agnostic)
        agent_mapping_file = (
            Path(__file__).parent / "configurations" / "agent_skill_mapping.yaml"
        )
        try:
            self.agent_skill_loader = AgentSkillMappingLoader(agent_mapping_file)
        except FileNotFoundError:
            self.agent_skill_loader = None

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Build tool-specific outputs from bundled IR agents.

        Filters skills and workflows based on the project's language (if specified
        in config) using the language_skill_mapping.yaml registry.

        Args:
            output: Output directory path
            config: Project configuration with optional keys:
                - 'variant': 'minimal' or 'verbose' (default: 'minimal')
                - 'spec': dict with optional 'language' key
            dry_run: If True, don't write files (preview only)

        Returns:
            List of action strings describing what was created
        """
        actions = []

        # Get variant and language from config
        variant = config.get("variant", "minimal") if config else "minimal"
        language = config.get("spec", {}).get("language") if config else None

        # Get all agents from registry
        all_agents = self.registry.get_all_agents()

        # Collect all unique skills from all agents (including subagents)
        all_skills_written = set()

        # For Kilo, write core convention files to .kilo/rules/ before building agents
        rules_files_written = []
        if isinstance(self.builder, KiloBuilder) and not dry_run:
            try:
                rules_files_written = self.builder.write_rules_files(output, config)
                actions.extend([f"✓ {f}" for f in rules_files_written])
            except Exception as e:
                actions.append(f"✗ Failed to write rules files: {e}")

        # Build each top-level agent (skip subagents, they're included in parent)
        for agent_name, agent in all_agents.items():
            if "/" in agent_name:  # Skip subagents for agent file generation
                continue

            try:
                # Filter agent for language before building
                filtered_agent = self._filter_agent_for_language(agent, language)

                # Build with specified variant
                options = BuildOptions(
                    variant=variant,
                    agent_name=agent_name,
                )

                output_content = self.builder.build(filtered_agent, options, config)

                # Write output
                if not dry_run:
                    written = self._write_output(output, agent_name, output_content)
                    actions.extend([f"✓ {f}" for f in written])

                # Build subagents as separate files under .kilo/agents/{agent_name}/{subagent}.md
                if agent.subagents and not dry_run:
                    for subagent_name in agent.subagents:
                        try:
                            # Load actual subagent from registry
                            subagent_key = f"{agent_name}/{subagent_name}"
                            if subagent_key in all_agents:
                                subagent = all_agents[subagent_key]

                                # Filter subagent for language
                                filtered_subagent = self._filter_agent_for_language(
                                    subagent, language, agent_name=subagent_key
                                )

                                # Build subagent with variant
                                subagent_options = BuildOptions(
                                    variant=variant,
                                    agent_name=subagent_key,
                                )

                                subagent_output = self.builder.build(
                                    filtered_subagent, subagent_options, config
                                )

                                # Write to .kilo/agents/{agent_name}/{subagent_name}.md
                                subagent_files = self._write_subagent_output(
                                    output, agent_name, subagent_name, subagent_output
                                )
                                actions.extend([f"✓ {f}" for f in subagent_files])
                        except Exception as e:
                            actions.append(
                                f"✗ Failed to build subagent {agent_name}/{subagent_name}: {e}"
                            )

            except Exception as e:
                actions.append(f"✗ Failed to build {agent_name}: {e}")

        # Now collect and write skills from ALL agents (including subagents)
        if not dry_run:
            for agent_name, agent in all_agents.items():
                if agent.skills:
                    try:
                        # Filter agent for language before writing skills
                        filtered_agent = self._filter_agent_for_language(
                            agent, language, agent_name=agent_name
                        )
                        skill_files = self._write_skill_files(
                            output, agent_name, filtered_agent, variant
                        )
                        for skill_file in skill_files:
                            if skill_file not in all_skills_written:
                                actions.append(f"✓ {skill_file}")
                                all_skills_written.add(skill_file)
                    except Exception as e:
                        actions.append(f"✗ Failed to write skills for {agent_name}: {e}")

        # Write workflows (for tools that use separate workflow files like Kilo)
        all_workflows_written = set()
        if not dry_run and self.tool_name == "kilo":
            for agent_name, agent in all_agents.items():
                if agent.workflows:
                    try:
                        # Filter agent for language before writing workflows
                        filtered_agent = self._filter_agent_for_language(
                            agent, language, agent_name=agent_name
                        )
                        workflow_files = self._write_workflow_files(
                            output, agent_name, filtered_agent, variant
                        )
                        for workflow_file in workflow_files:
                            if workflow_file not in all_workflows_written:
                                actions.append(f"✓ {workflow_file}")
                                all_workflows_written.add(workflow_file)
                    except Exception as e:
                        actions.append(f"✗ Failed to write workflows for {agent_name}: {e}")

        return actions

    def _filter_agent_for_language(
        self, agent: Agent, language: Optional[str], agent_name: Optional[str] = None
    ) -> Agent:
        """Filter agent skills/workflows based on agent and language.

        Uses two-tier resolution system:
        1. AgentSkillMappingLoader - language-agnostic skills/workflows for agent
        2. LanguageSkillMappingLoader - language-specific overrides (if exist)

        Priority resolution:
        1. agent_skill_mapping.yaml - Base skills for agent (language-agnostic)
        2. language_skill_mapping.yaml - Language+agent overrides (rare)
        3. Fallback - Original agent skills/workflows (if no mappings)

        Args:
            agent: Agent to filter
            language: Language code (e.g., 'python', 'typescript'), or None
            agent_name: Full agent name (e.g., 'orchestrator/maintenance'), optional

        Returns:
            New Agent instance with filtered skills and workflows, or original
            if no loaders available
        """
        # Get agent-level skills/workflows (language-agnostic)
        agent_skills = []
        agent_workflows = []
        
        if self.agent_skill_loader:
            agent_skills = self.agent_skill_loader.get_skills_for_agent(agent.name)
            agent_workflows = self.agent_skill_loader.get_workflows_for_agent(agent.name)

        # Get language-specific overrides (if any)
        language_skills = []
        language_workflows = []
        
        if language and self.language_skill_loader:
            # Use full agent_name as subagent path for mapping lookup
            # e.g., "python/orchestrator/maintenance"
            subagent_path = agent_name if agent_name and "/" in agent_name else None
            
            language_skills = self.language_skill_loader.get_skills_for_language(
                language, subagent=subagent_path
            )
            language_workflows = self.language_skill_loader.get_workflows_for_language(
                language, subagent=subagent_path
            )

        # Priority: language overrides > agent mapping > original
        # Language overrides take precedence if they exist (non-empty)
        final_skills = language_skills if language_skills else agent_skills
        final_workflows = language_workflows if language_workflows else agent_workflows
        
        # If no mappings found at all, use original agent skills/workflows
        if not final_skills:
            final_skills = agent.skills or []
        if not final_workflows:
            final_workflows = agent.workflows or []

        # Create filtered copy of agent
        filtered = Agent(
            name=agent.name,
            description=agent.description,
            mode=agent.mode,
            system_prompt=agent.system_prompt,
            tools=agent.tools,  # Tools never filtered (language-agnostic)
            skills=final_skills,
            workflows=final_workflows,
            subagents=agent.subagents,  # Subagents preserved (used-as-is)
            permissions=agent.permissions,
        )

        return filtered

    def _filter_subagent_for_language(
        self, agent_name: str, subagent_name: str, language: str
    ) -> Agent:
        """Filter subagent by language and subagent combination.

        Loads subagent from registry and filters using {language}/{agent_name}/{subagent_name}
        path for maximum specificity.

        Args:
            agent_name: Name of parent agent (e.g., 'code')
            subagent_name: Name of subagent (e.g., 'feature')
            language: Language code (e.g., 'python')

        Returns:
            New Agent instance with filtered skills and workflows

        Raises:
            KeyError: If subagent not found in registry
        """
        # Build full subagent path
        full_subagent_path = f"{agent_name}/{subagent_name}"
        subagent = self.registry.get_agent(full_subagent_path)

        if not self.language_skill_loader:
            return subagent

        # Get skills/workflows for this language and subagent combination
        skills = self.language_skill_loader.get_skills_for_language(
            language, subagent=subagent_name
        )
        workflows = self.language_skill_loader.get_workflows_for_language(
            language, subagent=subagent_name
        )

        # Create filtered copy
        skills_set = set(skills)
        workflows_set = set(workflows)

        filtered = Agent(
            name=subagent.name,
            description=subagent.description,
            mode=subagent.mode,
            system_prompt=subagent.system_prompt,
            tools=subagent.tools,
            skills=[s for s in subagent.skills if s in skills_set],
            workflows=[w for w in subagent.workflows if w in workflows_set],
            subagents=subagent.subagents,
            permissions=subagent.permissions,
        )

        return filtered

    def _write_output(
        self, output: Path, agent_name: str, content: str | dict[str, Any]
    ) -> list[str]:
        """Write builder output to appropriate files.

        Args:
            output: Output directory
            agent_name: Name of the agent
            content: Builder output (string or dict)

        Returns:
            List of files written
        """
        written_files = []

        if self.tool_name == "kilo":
            # Kilo: .kilo/agents/{agent_name}.md
            agents_dir = output / ".kilo" / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)

            file_path = agents_dir / f"{agent_name}.md"
            file_path.write_text(str(content), encoding="utf-8")
            written_files.append(f".kilo/agents/{agent_name}.md")

        elif self.tool_name == "cline":
            # Cline: .clinerules (concatenated)
            file_path = output / ".clinerules"

            # Append to existing or create new
            if file_path.exists():
                existing = file_path.read_text(encoding="utf-8")
                file_path.write_text(f"{existing}\n\n{content}", encoding="utf-8")
            else:
                file_path.write_text(str(content), encoding="utf-8")
            written_files.append(".clinerules")

        elif self.tool_name == "claude":
            # Claude: custom_instructions/{agent_name}.json
            instructions_dir = output / "custom_instructions"
            instructions_dir.mkdir(parents=True, exist_ok=True)

            import json

            file_path = instructions_dir / f"{agent_name}.json"
            file_path.write_text(json.dumps(content, indent=2), encoding="utf-8")
            written_files.append(f"custom_instructions/{agent_name}.json")

        elif self.tool_name == "copilot":
            # Copilot: .github/copilot-instructions.md (concatenated)
            github_dir = output / ".github"
            github_dir.mkdir(parents=True, exist_ok=True)

            file_path = github_dir / "copilot-instructions.md"
            if file_path.exists():
                existing = file_path.read_text(encoding="utf-8")
                file_path.write_text(f"{existing}\n\n{content}", encoding="utf-8")
            else:
                file_path.write_text(str(content), encoding="utf-8")
            written_files.append(".github/copilot-instructions.md")

        elif self.tool_name == "cursor":
            # Cursor: .cursorrules
            file_path = output / ".cursorrules"
            if file_path.exists():
                existing = file_path.read_text(encoding="utf-8")
                file_path.write_text(f"{existing}\n\n{content}", encoding="utf-8")
            else:
                file_path.write_text(str(content), encoding="utf-8")
            written_files.append(".cursorrules")

        return written_files

    def _write_subagent_output(
        self, output: Path, agent_name: str, subagent_name: str, content: str | dict[str, Any]
    ) -> list[str]:
        """Write subagent file to .kilo/agents/{agent}/{subagent}.md.

        Args:
            output: Output directory path
            agent_name: Parent agent name
            subagent_name: Subagent name
            content: File content (string or dict)

        Returns:
            List of written file paths
        """
        subagent_dir = output / ".kilo" / "agents" / agent_name
        subagent_dir.mkdir(parents=True, exist_ok=True)

        subagent_file = subagent_dir / f"{subagent_name}.md"
        subagent_file.write_text(str(content), encoding="utf-8")

        return [str(subagent_file.relative_to(output))]

    def _write_skill_files(
        self, output: Path, agent_name: str, agent: Any, variant: str
    ) -> list[str]:
        """Write skill files for agent's skills.

        Loads skills from top-level skills/ directory and writes to output.

        Args:
            output: Output directory
            agent_name: Name of the agent
            agent: Agent IR model
            variant: Variant (minimal/verbose)

        Returns:
            List of files written
        """
        written_files = []

        # Get list of skills from agent model
        if not hasattr(agent, "skills") or not agent.skills:
            return written_files

        # Top-level skills directory
        skills_dir = Path(__file__).parent / "skills"

        if not skills_dir.exists():
            return written_files

        # Load each skill the agent uses
        for skill_name in agent.skills:
            skill_variant_dir = skills_dir / skill_name / variant
            skill_file = skill_variant_dir / "SKILL.md"

            if not skill_file.exists():
                # Try other variant as fallback
                other_variant = "verbose" if variant == "minimal" else "minimal"
                skill_file = skills_dir / skill_name / other_variant / "SKILL.md"

            if skill_file.exists():
                # Read skill content
                skill_content = skill_file.read_text(encoding="utf-8")

                # Parse to extract name and content
                skill_data = {
                    "name": skill_name,
                    "full_content": skill_content,
                }

                # Write skill to tool-specific location
                skill_files = self._write_single_skill(output, skill_data)
                written_files.extend(skill_files)

        return written_files

    def _write_workflow_files(
        self, output: Path, agent_name: str, agent: Any, variant: str
    ) -> list[str]:
        """Write workflow files for agent's workflows.

        Loads workflows from top-level workflows/ directory and writes to output.
        Currently only used for Kilo (separate command files).

        Args:
            output: Output directory
            agent_name: Name of the agent
            agent: Agent IR model
            variant: Variant (minimal/verbose)

        Returns:
            List of files written
        """
        written_files = []

        if not hasattr(agent, "workflows") or not agent.workflows:
            return written_files

        # Write each workflow as a command file (Kilo-specific)
        if self.tool_name == "kilo":
            commands_dir = output / ".kilo" / "commands"
            commands_dir.mkdir(parents=True, exist_ok=True)

            for workflow_name in agent.workflows:
                # Load workflow content
                workflow_content = self._load_workflow_content(workflow_name, variant)

                if workflow_content:
                    # Write to .kilo/commands/{workflow-name}.md
                    command_file = commands_dir / f"{workflow_name}.md"
                    command_file.write_text(workflow_content, encoding="utf-8")
                    written_files.append(f".kilo/commands/{workflow_name}.md")

        return written_files

    def _load_workflow_content(self, workflow_name: str, variant: str) -> str | None:
        """Load workflow content from workflows/ directory.

        Args:
            workflow_name: Name of the workflow
            variant: Variant (minimal/verbose)

        Returns:
            Workflow content as string, or None if not found
        """
        workflows_dir = Path(__file__).parent / "workflows"
        workflow_file = workflows_dir / workflow_name / variant / "workflow.md"

        if not workflow_file.exists():
            # Try other variant as fallback
            other_variant = "verbose" if variant == "minimal" else "minimal"
            workflow_file = workflows_dir / workflow_name / other_variant / "workflow.md"

        if workflow_file.exists():
            return workflow_file.read_text(encoding="utf-8")

        return None

    def _parse_skills_file(self, content: str) -> list[dict[str, str]]:
        """Parse skills.md content into individual skills.

        Skills are in YAML format with --- delimiters.
        Each skill has frontmatter between --- markers, followed by body content.
        Skills are separated by standalone --- lines.

        Args:
            content: Full skills.md content

        Returns:
            List of skill dicts with 'name' and 'full_content' keys
        """
        import re

        skills = []

        # Split content into individual skill blocks
        # Pattern: ---\nfrontmatter\n---\nbody\n\n---\n (next skill)
        # We need to find each skill block that starts with ---

        current_pos = 0
        while True:
            # Find next ---
            start = content.find("---", current_pos)
            if start == -1:
                break

            # Find the closing --- for frontmatter
            frontmatter_end = content.find("\n---\n", start + 3)
            if frontmatter_end == -1:
                break

            # Extract frontmatter (between the two ---)
            frontmatter = content[start + 4 : frontmatter_end].strip()

            # Find the next skill's start (next standalone ---)
            body_start = frontmatter_end + 5
            next_skill = content.find("\n---\n", body_start)

            if next_skill == -1:
                # This is the last skill
                body = content[body_start:].strip()
                next_pos = len(content)
            else:
                body = content[body_start:next_skill].strip()
                next_pos = next_skill + 1

            # Parse skill name from frontmatter
            name_match = re.search(r"^name:\s*(.+)$", frontmatter, re.MULTILINE)
            if name_match:
                skill_name = name_match.group(1).strip()
                full_content = f"---\n{frontmatter}\n---\n\n{body}"

                skills.append(
                    {
                        "name": skill_name,
                        "frontmatter": frontmatter,
                        "body": body,
                        "full_content": full_content,
                    }
                )

            current_pos = next_pos

        return skills

    def _write_single_skill(self, output: Path, skill: dict[str, str]) -> list[str]:
        """Write a single skill file to output directory.

        Args:
            output: Output directory
            skill: Skill dict with name and full_content

        Returns:
            List of files written
        """
        written_files = []
        skill_name = skill["name"]
        content = skill["full_content"]

        if self.tool_name == "kilo":
            # Kilo: .kilo/skills/{skill_name}/SKILL.md
            skill_dir = output / ".kilo" / "skills" / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(content, encoding="utf-8")
            written_files.append(f".kilo/skills/{skill_name}/SKILL.md")

        elif self.tool_name == "cline":
            # Cline: .cline/skills/{skill_name}/SKILL.md
            skill_dir = output / ".cline" / "skills" / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(content, encoding="utf-8")
            written_files.append(f".cline/skills/{skill_name}/SKILL.md")

        elif self.tool_name == "claude":
            # Claude: .claude/skills/{skill_name}/SKILL.md
            skill_dir = output / ".claude" / "skills" / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(content, encoding="utf-8")
            written_files.append(f".claude/skills/{skill_name}/SKILL.md")

        elif self.tool_name == "copilot":
            # Copilot: .github/skills/{skill_name}.md
            skills_dir = output / ".github" / "skills"
            skills_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skills_dir / f"{skill_name}.md"
            skill_file.write_text(content, encoding="utf-8")
            written_files.append(f".github/skills/{skill_name}.md")

        elif self.tool_name == "cursor":
            # Cursor: .cursor/skills/{skill_name}/SKILL.md
            skill_dir = output / ".cursor" / "skills" / skill_name
            skill_dir.mkdir(parents=True, exist_ok=True)
            skill_file = skill_dir / "SKILL.md"
            skill_file.write_text(content, encoding="utf-8")
            written_files.append(f".cursor/skills/{skill_name}/SKILL.md")

        return written_files


def get_prompt_builder(tool: str):
    """Get prompt builder for a tool.

    Args:
        tool: Tool name (e.g., 'kilo-cli', 'kilo-ide', 'cline', 'cursor', 'copilot')

    Returns:
        Builder instance

    Raises:
        ValueError: If tool is unknown
    """
    # Map tool names to builder names
    tool_mapping = {
        "kilo-cli": "kilo",
        "kilo-ide": "kilo",
        "cline": "cline",
        "cursor": "cursor",
        "copilot": "copilot",
        "claude": "claude",
    }

    internal_tool = tool_mapping.get(tool)
    if not internal_tool:
        raise ValueError(f"Unknown tool: {tool}")

    return PromptBuilder(internal_tool)
