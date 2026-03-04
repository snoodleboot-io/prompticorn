"""
builders/kilo.py
Builds the .kilo/ directory structure for Kilo Code.

Output layout:
  {output}/.kilo/rules/              ← always-on (all modes)
  {output}/.kilo/rules-{mode}/       ← per-mode files
  {output}/.kilocodemodes           ← manifest defining custom modes
"""

import shutil
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from promptosaurus.builders.builder import Builder
from promptosaurus.registry import registry


class KiloBuilder(Builder):
    """Builder for Kilo Code .kilo/ directory structure."""

    # Map of language names to their core-conventions file suffixes
    LANGUAGE_FILE_MAP: dict[str, str] = {
        "python": "core-conventions-py.md",
        "typescript": "core-conventions-ts.md",
        "javascript": "core-conventions-js.md",
        "php": "core-conventions-php.md",
        "ruby": "core-conventions-ruby.md",
        "java": "core-conventions-java.md",
        "csharp": "core-conventions-cs.md",
        "go": "core-conventions-go.md",
        "rust": "core-conventions-rust.md",
        "r": "core-conventions-r.md",
        "elixir": "core-conventions-elixir.md",
        "elm": "core-conventions-elm.md",
        "c": "core-conventions-c.md",
        "cpp": "core-conventions-cpp.md",
        "scala": "core-conventions-scala.md",
        "kotlin": "core-conventions-kotlin.md",
        "swift": "core-conventions-swift.md",
        "objc": "core-conventions-objc.md",
        "dart": "core-conventions-dart.md",
        "julia": "core-conventions-julia.md",
        "haskell": "core-conventions-haskell.md",
        "clojure": "core-conventions-clojure.md",
        "fsharp": "core-conventions-fsharp.md",
        "shell": "core-conventions-shell.md",
        "groovy": "core-conventions-groovy.md",
        "lua": "core-conventions-lua.md",
        "sql": "core-conventions-sql.md",
        "terraform": "core-conventions-terraform.md",
        "html": "core-conventions-html.md",
    }

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """
        Write the Kilo .kilo/ structure under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []
        base = output / ".kilo"

        # Get selected language from config
        selected_language = config.get("defaults", {}).get("language", "") if config else ""
        language_file = (
            self.LANGUAGE_FILE_MAP.get(selected_language.lower()) if selected_language else None
        )

        # Always-on rules (filter language-specific files)
        for filename in registry.always_on:
            # Skip language-specific files that don't match the selected language
            if filename.startswith("core-conventions-") and filename != language_file:
                continue

            destination = base / "rules" / filename
            actions.append(self._copy(registry.prompt_path(filename), destination, dry_run, config))

        # Per-mode rules
        for mode_key, files in registry.mode_files.items():
            for filename in files:
                destination = base / f"rules-{mode_key}" / registry.dest_name(mode_key, filename)
                actions.append(
                    self._copy(registry.prompt_path(filename), destination, dry_run, config)
                )

        # Generate .kilocodemodes manifest
        actions.append(self._write_manifest(output / ".kilocodemodes", dry_run))

        # Build .kiloignore
        actions.extend(self._build_ignore(output, dry_run))

        return actions

    def _write_manifest(self, destination: Path, dry_run: bool) -> str:
        """Write the .kilocodemodes manifest file."""
        # Build data structure for YAML
        modes = []
        for mode_key, mode_info in registry.kilo_modes.items():
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

    def _copy(
        self,
        source_path: Path,
        destination: Path,
        dry_run: bool,
        config: dict[str, Any] | None = None,
    ) -> str:
        rel = str(destination).split(".kilo/", 1)[-1]
        label = f".kilo/{rel}"
        if dry_run:
            return f"[dry-run] {source_path.name} → {label}"
        destination.parent.mkdir(parents=True, exist_ok=True)

        # If config is provided and this is a language-specific conventions file,
        # perform template substitution
        if config and source_path.name.startswith("core-conventions-"):
            content = source_path.read_text(encoding="utf-8")
            content = self._substitute_template_variables(content, config)
            destination.write_text(content, encoding="utf-8")
        else:
            shutil.copy2(source_path, destination)

        return f"✓ {source_path.name} → {label}"

    def _substitute_template_variables(self, content: str, config: dict[str, Any]) -> str:
        """Replace {{VARIABLE}} templates with values from config."""
        defaults = config.get("defaults", {})

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
