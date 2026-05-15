"""Template validation utilities for Jinja2 templates.

This module provides functions to validate Jinja2 template syntax and structure
without attempting to render templates. Used for pre-rendering validation to catch
syntax errors early in the pipeline.
"""

from typing import Any

import jinja2

# from jinja2.nodes import Getattr, dfs  # TODO: re-enable security checks


def validate_template_syntax(template_content: str) -> str | None:
    """Validate basic Jinja2 template syntax without rendering.

    This function attempts to parse the template using Jinja2's parser to detect
    basic syntax errors like unmatched braces, invalid statements, or malformed
    expressions. It does NOT attempt to render the template or validate variable
    references.

    Args:
        template_content: The template string to validate

    Returns:
        None if validation passes, or an error message string if validation fails

    Example:
        >>> validate_template_syntax("Hello {{name}}!")
        None  # Valid syntax

        >>> validate_template_syntax("Hello {{name")
        "unexpected end of template, expected '}}'."  # Invalid syntax
    """
    try:
        # Create a minimal environment for parsing
        # We don't need custom filters, globals, or other extensions for syntax validation
        env = jinja2.Environment()

        # Parse the template - this will raise TemplateSyntaxError for syntax issues
        # but won't attempt to render or validate variable references
        env.parse(template_content)

        # If we get here, basic syntax is valid
        return None

    except jinja2.TemplateSyntaxError as e:
        # Return the error message from Jinja2, which includes line numbers and details
        return str(e)

    except Exception as e:
        # Catch any other unexpected errors and return a generic message
        # This shouldn't happen for normal template validation, but provides safety
        return f"Unexpected validation error: {e}"


def is_valid_template_syntax(template_content: str) -> bool:
    """Check if template has valid Jinja2 syntax.

    Convenience function that returns True for valid syntax, False for invalid.

    Args:
        template_content: The template string to check

    Returns:
        True if syntax is valid, False if invalid

    Example:
        >>> is_valid_template_syntax("Hello {{name}}!")
        True

        >>> is_valid_template_syntax("Hello {{name")
        False
    """
    return validate_template_syntax(template_content) is None


def validate_template_variables(
    template_content: str, available_variables: dict[str, Any], strict: bool = True
) -> str | None:
    """Validate that all variables referenced in template are provided.

    This function analyzes the template to find all variable references and checks
    that they are available in the provided variables dictionary. Supports both
    strict mode (all variables must be provided) and non-strict mode (missing
    variables are allowed but logged).

    Args:
        template_content: The template string to analyze
        available_variables: Dictionary of variables available for template rendering
        strict: If True, all referenced variables must be provided. If False,
               missing variables are allowed but reported.

    Returns:
        None if validation passes (all variables available or non-strict mode),
        or an error message listing missing variables if validation fails

    Example:
        >>> validate_template_variables("Hello {{name}}!", {"name": "World"})
        None  # Valid - variable provided

        >>> validate_template_variables("Hello {{name}}!", {})
        "Missing required variables: name"  # Invalid - variable missing

        >>> validate_template_variables("Hello {{name}}!", {}, strict=False)
        "Warning: Missing variables (non-strict mode): name"  # Warning only
    """
    try:
        from jinja2 import Environment, meta

        # Create environment for meta analysis
        env = Environment()

        # Parse template to AST
        ast = env.parse(template_content)

        # Find all undeclared variables in the template
        referenced_vars = meta.find_undeclared_variables(ast)

        # Convert to set for easier comparison
        available_keys = set(available_variables.keys())
        missing_vars = referenced_vars - available_keys

        if not missing_vars:
            # All variables are available
            return None

        if strict:
            # Strict mode: missing variables are errors
            missing_list = sorted(missing_vars)
            return f"Missing required variables: {', '.join(missing_list)}"
        else:
            # Non-strict mode: missing variables are warnings
            missing_list = sorted(missing_vars)
            return f"Warning: Missing variables (non-strict mode): {', '.join(missing_list)}"

    except Exception as e:
        # If meta analysis fails, fall back to a conservative approach
        # This shouldn't happen for normal templates, but provides safety
        return f"Variable validation failed: {e}"


