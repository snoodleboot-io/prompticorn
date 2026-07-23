"""Builder wrapper to generate tool-specific configs from bundled IR agents."""

import json
import warnings
from pathlib import Path
from typing import Any

from prompticorn.agent_registry.registry import Registry
from prompticorn.builders.agents_md import generate_agents_md
from prompticorn.builders.base import BuildOptions
from prompticorn.builders.claude_md import generate_claude_md
from prompticorn.builders.convention_generator import generate_all_conventions
from prompticorn.builders.factory import BuilderFactory
from prompticorn.builders.layouts import get_layout
from prompticorn.builders.template_handlers.primary_agents_handler import PrimaryAgentsHandler
from prompticorn.ir.loaders.agent_skill_mapping_loader import AgentSkillMappingLoader
from prompticorn.ir.loaders.language_skill_mapping_loader import LanguageSkillMappingLoader
from prompticorn.ir.models.agent import Agent
from prompticorn.personas import PersonaFilter, PersonaRegistry
from prompticorn.tools import builder_dispatch


class MissingSkillWarning(UserWarning):
    """Raised when an agent maps to a skill that has no SKILL.md on disk."""


def _dedupe_preserve_order(*lists: list[str] | None) -> list[str]:
    """Union the given lists, keeping first-seen order and dropping duplicates."""
    seen: set[str] = set()
    result: list[str] = []
    for lst in lists:
        for item in lst or []:
            if item not in seen:
                seen.add(item)
                result.append(item)
    return result


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
        self.layout = get_layout(tool_name)

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
        agent_mapping_file = Path(__file__).parent / "configurations" / "agent_skill_mapping.yaml"
        try:
            self.agent_skill_loader = AgentSkillMappingLoader(agent_mapping_file)
        except FileNotFoundError:
            self.agent_skill_loader = None

    @staticmethod
    def _extract_language_from_config(config: dict[str, Any] | None) -> str | None:
        """Extract primary language from config.

        Handles both single-language and multi-language-monorepo configurations.

        Args:
            config: Project configuration

        Returns:
            Primary language string, or None if not found
        """
        if not config:
            return None

        spec = config.get("spec")

        if spec is None:
            return None
        elif isinstance(spec, dict):
            # Single-language repo: spec is a dict with 'language' key
            return spec.get("language")
        elif isinstance(spec, list) and len(spec) > 0:
            # Multi-language-monorepo: spec is a list of folder specs
            # Use first folder's language as primary language
            return spec[0].get("language")
        else:
            return None

    @staticmethod
    def _extract_all_languages_from_config(config: dict[str, Any] | None) -> list[str] | None:
        """Extract all selected languages from config.

        Args:
            config: Project configuration

        Returns:
            List of language strings, or None if not found
        """
        if not config:
            return None

        spec = config.get("spec")

        if spec is None:
            return None
        elif isinstance(spec, dict):
            lang = spec.get("language")
            return [lang] if lang else None
        elif isinstance(spec, list) and len(spec) > 0:
            langs = [folder.get("language") for folder in spec if folder.get("language")]
            return langs if langs else None
        else:
            return None

    @staticmethod
    def _extract_all_specs_from_config(
        config: dict[str, Any] | None,
    ) -> list[dict[str, Any]] | None:
        """Extract all language/folder specs from config.

        Unlike :meth:`_extract_all_languages_from_config`, this returns the full
        spec dicts (runtime, package_manager, test_framework, linter, formatter,
        coverage, ...) so convention templates can be populated with the user's
        actual choices.

        Args:
            config: Project configuration

        Returns:
            List of spec dicts, or None if no usable spec is present.
        """
        if not config:
            return None

        spec = config.get("spec")

        if isinstance(spec, dict) and spec.get("language"):
            return [spec]
        elif isinstance(spec, list):
            specs = [
                folder for folder in spec if isinstance(folder, dict) and folder.get("language")
            ]
            return specs if specs else None
        return None

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
        language = self._extract_language_from_config(config)

        # Get all agents from registry
        all_agents = self.registry.get_all_agents()

        # Persona-based filtering: Only build agents for selected personas
        active_personas = config.get("active_personas", []) if config else []

        if active_personas is not None:
            # Load persona registry and filter agents
            try:
                personas_yaml_path = Path(__file__).parent / "personas" / "personas.yaml"
                persona_registry = PersonaRegistry.from_yaml(personas_yaml_path)
                persona_filter = PersonaFilter(persona_registry, active_personas)

                # Get enabled agents for selected personas
                enabled_agent_names = persona_filter.get_enabled_agents()

                # Filter all_agents to only include enabled agents
                # Keep only top-level agents that are enabled (subagents inherit parent status)
                filtered_agents = {}
                for agent_key, agent in all_agents.items():
                    if "/" in agent_key:
                        # Subagent - check if parent is enabled
                        parent_name = agent_key.split("/")[0]
                        if parent_name in enabled_agent_names:
                            filtered_agents[agent_key] = agent
                    else:
                        # Top-level agent - check if enabled
                        if agent_key in enabled_agent_names:
                            filtered_agents[agent_key] = agent

                all_agents = filtered_agents

                # Log persona filtering info
                actions.append(f"ℹ Persona filtering: {len(active_personas)} persona(s) selected")
                actions.append(
                    f"ℹ Building {len([k for k in all_agents.keys() if '/' not in k])} primary agents (from {len(enabled_agent_names)} enabled)"
                )
            except Exception as e:
                # If persona filtering fails, log warning and continue without filtering
                actions.append(f"⚠ Persona filtering failed ({e}), building all agents")

        # Collect all unique skills from all agents (including subagents)
        all_skills_written = set()
        all_files_written = set()  # Track unique files for Claude deduplication

        # Track primary agents being built (for AGENTS.md)
        primary_agents_built = []

        # Per-agent build outputs, for layouts that emit an aggregate file (Roo).
        built_agent_outputs: list[Any] = []

        # For Kilo, write core convention files to .kilo/rules/ before building agents
        rules_files_written = []
        if self.layout.writes_rules and not dry_run:
            try:
                rules_files_written = self.builder.write_rules_files(output, config)
                actions.extend([f"✓ {f}" for f in rules_files_written])
            except Exception as e:
                actions.append(f"✗ Failed to write rules files: {e}")

        # Build each top-level agent (skip subagents, they're included in parent)
        for agent_name, agent in all_agents.items():
            if "/" in agent_name:  # Skip subagents for agent file generation
                continue

            # Track this primary agent for AGENTS.md
            primary_agents_built.append(
                {"name": agent_name, "description": agent.description or f"Agent: {agent_name}"}
            )

            try:
                # Filter agent for language before building
                filtered_agent = self._filter_agent_for_language(agent, language)

                # Build with specified variant
                options = BuildOptions(
                    variant=variant,
                    agent_name=agent_name,
                )

                output_content = self.builder.build(filtered_agent, options, config)
                built_agent_outputs.append(output_content)

                # Write output
                if not dry_run:
                    written = self._write_output(output, agent_name, output_content)
                    # Deduplicate file reports (especially for Claude workflows)
                    new_files = [f for f in written if f not in all_files_written]
                    all_files_written.update(written)
                    actions.extend([f"✓ {f}" for f in new_files])

                # Build subagents as separate files under .kilo/agents/{agent_name}/{subagent}.md
                if agent.subagents and not dry_run and self.layout.writes_subagents:
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

        # Now collect and write skills from ALL agents (including subagents).
        # Skills live in the agent/language mapping registries, not the raw IR
        # model (whose .skills is empty for most agents), so gate on the FILTERED
        # agent's skills — otherwise the SKILL.md files an agent's markdown table
        # references would never be written, leaving dangling links.
        if not dry_run:
            for agent_name, agent in all_agents.items():
                try:
                    # Filter agent for language before writing skills
                    filtered_agent = self._filter_agent_for_language(
                        agent, language, agent_name=agent_name
                    )
                    if not filtered_agent.skills:
                        continue
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
        if not dry_run and self.layout.writes_workflows:
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

        # Generate root AGENTS.md or CLAUDE.md file (only for primary agents in scope)
        if not dry_run:
            try:
                if self.layout.emits_claude_md:
                    # Generate CLAUDE.md for Claude
                    persona_name = (
                        config.get("persona", "software_engineer")
                        if config
                        else "software_engineer"
                    )
                    claude_md_content = generate_claude_md(primary_agents_built, persona_name)
                    claude_md_path = output / "CLAUDE.md"
                    claude_md_path.write_text(claude_md_content, encoding="utf-8")
                    actions.append("✓ CLAUDE.md")

                    # Generate convention files for Claude (only selected languages)
                    try:
                        selected_specs = self._extract_all_specs_from_config(config)
                        repository_type = (
                            (config.get("repository") or {}).get("type", "") if config else ""
                        )
                        project = config.get("project") if config else None
                        conventions = generate_all_conventions(
                            selected_specs, repository_type, project
                        )
                        for file_path_str, content_str in conventions.items():
                            full_path = output / file_path_str
                            full_path.parent.mkdir(parents=True, exist_ok=True)
                            full_path.write_text(content_str, encoding="utf-8")
                        actions.append(f"✓ {len(conventions)} convention files")
                    except Exception as conv_error:
                        actions.append(f"⚠ Failed to generate conventions: {conv_error}")
                elif self.layout.emits_agents_md:
                    # Generate self-contained AGENTS.md for other tools: routing
                    # index + inlined core conventions (sourced from the primary spec).
                    selected_specs = self._extract_all_specs_from_config(config)
                    primary_spec = selected_specs[0] if selected_specs else {}
                    repository_type = (
                        (config.get("repository") or {}).get("type", "") if config else ""
                    )
                    project = config.get("project") if config else None
                    agents_md_content = generate_agents_md(
                        primary_agents_built,
                        repository_type=repository_type,
                        project=project,
                        primary_language=primary_spec.get("language", ""),
                        primary_spec=primary_spec,
                        language_specs=selected_specs,
                    )
                    agents_md_path = output / "AGENTS.md"
                    agents_md_path.write_text(agents_md_content, encoding="utf-8")
                    actions.append("✓ AGENTS.md")
            except Exception as e:
                file_name = self.layout.root_doc_filename()
                actions.append(f"⚠ Failed to generate {file_name}: {e}")

        # Emit any aggregate file built from all agents (e.g. Roo's .roomodes).
        if not dry_run:
            try:
                for finalized in self.layout.finalize(output, built_agent_outputs, config):
                    actions.append(f"✓ {finalized}")
            except Exception as e:
                actions.append(f"⚠ Failed to finalize output: {e}")

        # Resolve legacy {{PRIMARY_AGENTS_LIST}} in whatever files carry it. The
        # IR-based builders (gemini/roo/zed/junie/codex/amazonq/windsurf/continue/
        # copilot-chat) emit the orchestrator's system prompt and skill files
        # verbatim, so unlike the Claude/Cline/Cursor/Copilot path they never run
        # the substitution. Resolving here — after every file is written — covers
        # agent, skill and workflow files uniformly and is a no-op for builders
        # that already substituted (the token is gone). (PRO-72)
        if not dry_run:
            self._resolve_primary_agents_token(output, config)

        return actions

    def _resolve_primary_agents_token(self, output: Path, config: dict[str, Any] | None) -> None:
        """Replace any literal ``{{PRIMARY_AGENTS_LIST}}`` in emitted files.

        Computes the list once (it depends on the config's active personas) and
        rewrites only files that actually contain the token, via plain string
        replacement — never a Jinja re-render, so literal ``{{ }}`` in code
        examples is untouched.

        The replacement is a multi-line markdown bullet list. In a markdown/YAML
        body those newlines are harmless, but a builder that embeds the token
        inside a **JSON string** (Amazon Q's agent ``prompt``) already escaped the
        placeholder via ``json.dumps``; substituting the raw value there would
        inject unescaped control characters and corrupt the JSON. So the value is
        JSON-escaped for ``.json`` files (PRO-80).
        """
        token = "{{PRIMARY_AGENTS_LIST}}"
        value: str | None = None
        for path in output.rglob("*"):
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            if token not in text:
                continue
            if value is None:
                value = PrimaryAgentsHandler().handle("PRIMARY_AGENTS_LIST", config or {})
            # In .json the token sits inside an already-escaped JSON string; escape
            # the replacement to match (json.dumps(...)[1:-1] = the escaped inner
            # content, without the surrounding quotes).
            replacement = json.dumps(value)[1:-1] if path.suffix == ".json" else value
            path.write_text(text.replace(token, replacement), encoding="utf-8")

    def _filter_agent_for_language(
        self, agent: Agent, language: str | None, agent_name: str | None = None
    ) -> Agent:
        """Filter agent skills/workflows based on agent and language.

        Uses two-tier resolution system:
        1. AgentSkillMappingLoader - language-agnostic skills/workflows for agent
        2. LanguageSkillMappingLoader - language-specific additions (if any)

        Resolution: the agent-level skills/workflows are the base; language-specific
        ones are ADDED to them (union, not replacement). Previously a language
        mapping replaced the agent-level set entirely, which silently dropped
        agent-level skills (e.g. the orchestrator's) from single-language builds.
        Falls back to the agent's own declared skills/workflows if neither loader
        yields anything.

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

        # Union: agent-level skills are the base; language-specific ones are added
        # on top (order-preserving, de-duplicated). A language mapping augments the
        # agent set rather than replacing it.
        final_skills = _dedupe_preserve_order(agent_skills, language_skills)
        final_workflows = _dedupe_preserve_order(agent_workflows, language_workflows)

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
        return self.layout.write_agent(output, agent_name, content)

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

            if not skill_file.exists():
                # A skill an agent maps to but that has no SKILL.md on disk would
                # otherwise vanish from the build with no signal at all (PRO-89).
                warnings.warn(
                    f"Agent '{agent_name}' maps to skill '{skill_name}', but no "
                    f"SKILL.md exists in either variant under "
                    f"{skills_dir / skill_name}; the skill will be missing from "
                    "the build. Check the skill name and the file's casing.",
                    MissingSkillWarning,
                    stacklevel=2,
                )
                continue

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

        # Write each workflow as a command file via the tool's layout.
        if self.layout.writes_workflows:
            for workflow_name in agent.workflows:
                workflow_content = self._load_workflow_content(workflow_name, variant)
                if workflow_content:
                    written_files.extend(
                        self.layout.write_workflow(output, workflow_name, workflow_content)
                    )

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
        return self.layout.write_skill(output, skill["name"], skill["full_content"])


def get_prompt_builder(tool: str):
    """Get prompt builder for a tool.

    Args:
        tool: Tool name (e.g., 'kilo-cli', 'kilo-ide', 'cline', 'cursor', 'copilot')

    Returns:
        Builder instance

    Raises:
        ValueError: If tool is unknown
    """
    # Map tool ids to internal builder names (from the central tool registry).
    internal_tool = builder_dispatch().get(tool)
    if not internal_tool:
        raise ValueError(f"Unknown tool: {tool}")

    return PromptBuilder(internal_tool)
