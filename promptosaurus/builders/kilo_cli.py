"""
builders/kilo_cli.py
Kilo Code CLI builder - outputs .opencode/rules/ structure.

Output layout:
  {output}/AGENTS.md                    ← user guide
  {output}/.opencode/rules/_base.md    ← collapsed core files
  {output}/.opencode/rules/{MODE}.md   ← collapsed mode files (all 15 modes)
  {output}/opencode.json               ← instructions config
  {output}/.kilocodemodes              ← custom mode definitions (for IDE compatibility)
  {output}/.kiloignore                 ← ignore patterns
"""

import json
from pathlib import Path
from typing import Any

from promptosaurus.builders.kilo import KiloCodeBuilder
from promptosaurus.registry import registry


class KiloCLIBuilder(KiloCodeBuilder):
    """Builder for Kilo Code .opencode/rules/ directory structure (CLI format)."""

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Write the Kilo .opencode/rules/ structure under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []
        rules_dir = output / ".opencode" / "rules"

        # Get selected language from config
        selected_language = config.get("spec", {}).get("language", "") if config else ""
        language_file = (
            self.language_file_map.get(selected_language.lower()) if selected_language else None
        )

        # 1. Create AGENTS.md user guide
        actions.append(self._create_agents_md(output, dry_run))

        # 2. Create _base.md (collapsed core files + language convention)
        actions.append(self._create_base_md(rules_dir, language_file, dry_run, config))

        # 3. Create collapsed mode files for custom modes only
        for mode_key in self.custom_modes:
            if mode_key in registry.mode_files:
                actions.append(
                    self._create_collapsed_mode_md(
                        rules_dir, mode_key, registry.mode_files[mode_key], dry_run, config
                    )
                )

        # 4. Generate opencode.json and .kilocodemodes manifest
        actions.append(self._create_opencode_json(output, dry_run))
        actions.append(self._write_manifest(output / ".kilocodemodes", dry_run))

        # 5. Build .kiloignore
        actions.extend(self._build_ignore(output, dry_run))

        return actions

    def _create_opencode_json(self, output: Path, dry_run: bool) -> str:
        """Generate opencode.json configuration file."""
        destination = output / "opencode.json"
        label = "opencode.json"

        # Build instructions array - AGENTS.md, _base.md, and all mode files
        instructions = [
            "AGENTS.md",
            ".opencode/rules/_base.md",
        ]
        # Add custom mode files
        for mode_key in sorted(self.custom_modes):
            instructions.append(f".opencode/rules/{mode_key}.md")

        data = {
            "instructions": instructions,
        }

        content = json.dumps(data, indent=2)

        if dry_run:
            return f"[dry-run] {label}"
        destination.write_text(content, encoding="utf-8")
        return f"✓ {label}"

    def _get_agents_md_content(self) -> str:
        """Get the AGENTS.md content for CLI format."""
        return """# Kilo Code Agents

This directory contains the agent instructions for Kilo Code (CLI format).

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents
- **`.opencode/rules/_base.md`** — Core behaviors, conventions, and session management (always loaded)
- **`.opencode/rules/{MODE}.md`** — Mode-specific behaviors for each agent

## Core Instructions

The `_base.md` file contains:
- Core system behaviors (from `core-system.md`)
- General conventions (from `core.md`)
- Session management (from `core-session.md`)
- Language-specific conventions (if configured)

**Important:** Always load `_base.md` first for any task, as it contains the foundational behaviors and conventions for this project.

## Available Agents

Custom agents are collapsed into individual `.opencode/rules/{MODE}.md` files:

| Mode | Purpose |
|------|---------|
| **test** | Write comprehensive tests with coverage-first approach |
| **refactor** | Improve code structure while preserving behavior |
| **document** | Generate documentation, READMEs, and changelogs |
| **explain** | Code walkthroughs and onboarding assistance |
| **migration** | Handle dependency upgrades and framework migrations |
| **review** | Code, performance, and accessibility reviews |
| **security** | Security reviews for code and infrastructure |
| **compliance** | SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance |
| **enforcement** | Reviews code against established coding standards |
| **planning** | Develops PRDs and works with architects to create ARDs |

> **Note:** The architect, code, ask, debug, and orchestrator modes are built-in to Kilo and are not generated here.

## Usage

Switch between agents based on the task at hand. Each agent has specialized
behaviors and will suggest switching when appropriate.

## Configuration

The `opencode.json` file references these instructions:

```json
{
  "instructions": [
    "AGENTS.md",
    ".opencode/rules/_base.md",
    ".opencode/rules/{MODE}.md"
  ]
}
```

Replace `{MODE}` with the agent you want to use (architect, code, ask, etc.).
"""
