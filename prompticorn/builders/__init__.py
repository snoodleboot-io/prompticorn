"""Builders module for tool-specific output generation.

This module provides builder base classes, factory patterns, and
interface classes for generating tool-specific configurations from the
Intermediate Representation (IR) Agent models.
"""

from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.cline_builder import ClineBuilder
from prompticorn.builders.component_composer import ComponentComposer
from prompticorn.builders.component_selector import (
    ComponentBundle,
    ComponentSelector,
    Variant,
)
from prompticorn.builders.copilot_builder import CopilotBuilder
from prompticorn.builders.cursor_builder import CursorBuilder
from prompticorn.builders.errors import (
    BuilderException,
    BuilderNotFoundError,
    BuilderValidationError,
    ComponentNotFoundError,
    UnsupportedFeatureError,
    VariantNotFoundError,
)
from prompticorn.builders.factory import BuilderFactory
from prompticorn.builders.interfaces import (
    SupportsRules,
    SupportsSkills,
    SupportsSubagents,
    SupportsWorkflows,
)
from prompticorn.builders.kilo_builder import KiloBuilder
from prompticorn.builders.registry import BuilderRegistry

__all__ = [
    "Builder",
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
