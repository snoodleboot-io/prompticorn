"""Jinja2-powered template renderer for promptosaurus."""

import logging
import re
from typing import Any

import jinja2

from promptosaurus.builders.template_handlers.resolvers.template_rendering_error import (
    TemplateRenderingError,
)
from promptosaurus.registry import registry

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

    def _detect_inheritance(self, template_content: str) -> str | None:
        """Detect if template uses inheritance and extract base template name.

        Args:
            template_content: The template content to check

        Returns:
            Base template name if inheritance detected, None otherwise
        """
        # Look for {% extends "template-name" %} at the beginning of the template
        extends_pattern = r'^\s*\{\%\s*extends\s+["\']([^"\']+)["\']\s*\%\}'
        match = re.search(extends_pattern, template_content, re.MULTILINE)
        return match.group(1) if match else None

    def _resolve_inheritance_chain(
        self, template_content: str, visited_templates: set[str] | None = None, depth: int = 0
    ) -> tuple[str, dict[str, str]]:
        """Recursively resolve template inheritance chain and collect all blocks.

        Args:
            template_content: The template content to process
            visited_templates: Set of visited template names for circular dependency detection
            depth: Current inheritance depth

        Returns:
            Tuple of (final_base_content, merged_blocks_dict)

        Raises:
            TemplateRenderingError: For circular dependencies or depth limits
        """
        if visited_templates is None:
            visited_templates = set()

        # Check depth limit (max 10 levels)
        max_depth = 10
        if depth > max_depth:
            raise TemplateRenderingError(
                f"Template inheritance depth limit ({max_depth}) exceeded",
                template_content=template_content,
            )

        # Check for inheritance
        base_template_name = self._detect_inheritance(template_content)

        if not base_template_name:
            # No inheritance - this is the base template
            blocks = self._extract_blocks(template_content)
            return template_content, blocks

        # Check for circular dependency
        if base_template_name in visited_templates:
            chain = list(visited_templates) + [base_template_name]
            raise TemplateRenderingError(
                f"Circular template inheritance detected: {' -> '.join(chain)}",
                template_content=template_content,
            )

        # Load base template content
        try:
            base_content = registry.prompt_body(base_template_name)
        except Exception as e:
            raise TemplateRenderingError(
                f"Failed to load base template '{base_template_name}': {e}",
                template_content=template_content,
                original_error=e,
            ) from e

        # Add to visited set and recurse
        visited_templates.add(base_template_name)
        final_base_content, parent_blocks = self._resolve_inheritance_chain(
            base_content, visited_templates, depth + 1
        )
        visited_templates.remove(base_template_name)

        # Extract blocks from current template
        current_blocks = self._extract_blocks(template_content)

        # Merge blocks: child blocks override parent blocks
        merged_blocks = parent_blocks.copy()
        merged_blocks.update(current_blocks)

        return final_base_content, merged_blocks

    def _extract_blocks(self, template_content: str) -> dict[str, str]:
        """Extract blocks from template content, handling nested blocks properly.

        Args:
            template_content: The template content to parse

        Returns:
            Dictionary mapping block names to their content

        Raises:
            TemplateRenderingError: If block syntax is malformed
        """
        blocks = {}

        # Use a more sophisticated approach to handle nested blocks
        # We need to parse blocks while respecting nesting levels
        i = 0
        content_length = len(template_content)

        while i < content_length:
            # Find block start
            block_start = template_content.find("{% block ", i)
            if block_start == -1:
                break

            # Find the block name
            block_start_end = template_content.find("%}", block_start)
            if block_start_end == -1:
                raise TemplateRenderingError(
                    "Malformed block syntax: missing closing %}",
                    template_content=template_content,
                )

            block_declaration = template_content[block_start : block_start_end + 2]
            # Extract block name
            name_match = re.search(r"block\s+(\w+)", block_declaration)
            if not name_match:
                raise TemplateRenderingError(
                    f"Invalid block declaration: {block_declaration}",
                    template_content=template_content,
                )

            block_name = name_match.group(1)

            # Find matching endblock, accounting for nesting
            nested_level = 0
            j = block_start_end + 2

            while j < content_length:
                # Check for block/endblock tags
                next_block = template_content.find("{% block ", j)
                next_endblock = template_content.find("{% endblock ", j)

                # If no more tags, we're done
                if next_block == -1 and next_endblock == -1:
                    raise TemplateRenderingError(
                        f"Unclosed block '{block_name}': no matching endblock found",
                        template_content=template_content,
                    )

                # If endblock comes first, check nesting level
                if next_endblock != -1 and (next_block == -1 or next_endblock < next_block):
                    if nested_level == 0:
                        # This is our matching endblock
                        endblock_end = template_content.find("%}", next_endblock)
                        if endblock_end == -1:
                            raise TemplateRenderingError(
                                f"Malformed endblock for block '{block_name}': missing closing %}}",
                                template_content=template_content,
                            )

                        # Extract block content
                        block_content = template_content[block_start_end + 2 : next_endblock]
                        blocks[block_name] = block_content.strip()

                        # Move past this block
                        i = endblock_end + 2
                        break
                    else:
                        # This is an endblock for a nested block
                        nested_level -= 1
                        j = next_endblock + 2
                elif next_block != -1:
                    # Nested block start
                    nested_level += 1
                    j = next_block + 2
                else:
                    j += 1

        return blocks

    def _merge_templates(self, template_content: str) -> str:
        """Resolve template inheritance and merge all blocks in the hierarchy.

        Args:
            template_content: The template content that may contain inheritance

        Returns:
            Fully merged template content with inheritance resolved

        Raises:
            TemplateRenderingError: For inheritance or block syntax errors
        """
        try:
            # Resolve the full inheritance chain
            final_base_content, merged_blocks = self._resolve_inheritance_chain(template_content)

            # Handle {% super() %} calls by expanding them to parent block content
            # This needs to be done in reverse order (from deepest to shallowest)
            inheritance_levels = []
            current_content = template_content
            while True:
                base_name = self._detect_inheritance(current_content)
                if not base_name:
                    break
                try:
                    parent_content = registry.prompt_body(base_name)
                    inheritance_levels.append((current_content, parent_content))
                    current_content = parent_content
                except Exception:
                    break  # Stop if we can't load parent

            # Process blocks from deepest parent to child
            resolved_blocks = merged_blocks.copy()

            # Process {% super() %} calls in reverse inheritance order
            for child_content, parent_content in reversed(inheritance_levels):
                child_blocks = self._extract_blocks(child_content)
                parent_blocks = self._extract_blocks(parent_content)

                for block_name, child_block_content in child_blocks.items():
                    if "{% super() %}" in child_block_content:
                        parent_block_content = parent_blocks.get(block_name, "")
                        resolved_blocks[block_name] = child_block_content.replace(
                            "{% super() %}", parent_block_content
                        )

            # Replace blocks in final base template with resolved content
            merged_content = final_base_content
            for block_name, block_content in resolved_blocks.items():
                # Replace the entire block in base template
                block_pattern = (
                    r"\{\%\s*block\s+"
                    + re.escape(block_name)
                    + r"\s*\%\}[\s\S]*?\{\%\s*endblock\s*\%\}"
                )
                replacement = f"{{% block {block_name} %}}{block_content}{{% endblock %}}"
                merged_content = re.sub(block_pattern, replacement, merged_content)

            return merged_content

        except TemplateRenderingError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            raise TemplateRenderingError(
                f"Failed to merge template inheritance: {e}",
                template_content=template_content,
                original_error=e,
            ) from e

    def handle(self, template_content: str, variables: dict[str, Any]) -> str:
        """Render the template content using Jinja2 with full feature support.

        Supports all Jinja2 features including:
        - Variable substitution: {{variable}}
        - Filters: {{value | filter}}
        - Conditionals: {% if condition %}...{% endif %}
        - Loops: {% for item in items %}...{% endfor %}
        - Template inheritance: {% extends "base.html" %}{% block name %}...{% endblock %}
        - Includes: {% include "partial.html" %} - inserts template content with shared context
        - Macros: {% macro name(params) %}...{% endmacro %} - reusable template functions
        - Imports: {% import "macros.html" as m %} - import macros from other templates
        - Selective imports: {% from "macros.html" import macro1, macro2 %}

        Args:
            template_content: The template string to render
            variables: Dictionary of variables to substitute in the template

        Returns:
            The rendered template string

        Raises:
            TemplateRenderingError: If template rendering fails
        """
        try:
            # Check for template inheritance
            base_template_name = self._detect_inheritance(template_content)

            if base_template_name:
                # Merge templates with full inheritance resolution
                merged_content = self._merge_templates(template_content)

                # Compile and render the merged template
                template = self._get_or_compile_template(merged_content)
            else:
                # No inheritance - compile template normally
                template = self._get_or_compile_template(template_content)

            # Render with provided variables
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

    def handle_by_name(self, template_name: str, variables: dict[str, Any]) -> str:
        """Render a template by name using the registry loader for full Jinja2 support.

        This method loads a template from the registry by name and renders it,
        enabling full template features:
        - Template inheritance: {% extends "template-name" %}{% block %}...{% endblock %}
        - Includes: {% include "template-name" %} - loads templates from registry
        - Imports: {% import "template-name" as m %} - import macros from registry templates
        - All other Jinja2 features (macros, filters, conditionals, loops)

        Template files loaded via include/import are resolved from the registry,
        enabling modular template organization across multiple prompt files.

        Args:
            template_name: Name of the template to load from registry
            variables: Dictionary of variables to substitute in the template

        Returns:
            The rendered template string

        Raises:
            TemplateRenderingError: If template loading or rendering fails
        """
        try:
            # Reset inheritance chain for new rendering operation
            if hasattr(self._environment.loader, "reset_inheritance_chain"):
                # Type: ignore for dynamic attribute access
                self._environment.loader.reset_inheritance_chain()  # type: ignore

            # Load template by name using the registry loader
            template = self._environment.get_template(template_name)

            # Render with provided variables
            rendered = template.render(**variables)

            return rendered

        except jinja2.UndefinedError as e:
            # Handle undefined variable errors specifically
            raise TemplateRenderingError(
                f"Undefined variable in template '{template_name}': {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            ) from e

        except jinja2.TemplateRuntimeError as e:
            # Handle runtime errors during rendering
            raise TemplateRenderingError(
                f"Template runtime error in '{template_name}': {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            ) from e

        except jinja2.TemplateNotFound as e:
            # Handle template not found errors
            raise TemplateRenderingError(
                f"Template '{template_name}' not found in registry: {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            ) from e

        except jinja2.TemplateError as e:
            # Catch any other Jinja2 template errors
            raise TemplateRenderingError(
                f"Template rendering failed for '{template_name}': {e}",
                template_content=f"Template: {template_name}",
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
