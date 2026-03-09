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

from promptosaurus.builders.kilo.kilo_code_builder import KiloCodeBuilder
from promptosaurus.registry import registry


class KiloCLIBuilder(KiloCodeBuilder):
    """Builder for Kilo Code .opencode/rules/ directory structure (CLI format)."""

    @property
    def custom_modes(self) -> list[str]:
        """Return list of custom modes (excluding built-in Kilo modes)."""
        return [m for m in registry.modes.keys() if m not in self._kilo_builtin_modes]

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
        """Get the AGENTS.md content for CLI format by reading from template file."""
        path = Path(__file__).parent / "AGENTS_KILO_CLI.md"
        if not path.exists():
            raise ValueError("The AGENTS.md file was not found.")
        return path.read_text(encoding="utf-8")
