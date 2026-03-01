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

import yaml  # type: ignore[import-untyped]

from promptcli.builders.builder import Builder
from promptcli.registry import registry


class KiloBuilder(Builder):
    """Builder for Kilo Code .kilo/ directory structure."""

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """
        Write the Kilo .kilo/ structure under `output`.
        Returns a list of action strings for display.
        """
        actions: list[str] = []
        base = output / ".kilo"

        # Always-on rules
        for filename in registry.always_on:
            destination = base / "rules" / filename
            actions.append(self._copy(registry.prompt_path(filename), destination, dry_run))

        # Per-mode rules
        for mode_key, files in registry.mode_files.items():
            for filename in files:
                destination = base / f"rules-{mode_key}" / registry.dest_name(mode_key, filename)
                actions.append(self._copy(registry.prompt_path(filename), destination, dry_run))

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

    def _copy(self, source_path: Path, destination: Path, dry_run: bool) -> str:
        rel = str(destination).split(".kilo/", 1)[-1]
        label = f".kilo/{rel}"
        if dry_run:
            return f"[dry-run] {source_path.name} → {label}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, destination)
        return f"✓ {source_path.name} → {label}"

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
