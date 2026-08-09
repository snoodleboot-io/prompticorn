"""Small text helpers shared across builders and loaders (no internal deps)."""

import re

import yaml

# Internal source-path bookkeeping comment (e.g. ``<!-- path: prompticorn/... -->``)
# that must never appear in generated output, wherever it occurs in a file.
_PATH_COMMENT = re.compile(r"^[ \t]*<!--\s*path:.*?-->[ \t]*\n?", re.MULTILINE)

# A leading YAML frontmatter block: ``---`` on its own line, the block, then a
# closing ``---``. Authored content uses it for name/description metadata.
_FRONTMATTER = re.compile(r"\A﻿?\s*---[ \t]*\r?\n(.*?)\r?\n---[ \t]*(?:\r?\n|\Z)", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    """Split leading YAML frontmatter from the body.

    Content without a frontmatter block, or whose block is not a YAML mapping,
    yields an empty mapping and the text unchanged — callers fall back to their
    own defaults rather than failing a build over authored metadata.

    Args:
        text: Raw file content.

    Returns:
        A ``(metadata, body)`` pair.
    """
    if not text:
        return {}, text

    match = _FRONTMATTER.match(text)
    if match is None:
        return {}, text

    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}, text

    if not isinstance(parsed, dict):
        return {}, text

    return parsed, text[match.end() :]


def frontmatter_field(text: str, field: str) -> str | None:
    """The value of a scalar frontmatter field, or None when absent or blank.

    Non-scalar values (lists, mappings) are treated as absent: every caller
    renders the result as a single table cell.

    Args:
        text: Raw file content.
        field: Frontmatter key to read.

    Returns:
        The stripped scalar value, or None.
    """
    metadata, _ = parse_frontmatter(text)
    value = metadata.get(field)
    if not isinstance(value, str):
        return None
    collapsed = re.sub(r"\s+", " ", value).strip()
    return collapsed or None


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
