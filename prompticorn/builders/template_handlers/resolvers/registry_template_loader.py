"""Registry-based Jinja2 template loader for template inheritance.

This module provides a custom Jinja2 loader that can load templates from the
prompticorn registry by name, enabling template inheritance features.
"""

import logging

import jinja2

from prompticorn.registry import registry

logger = logging.getLogger(__name__)


class RegistryTemplateLoader(jinja2.BaseLoader):
    """Jinja2 loader that loads templates from the prompticorn registry.

    This loader enables template inheritance by allowing templates to reference
    other templates by name (e.g., {% extends "base-template.md" %}).
    """

    def __init__(self) -> None:
        """Initialize the registry template loader."""
        self._inheritance_chain: list[str] = []
        self._max_inheritance_depth = 10  # Prevent infinite loops

    def get_source(self, environment, template):
        """Get template source from registry.

        Args:
            environment: Jinja2 environment (unused but required by interface)
            template: Name of template to load from registry

        Returns:
            Tuple of (source, filename, uptodate_func)

        Raises:
            jinja2.TemplateNotFound: If template not found in registry
            ValueError: If circular inheritance detected
        """
        template_name = str(template)

        # Check for circular inheritance
        if template_name in self._inheritance_chain:
            chain_str = " -> ".join(self._inheritance_chain + [template_name])
            raise ValueError(f"Circular template inheritance detected: {chain_str}")

        # Check inheritance depth
        if len(self._inheritance_chain) >= self._max_inheritance_depth:
            chain_str = " -> ".join(self._inheritance_chain + [template_name])
            raise ValueError(f"Template inheritance depth limit exceeded: {chain_str}")

        try:
            # Load template content from registry
            source = registry.prompt_body(template_name)

            # Add to inheritance chain for circular dependency detection
            self._inheritance_chain.append(template_name)

            # Return source, filename, and uptodate function
            # Since templates are loaded from registry, they're always "up to date"
            def uptodate_func():
                return True

            return source, template_name, uptodate_func

        except Exception as e:
            logger.error(f"Failed to load template '{template_name}' from registry: {e}")
            raise jinja2.TemplateNotFound(
                f"Template '{template_name}' not found in registry"
            ) from e

    def reset_inheritance_chain(self) -> None:
        """Reset the inheritance chain for a new template rendering operation."""
        self._inheritance_chain = []
