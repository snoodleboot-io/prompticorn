"""Convention file generator for Claude artifacts."""

from pathlib import Path
from typing import Any

import jinja2

# Keys that may appear in a folder/language spec and should be exposed as
# top-level template variables when rendering a convention file.
_SPEC_TEMPLATE_KEYS = (
    "language",
    "runtime",
    "package_manager",
    "test_framework",
    "linter",
    "linters",
    "formatter",
    "abstract_class_style",
    "coverage",
)


def _get_convention_environment() -> jinja2.Environment:
    """Build a Jinja2 environment for rendering convention templates.

    The loader is rooted at ``prompticorn/prompts`` so that convention files can
    resolve macro imports like ``{% import 'macros/coverage_targets.jinja2' %}``.

    Returns:
        Configured Jinja2 environment.
    """
    prompts_dir = Path(__file__).parent.parent / "prompts"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(prompts_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _build_template_context(spec: dict[str, Any] | None) -> dict[str, Any]:
    """Build the Jinja2 render context for a language convention from a spec.

    Spec values are exposed both as top-level variables (e.g. ``{{ language }}``)
    and via a ``config`` object (e.g. ``{{ config.abstract_class_style }}``), since
    convention templates reference both forms.

    Args:
        spec: Folder/language spec dict, or None for an empty context.

    Returns:
        Dictionary of template variables.
    """
    spec = spec or {}
    context: dict[str, Any] = {key: spec.get(key, "") for key in _SPEC_TEMPLATE_KEYS}
    # Expose the full spec as ``config`` for templates using ``config.<field>``.
    context["config"] = spec
    # ``coverage_targets`` is the documented name for the coverage dict passed to
    # the testing/coverage macros (the templates alias the coverage *macro module*
    # as ``coverage``, so the data must use a distinct name to avoid shadowing).
    context["coverage_targets"] = spec.get("coverage") or {}
    return context


def generate_core_convention(repository_type: str = "") -> str:
    """Generate core general.md convention file.

    Combines system.md, conventions.md, and session.md into one file.

    Args:
        repository_type: Repository type from config (e.g. 'single-language',
            'multi-language-monorepo') used to populate the core conventions.

    Returns:
        Content for .claude/conventions/core/general.md
    """
    core_dir = Path(__file__).parent.parent / "agents" / "core"
    environment = _get_convention_environment()
    context = {"repository_type": repository_type}

    def _render_section(path: Path) -> str:
        """Read and render a core convention source (resolves macro imports)."""
        return environment.from_string(path.read_text(encoding="utf-8")).render(**context)

    sections = []

    # Read system.md
    system_path = core_dir / "system.md"
    if system_path.exists():
        sections.append("# System Instructions\n\n" + _render_section(system_path))

    # Read conventions.md
    conventions_path = core_dir / "conventions.md"
    if conventions_path.exists():
        sections.append("# General Conventions\n\n" + _render_section(conventions_path))

    # Read session.md
    session_path = core_dir / "session.md"
    if session_path.exists():
        sections.append("# Session Management\n\n" + _render_section(session_path))

    return "\n\n---\n\n".join(sections)


def generate_language_convention(language: str, spec: dict[str, Any] | None = None) -> str | None:
    """Generate language-specific convention file.

    The convention source files are Jinja2 templates that reference spec values
    (``{{ language }}``, ``{{ test_framework }}``, etc.) and macro imports. This
    renders the template with the provided spec so the generated file contains the
    user's actual choices instead of raw template syntax.

    Args:
        language: Language name (e.g., "python", "typescript", "rust")
        spec: Optional folder/language spec providing values for template
            substitution (runtime, package_manager, test_framework, linter,
            formatter, coverage, abstract_class_style). When None, the template is
            still rendered (with empty values) so no raw Jinja2 is emitted.

    Returns:
        Rendered content for .claude/conventions/languages/{language}.md, or None
        if no convention template exists for the language.
    """
    core_dir = Path(__file__).parent.parent / "agents" / "core"
    convention_path = core_dir / f"conventions-{language}.md"

    if not convention_path.exists():
        return None

    template_source = convention_path.read_text(encoding="utf-8")
    environment = _get_convention_environment()
    context = _build_template_context(spec)
    return environment.from_string(template_source).render(**context)


def get_all_languages() -> list[str]:
    """Get list of all available language conventions.

    Returns:
        List of language names (e.g., ["python", "typescript", "rust"])
    """
    core_dir = Path(__file__).parent.parent / "agents" / "core"
    languages = []

    for path in core_dir.glob("conventions-*.md"):
        # Extract language from "conventions-{language}.md"
        language = path.stem.replace("conventions-", "")
        languages.append(language)

    return sorted(languages)


def _normalize_specs(
    specs: list[dict[str, Any]] | dict[str, Any] | list[str] | None,
) -> list[dict[str, Any]]:
    """Normalize the ``specs`` argument into a list of spec dicts.

    Accepts a single spec dict (single-language), a list of spec dicts
    (multi-language-monorepo), a list of bare language names (legacy callers), or
    None (all languages, no spec values).

    Args:
        specs: Spec(s) or language name(s) to generate conventions for.

    Returns:
        List of spec dicts, each containing at least a ``language`` key.
    """
    if specs is None:
        return [{"language": language} for language in get_all_languages()]
    if isinstance(specs, dict):
        return [specs]
    normalized: list[dict[str, Any]] = []
    for entry in specs:
        if isinstance(entry, str):
            normalized.append({"language": entry})
        elif isinstance(entry, dict) and entry.get("language"):
            normalized.append(entry)
    return normalized


def generate_all_conventions(
    specs: list[dict[str, Any]] | dict[str, Any] | list[str] | None = None,
    repository_type: str = "",
) -> dict[str, str]:
    """Generate convention files for Claude.

    Args:
        specs: Language/folder spec(s) to generate conventions for. May be a single
            spec dict (single-language), a list of spec dicts
            (multi-language-monorepo), a list of language names (legacy), or None to
            generate conventions for all available languages. Spec values are
            substituted into each language convention template.
        repository_type: Repository type from config, used to populate the core
            convention (e.g. 'single-language', 'multi-language-monorepo').

    Returns:
        Dictionary mapping file paths to content
        Example:
        {
            ".claude/conventions/core/general.md": "# System Instructions\n...",
            ".claude/conventions/languages/python.md": "# Python Conventions\n...",
        }
    """
    output = {}

    # Generate core general.md
    core_content = generate_core_convention(repository_type)
    output[".claude/conventions/core/general.md"] = core_content

    # Generate a convention per language, substituting that folder's spec values.
    # NOTE: if two folders share a language, the later spec wins (keyed by language).
    for spec in _normalize_specs(specs):
        language = spec["language"]
        lang_content = generate_language_convention(language, spec)
        if lang_content:
            output[f".claude/conventions/languages/{language}.md"] = lang_content

    return output
