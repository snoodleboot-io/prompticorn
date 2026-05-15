"""Convention file generator for Claude artifacts."""

from pathlib import Path


def generate_core_convention() -> str:
    """Generate core general.md convention file.

    Combines system.md, conventions.md, and session.md into one file.

    Returns:
        Content for .claude/conventions/core/general.md
    """
    core_dir = Path(__file__).parent.parent / "agents" / "core"

    sections = []

    # Read system.md
    system_path = core_dir / "system.md"
    if system_path.exists():
        sections.append("# System Instructions\n\n" + system_path.read_text(encoding="utf-8"))

    # Read conventions.md
    conventions_path = core_dir / "conventions.md"
    if conventions_path.exists():
        sections.append("# General Conventions\n\n" + conventions_path.read_text(encoding="utf-8"))

    # Read session.md
    session_path = core_dir / "session.md"
    if session_path.exists():
        sections.append("# Session Management\n\n" + session_path.read_text(encoding="utf-8"))

    return "\n\n---\n\n".join(sections)


def generate_language_convention(language: str) -> str | None:
    """Generate language-specific convention file.

    Args:
        language: Language name (e.g., "python", "typescript", "rust")

    Returns:
        Content for .claude/conventions/languages/{language}.md or None if not found
    """
    core_dir = Path(__file__).parent.parent / "agents" / "core"
    convention_path = core_dir / f"conventions-{language}.md"

    if convention_path.exists():
        return convention_path.read_text(encoding="utf-8")

    return None


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


def generate_all_conventions() -> dict[str, str]:
    """Generate all convention files for Claude.

    Returns:
        Dictionary mapping file paths to content
        Example:
        {
            ".claude/conventions/core/general.md": "# System Instructions\n...",
            ".claude/conventions/languages/python.md": "# Python Conventions\n...",
            ".claude/conventions/languages/typescript.md": "# TypeScript Conventions\n...",
        }
    """
    output = {}

    # Generate core general.md
    core_content = generate_core_convention()
    output[".claude/conventions/core/general.md"] = core_content

    # Generate all language conventions
    for language in get_all_languages():
        lang_content = generate_language_convention(language)
        if lang_content:
            output[f".claude/conventions/languages/{language}.md"] = lang_content

    return output
