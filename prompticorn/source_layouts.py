"""Per-language standard source-tree layouts for the core convention.

Loads ``configurations/source_layouts.yaml`` and exposes the standard source
layout for a language, falling back to a generic layout when the language has no
specific entry. No internal deps (safe to import from builders and ir.loaders).
"""

from pathlib import Path

import yaml

_LAYOUTS_FILE = Path(__file__).parent / "configurations" / "source_layouts.yaml"
_DEFAULT_KEY = "default"
DEFAULT_STYLE = "flat"

# Cache of language -> (style -> layout). Single-layout languages are stored under
# the DEFAULT_STYLE key so every entry has a uniform shape.
_cache: dict[str, dict[str, str]] | None = None


def _load() -> dict[str, dict[str, str]]:
    global _cache
    if _cache is None:
        with open(_LAYOUTS_FILE, encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        cache: dict[str, dict[str, str]] = {}
        for key, value in data.items():
            name = str(key).lower()
            if isinstance(value, dict):
                cache[name] = {str(s).lower(): str(v).rstrip("\n") for s, v in value.items()}
            else:
                # Single canonical layout (ecosystem-dictated): same for any style.
                cache[name] = {DEFAULT_STYLE: str(value).rstrip("\n")}
        _cache = cache
    return _cache


def get_source_layout(language: str | None, style: str = DEFAULT_STYLE) -> str:
    """Return the standard source-tree layout for a language and layout style.

    Args:
        language: Language key (e.g. 'python', 'typescript'). Falls back to the
            generic layout when None or not in the registry.
        style: Layout style, 'flat' (default) or 'src'. Languages with a single
            canonical layout ignore the style.

    Returns:
        The source-tree layout block (no trailing newline).
    """
    layouts = _load()
    style = (style or DEFAULT_STYLE).lower()
    entry = (layouts.get(language.lower()) if language else None) or layouts.get(_DEFAULT_KEY, {})
    if not entry:
        return "src/\ntests/"
    # Prefer the requested style, then flat, then whatever single layout exists.
    return entry.get(style) or entry.get(DEFAULT_STYLE) or next(iter(entry.values()))
