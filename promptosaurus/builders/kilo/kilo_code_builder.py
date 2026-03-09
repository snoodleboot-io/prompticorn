"""
builders/kilo_code_builder.py
Base class for Kilo Code configuration builders.

Common functionality shared between CLI and IDE targets.
"""

import shutil
from pathlib import Path
from typing import Any

from promptosaurus.builders.builder import Builder
from promptosaurus.builders.config import KiloConfig
from promptosaurus.builders.ignore_generator import KiloIgnoreBuilder
from promptosaurus.builders.utils import HeaderStripper
from promptosaurus.registry import registry


class KiloCodeBuilder(Builder):
    """Base builder for Kilo Code configurations.

    Args:
        config: Optional KiloConfig instance. If not provided, uses default config.
    """

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

    def __init__(self, config: KiloConfig | None = None) -> None:
        """Initialize builder with optional config.

        Args:
            config: KiloConfig instance. Uses default if not provided.
        """
        self._config = config or KiloConfig()

    @property
    def kilo_modes(self) -> dict[str, Any]:
        """Return the kilo modes from config."""
        return self._config.kilo_modes

    @property
    def language_file_map(self) -> dict[str, str]:
        """Return the language file map from config."""
        return self._config.language_file_map

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Build Kilo Code configuration. Subclasses implement specific output formats.
        Returns a list of action strings for display.
        """
        raise NotImplementedError()

    def _get_agents_md_content(self) -> str:
        """Get the AGENTS.md content specific to the builder type."""
        raise NotImplementedError()

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
        # Coverage can be either a dict (legacy) or a string preset from the question
        coverage_value = defaults.get("coverage", {})

        # If coverage is a string preset, convert it to a dict
        if isinstance(coverage_value, str):
            COVERAGE_PRESETS = {
                "strict": {
                    "line": 90,
                    "branch": 80,
                    "function": 95,
                    "statement": 90,
                    "mutation": 85,
                    "path": 70,
                },
                "standard": {
                    "line": 80,
                    "branch": 70,
                    "function": 90,
                    "statement": 85,
                    "mutation": 80,
                    "path": 60,
                },
                "minimal": {
                    "line": 70,
                    "branch": 60,
                    "function": 80,
                    "statement": 75,
                    "mutation": 70,
                    "path": 50,
                },
            }
            coverage = COVERAGE_PRESETS.get(coverage_value, {})
        else:
            coverage = coverage_value if isinstance(coverage_value, dict) else {}

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
        """Write the .kilocodemodes manifest file.

        Simply copies the kilo_modes.yaml source file to preserve exact formatting.
        """
        # Read from the source YAML file to preserve exact formatting
        source_path = Path(__file__).parent / "kilo_modes.yaml"

        if dry_run:
            return "[dry-run] .kilocodemodes (copied from kilo_modes.yaml)"

        # Copy the file content directly
        content = source_path.read_text(encoding="utf-8")
        destination.write_text(content, encoding="utf-8")
        return "✓ .kilocodemodes"

    def _build_ignore(self, output: Path, dry_run: bool) -> list[str]:
        """Generate .kiloignore file."""
        return KiloIgnoreBuilder().build(output, dry_run)

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

        for filename in self._base_files:
            source_path = registry.prompt_path(filename)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                parts.append(HeaderStripper.strip(content))

        # Add language-specific conventions if selected
        if language_file:
            source_path = registry.prompt_path(language_file)
            if source_path.exists():
                content = source_path.read_text(encoding="utf-8")
                # Apply template substitution for language files
                if config:
                    content = self._substitute_template_variables(content, config)
                parts.append(HeaderStripper.strip(content))

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
                parts.append(HeaderStripper.strip(content))

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
