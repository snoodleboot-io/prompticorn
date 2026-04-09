"""Kilo Code IDE builder - outputs .kilo/agents/*.md structure (new format).

This module provides the KiloIDEBuilder class that generates the configuration
files for Kilo in the new format (individual agent markdown files).

Output layout:
  {output}/.kilocode/rules/                 <- core files (always loaded)
  {output}/.kilo/agents/                    <- individual agent files (new format)
  {output}/.kiloignore                      <- ignore patterns

This format is used by the current Kilo platform (>= 2.0).

Note: Legacy .kilocode/rules-{mode}/ and .kilocodemodes are no longer generated.

Functions:
    _make_dest_filename: Convert prompt source path to destination filename.
    _flatten_agent_path: Flatten agent path by removing mode prefix dynamically.

Classes:
    KiloIDEBuilder: Builder for Kilo .kilo/agents/*.md directory structure.
"""

import re
import yaml
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
    """Builder for Kilo .kilo/agents/*.md directory structure (new format).

    This builder creates the new-format configuration for Kilo IDE (>= 2.0).
    It generates:
    - AGENTS.md: User guide
    - .kilocode/rules/: Core convention files (always loaded)
    - .kilo/agents/{agent-name}.md: Individual agent files with YAML frontmatter
    - .kiloignore: Ignore patterns

    The new format uses individual markdown files with YAML frontmatter,
    replacing the legacy .kilocode/rules-{mode}/ directory structure.

    Attributes:
        Inherits all attributes from KiloCodeBuilder.
    """

    # Map mode slugs to colors for UI theming
    MODE_COLORS = {
        "architect": "#FF9500",
        "test": "#7C3AED",
        "refactor": "#059669",
        "document": "#06B6D4",
        "explain": "#14B8A6",
        "migration": "#3B82F6",
        "review": "#EC4899",
        "security": "#EF4444",
        "compliance": "#8B5CF6",
        "enforcement": "#F59E0B",
        "planning": "#6366F1",
        "general": "#4B5563",
    }

    def build(
        self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False
    ) -> list[str]:
        """Write the Kilo .kilo/agents/*.md structure under `output`.

        Generates the new-format configuration by:
        1. Creating AGENTS.md user guide
        2. Creating core files in .kilocode/rules/
        3. Adding language-specific conventions if selected
        4. Creating individual agent files in .kilo/agents/
        5. Building .kiloignore

        Args:
            output: Directory path where files will be created.
            config: Optional configuration dict with template variables.
            dry_run: If True, preview what would be written without touching filesystem.

        Returns:
            List of action strings describing what was created.
        """
        actions: list[str] = []

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

        # 2. Create core files in .kilocode/rules/
        for filename in self._config.base_files:
            source_path = registry.prompt_path(filename)
            if not source_path.exists():
                continue
            new_filename = _make_dest_filename(filename)  # No mode_key for core files
            destination = output / ".kilocode" / "rules" / new_filename
            actions.append(self._copy(source_path, destination, dry_run, config))

        # 2b. Add language-specific conventions for ALL languages in multi-language monorepo
        languages_added: set[str] = set()
        for selected_language in selected_languages:
            language_file = (
                self.language_file_map.get(selected_language.lower()) if selected_language else None
            )
            if language_file and selected_language.lower() not in languages_added:
                source_path = registry.prompt_path(language_file)
                if source_path.exists():
                    new_filename = _make_dest_filename(language_file)
                    destination_rules = output / ".kilocode" / "rules" / new_filename
                    actions.append(self._copy(source_path, destination_rules, dry_run, config))
                    languages_added.add(selected_language.lower())

        # 3. Create individual agent files in .kilo/agents/ (NEW FORMAT)
        actions.extend(self._write_agents_md_files(output, dry_run))

        # 4. Build .kiloignore
        actions.extend(self._build_ignore(output, dry_run))

        return actions

    def _write_agents_md_files(self, output: Path, dry_run: bool) -> list[str]:
        """Generate individual .kilo/agents/{agent-name}.md files from kilo_modes.yaml.

        Reads the kilo_modes.yaml file and creates individual markdown files
        for each mode, with YAML frontmatter containing metadata and permissions.

        Args:
            output: Output directory path.
            dry_run: If True, return preview without writing.

        Returns:
            List of action strings describing generated files.
        """
        actions: list[str] = []
        agents_dir = output / ".kilo" / "agents"

        # Read kilo_modes.yaml to get mode definitions
        kilo_modes_path = Path(__file__).parent / "kilo_modes.yaml"
        if not kilo_modes_path.exists():
            return [f"[ERROR] kilo_modes.yaml not found at {kilo_modes_path}"]

        try:
            with open(kilo_modes_path, encoding="utf-8") as f:
                kilo_data = yaml.safe_load(f)
        except Exception as e:
            return [f"[ERROR] Failed to parse kilo_modes.yaml: {e}"]

        custom_modes = kilo_data.get("customModes", [])
        if not custom_modes:
            return ["[WARNING] No customModes found in kilo_modes.yaml"]

        # Generate one .md file per mode
        for mode_def in custom_modes:
            slug = mode_def.get("slug", "").lower()
            if not slug:
                continue

            # Extract mode metadata
            description = mode_def.get("description", "")
            role_definition = mode_def.get("roleDefinition", "")
            when_to_use = mode_def.get("whenToUse", "")
            groups = mode_def.get("groups", [])

            # Map permissions from old format to new format
            permission_obj = self._map_groups_to_permissions(groups)

            # Get color for this mode
            color = self.MODE_COLORS.get(slug, "#4B5563")  # Default: gray

            # Build YAML frontmatter
            frontmatter = self._build_frontmatter(
                description=description,
                mode="primary",
                permission=permission_obj,
                color=color,
            )

            # Build markdown body (roleDefinition + whenToUse)
            body_parts = []
            if role_definition:
                body_parts.append(role_definition.strip())
            if when_to_use:
                body_parts.append(when_to_use.strip())
            body = "\n\n".join(body_parts) if body_parts else ""

            # Combine frontmatter and body
            if body:
                file_content = f"{frontmatter}\n\n{body}"
            else:
                file_content = frontmatter

            # Write to file
            if dry_run:
                actions.append(f"[dry-run] .kilo/agents/{slug}.md")
            else:
                destination = agents_dir / f"{slug}.md"
                try:
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_text(file_content, encoding="utf-8")
                    actions.append(f"✓ .kilo/agents/{slug}.md")
                except Exception as e:
                    actions.append(f"[ERROR] Failed to write {slug}.md: {e}")

        return actions

    def _map_groups_to_permissions(self, groups: list[Any]) -> dict[str, Any]:
        """Map old 'groups' format to new 'permission' object format.

        Converts the legacy groups array format to the new permission object format:
        - Old: [["read"], ["edit", [{fileRegex: "..."}]], ["command"]]
        - New: {read: {*: allow}, edit: {...}, bash: allow}

        Args:
            groups: The groups array from kilo_modes.yaml.

        Returns:
            Permission object dict suitable for YAML frontmatter.
        """
        permission: dict[str, Any] = {}

        # Process each group entry
        for group_entry in groups:
            if isinstance(group_entry, str):
                # Simple permission: "read", "edit", "command", "browser"
                if group_entry == "read":
                    permission["read"] = {"*": "allow"}
                elif group_entry == "edit":
                    # Unrestricted edit
                    permission["edit"] = {"*": "allow"}
                elif group_entry == "command":
                    # Allow bash commands
                    permission["bash"] = "allow"
                elif group_entry == "browser":
                    # Browser access: No direct mapping in current Kilo format
                    # Deferred to Phase 2 - may map to webfetch/websearch
                    pass

            elif isinstance(group_entry, list) and len(group_entry) >= 2:
                # Complex permission with restrictions: ["edit", [{fileRegex: "..."}]]
                perm_type = group_entry[0]
                restrictions = group_entry[1]

                if perm_type == "edit":
                    permission["edit"] = {}
                    # Add file patterns from restrictions
                    if isinstance(restrictions, list):
                        for restriction in restrictions:
                            if isinstance(restriction, dict):
                                file_regex = restriction.get("fileRegex", "")
                                # Convert regex patterns to glob-like patterns
                                glob_pattern = file_regex  # Use regex as-is for MVP
                                if glob_pattern:
                                    permission["edit"][glob_pattern] = "allow"
                    # Deny by default
                    permission["edit"]["*"] = "deny"

        # Ensure read permission exists (if not explicitly set)
        if "read" not in permission:
            permission["read"] = {"*": "allow"}

        return permission

    def _regex_to_glob(self, regex_pattern: str) -> str:
        """Convert regex file pattern to glob pattern.

        Attempts to convert regex patterns to glob patterns for readability.
        Falls back to regex pattern if conversion is complex.

        Args:
            regex_pattern: Regex pattern string.

        Returns:
            Glob-style pattern string.
        """
        # Simple conversions
        # Replace regex escape sequences with glob patterns
        pattern = regex_pattern

        # Handle common patterns
        # (docs|path)/something.md$ -> docs/**/*.md or path/**/*.md
        if pattern.startswith("(") and "|" in pattern:
            # Extract alternatives: (docs|path)/...
            match = re.match(r"\(([^)]+)\)", pattern)
            if match:
                alts = match.group(1).split("|")
                # For now, use first alternative (could extend to generate multiple)
                pattern = pattern.replace(f"({match.group(1)})", alts[0])

        # Remove common regex anchors
        pattern = pattern.rstrip("$")
        pattern = pattern.lstrip("^")

        # Convert regex . to * (with caution)
        if pattern.startswith("."):
            pattern = pattern.replace(".", "")

        # Unescape common patterns
        pattern = pattern.replace(r"\.", ".")
        pattern = pattern.replace(r"\/", "/")
        pattern = pattern.replace(r"\d+", "*")
        pattern = pattern.replace(r"\w+", "*")

        # If pattern still has regex metacharacters, keep it as-is
        if re.search(r"[\\^$|?+\(\)\[\]{}]", pattern.replace("*", "")):
            return regex_pattern

        # Clean up any remaining oddities
        pattern = pattern.strip()
        if pattern.endswith("/"):
            pattern += "**"

        return pattern if pattern else regex_pattern

    def _build_frontmatter(
        self,
        description: str,
        mode: str,
        permission: dict[str, Any],
        color: str,
    ) -> str:
        """Build YAML frontmatter for an agent markdown file.

        Args:
            description: Agent description.
            mode: Agent mode ("primary", "subagent", etc).
            permission: Permission object dict.
            color: Hex color code.

        Returns:
            YAML frontmatter string (with leading/trailing ---).
        """
        # Build YAML dict
        frontmatter_dict = {
            "description": description,
            "mode": mode,
            "permission": permission,
            "color": color,
        }

        # Serialize to YAML
        yaml_str = yaml.dump(frontmatter_dict, default_flow_style=False, sort_keys=False)

        # Return wrapped in --- markers
        return f"---\n{yaml_str}\n---"

    def _validate_agent_file(self, file_path: Path) -> bool:
        """Validate that a generated agent file has correct format.
        
        Checks:
        - YAML frontmatter is parseable
        - Required fields present: description, mode, permission
        - Permission object has correct structure
        
        Args:
            file_path: Path to the generated .md file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Extract frontmatter
            if not content.startswith("---"):
                return False
            
            # Find closing ---
            end_marker = content.find("---", 3)
            if end_marker == -1:
                return False
            
            frontmatter_str = content[3:end_marker].strip()
            
            # Parse YAML
            import yaml
            frontmatter = yaml.safe_load(frontmatter_str)
            
            # Check required fields
            required_fields = ["description", "mode", "permission"]
            for field in required_fields:
                if field not in frontmatter:
                    return False
            
            # Check permission structure (should be dict)
            if not isinstance(frontmatter.get("permission"), dict):
                return False
            
            return True
        except Exception:
            return False

    def _log_agent_creation(self, slug: str, permission: dict[str, Any]) -> None:
        """Log agent file creation for debugging.
        
        Args:
            slug: Agent slug/name
            permission: Permission object
        """
        # Build simple permission summary
        perms = []
        if "read" in permission:
            perms.append("read")
        if "edit" in permission:
            edit_rules = permission["edit"]
            if isinstance(edit_rules, dict):
                restricted = any(k != "*" for k in edit_rules.keys())
                perms.append(f"edit{'(restricted)' if restricted else ''}")
        if "bash" in permission:
            perms.append("bash")
        
        # For debugging: could add logging here in future
        # For now, just silently track that we processed it
        pass

    def _get_agents_md_content(self) -> str:
        """Get the AGENTS.md content for IDE format by reading from template file.

        Returns:
            The content for the AGENTS.md file.

        Raises:
            ValueError: If the AGENTS.md template file is not found.
        """
        path = Path(__file__).parent / "AGENTS_KILO_IDE.md"
        if not path.exists():
            raise ValueError("The AGENTS.md file was not found.")
        return path.read_text(encoding="utf-8")

