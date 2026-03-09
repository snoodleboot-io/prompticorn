"""Kilo Code builder implementations.

This package provides builder classes for generating Kilo Code configuration
files in both CLI and IDE formats.

Classes:
    KiloCodeBuilder: Base class for Kilo Code builders.
    KiloCLIBuilder: Builder for CLI format (.opencode/rules/).
    KiloIDEBuilder: Builder for IDE format (.kilocode/rules-{mode}/).

Functions:
    KiloConfig: Configuration loader for Kilo builder settings.

Example:
    >>> from promptosaurus.builders.kilo import KiloCLIBuilder, KiloIDEBuilder
    >>> from pathlib import Path

    >>> # CLI format
    >>> cli_builder = KiloCLIBuilder()
    >>> cli_actions = cli_builder.build(Path("./cli-output"))

    >>> # IDE format
    >>> ide_builder = KiloIDEBuilder()
    >>> ide_actions = ide_builder.build(Path("./ide-output"))
"""
