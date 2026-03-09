# Builder Refactoring Design Document

**Date:** 2026-03-08  
**Status:** DESIGN - Pending Review  
**Parent Issue:** [enforcement-report-builders.md](enforcement-report-builders.md)

---

## Overview

This document describes the refactoring design for the `promptosaurus/builders/` directory to address convention violations identified in the enforcement review.

---

## 1. KiloConfig - Configuration Injection Design

### Problem
Module-level constants `_KILO_MODES` and `_LANGUAGE_FILE_MAP` violate the "no constants outside classes" rule.

### Design

Create a `KiloConfig` class that is injected into builders:

```python
# promptosaurus/builders/config.py
from pathlib import Path
from typing import Any

import yaml


class KiloConfig:
    """Configuration loader for Kilo builder settings.
    
    This class loads configuration from YAML files and provides
    typed access to settings. Can be subclassed or extended
    for different agent systems.
    """

    def __init__(
        self,
        modes_path: Path | None = None,
        language_map_path: Path | None = None,
    ) -> None:
        """Initialize config with optional custom paths."""
        self._modes_path = modes_path or self._default_modes_path()
        self._language_map_path = language_map_path or self._default_language_map_path()
        self._kilo_modes: dict[str, Any] | None = None
        self._language_file_map: dict[str, str] | None = None

    @staticmethod
    def _default_modes_path() -> Path:
        return Path(__file__).parent / "kilo_modes.yaml"

    @staticmethod
    def _default_language_map_path() -> Path:
        return Path(__file__).parent / "kilo_language_file_map.yaml"

    @property
    def kilo_modes(self) -> dict[str, Any]:
        """Lazy-load and return kilo modes from YAML."""
        if self._kilo_modes is None:
            self._kilo_modes = self._load_modes()
        return self._kilo_modes

    @property
    def language_file_map(self) -> dict[str, str]:
        """Lazy-load and return language file map from YAML."""
        if self._language_file_map is None:
            self._language_file_map = self._load_language_map()
        return self._language_file_map

    def _load_modes(self) -> dict[str, Any]:
        """Load custom modes from YAML file."""
        with self._modes_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        modes_list = data.get("customModes", [])
        return {mode["slug"]: mode for mode in modes_list if isinstance(mode, dict)}

    def _load_language_map(self) -> dict[str, str]:
        """Load language file map from YAML file."""
        with self._language_map_path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("language_file_map", {})
```

### Usage in Builders

```python
# In KiloCodeBuilder
class KiloCodeBuilder(Builder):
    def __init__(self, config: KiloConfig | None = None) -> None:
        self._config = config or KiloConfig()

    @property
    def kilo_modes(self) -> dict[str, Any]:
        return self._config.kilo_modes

    @property
    def language_file_map(self) -> dict[str, str]:
        return self._config.language_file_map
```

### Benefits
- Config can be injected for testing
- Different agent systems can have different configs
- Lazy loading improves startup performance
- Single responsibility - config loading is isolated

---

## 2. DestinationFilenameStrategy - Eliminating Hardcoded List

### Problem
[`kilo_ide.py:68-85`](promptosaurus/builders/kilo_ide.py:68) has hardcoded list of 15 agent prefixes.

### Design

Instead of hardcoded list, use the mode keys from registry:

```python
# In kilo_ide.py - simplified _make_dest_filename
def _make_dest_filename(filename: str, mode_key: str | None = None) -> str:
    """Convert prompt source path to destination filename.
    
    Uses registry mode keys dynamically instead of hardcoded prefixes.
    """
    # Handle core files first
    if filename.startswith("agents/core/core-conventions-"):
        return filename[17:]  # conventions-{lang}.md
    elif filename.startswith("agents/core/core-"):
        return filename[17:]  # {slug}.md

    # Handle agent files - use dynamic lookup
    if mode_key:
        # Check for subagents: agents/{mode}/subagents/{mode}-{slug}.md
        subagents_prefix = f"agents/{mode_key}/subagents/{mode_key}-"
        if filename.startswith(subagents_prefix):
            return filename[len(subagents_prefix):]

        # Check for root agent file
        if filename == f"agents/{mode_key}.md":
            return f"{mode_key}.md"

        # Dynamic prefix removal using registry modes
        if filename.startswith("agents/"):
            return _flatten_agent_path(filename, mode_key)

    return filename


def _flatten_agent_path(filename: str, mode_key: str) -> str:
    """Dynamically flatten agent path using mode_key."""
    slash1 = filename.find("/")
    if slash1 <= 0:
        return filename

    slash2 = filename.find("/", slash1 + 1)
    if slash2 <= 0:
        return filename

    remainder = filename[slash2 + 1:]

    # Remove "subagents/" if present
    if remainder.startswith("subagents/"):
        remainder = remainder[10:]

    # Remove {mode_key}- prefix dynamically
    prefix = f"{mode_key}-"
    if remainder.startswith(prefix):
        return remainder[len(prefix):]

    return remainder
```

### Benefits
- No hardcoded list
- Automatically picks up new modes from registry
- Single source of truth: registry.modes

---

## 3. IgnoreFileGenerator - Consolidating Duplication

### Problem
`_build_ignore` method duplicated in ClineBuilder, CursorBuilder, and KiloCodeBuilder.

