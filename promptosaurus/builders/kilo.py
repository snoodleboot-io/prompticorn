"""
builders/kilo.py
Builds the .opencode/rules/ directory structure for Kilo Code.

Output layout:
  {output}/AGENTS.md                    ← user guide
  {output}/.opencode/rules/_base.md    ← collapsed core files
  {output}/.opencode/rules/{MODE}.md   ← collapsed mode files (architect, code, ask, orchestrator, debug)
  {output}/.kilocodemodes              ← manifest for remaining custom modes
"""

import shutil
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from promptosaurus.builders.builder import Builder
from promptosaurus.registry import registry


class KiloBuilder(Builder):
    """Builder for Kilo Code .opencode/rules/ directory structure."""

    # Map of language names to their core file suffixes
    LANGUAGE_FILE_MAP: dict[str, str] = {
        "python": "core-py.md",
        "typescript": "core-ts.md",
        "javascript": "core-js.md",
        "php": "core-php.md",
        "ruby": "core-ruby.md",
        "java": "core-java.md",
        "csharp": "core-cs.md",
        "go": "core-go.md",
        "rust": "core-rust.md",
        "r": "core-r.md",
        "elixir": "core-elixir.md",
        "elm": "core-elm.md",
        "c": "core-c.md",
        "cpp": "core-cpp.md",
        "scala": "core-scala.md",
        "kotlin": "core-kotlin.md",
        "swift": "core-swift.md",
        "objc": "core-objc.md",
        "dart": "core-dart.md",
        "julia": "core-julia.md",
        "haskell": "core-haskell.md",
        "clojure": "core-clojure.md",
        "fsharp": "core-fsharp.md",
        "shell": "core-shell.md",
        "groovy": "core-groovy.md",
        "lua": "core-lua.md",
        "sql": "core-sql.md",
        "terraform": "core-terraform.md",
        "html": "core-html.md",
    }

    # All modes are collapsed into single .opencode/rules/{MODE}.md files
    # (modes are sourced from registry.modes)

    # Core files that get concatenated into _base.md
    BASE_FILES = [
        "core-system.md",
        "core.md",
        "core-session.md",
    ]

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
        selected_language = config.get("defaults", {}).get("language", "") if config else ""
        language_file = (
            self.LANGUAGE_FILE_MAP.get(selected_language.lower()) if selected_language else None
        )

        # 1. Create AGENTS.md user guide
        actions.append(self._create_agents_md(output, dry_run))

        # 2. Create _base.md (collapsed core files + language convention)
        actions.append(self._create_base_md(rules_dir, language_file, dry_run, config))

        # 3. Create collapsed mode files for all modes
        for mode_key in registry.modes.keys():
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
        # Add all mode files
        for mode_key in sorted(registry.modes.keys()):
            instructions.append(f".opencode/rules/{mode_key}.md")

        data = {
            "instructions": instructions,
        }

        import json

        content = json.dumps(data, indent=2)

        if dry_run:
            return f"[dry-run] {label}"
        destination.write_text(content, encoding="utf-8")
        return f"✓ {label}"

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
        if config and source_path.name.startswith("core-"):
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

    def _create_agents_md(self, output: Path, dry_run: bool) -> str:
        """Create AGENTS.md user guide."""
        destination = output / "AGENTS.md"
        label = "AGENTS.md"

        content = """# Kilo Code Agents

This directory contains the agent instructions for Kilo Code.

## Structure

- **`AGENTS.md`** (this file) — User guide for understanding the agents
- **`.opencode/rules/_base.md`** — Core behaviors, conventions, and session management (always loaded)
- **`.opencode/rules/{MODE}.md`** — Mode-specific behaviors for each agent

## Available Agents

All agents are collapsed into individual `.opencode/rules/{MODE}.md` files:

| Mode | Purpose |
|------|---------|
| **architect** | Scaffold projects, create task breakdowns, design data models |
| **code** | Feature implementation and boilerplate generation |
| **ask** | Q&A, decision logs, and documentation lookup |
| **orchestrator** | CI/CD, DevOps, and PR descriptions |
| **debug** | Root cause analysis, log analysis, and problem solving |
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

        if dry_run:
            return f"[dry-run] {label}"

        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")
        return f"✓ {label}"

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
