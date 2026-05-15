"""Component selector for loading minimal/verbose variants.

This module provides utilities for selecting and loading component variants
(minimal or verbose) for agents, with fallback to verbose if minimal is
unavailable.
"""

import logging
from enum import Enum
from pathlib import Path
from typing import NamedTuple

from prompticorn.builders.errors import ComponentNotFoundError, VariantNotFoundError
from prompticorn.ir.models import Agent

logger = logging.getLogger(__name__)


class Variant(str, Enum):
    """Component variant types."""

    MINIMAL = "minimal"
    VERBOSE = "verbose"


class ComponentBundle(NamedTuple):
    """Bundle of loaded components from a selected variant.

    Attributes:
        variant: The selected variant (MINIMAL or VERBOSE)
        prompt: Raw content of prompt file (required)
        skills: Raw content of skills file (optional)
        workflow: Raw content of workflow file (optional)
        fallback_used: True if verbose was used as fallback for missing minimal
    """

    variant: Variant
    prompt: str
    skills: str | None = None
    workflow: str | None = None
    fallback_used: bool = False


class ComponentSelector:
    """Select and load component variants (minimal/verbose) for agents."""

    def __init__(self, agents_dir: Path | str = "agents") -> None:
        """Initialize ComponentSelector.

        Args:
            agents_dir: Path to agents directory (default: "agents")
        """
        self.agents_dir = Path(agents_dir)

    def select(self, agent: Agent, variant: Variant = Variant.MINIMAL) -> ComponentBundle:
        """Select and load components for given agent and variant.

        Tries to load the requested variant. If minimal is requested but not
        available, falls back to verbose with a warning log.

        Args:
            agent: Agent IR model
            variant: MINIMAL or VERBOSE (default: MINIMAL)

        Returns:
            ComponentBundle with loaded content

        Raises:
            ComponentNotFoundError: If required prompt.md is missing
            VariantNotFoundError: If both minimal and verbose are missing
        """
        # Try requested variant first
        variant_path = self.get_variant_path(agent.name, variant)

        if variant_path.exists() and (variant_path / "prompt.md").exists():
            return self._load_variant(agent.name, variant, variant_path)

        # If minimal requested but not found, try verbose as fallback
        if variant == Variant.MINIMAL:
            logger.warning(
                f"Minimal variant not found for agent '{agent.name}', falling back to verbose"
            )
            verbose_path = self.get_variant_path(agent.name, Variant.VERBOSE)

            if verbose_path.exists() and (verbose_path / "prompt.md").exists():
                return self._load_variant(
                    agent.name, Variant.VERBOSE, verbose_path, fallback_used=True
                )

        # Neither variant found - raise error
        raise VariantNotFoundError(
            agent.name, variant.value, message=f"No variants found for agent '{agent.name}'"
        )

    def get_variant_path(self, agent_name: str, variant: Variant) -> Path:
        """Get path for agent variant directory.

        Path structure: agents_dir/{agent_name}/{variant}/

        Args:
            agent_name: Name of the agent
            variant: MINIMAL or VERBOSE

        Returns:
            Path to variant directory (may not exist)
        """
        return self.agents_dir / agent_name / variant.value

    def variant_exists(self, agent_name: str, variant: Variant) -> bool:
        """Check if variant exists and has required prompt.md.

        Args:
            agent_name: Name of the agent
            variant: MINIMAL or VERBOSE

        Returns:
            True if variant directory exists and contains prompt.md
        """
        variant_path = self.get_variant_path(agent_name, variant)
        return (variant_path / "prompt.md").exists()

    def list_available_variants(self, agent_name: str) -> list[Variant]:
        """List available variants for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            List of available Variant enums (minimal, verbose, or both)
        """
        available = []
        for variant in Variant:
            if self.variant_exists(agent_name, variant):
                available.append(variant)
        return available

    def _load_variant(
        self,
        agent_name: str,
        variant: Variant,
        variant_path: Path,
        fallback_used: bool = False,
    ) -> ComponentBundle:
        """Load components from a variant directory.

        Args:
            agent_name: Name of the agent
            variant: MINIMAL or VERBOSE
            variant_path: Path to variant directory
            fallback_used: True if this is a fallback variant

        Returns:
            ComponentBundle with loaded content

        Raises:
            ComponentNotFoundError: If required prompt.md is missing
        """
        prompt_file = variant_path / "prompt.md"

        if not prompt_file.exists():
            raise ComponentNotFoundError(
                "prompt.md",
                str(variant_path),
                message=f"Required prompt.md not found in {variant_path}",
            )

        try:
            # Load prompt content (required)
            with open(prompt_file, encoding="utf-8") as f:
                prompt_content = f.read()

            # Load skills content (optional)
            skills_content: str | None = None
            skills_file = variant_path / "skills.md"
            if skills_file.exists():
                with open(skills_file, encoding="utf-8") as f:
                    skills_content = f.read()

            # Load workflow content (optional)
            workflow_content: str | None = None
            workflow_file = variant_path / "workflow.md"
            if workflow_file.exists():
                with open(workflow_file, encoding="utf-8") as f:
                    workflow_content = f.read()

            return ComponentBundle(
                variant=variant,
                prompt=prompt_content,
                skills=skills_content,
                workflow=workflow_content,
                fallback_used=fallback_used,
            )

        except Exception as e:
            raise ComponentNotFoundError(
                "component bundle",
                str(variant_path),
                message=f"Failed to load components from {variant_path}: {str(e)}",
            ) from e