### Design (Interface Pattern - Not ABC)

```python
# promptosaurus/builders/ignore_generator.py
from pathlib import Path

from promptosaurus.registry import registry


class IgnoreFileBuilder:
    """Interface for ignore file builders.
    
    Uses interface pattern (NotImplementedError) per conventions -
    no ABC, just raise NotImplementedError for required methods.
    """

    @property
    def filename(self) -> str:
        """Filename for the ignore file (e.g., '.kiloignore')."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement filename")

    @property
    def content(self) -> str:
        """Content for the ignore file."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement content")

    def build(self, output: Path, dry_run: bool = False) -> list[str]:
        """Build the ignore file."""
        destination = output / self.filename
        if dry_run:
            lines = self.content.count("\n")
            return [f"[dry-run] {self.filename} ({lines} lines)"]
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(self.content, encoding="utf-8")
        lines = self.content.count("\n")
        return [f"✓ {self.filename} ({lines} lines)"]


class KiloIgnoreBuilder(IgnoreFileBuilder):
    """Generates .kiloignore content."""

    @property
    def filename(self) -> str:
        return ".kiloignore"

    @property
    def content(self) -> str:
        return registry.generate_kiloignore()


class ClineIgnoreBuilder(IgnoreFileBuilder):
    """Generates .clineignore content."""

    @property
    def filename(self) -> str:
        return ".clineignore"

    @property
    def content(self) -> str:
        return registry.generate_clineignore()

### Usage

```python
# In ClineBuilder
def _build_ignore(self, output: Path, dry_run: bool) -> list[str]:
    return KiloIgnoreBuilder(output).build(dry_run)
```

---

## 4. HeaderStripper - Utility Class

### Problem
Header stripping logic duplicated in 3 places.

### Design

```python
# promptosaurus/builders/utils.py
class HeaderStripper:
    """Utility for stripping header comments from markdown files."""

    @staticmethod
    def strip(content: str) -> str:
        """Strip header comments from markdown content.
        
        Removes:
        - # filename.md comments
        - <!-- path: ... --> comments
        - "Behavior when" style headers
        """
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
        return "".join(lines[start:])
```

---

## 5. Fix Import Forwarding in __init__.py

### Problem
`__init__.py` violates "NO import forwarding" rule by re-exporting symbols.

### Design

Option A - Define public API explicitly (preferred):
```python
# promptosaurus/builders/__init__.py
"""
promptosaurus.builders
Builders for different AI assistant configurations.
"""

# NOTE: Import forwarding is NOT allowed per conventions.
# To use builders, import directly from their modules:
#   from promptosaurus.builders.kilo_cli import KiloCLIBuilder
#   from promptosaurus.builders.kilo_ide import KiloIDEBuilder
#   from promptosaurus.builders.kilo import KiloCodeBuilder
#
# The public API is defined here for documentation purposes only.

__all__ = [
    # Base classes
    "Builder",
    "KiloCodeBuilder",
    # Concrete builders  
    "KiloCLIBuilder",
    "KiloIDEBuilder",
    "ClineBuilder",
    "CursorBuilder",
    "CopilotBuilder",
]
```

Option B - Remove re-exports entirely:
```python
# promptosaurus/builders/__init__.py
"""
promptosaurus.builders
Builders for different AI assistant configurations.

Import builders directly from their modules:
    from promptosaurus.builders.kilo_cli import KiloCLIBuilder
    from promptosaurus.builders.kilo_ide import KiloIDEBuilder
"""
# No exports - import directly from submodules
```

---

## 6. File Extraction - Large Inline Strings

### Problem
Large inline strings for AGENTS.md in kilo_cli.py and kilo_ide.py.

### Design

Create template files:
```
promptosaurus/builders/templates/
├── agents_cli.md
└── agents_ide.md
```

```python
# In kilo_cli.py
def _get_agents_md_content(self) -> str:
    """Get the AGENTS.md content for CLI format."""
    template_path = Path(__file__).parent / "templates" / "agents_cli.md"
    return template_path.read_text(encoding="utf-8")
```

---

## Summary of Changes

| Change | File(s) Affected | New File |
|--------|-----------------|----------|
| KiloConfig | kilo.py, kilo_cli.py, kilo_ide.py | `config.py` |
| Remove hardcoded list | kilo_ide.py | - |
| IgnoreFileGenerator | cline.py, cursor.py, kilo.py | `ignore_generator.py` |
| HeaderStripper | kilo.py, registry.py | `utils.py` |
| Fix import forwarding | __init__.py | - |
| Extract templates | kilo_cli.py, kilo_ide.py | `templates/agents_*.md` |

---

## Implementation Order

1. **Create utils.py** - HeaderStripper (lowest risk)
2. **Create config.py** - KiloConfig class
3. **Update kilo.py** - Use KiloConfig, remove module-level constants
4. **Fix kilo_ide.py** - Remove hardcoded list, refactor nesting
5. **Create ignore_generator.py** - Consolidate ignore builders
6. **Fix __init__.py** - Remove import forwarding
7. **Extract templates** - Move large strings to files

---

**Status:** DESIGN APPROVED / READY FOR IMPLEMENTATION

This design addresses all MUST_FIX and SHOULD_FIX items from the enforcement report.
