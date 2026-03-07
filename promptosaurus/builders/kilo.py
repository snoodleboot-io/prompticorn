"""
builders/kilo.py
Base class for Kilo Code configuration builders.

Common functionality shared between CLI and IDE targets.
"""

import shutil
from abc import abstractmethod
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from promptosaurus.builders.builder import Builder
from promptosaurus.registry import registry


def _load_kilo_modes_from_yaml() -> dict[str, Any]:
    """Load kilo modes from the YAML file in the builders directory."""
    yaml_path = Path(__file__).parent / "kilo_modes.yaml"
    if not yaml_path.exists():
        msg = (
            f"Kilo modes YAML file not found: {yaml_path}\n"
            "Please ensure kilo_modes.yaml exists in the promptosaurus/builders/ directory."
        )
        raise FileNotFoundError(msg)

    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data.get("modes", {})


def _load_language_file_map_from_yaml() -> dict[str, str]:
    """Load language file map from the YAML file in the builders directory."""
    yaml_path = Path(__file__).parent / "kilo_language_file_map.yaml"
    if not yaml_path.exists():
        msg = (
            f"Language file map YAML not found: {yaml_path}\n"
            "Please ensure kilo_language_file_map.yaml exists in the promptosaurus/builders/ directory."
        )
        raise FileNotFoundError(msg)

    with yaml_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data.get("language_file_map", {})


# Load YAML at module level (not in class __init_subclass__)
_KILO_MODES: dict[str, Any] = _load_kilo_modes_from_yaml()
_LANGUAGE_FILE_MAP: dict[str, str] = _load_language_file_map_from_yaml()


