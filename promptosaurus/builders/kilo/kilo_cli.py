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

Example:
    >>> from pathlib import Path
    >>> from promptosaurus.builders.kilo.kilo_cli import KiloCLIBuilder
    >>> builder = KiloCLIBuilder()
    >>> actions = builder.build(Path("./output"))
    >>> for action in actions[:3]:
    ...     print(action)
    ✓ AGENTS.md
    ✓ .opencode/rules/_base.md
    ✓ .opencode/rules/code.md
"""

import json
from pathlib import Path
from typing import Any

from promptosaurus.builders.kilo.kilo_code_builder import KiloCodeBuilder
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

    Example:
        >>> builder = KiloCLIBuilder()
        >>> # Build files
        >>> actions = builder.build(Path("./my-project"))
        >>> print(f\"Generated {len(actions)} files\")
    """

    @property
    def custom_modes(self) -> list[str]:
        """Return list of custom modes (excluding built-in Kilo modes).

        Built-in modes (architect, code, ask, debug, orchestrator) are
        excluded because they are built into Kilo itself.

        Returns:
            List of custom mode slugs.

        Example:
            >>> builder = KiloCLIBuilder()
            >>> modes = builder.custom_modes
            >>> print([m for m in modes if m not in builder._kilo_builtin_modes])
            ['refactor', 'document', 'review', ...]
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

        Example:
            >>> from pathlib import Path
            >>> builder = KiloCLIBuilder()
            >>> # Normal run
            >>> actions = builder.build(Path("./output"))
            >>> # Dry run
            >>> actions = builder.build(Path("./output"), dry_run=True)
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
        """Generate opencode.json configuration file.

        Creates the opencode.json file that tells OpenCode which
        instruction files to load and in what order.

        Args:
            output: Output directory path.
            dry_run: If True, return preview without writing.

        Returns:
            Action string describing the operation.

        Example:
            >>> action = self._create_opencode_json(Path("."), False)
            >>> print(action)
            ✓ opencode.json
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

        Example:
            >>> content = self._get_agents_md_content()
            >>> print(len(content) > 0)
            True
        """
        path = Path(__file__).parent / "AGENTS_KILO_CLI.md"
        if not path.exists():
            raise ValueError("The AGENTS.md file was not found.")
        return path.read_text(encoding="utf-8")
