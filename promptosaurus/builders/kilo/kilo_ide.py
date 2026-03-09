"""Kilo Code IDE builder - outputs .kilocode/rules-{mode}/ structure.

This module provides the KiloIDEBuilder class that generates the configuration
files for Kilo Code in IDE format (used by VSCode/JetBrains extensions).

Output layout:
  {output}/.kilocode/rules/                 <- core files (always loaded)
  {output}/.kilocode/rules-{mode}/           <- per-mode directories with files
  {output}/.kilocodemodes                <- all mode definitions (for IDE)
  {output}/.kiloignore                  <- ignore patterns

This format is used by the KiloCode IDE extensions (VSCode/JetBrains).

Functions:
    _make_dest_filename: Convert prompt source path to destination filename.
    _flatten_agent_path: Flatten agent path by removing mode prefix dynamically.

Classes:
    KiloIDEBuilder: Builder for Kilo Code .kilocode/rules-{mode}/ directory structure.

Example:
    >>> from pathlib import Path
    >>> from promptosaurus.builders.kilo.kilo_ide import KiloIDEBuilder
    >>> builder = KiloIDEBuilder()
    >>> actions = builder.build(Path("./output"))
    >>> for action in actions[:3]:
    ...     print(action)
    ✓ AGENTS.md
    ✓ core-system.md → .kilocode/rules/core-system.md
    ✓ core-conventions.md → .kilocode/rules/core-conventions.md
"""

from pathlib import Path
from typing import Any

from promptosaurus.builders.kilo.kilo_code_builder import KiloCodeBuilder
from promptosaurus.registry import registry


def _make_dest_filename(filename: str, mode_key: str | None = None) -> str:
    """Convert prompt source path to destination filename.

    This function transforms the prompt source file paths into appropriate
    destination filenames based on the file type and mode.

    Mapping rules:
    - agents/core/core-conventions-{lang}.md -> conventions-{lang}.md (language goes to rules/)
    - agents/core/core-{slug}.md -> {slug}.md (core files go to rules/)
    - agents/{agent}/subagents/{agent}-{slug}.md -> {slug}.md (subagent files)
    - agents/{agent}/{agent}.md -> {agent}.md (root agent files)
    - Any other agents/{agent}/ path -> flatten (remove subagents folder and agent prefix)

    Args:
        filename: The source prompt filename.
        mode_key: Optional mode key for agent file transformations.

    Returns:
        The destination filename.

    Example:
        >>> _make_dest_filename("agents/core/core-system.md")
        'system.md'
        >>> _make_dest_filename("agents/core/core-conventions-python.md")
        'conventions-python.md'
        >>> _make_dest_filename("agents/code/subagents/code-feature.md", "code")
        'feature.md'
    """
    # Handle core files first
    if filename.startswith("agents/core/core-conventions-"):
        return filename[17:]  # Keep "conventions-{lang}.md"
    if filename.startswith("agents/core/core-"):
        return filename[17:]  # Remove "agents/core/core-"

    # Handle agent files
    if not mode_key:
        return filename

    # Check for subagents: agents/{mode}/subagents/{mode}-{slug}.md -> {slug}.md
    subagents_prefix = f"agents/{mode_key}/subagents/{mode_key}-"
    if filename.startswith(subagents_prefix):
        return filename[len(subagents_prefix) :]

    # Check for root agent file: agents/{mode}.md -> {mode}.md
    if filename == f"agents/{mode_key}.md":
        return f"{mode_key}.md"

    # For any other agents/{something}/ path, flatten it
    # e.g. agents/code/subagents/code-feature.md -> when in migration mode
    if filename.startswith("agents/"):
        return _flatten_agent_path(filename, mode_key)

    return filename


def _flatten_agent_path(filename: str, mode_key: str) -> str:
    """Flatten agent path by removing mode prefix dynamically.

    Extracts the mode prefix from the filename itself rather than
    using a hardcoded list. This handles cases where prompts are
    organized in non-standard ways.

    Args:
        filename: The source prompt filename to flatten.
        mode_key: The mode key being processed.

    Returns:
        The flattened filename with mode prefix removed.

    Example:
        >>> _flatten_agent_path("agents/code/subagents/code-feature.md", "code")
        'feature.md'
        >>> _flatten_agent_path("agents/refactor/subagents/refactor-structure.md", "refactor")
        'structure.md'
    """
    slash1 = filename.find("/")
    if slash1 <= 0:
        return filename

    slash2 = filename.find("/", slash1 + 1)
    if slash2 <= 0:
        return filename

    remainder = filename[slash2 + 1 :]

    # Remove "subagents/" if present
    if remainder.startswith("subagents/"):
        remainder = remainder[10:]

    # Dynamically detect and remove mode prefix from filename
    # e.g., "code-feature.md" -> "feature.md" by detecting "-{suffix}"
    dash_pos = remainder.rfind("-")
    if dash_pos > 0:
        potential_prefix = remainder[:dash_pos]
        # Check if this looks like a valid mode prefix (simple heuristic)
        if len(potential_prefix) > 2 and potential_prefix.islower():
            return remainder[dash_pos + 1 :]

    return remainder


class KiloIDEBuilder(KiloCodeBuilder):
    """Builder for Kilo Code .kilocode/rules-{mode}/ directory structure (IDE format).

    This builder creates the IDE-format configuration used by the KiloCode
    VSCode and JetBrains extensions. It generates:
    - AGENTS.md: User guide
    - .kilocode/rules/: Core convention files (always loaded)
    - .kilocode/rules-{mode}/: Per-mode directories with individual files
    - .kilocodemodes: All mode definitions
    - .kiloignore: Ignore patterns

    The IDE format keeps each prompt as a separate file in mode-specific
    directories, allowing for more granular control.

    Attributes:
        Inherits all attributes from KiloCodeBuilder.

    Example:
        >>> builder = KiloIDEBuilder()
        >>> # Build files
        >>> actions = builder.build(Path("./my-project"))
        >>> print(f\"Generated {len(actions)} files\")
    """

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Write the Kilo .kilocode/rules-{mode}/ structure under `output`.

        Generates the IDE-format configuration by:
        1. Creating AGENTS.md user guide
        2. Creating core files in .kilocode/rules/
        3. Adding language-specific conventions if selected
        4. Creating per-mode directories with individual files
        5. Generating .kilocodemodes manifest
        6. Building .kiloignore

        Args:
            output: Directory path where files will be created.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings describing what was created.

        Example:
            >>> from pathlib import Path
            >>> builder = KiloIDEBuilder()
            >>> # Normal run
            >>> actions = builder.build(Path("./output"))
            >>> # Dry run
            >>> actions = builder.build(Path("./output"), dry_run=True)
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
        for filename in self._config.base_files:
            source_path = registry.prompt_path(filename)
            if not source_path.exists():
                continue
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
            if mode_key not in registry.mode_files:
                continue
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
        """Get the AGENTS.md content for IDE format by reading from template file.

        Returns:
            The content for the AGENTS.md file.

        Raises:
            ValueError: If the AGENTS.md template file is not found.

        Example:
            >>> content = self._get_agents_md_content()
            >>> print(len(content) > 0)
            True
        """
        path = Path(__file__).parent / "AGENTS_KILO_IDE.md"
        if not path.exists():
            raise ValueError("The AGENTS.md file was not found.")
        return path.read_text(encoding="utf-8")
