"""Builders module for tool-specific output generation.

This module provides builder base classes, factory patterns, and
interface classes for generating tool-specific configurations from the
Intermediate Representation (IR) Agent models.
"""

from prompticorn.builders.amazonq_builder import AmazonQBuilder
from prompticorn.builders.base import Builder, BuildOptions
from prompticorn.builders.claude_builder import ClaudeBuilder
from prompticorn.builders.cline_builder import ClineBuilder
from prompticorn.builders.component_composer import ComponentComposer
from prompticorn.builders.component_selector import (
    ComponentBundle,
    ComponentSelector,
    Variant,
)
from prompticorn.builders.continue_builder import ContinueBuilder
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
from prompticorn.builders.gemini_builder import GeminiBuilder
from prompticorn.builders.interfaces import (
    SupportsRules,
    SupportsSkills,
    SupportsSubagents,
    SupportsWorkflows,
)
from prompticorn.builders.junie_builder import JunieBuilder
from prompticorn.builders.kilo_builder import KiloBuilder
from prompticorn.builders.registry import BuilderRegistry
from prompticorn.builders.roo_builder import RooBuilder
from prompticorn.builders.windsurf_builder import WindsurfBuilder
from prompticorn.builders.zed_builder import ZedBuilder

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
    "RooBuilder",
    "JunieBuilder",
    "ZedBuilder",
    "GeminiBuilder",
    "AmazonQBuilder",
    "WindsurfBuilder",
    "ContinueBuilder",
]

# Auto-register all builders when module is imported
BuilderFactory.register("kilo", KiloBuilder)
BuilderFactory.register("cline", ClineBuilder)
BuilderFactory.register("claude", ClaudeBuilder)
BuilderFactory.register("copilot", CopilotBuilder)
BuilderFactory.register("cursor", CursorBuilder)
BuilderFactory.register("roo", RooBuilder)
BuilderFactory.register("junie", JunieBuilder)
BuilderFactory.register("zed", ZedBuilder)
BuilderFactory.register("gemini", GeminiBuilder)
BuilderFactory.register("amazonq", AmazonQBuilder)
BuilderFactory.register("windsurf", WindsurfBuilder)
BuilderFactory.register("continue", ContinueBuilder)