class KiloCodeBuilder(Builder):
    """Base builder for Kilo Code configurations."""

    # Modes that are built-in to Kilo and should not be generated in output
    _kilo_builtin_modes = frozenset(
        {
            "architect",
            "code",
            "ask",
            "debug",
            "orchestrator",
        }
    )

    # Use YAML loaded at module level
    _kilo_modes: dict[str, Any] = _KILO_MODES
    _language_file_map: dict[str, str] = _LANGUAGE_FILE_MAP

    @property
    def kilo_modes(self) -> dict[str, Any]:
        """Return the kilo modes loaded from YAML."""
        return self._kilo_modes

    @property
    def language_file_map(self) -> dict[str, str]:
        """Return the language file map loaded from YAML."""
        return self._language_file_map

    @property
    def custom_modes(self) -> list[str]:
        """Return list of custom modes (excluding built-in Kilo modes)."""
        return [m for m in registry.modes.keys() if m not in self._kilo_builtin_modes]

    # Core files that get concatenated into _base.md
    BASE_FILES = [
        "agents/core/core-system.md",
        "agents/core/core-conventions.md",
        "agents/core/core-session.md",
    ]

    @abstractmethod
    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Build Kilo Code configuration. Subclasses implement specific output formats.
        Returns a list of action strings for display.
        """
        pass

    @abstractmethod
    def _get_agents_md_content(self) -> str:
        """Get the AGENTS.md content specific to the builder type."""
        pass

    def _copy(
        self,
        source_path: Path,
        destination: Path,
        dry_run: bool,
        config: dict[str, Any] | None = None,
    ) -> str:
        rel = str(destination).split(".kilocode/", 1)[-1]
        label = f".kilocode/{rel}"
        if dry_run:
            return f"[dry-run] {source_path.name} → {label}"
        destination.parent.mkdir(parents=True, exist_ok=True)

        # If config is provided and this is a language-specific conventions file,
        # perform template substitution
        if config and source_path.name.startswith("core-"):
            content = source_path.read_text(encoding="utf-8")
            content = self._substitute_template_variables(content, config)
            destination.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(source_path, destination)

        return f"✓ {source_path.name} → {label}"

    def _substitute_template_variables(self, content: str, config: dict[str, Any]) -> str:
        """Replace {{VARIABLE}} templates with values from config."""
        defaults = config.get("spec", {})

        def format_value(value: Any) -> str:
            """Format a value for substitution, handling lists."""
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value) if value is not None else ""

        # Build mapping of template variables to config values
        substitutions: dict[str, str] = {
            "{{LANGUAGE}}": format_value(defaults.get("language", "")),
            "{{RUNTIME}}": format_value(defaults.get("runtime", "")),
            "{{PACKAGE_MANAGER}}": format_value(defaults.get("package_manager", "")),
            "{{LINTER}}": format_value(defaults.get("linter", "")),
            "{{FORMATTER}}": format_value(defaults.get("formatter", "")),
            "{{ABSTRACT_CLASS_STYLE}}": format_value(defaults.get("abstract_class_style", "")),
            "{{TESTING_FRAMEWORK}}": format_value(defaults.get("test_framework", "")),
            "{{TEST_RUNNER}}": format_value(defaults.get("test_runner", "")),
        }

        # Add coverage variables
        coverage = defaults.get("coverage", {})
        substitutions["{{LINE_COVERAGE_%}}"] = str(coverage.get("line", 80))
        substitutions["{{BRANCH_COVERAGE_%}}"] = str(coverage.get("branch", 70))
        substitutions["{{FUNCTION_COVERAGE_%}}"] = str(coverage.get("function", 90))
        substitutions["{{STATEMENT_COVERAGE_%}}"] = str(coverage.get("statement", 85))
        substitutions["{{MUTATION_COVERAGE_%}}"] = str(coverage.get("mutation", 80))
        substitutions["{{PATH_COVERAGE_%}}"] = str(coverage.get("path", 60))

        # Perform substitutions
        for template_var, value in substitutions.items():
            content = content.replace(template_var, value)

        return content

    def _write_manifest(self, destination: Path, dry_run: bool) -> str:
        """Write the .kilocodemodes manifest file."""
        # Build data structure for YAML
        modes = []
        for mode_key, mode_info in self.kilo_modes.items():
            mode_data = {
                "slug": mode_key,
                "name": mode_info.get("name", mode_key.title()),
                "description": mode_info.get("description", ""),
                "roleDefinition": mode_info.get("roleDefinition", ""),
                "whenToUse": mode_info.get("whenToUse", ""),
                "groups": mode_info.get("groups", ["read", "edit", "command"]),
            }
            modes.append(mode_data)

        data = {"customModes": modes}

        # Generate YAML
        content = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

        # Post-process: quote roleDefinition values that contain colons
        lines = content.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("    roleDefinition:"):
                key, value = line.split(":", 1)
                value = value.strip()
                # Quote if contains colon and not already quoted
                if ":" in value:
                    # Escape backslashes first, then quotes
                    value = value.replace("\\", "\\\\").replace('"', '\\"')
                    value = '"' + value + '"'
                line = f"{key}: {value}"
            new_lines.append(line)

        content = "\n".join(new_lines)

        label = ".kilocodemodes"

        if dry_run:
            return f"[dry-run] {label}"
        destination.write_text(content, encoding="utf-8")
        return f"✓ {label}"

    def _build_ignore(self, output: Path, dry_run: bool) -> list[str]:
        """Generate .kiloignore file."""
        destination = output / ".kiloignore"
        content = registry.generate_kiloignore()

        if dry_run:
            lines = content.count("\n")
            return [f"[dry-run] .kiloignore ({lines} lines)"]

        destination.write_text(content, encoding="utf-8")
        lines = content.count("\n")
        return [f"✓ .kiloignore ({lines} lines)"]

    def _create_base_md(
        self,
        rules_dir: Path,
        language_file: str | None,
        dry_run: bool,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Create _base.md by concatenating core files."""
        destination = rules_dir / "_base.md"
        label = ".opencode/rules/_base.md"

        if dry_run:
            return f"[dry-run] {label}"

        # Collect content from base files
        parts: list[str] = []

        for filename in self.BASE_FILES:
            source_path = registry.prompt_path(filename)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                # Strip header comments
                lines = content.splitlines(keepends=True)
                start = 0
                for i, line in enumerate(lines[:3]):
                    stripped = line.strip()
                    if stripped.startswith("# ") and (
                        stripped.endswith(".md") or "Behavior when" in stripped
                    ):
                        start = i + 1
                    elif stripped.startswith("<!--") and stripped.endswith("-->"):
                        start = i + 1
                parts.append("".join(lines[start:]))

        # Add language-specific conventions if selected
        if language_file:
            source_path = registry.prompt_path(language_file)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                # Apply template substitution for language files
                if config:
                    content = self._substitute_template_variables(content, config)
                # Strip header comments
                lines = content.splitlines(keepends=True)
                start = 0
                for i, line in enumerate(lines[:3]):
                    stripped = line.strip()
                    if stripped.startswith("# ") and stripped.endswith(".md"):
                        start = i + 1
                    elif stripped.startswith("<!--") and stripped.endswith("-->"):
                        start = i + 1
                parts.append("".join(lines[start:]))

        # Join all parts with clear separators
        full_content = "\n---\n\n".join(parts)

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(full_content, encoding="utf-8")
        return f"✓ {label}"

    def _create_collapsed_mode_md(
        self,
        rules_dir: Path,
        mode_key: str,
        filenames: list[str],
        dry_run: bool,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Create a collapsed {MODE}.md file from multiple subagent files."""
        destination = rules_dir / f"{mode_key}.md"
        label = f".opencode/rules/{mode_key}.md"

        if dry_run:
            return f"[dry-run] {label}"

        # Collect content from all subagent files
        parts: list[str] = []

        for filename in filenames:
            source_path = registry.prompt_path(filename)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                # Strip header comments
                lines = content.splitlines(keepends=True)
                start = 0
                for i, line in enumerate(lines[:3]):
                    stripped = line.strip()
                    if stripped.startswith("# ") and (
                        stripped.endswith(".md") or "Behavior when" in stripped
                    ):
                        start = i + 1
                    elif stripped.startswith("<!--") and stripped.endswith("-->"):
                        start = i + 1
                parts.append("".join(lines[start:]))

        # Join all parts with clear separators
        full_content = "\n---\n\n".join(parts)

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(full_content, encoding="utf-8")
        return f"✓ {label}"

    def _create_agents_md(self, output: Path, dry_run: bool) -> str:
        """Create AGENTS.md user guide."""
        destination = output / "AGENTS.md"
        label = "AGENTS.md"

        # Get builder-specific content
        content = self._get_agents_md_content()

        if dry_run:
            return f"[dry-run] {label}"

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return f"✓ {label}"


# NOTE: For backwards compatibility, import KiloBuilder from:
# - promptosaurus.builders.kilo_cli (CLI format, default)
# - promptosaurus.builders.kilo_ide (IDE format)
# - promptosaurus.builders (exports KiloBuilder as alias to KiloCLIBuilder)
# - promptosaurus.builders.kilo (this file, exports KiloCodeBuilder base class)
