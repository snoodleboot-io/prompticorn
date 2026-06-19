"""Small text helpers shared across builders and loaders (no internal deps)."""

import re

# Internal source-path bookkeeping comment (e.g. ``<!-- path: prompticorn/... -->``)
# that must never appear in generated output, wherever it occurs in a file.
_PATH_COMMENT = re.compile(r"^[ \t]*<!--\s*path:.*?-->[ \t]*\n?", re.MULTILINE)


def strip_source_header_comments(text: str) -> str:
    """Strip internal source-path header comments from a prompt/convention file.

    Source files start with (or, after YAML frontmatter, contain) bookkeeping
    headers like ``<!-- path: prompticorn/prompts/... -->`` or
    ``# core-conventions-python.md`` that must not leak into generated output.
    Removes path comments wherever they occur, plus leading header comment lines
    and any blank lines immediately following them.

    Args:
        text: Raw file/template content.

    Returns:
        Content with source-path header comments removed.
    """
    # Remove internal source-path comments wherever they occur (some files carry
    # them after a YAML frontmatter block, not just on the first line).
    text = _PATH_COMMENT.sub("", text)

    lines = text.splitlines(keepends=True)
    index = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("<!--") and stripped.endswith("-->"):
            index += 1
        elif stripped.startswith("# ") and stripped.endswith(".md"):
            index += 1
        else:
            break
    # Drop blank lines left immediately after the stripped header(s).
    while index < len(lines) and not lines[index].strip():
        index += 1
    return "".join(lines[index:])