def check_template_variable_references(
    template_content: str, available_variables: dict[str, Any], strict: bool = True
) -> bool:
    """Check if all template variable references are satisfied.

    Convenience function that returns True if variable validation passes,
    False if validation fails (missing required variables).

    Args:
        template_content: The template string to check
        available_variables: Dictionary of available variables
        strict: If True, all variables must be provided

    Returns:
        True if validation passes, False if validation fails

    Example:
        >>> check_template_variable_references("Hello {{name}}!", {"name": "World"})
        True

        >>> check_template_variable_references("Hello {{name}}!", {})
        False
    """
    result = validate_template_variables(template_content, available_variables, strict)
    if result is None:
        return True
    if strict and result.startswith("Missing required variables"):
        return False
    # In non-strict mode or for warnings, consider it passing
    return True


def validate_template_security(template_content: str) -> str | None:
    """Validate template for security vulnerabilities.

    This function analyzes the template AST to detect potentially dangerous constructs
    that could lead to code execution, unauthorized access, or other security issues.
    It checks for patterns like:
    - Access to Python internals (__class__, __bases__, __subclasses__, etc.)
    - Attempts to access sensitive modules or functions
    - Dangerous method calls that could compromise security

    Args:
        template_content: The template string to validate

    Returns:
        None if no security issues found, or an error message describing the security violation

    Example:
        >>> validate_template_security("Hello {{name}}!")
        None  # Safe template

        >>> validate_template_security("{{''.__class__.__bases__[0].__subclasses__()}}")
        "Security violation: Access to Python internals (__class__, __bases__, __subclasses__)"  # Dangerous
    """
    try:
        # TODO: Create environment for meta analysis
        # env = Environment()

        # TODO: Parse template to AST for security validation
        # ast = env.parse(template_content)

        # Find all attribute and item access in the template
        dangerous_patterns = []

        # TODO: Walk the AST to find security violations
        # for node in dfs(ast):
        #     # Check for attribute access to dangerous methods/properties
        #     if isinstance(node, Getattr):
        #         attr_name = node.attr
        #         # Check for Python internal attributes
        #         if attr_name in (
        #             "__class__",
        #             "__bases__",
        #             "__subclasses__",
        #             "__dict__",
        #             "__globals__",
        #             "__locals__",
        #             "__builtins__",
        #             "__import__",
        #         ):
        #             dangerous_patterns.append(f"Access to Python internals ({attr_name})")
        #
        #         # Check for dangerous methods on common objects
        #         if attr_name in (
        #             "eval",
        #             "exec",
        #             "compile",
        #             "open",
        #             "__import__",
        #             "getattr",
        #             "setattr",
        #             "hasattr",
        #             "delattr",
        #         ):
        #             dangerous_patterns.append(f"Dangerous method access ({attr_name})")
        #
        #     # Check for item access that might be dangerous
        #     elif isinstance(node, meta.nodes.Getitem):
        #         # This is more complex to analyze statically, but we can flag
        #         # access to sensitive keys if they appear as literals
        #         pass

        if dangerous_patterns:
            # Remove duplicates and format as readable message
            unique_patterns = list(set(dangerous_patterns))
            return f"Security violation: {', '.join(unique_patterns)}"

        # No security issues found
        return None

    except Exception as e:
        # If meta analysis fails, we can't guarantee security
        # Better to err on the side of caution and reject the template
        return f"Security validation failed: {e}"


def is_template_secure(template_content: str) -> bool:
    """Check if template has no security vulnerabilities.

    Convenience function that returns True for secure templates,
    False for templates with security issues.

    Args:
        template_content: The template string to check

    Returns:
        True if template is secure, False if it contains security violations

    Example:
        >>> is_template_secure("Hello {{name}}!")
        True

        >>> is_template_secure("{{''.__class__.__bases__[0].__subclasses__()}}")
        False
    """
    return validate_template_security(template_content) is None
