"""Kilo Code CLI builder - outputs .opencode/rules/ structure.

This module provides the KiloCLIBuilder class that generates the configuration
files for Kilo Code in CLI format (used by OpenCode/Continue).

Output layout:
  {output}/AGENTS.md                    ← user guide
  {output}/.opencode/rules/_base.md    ← collapsed core files
  {output}/.opencode/rules/{MODE}.md   ← collapsed mode files (all 15 modes)
  {output}/opencode.json               ← instructions config
  {output}/.kilocodemodes              ← custom mode definitions (for IDE compatibility)
  {output}/.kiloignore                 ← ignore patterns

Classes:
    KiloCLIBuilder: Builder for Kilo Code .opencode/rules/ directory structure.
"""

import json
from pathlib import Path
from typing import Any

from promptosaurus.builders.kilo.kilo_code_builder import KiloCodeBuilder
from promptosaurus.builders.kilo.kilo_ide import _make_dest_filename
from promptosaurus.registry import registry


class KiloCLIBuilder(KiloCodeBuilder):
    """Builder for Kilo Code .opencode/rules/ directory structure (CLI format).

    This builder creates the collapsed format used by the OpenCode/Continue CLI.
    It generates:
    - AGENTS.md: User guide
    - _base.md: Collapsed core convention files
    - {MODE}.md: Collapsed mode files for each custom mode
    - opencode.json: Instructions configuration
    - .kilocodemodes: Mode definitions
    - .kiloignore: Ignore patterns

    The CLI format uses collapsed files where all subagent prompts for a mode
    are combined into a single markdown file.

    Attributes:
        custom_modes: Property returning list of custom modes (excluding built-in).
    """

    @property
    def custom_modes(self) -> list[str]:
        """Return list of custom modes (excluding built-in Kilo modes).

        Built-in modes (architect, code, ask, debug, orchestrator) are
        excluded because they are built into Kilo itself.

        Returns:
            List of custom mode slugs.
        """
        return [m for m in registry.modes.keys() if m not in self._kilo_builtin_modes]

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Write the Kilo .opencode/rules/ structure under `output`.

        Generates the CLI-format configuration by:
        1. Creating AGENTS.md user guide
        2. Creating _base.md with collapsed core files + language convention
        3. Creating collapsed mode files for each custom mode
        4. Generating opencode.json and .kilocodemodes manifest
        5. Building .kiloignore

        Args:
            output: Directory path where files will be created.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings describing what was created.
        """
        actions: list[str] = []
        rules_dir = output / ".opencode" / "rules"

        # Get selected language(s) from config
        # Handle both single-language (dict) and multi-language (list) configs
        spec = config.get("spec", {}) if config else {}
        selected_languages: list[str] = []
        if isinstance(spec, list):
            # Multi-language monorepo: get ALL unique languages from all folders
            languages_seen = set()
            for folder_spec in spec:
                lang = folder_spec.get("language", "")
                if lang and lang.lower() not in languages_seen:
                    languages_seen.add(lang.lower())
                    selected_languages.append(lang)
        else:
            # Single language: use existing behavior
            lang = spec.get("language", "") if spec else ""
            if lang:
                selected_languages.append(lang)

        # 1. Create AGENTS.md user guide
        actions.append(self._create_agents_md(output, dry_run))

        # 2. Create _base.md (collapsed core files + language convention)
        # For multi-language, use first language for base.md
        selected_language = selected_languages[0] if selected_languages else ""
        language_file = (
            self.language_file_map.get(selected_language.lower()) if selected_language else None
        )
        actions.append(self._create_base_md(rules_dir, language_file, dry_run, config))

        # 3. Add language-specific convention files for ALL languages
        languages_added: set[str] = set()
        for lang in selected_languages:
            lang_file = self.language_file_map.get(lang.lower()) if lang else None
            if lang_file and lang.lower() not in languages_added:
                source_path = registry.prompt_path(lang_file)
                if source_path.exists():
                    new_filename = _make_dest_filename(lang_file)
                    destination_rules = output / ".opencode" / "rules" / new_filename
                    actions.append(self._copy(source_path, destination_rules, dry_run, config))
                    languages_added.add(lang.lower())

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
        """Generate opencode.json configuration file.

        Creates the opencode.json file that tells OpenCode which
        instruction files to load and in what order.

        Args:
            output: Output directory path.
            dry_run: If True, return preview without writing.

        Returns:
            Action string describing the operation.
        """
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
        """Get the AGENTS.md content for CLI format by reading from template file.

        Returns:
            The content for the AGENTS.md file.

        Raises:
            ValueError: If the AGENTS.md template file is not found.
        """
        path = Path(__file__).parent / "AGENTS_KILO_CLI.md"
        if not path.exists():
            raise ValueError("The AGENTS.md file was not found.")
        return path.read_text(encoding="utf-8")
