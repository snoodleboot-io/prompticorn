"""Per-language standard source-tree layouts for the core convention.

Loads ``configurations/source_layouts.yaml`` and exposes the standard source
layout for a language, falling back to a generic layout when the language has no
specific entry. No internal deps (safe to import from builders and ir.loaders).
"""

from pathlib import Path

import yaml

_LAYOUTS_FILE = Path(__file__).parent / "configurations" / "source_layouts.yaml"
_DEFAULT_KEY = "default"

_cache: dict[str, str] | None = None


def _load() -> dict[str, str]:
    global _cache
    if _cache is None:
        with open(_LAYOUTS_FILE, encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        _cache = {str(k).lower(): str(v).rstrip("\n") for k, v in data.items()}
    return _cache


def get_source_layout(language: str | None) -> str:
    """Return the standard source-tree layout for a language.

    Args:
        language: Language key (e.g. 'python', 'typescript'). Falls back to the
            generic layout when None or not in the registry.

    Returns:
        The source-tree layout block (no trailing newline).
    """
    layouts = _load()
    if language:
        layout = layouts.get(language.lower())
        if layout:
            return layout
    return layouts.get(_DEFAULT_KEY, "src/\ntests/")
