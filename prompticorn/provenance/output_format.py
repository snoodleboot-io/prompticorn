"""The output formats prompticorn emits, and how each carries a comment (PRO-112).

The whole design turns on one fact: **JSON has no comment syntax.** Amazon Q,
Bedrock and Gemini ship JSON agents, and a `_prompticorn` key would pollute a
schema the consuming tool validates — possibly to the point of rejection.

That is why the sidecar is the *general* mechanism and inline headers are a
convenience for the formats that can take one. Provenance that existed for
markdown but not for JSON would be an audit trail with a hole in exactly the
place a reader is least able to check by eye.
"""

from __future__ import annotations

from enum import Enum

_MARKDOWN_SUFFIXES = frozenset({".md", ".markdown", ".mdc"})
_YAML_SUFFIXES = frozenset({".yaml", ".yml"})
_TOML_SUFFIXES = frozenset({".toml"})
_JSON_SUFFIXES = frozenset({".json"})


class OutputFormat(Enum):
    """A generated file's format, which decides how provenance is attached."""

    MARKDOWN = "markdown"
    YAML = "yaml"
    TOML = "toml"
    JSON = "json"

    @classmethod
    def of(cls, path: str) -> OutputFormat:
        """Classify by file extension.

        Unknown extensions fall back to :attr:`MARKDOWN`, because every
        non-JSON format prompticorn emits is line-comment-or-HTML-comment based
        and markdown is the overwhelming majority. Guessing JSON would be the
        dangerous default: it would silently *omit* the inline header rather
        than add a harmless one.
        """
        suffix = _suffix(path)
        if suffix in _JSON_SUFFIXES:
            return cls.JSON
        if suffix in _YAML_SUFFIXES:
            return cls.YAML
        if suffix in _TOML_SUFFIXES:
            return cls.TOML
        return cls.MARKDOWN

    @property
    def supports_inline_header(self) -> bool:
        """Whether a comment can be written into this format at all."""
        return self is not OutputFormat.JSON

    @property
    def comment_prefix(self) -> str:
        """What opens a comment in this format."""
        return _PREFIXES[self]

    @property
    def comment_suffix(self) -> str:
        """What closes a comment, empty for line-comment formats."""
        return _SUFFIXES[self]


def _suffix(path: str) -> str:
    _, separator, tail = path.rpartition(".")
    return f".{tail.lower()}" if separator else ""


_PREFIXES: dict[OutputFormat, str] = {
    OutputFormat.MARKDOWN: "<!--",
    OutputFormat.YAML: "#",
    OutputFormat.TOML: "#",
    OutputFormat.JSON: "",
}

_SUFFIXES: dict[OutputFormat, str] = {
    OutputFormat.MARKDOWN: "-->",
    OutputFormat.YAML: "",
    OutputFormat.TOML: "",
    OutputFormat.JSON: "",
}
