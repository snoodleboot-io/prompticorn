"""Builders module for tool-specific output generation.

This module provides abstract builder base classes, factory patterns, and
mixin interfaces for generating tool-specific configurations from the
Intermediate Representation (IR) Agent models.
"""

from promptosaurus.builders.base import AbstractBuilder, BuildOptions
from promptosaurus.builders.interfaces import (
    SupportsSkills,
    SupportsWorkflows,
    SupportsRules,
    SupportsSubagents,
)
from promptosaurus.builders.factory import BuilderFactory
from promptosaurus.builders.registry import BuilderRegistry
from promptosaurus.builders.errors import (
    BuilderException,
    BuilderNotFoundError,
    BuilderValidationError,
    UnsupportedFeatureError,
    ComponentNotFoundError,
    VariantNotFoundError,
)
from promptosaurus.builders.component_selector import (
    Variant,
    ComponentBundle,
    ComponentSelector,
)
from promptosaurus.builders.component_composer import ComponentComposer
from promptosaurus.builders.kilo_builder import KiloBuilder
from promptosaurus.builders.cline_builder import ClineBuilder
from promptosaurus.builders.claude_builder import ClaudeBuilder
from promptosaurus.builders.copilot_builder import CopilotBuilder
from promptosaurus.builders.cursor_builder import CursorBuilder

__all__ = [
    "AbstractBuilder",
    "BuildOptions",
    "SupportsSkills",
    "SupportsWorkflows",
    "SupportsRules",
    "SupportsSubagents",
    "BuilderFactory",
    "BuilderRegistry",
    "BuilderException",
    "BuilderNotFoundError",
    "BuilderValidationError",
    "UnsupportedFeatureError",
    "ComponentNotFoundError",
    "VariantNotFoundError",
    "Variant",
    "ComponentBundle",
    "ComponentSelector",
    "ComponentComposer",
    "KiloBuilder",
    "ClineBuilder",
    "ClaudeBuilder",
    "CopilotBuilder",
    "CursorBuilder",
]

# Auto-register all builders when module is imported
BuilderFactory.register("kilo", KiloBuilder)
BuilderFactory.register("cline", ClineBuilder)
BuilderFactory.register("claude", ClaudeBuilder)
BuilderFactory.register("copilot", CopilotBuilder)
BuilderFactory.register("cursor", CursorBuilder)
