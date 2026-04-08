"""Jinja2-powered template renderer for promptosaurus."""

import logging
import re
from typing import Any

import jinja2

from promptosaurus.builders.template_handlers.resolvers.error_recovery import (
    ErrorContextBuilder,
    SafeAccessor,
)
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
        self._fallback_templates: dict[str, str] = {}  # template_name -> fallback_content
        self._error_log: list[dict[str, Any]] = []  # Error history for debugging
        self._safe_accessor = SafeAccessor()  # Safe property access helper
        self._enable_error_recovery = True  # Allow graceful degradation

    @property
    def environment(self) -> jinja2.Environment:
        """Get the Jinja2 environment (read-only access)."""
        return self._environment

    def register_fallback_template(self, template_name: str, fallback_content: str) -> None:
        """Register a fallback template for missing templates.

        Args:
            template_name: Name of the template to provide fallback for
            fallback_content: Content to use if template is missing
        """
        self._fallback_templates[template_name] = fallback_content
        logger.info(f"Registered fallback template for '{template_name}'")

    def get_error_log(self) -> list[dict[str, Any]]:
        """Get list of errors that occurred during rendering.

        Returns:
            List of error dictionaries with context
        """
        return self._error_log.copy()

    def clear_error_log(self) -> None:
        """Clear the error log."""
        self._error_log = []

    def _record_error(
        self,
        error_type: str,
        message: str,
        template_name: str | None = None,
        variables: dict[str, Any] | None = None,
        severity: str = "warning",
    ) -> None:
        """Record an error for diagnostics.

        Args:
            error_type: Type of error (e.g., 'undefined_variable')
            message: Error message
            template_name: Template name where error occurred
            variables: Context variables
            severity: Error severity (debug, info, warning, error)
        """
        error_record = ErrorContextBuilder.build_context(
            error_type=error_type,
            template_name=template_name,
            variables=variables,
        )
        error_record["message"] = message
        error_record["severity"] = severity

        self._error_log.append(error_record)

        # Log with appropriate level
        log_func = getattr(logger, severity, logger.warning)
        log_func(f"[{error_type}] {message} (template: {template_name})")

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

    def handle(
        self, template_content: str, variables: dict[str, Any], allow_recovery: bool | None = None
    ) -> str:
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
            allow_recovery: Override error recovery setting (None = use class setting)

        Returns:
            The rendered template string

        Raises:
            TemplateRenderingError: If template rendering fails and recovery is disabled
        """
        enable_recovery = (
            allow_recovery if allow_recovery is not None else self._enable_error_recovery
        )

        try:
            # Validate syntax early for better error messages
            is_valid, error_msg = self._validate_template_syntax(template_content)
            if not is_valid and enable_recovery:
                self._record_error("syntax_error", error_msg or "Unknown syntax error")
                logger.error(f"Template syntax error: {error_msg}")
                raise TemplateRenderingError(
                    f"Template syntax error: {error_msg}",
                    template_content=template_content,
                )

            # Check for undefined variables and log warnings
            check_result = self.check_missing_variables(template_content, variables)
            for undefined_var in check_result["undefined"]:
                suggestions = undefined_var["suggestions"]
                self._record_error(
                    "undefined_variable",
                    f"Variable '{undefined_var['variable']}' not defined in context. "
                    f"Did you mean: {', '.join(suggestions)}?",
                    variables=variables,
                    severity="warning",
                )

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
            error = TemplateRenderingError(
                f"Undefined variable in template: {e}",
                template_content=template_content,
                variables=variables,
                original_error=e,
            )
            self._record_error("undefined_variable", str(e), variables=variables)

            if enable_recovery:
                # Return template with placeholders for undefined variables
                logger.warning(f"Recovering from undefined variable error: {e}")
                return self._recover_with_placeholders(template_content, variables)
            raise error from e

        except jinja2.TemplateRuntimeError as e:
            # Handle runtime errors during rendering (e.g., filter errors)
            error = TemplateRenderingError(
                f"Template runtime error: {e}",
                template_content=template_content,
                variables=variables,
                original_error=e,
            )
            self._record_error("runtime_error", str(e), variables=variables)

            if enable_recovery:
                logger.warning(f"Recovering from runtime error: {e}")
                return self._recover_gracefully(template_content)
            raise error from e

        except jinja2.TemplateError as e:
            # Catch any other Jinja2 template errors
            error = TemplateRenderingError(
                f"Template rendering failed: {e}",
                template_content=template_content,
                variables=variables,
                original_error=e,
            )
            self._record_error("template_error", str(e), variables=variables)

            if enable_recovery:
                logger.warning(f"Recovering from template error: {e}")
                return self._recover_gracefully(template_content)
            raise error from e

        except Exception as e:
            # Catch unexpected errors
            error = TemplateRenderingError(
                f"Unexpected error during template rendering: {e}",
                template_content=template_content,
                variables=variables,
                original_error=e,
            )
            self._record_error("unexpected_error", str(e), variables=variables, severity="error")

            if enable_recovery:
                logger.error(f"Unexpected error during rendering: {e}")
                return self._recover_gracefully(template_content)
            raise error from e

    def _recover_with_placeholders(self, template_content: str, variables: dict[str, Any]) -> str:
        """Recover from undefined variable errors by replacing undefined vars with placeholders.

        Args:
            template_content: The template content
            variables: Available variables

        Returns:
            Template with undefined variables marked with placeholders
        """
        result = template_content
        required_vars = self.validate_and_get_variables(template_content)

        for var_name in required_vars:
            if var_name not in variables:
                # Replace {{ var }} with [UNDEFINED: var]
                pattern = r"\{\{\s*" + re.escape(var_name) + r"\s*\}\}"
                result = re.sub(pattern, f"[UNDEFINED: {var_name}]", result)

        return result

    def _recover_gracefully(self, template_content: str) -> str:
        """Recover gracefully by returning a safe version of the template.

        Removes problematic Jinja2 constructs that may have caused errors.

        Args:
            template_content: The template content

        Returns:
            Simplified template content
        """
        result = template_content

        # Remove complex control structures that might have errors
        # Keep structure but make safe
        result = re.sub(r"\{%\s*if\s+.+?\s*%\}", "<!--REMOVED: if block-->", result)
        result = re.sub(r"\{%\s*for\s+.+?\s*%\}", "<!--REMOVED: for block-->", result)

        logger.warning("Graceful recovery: Removed problematic control structures from template")
        return result

    def handle_by_name(
        self, template_name: str, variables: dict[str, Any], allow_recovery: bool | None = None
    ) -> str:
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
            allow_recovery: Override error recovery setting (None = use class setting)

        Returns:
            The rendered template string

        Raises:
            TemplateRenderingError: If template loading or rendering fails and recovery disabled
        """
        enable_recovery = (
            allow_recovery if allow_recovery is not None else self._enable_error_recovery
        )

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

        except jinja2.TemplateNotFound as e:
            # Handle template not found errors - try fallback
            self._record_error(
                "missing_template",
                f"Template '{template_name}' not found in registry",
                template_name=template_name,
                severity="warning",
            )

            if enable_recovery and template_name in self._fallback_templates:
                logger.warning(f"Using fallback template for '{template_name}'")
                fallback_content = self._fallback_templates[template_name]
                return self.handle(fallback_content, variables, allow_recovery=enable_recovery)

            error = TemplateRenderingError(
                f"Template '{template_name}' not found in registry: {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            )

            if enable_recovery:
                logger.error(f"No fallback template available for '{template_name}'")
                return f"[MISSING TEMPLATE: {template_name}]"
            raise error from e

        except jinja2.UndefinedError as e:
            # Handle undefined variable errors specifically
            self._record_error(
                "undefined_variable",
                f"Undefined variable in template '{template_name}': {e}",
                template_name=template_name,
                variables=variables,
            )

            error = TemplateRenderingError(
                f"Undefined variable in template '{template_name}': {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            )

            if enable_recovery:
                logger.warning(f"Recovering from undefined variable in '{template_name}'")
                return f"[UNDEFINED VARIABLES IN: {template_name}]"
            raise error from e

        except jinja2.TemplateRuntimeError as e:
            # Handle runtime errors during rendering
            self._record_error(
                "runtime_error",
                f"Template runtime error in '{template_name}': {e}",
                template_name=template_name,
            )

            error = TemplateRenderingError(
                f"Template runtime error in '{template_name}': {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            )

            if enable_recovery:
                logger.warning(f"Recovering from runtime error in '{template_name}'")
                return f"[RUNTIME ERROR IN: {template_name}]"
            raise error from e

        except jinja2.TemplateError as e:
            # Catch any other Jinja2 template errors
            self._record_error(
                "template_error",
                f"Template rendering failed for '{template_name}': {e}",
                template_name=template_name,
            )

            error = TemplateRenderingError(
                f"Template rendering failed for '{template_name}': {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            )

            if enable_recovery:
                logger.warning(f"Recovering from template error in '{template_name}'")
                return f"[TEMPLATE ERROR IN: {template_name}]"
            raise error from e

        except Exception as e:
            # Catch unexpected errors
            self._record_error(
                "unexpected_error",
                f"Unexpected error rendering '{template_name}': {e}",
                template_name=template_name,
                severity="error",
            )

            error = TemplateRenderingError(
                f"Unexpected error rendering '{template_name}': {e}",
                template_content=f"Template: {template_name}",
                variables=variables,
                original_error=e,
            )

            if enable_recovery:
                logger.error(f"Unexpected error in '{template_name}': {e}")
                return f"[ERROR IN: {template_name}]"
            raise error from e

    def _validate_template_syntax(self, template_content: str) -> tuple[bool, str | None]:
        """Validate Jinja2 template syntax early.

        This catches syntax errors before rendering, providing better error messages.

        Args:
            template_content: The template content to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Try to compile without rendering
            self._environment.from_string(template_content)
            return True, None
        except jinja2.TemplateSyntaxError as e:
            error_msg = (
                f"Syntax error at line {e.lineno}: {e.message}\n"
                f"Context: {e.source[max(0, e.lineno - 5) : e.lineno + 2] if e.source else 'N/A'}"
            )
            return False, error_msg
        except Exception as e:
            return False, f"Compilation error: {e}"

    def validate_and_get_variables(self, template_content: str) -> list[str]:
        """Extract variable names from template for validation.

        Args:
            template_content: The template content

        Returns:
            List of variable names used in template
        """
        variables = set()

        # Match {{ variable }} patterns
        var_pattern = r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_\.]*)"
        for match in re.finditer(var_pattern, template_content):
            var_name = match.group(1).split(".")[0]  # Get top-level variable
            variables.add(var_name)

        # Match {% if/for variable %} patterns
        control_pattern = r"\{%\s*(?:if|for|elif)\s+([a-zA-Z_][a-zA-Z0-9_\.]*)"
        for match in re.finditer(control_pattern, template_content):
            var_name = match.group(1).split(".")[0]
            variables.add(var_name)

        return list(variables)

    def check_missing_variables(
        self, template_content: str, available_variables: dict[str, Any]
    ) -> dict[str, Any]:
        """Check for undefined variables in template.

        Args:
            template_content: The template content
            available_variables: Dictionary of available variables

        Returns:
            Dictionary with 'undefined' and 'suggestions' keys
        """
        required_vars = self.validate_and_get_variables(template_content)
        undefined = []
        available_keys = set(available_variables.keys())

        for var_name in required_vars:
            if var_name not in available_keys:
                # Find similar variable names
                similar = self._find_similar_variables(var_name, available_keys)
                undefined.append({"variable": var_name, "suggestions": similar})

        return {"undefined": undefined, "total_required": len(required_vars)}

    @staticmethod
    def _find_similar_variables(
        target: str, available: set[str], threshold: float = 0.6
    ) -> list[str]:
        """Find similar variable names using simple string matching.

        Args:
            target: Target variable name
            available: Set of available variable names
            threshold: Similarity threshold (0.0-1.0)

        Returns:
            List of similar variable names
        """
        similar = []

        for var in available:
            # Simple similarity: check if target is substring or vice versa
            target_lower = target.lower()
            var_lower = var.lower()

            if target_lower == var_lower:
                similar.append((var, 1.0))
            elif target_lower in var_lower or var_lower in target_lower:
                similar.append((var, 0.8))
            elif target_lower[:3] == var_lower[:3]:
                similar.append((var, 0.7))

        # Sort by similarity and return top 3
        similar.sort(key=lambda x: x[1], reverse=True)
        return [var for var, _ in similar[:3]]

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
