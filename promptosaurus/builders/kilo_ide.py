"""
builders/kilo_ide.py
Kilo Code IDE builder - outputs .kilocode/rules-{mode}/ structure.

Output layout:
  {output}/.kilocode/rules/                 <- core files (always loaded)
  {output}/.kilocode/rules-{mode}/           <- per-mode directories with files
  {output}/.kilocodemodes                <- all mode definitions (for IDE)
  {output}/.kiloignore                  <- ignore patterns

This format is used by the KiloCode IDE extensions (VSCode/JetBrains).
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.kilo import KiloCodeBuilder
from promptosaurus.registry import registry


def _make_dest_filename(filename: str, mode_key: str | None = None) -> str:
    """
    Convert prompt source path to destination filename.

    Mapping rules:
    - agents/core/core-conventions-{lang}.md -> conventions-{lang}.md (language goes to rules/)
    - agents/core/core-{slug}.md -> {slug}.md (core files go to rules/)
    - agents/{agent}/subagents/{agent}-{slug}.md -> {slug}.md (subagent files)
    - agents/{agent}/{agent}.md -> {agent}.md (root agent files)
    - Any other agents/{agent}/ path -> flatten (remove subagents folder and agent prefix)
    """
    # Handle core files first
    if filename.startswith("agents/core/core-conventions-"):
        # Language conventions: core-conventions-python.md -> conventions-python.md
        # Remove "agents/core/" (12) + "core-" (5) = 17 chars
        return filename[17:]  # Keep "conventions-{lang}.md"
    elif filename.startswith("agents/core/core-"):
        # Core files: core-session.md -> session.md
        # Remove "agents/core/core-" (17 chars)
        return filename[17:]  # Remove "agents/core/core-"

    # Handle agent files
    if mode_key:
        # Check for subagents: agents/{mode}/subagents/{mode}-{slug}.md -> {slug}.md
        subagents_prefix = f"agents/{mode_key}/subagents/{mode_key}-"
        if filename.startswith(subagents_prefix):
            return filename[len(subagents_prefix) :]

        # Check for root agent file: agents/{mode}.md -> {mode}.md
        root_agent_file = f"agents/{mode_key}.md"
        if filename == root_agent_file:
            return f"{mode_key}.md"

        # For any other agents/{something}/ path, flatten it
        # e.g., agents/code/subagents/code-feature.md -> when in migration mode
        if filename.startswith("agents/"):
            # Find and remove "agents/{something}/" prefix
            slash1 = filename.find("/")
            if slash1 > 0:
                # Find next slash after "agents/"
                slash2 = filename.find("/", slash1 + 1)
                if slash2 > 0:
                    remainder = filename[slash2 + 1 :]
                    # Remove "subagents/" if present
                    if remainder.startswith("subagents/"):
                        remainder = remainder[10:]  # Remove "subagents/"
                    # Remove any {agent}- prefix from the filename
                    for agent_prefix in [
                        "code-",
                        "test-",
                        "refactor-",
                        "document-",
                        "explain-",
                        "migration-",
                        "review-",
                        "security-",
                        "compliance-",
                        "architect-",
                        "ask-",
                        "orchestrator-",
                        "enforcement-",
                        "planning-",
                        "debug-",
                    ]:
                        if remainder.startswith(agent_prefix):
                            return remainder[len(agent_prefix) :]
                    return remainder

    # Fallback: return as-is
    return filename


class KiloIDEBuilder(KiloCodeBuilder):
    """Builder for Kilo Code .kilocode/rules-{mode}/ directory structure (IDE format)."""

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Write the Kilo .kilocode/rules-{mode}/ structure under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []

        # Get selected language from config
        selected_language = config.get("spec", {}).get("language", "") if config else ""
        language_file = (
            self.language_file_map.get(selected_language.lower()) if selected_language else None
        )

        # 1. Create AGENTS.md user guide
        actions.append(self._create_agents_md(output, dry_run))

        # 2. Create core files in .kilocode/rules/
        for filename in self.BASE_FILES:
            source_path = registry.prompt_path(filename)
            if source_path.exists():
                new_filename = _make_dest_filename(filename)  # No mode_key for core files
                destination = output / ".kilocode" / "rules" / new_filename
                actions.append(self._copy(source_path, destination, dry_run, config))

        # 2b. Add language-specific conventions to .kilocode/rules/ if selected
        if language_file:
            source_path = registry.prompt_path(language_file)
            if source_path.exists():
                new_filename = _make_dest_filename(language_file)
                destination_rules = output / ".kilocode" / "rules" / new_filename
                actions.append(self._copy(source_path, destination_rules, dry_run, config))

        # 3. Create per-mode directories with their files (ALL 15 modes for IDE)
        for mode_key in self.kilo_modes.keys():
            if mode_key in registry.mode_files:
                mode_dir = output / ".kilocode" / f"rules-{mode_key}"
                for filename in registry.mode_files[mode_key]:
                    source_path = registry.prompt_path(filename)
                    if source_path.exists():
                        new_filename = _make_dest_filename(filename, mode_key)
                        destination = mode_dir / new_filename
                        actions.append(self._copy(source_path, destination, dry_run, config))

        # 4. Generate .kilocodemodes manifest
        actions.append(self._write_manifest(output / ".kilocodemodes", dry_run))

        # 5. Build .kiloignore
        actions.extend(self._build_ignore(output, dry_run))

        return actions

    def _get_agents_md_content(self) -> str:
        """Get the AGENTS.md content for IDE format."""
        return """# Kilo Code Agents

This directory contains the agent instructions for Kilo Code (IDE format).

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents
- **`.kilocode/rules/`** — Core behaviors and conventions (always loaded)
- **`.kilocode/rules-{mode}/`** — Mode-specific behaviors for each agent

## Core Instructions

The `.kilocode/rules/` directory contains core files that are always loaded:
- `system.md` — Core system behaviors
- `conventions.md` — General conventions
- `session.md` — Session management
- `{language}.md` — Language-specific conventions (if configured)

**Important:** Always load the core files from `.kilocode/rules/` for any task, as they contain the foundational behaviors and conventions for this project.

## Available Agents

Each agent has its own directory under `.kilocode/rules-{mode}/`:

| Mode | Directory | Purpose |
|------|-----------|---------|
| **test** | `.kilocode/rules-test/` | Write comprehensive tests with coverage-first approach |
| **refactor** | `.kilocode/rules-refactor/` | Improve code structure while preserving behavior |
| **document** | `.kilocode/rules-document/` | Generate documentation, READMEs, and changelogs |
| **explain** | `.kilocode/rules-explain/` | Code walkthroughs and onboarding assistance |
| **migration** | `.kilocode/rules-migration/` | Handle dependency upgrades and framework migrations |
| **review** | `.kilocode/rules-review/` | Code, performance, and accessibility reviews |
| **security** | `.kilocode/rules-security/` | Security reviews for code and infrastructure |
| **compliance** | `.kilocode/rules-compliance/` | SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance |
| **enforcement** | `.kilocode/rules-enforcement/` | Reviews code against established coding standards |
| **planning** | `.kilocode/rules-planning/` | Develops PRDs and works with architects to create ARDs |

> **Note:** The architect, code, ask, debug, and orchestrator modes are built-in to Kilo and are not generated here.

## Usage

Switch between agents based on the task at hand. Each agent has specialized
behaviors and will suggest switching when appropriate.

## Configuration

The KiloCode IDE extensions automatically load the appropriate mode instructions
from the `.kilocode/` directory based on the current mode selection.
"""
