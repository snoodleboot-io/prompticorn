"""Jinja2-powered template renderer for promptosaurus."""

import logging
from typing import Any

import jinja2

from promptosaurus.builders.template_handlers.resolvers.template_rendering_error import (
    TemplateRenderingError,
)

logger = logging.getLogger(__name__)


class Jinja2TemplateRenderer:
    """Jinja2-powered template renderer that replaces string-based template substitution.

    This class implements the TemplateVariableHandler protocol using Jinja2
    for powerful template rendering with variables, filters, conditionals,
    loops, and includes.
    """

    def __init__(self, environment: jinja2.Environment) -> None:
        """Initialize the Jinja2 template renderer.

        Args:
            environment: Configured Jinja2 environment with templates and settings
        """
        self._environment = environment
        self._template_cache: dict[int, jinja2.Template] = {}

    @property
    def environment(self) -> jinja2.Environment:
        """Get the Jinja2 environment (read-only access)."""
        return self._environment

    def handle(self, template_content: str, variables: dict[str, Any]) -> str:
        """Render the template content using Jinja2 with full feature support.

        Supports all Jinja2 features including:
        - Variable substitution: {{variable}}
        - Filters: {{value | filter}}
        - Conditionals: {% if condition %}...{% endif %}
        - Loops: {% for item in items %}...{% endfor %}
        - Template inheritance: {% extends "base.html" %}
        - Includes: {% include "partial.html" %}
        - Macros: {% macro name(params) %}...{% endmacro %}

        Args:
            template_content: The template string to render
            variables: Dictionary of variables to substitute in the template

        Returns:
            The rendered template string

        Raises:
            TemplateRenderingError: If template rendering fails
        """
        try:
            # Compile template (with caching for performance)
            template = self._get_or_compile_template(template_content)

            # Render with provided variables - Jinja2 handles all the complex
            # features like filters, conditionals, loops, inheritance, includes
            rendered = template.render(**variables)

            return rendered

        except jinja2.UndefinedError as e:
            # Handle undefined variable errors specifically
            raise TemplateRenderingError(
                f"Undefined variable in template: {e}",
                template_content=template_content,
                variables=variables,
                original_error=e,
            ) from e

        except jinja2.TemplateRuntimeError as e:
            # Handle runtime errors during rendering (e.g., filter errors)
            raise TemplateRenderingError(
                f"Template runtime error: {e}",
                template_content=template_content,
                variables=variables,
                original_error=e,
            ) from e

        except jinja2.TemplateError as e:
            # Catch any other Jinja2 template errors
            raise TemplateRenderingError(
                f"Template rendering failed: {e}",
                template_content=template_content,
                variables=variables,
                original_error=e,
            ) from e

    def _get_or_compile_template(self, template_content: str) -> jinja2.Template:
        """Get cached template or compile new one.

        Args:
            template_content: The template content to compile

        Returns:
            Compiled Jinja2 template

        Raises:
            TemplateRenderingError: If template compilation fails
        """
        # Use template content hash as cache key for performance
        cache_key = hash(template_content)

        if cache_key not in self._template_cache:
            try:
                # Compile template with syntax validation
                self._template_cache[cache_key] = self._environment.from_string(template_content)
            except jinja2.TemplateSyntaxError as e:
                # Convert Jinja2 syntax errors to our custom error type
                raise TemplateRenderingError(
                    f"Template syntax error: {e}",
                    template_content=template_content,
                    original_error=e,
                ) from e
            except jinja2.TemplateError as e:
                # Handle other template compilation errors
                raise TemplateRenderingError(
                    f"Template compilation failed: {e}",
                    template_content=template_content,
                    original_error=e,
                ) from e

        return self._template_cache[cache_key]
