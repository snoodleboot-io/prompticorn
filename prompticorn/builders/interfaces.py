"""Protocol-based mixin interfaces for optional builder features.

This module defines Protocol-based interfaces that enable builders to
declare optional feature support without tight coupling. A builder that
implements the SupportsSkills protocol gains access to the build_skills
method, and the type system understands this relationship.

Using protocols instead of traditional mixins provides:
1. Structural subtyping - no need to explicitly inherit
2. Type safety without runtime overhead
3. Flexibility for third-party builder implementations
4. Clear intent about optional features
"""

from typing import Any, Protocol

from prompticorn.ir.models import Agent, Rules, Skill, Workflow


class SupportsSkills(Protocol):
    """Protocol for builders that support building skills.

    Any builder that implements the build_skills method automatically
    conforms to this protocol and can be used wherever SupportsSkills
    is expected, without explicitly inheriting from it.
    """

    def build_skills(self, skills: list[Skill]) -> str | dict[str, Any]:
        """Build tool-specific output for a collection of skills.

        Args:
            skills: List of Skill IR models to build

        Returns:
            Tool-specific representation of the skills
        """
        ...


class SupportsWorkflows(Protocol):
    """Protocol for builders that support building workflows.

    Any builder that implements the build_workflows method automatically
    conforms to this protocol and can be used wherever SupportsWorkflows
    is expected, without explicitly inheriting from it.
    """

    def build_workflows(self, workflows: list[Workflow]) -> str | dict[str, Any]:
        """Build tool-specific output for a collection of workflows.

        Args:
            workflows: List of Workflow IR models to build

        Returns:
            Tool-specific representation of the workflows
        """
        ...


class SupportsRules(Protocol):
    """Protocol for builders that support building rules.

    Any builder that implements the build_rules method automatically
    conforms to this protocol and can be used wherever SupportsRules
    is expected, without explicitly inheriting from it.
    """

    def build_rules(self, rules: Rules) -> str | dict[str, Any]:
        """Build tool-specific output for a Rules IR model.

        Args:
            rules: The Rules IR model to build

        Returns:
            Tool-specific representation of the rules
        """
        ...


class SupportsSubagents(Protocol):
    """Protocol for builders that support building subagents.

    Any builder that implements the build_subagents method automatically
    conforms to this protocol and can be used wherever SupportsSubagents
    is expected, without explicitly inheriting from it.
    """

    def build_subagents(self, subagents: list[Agent]) -> str | dict[str, Any]:
        """Build tool-specific output for a collection of subagents.

        Args:
            subagents: List of Agent IR models representing subagents

        Returns:
            Tool-specific representation of the subagents
        """
        ...


class SupportsTools(Protocol):
    """Protocol for builders that support building tools.

    Any builder that implements the build_tools method automatically
    conforms to this protocol and can be used wherever SupportsTools
    is expected, without explicitly inheriting from it.
    """

    def build_tools(self, tool_names: list[str]) -> str | dict[str, Any]:
        """Build tool-specific output for a collection of tools.

        Args:
            tool_names: List of tool names to build

        Returns:
            Tool-specific representation of the tools
        """
        ...
