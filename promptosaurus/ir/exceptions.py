"""Custom exceptions for the IR layer.

This module defines custom exceptions for parsing, loading, and validating
IR models from files and configuration sources.
"""


class IRException(Exception):
    """Base exception for all IR layer errors."""

    pass


class ParseError(IRException):
    """Raised when parsing a file fails (YAML, Markdown, or other format)."""

    pass


class MissingFileError(IRException):
    """Raised when a required file is missing."""

    pass


class ValidationError(IRException):
    """Raised when a loaded model fails validation."""

    pass
