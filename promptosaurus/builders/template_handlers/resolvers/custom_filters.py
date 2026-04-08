"""Custom Jinja2 filters for domain-specific template needs in promptosaurus.

This module provides a collection of custom filters for string transformations
commonly needed in code generation and configuration templating.

Filters:
    kebab_case: Convert string to kebab-case (my-variable-name)
    snake_case: Convert string to snake_case (my_variable_name)
    pascal_case: Convert string to PascalCase (MyVariableName)
    title_case: Convert string to Title Case (My Variable Name)
    indent: Indent text by N spaces
    pluralize: Simple pluralization (add 's' or 'es')
    camel_case: Convert string to camelCase (myVariableName)
"""

import re
from typing import Any


def kebab_case(value: Any) -> str:
    """Convert string to kebab-case.

    Converts spaces, underscores, and mixed case to hyphen-separated lowercase.

    Args:
        value: The value to convert (will be coerced to string)

    Returns:
        The kebab-case string

    Example:
        {{ 'my variable name' | kebab_case }} → 'my-variable-name'
        {{ 'MyClassName' | kebab_case }} → 'my-class-name'
    """
    value_str = str(value).strip()

    # Insert hyphens before uppercase letters (for camelCase or PascalCase)
    value_str = re.sub(r"([a-z])([A-Z])", r"\1-\2", value_str)

    # Replace spaces, underscores with hyphens
    value_str = re.sub(r"[\s_]+", "-", value_str)

    # Remove multiple consecutive hyphens
    value_str = re.sub(r"-+", "-", value_str)

    # Convert to lowercase and strip leading/trailing hyphens
    return value_str.lower().strip("-")


def snake_case(value: Any) -> str:
    """Convert string to snake_case.

    Converts spaces, hyphens, and mixed case to underscore-separated lowercase.

    Args:
        value: The value to convert (will be coerced to string)

    Returns:
        The snake_case string

    Example:
        {{ 'my variable name' | snake_case }} → 'my_variable_name'
        {{ 'MyClassName' | snake_case }} → 'my_class_name'
    """
    value_str = str(value).strip()

    # Insert underscores before uppercase letters (for camelCase or PascalCase)
    value_str = re.sub(r"([a-z])([A-Z])", r"\1_\2", value_str)

    # Replace spaces, hyphens with underscores
    value_str = re.sub(r"[\s\-]+", "_", value_str)

    # Remove multiple consecutive underscores
    value_str = re.sub(r"_+", "_", value_str)

    # Convert to lowercase and strip leading/trailing underscores
    return value_str.lower().strip("_")


def pascal_case(value: Any) -> str:
    """Convert string to PascalCase.

    Capitalizes each word and removes spaces, underscores, hyphens.

    Args:
        value: The value to convert (will be coerced to string)

    Returns:
        The PascalCase string

    Example:
        {{ 'my variable name' | pascal_case }} → 'MyVariableName'
        {{ 'my_class_name' | pascal_case }} → 'MyClassName'
    """
    value_str = str(value).strip()

    # First, insert separators before uppercase letters (for camelCase)
    # This helps split existing camelCase/PascalCase
    value_str = re.sub(r"([a-z])([A-Z])", r"\1_\2", value_str)

    # Split on word boundaries (spaces, hyphens, underscores)
    words = re.split(r"[\s\-_]+", value_str)

    # Capitalize each word and join
    return "".join(word.capitalize() for word in words if word)


def camel_case(value: Any) -> str:
    """Convert string to camelCase.

    Like PascalCase but with the first letter lowercase.

    Args:
        value: The value to convert (will be coerced to string)

    Returns:
        The camelCase string

    Example:
        {{ 'my variable name' | camel_case }} → 'myVariableName'
        {{ 'my_class_name' | camel_case }} → 'myClassName'
    """
    # Use pascal_case as the base, then lowercase first letter
    pascal = pascal_case(value)
    if not pascal:
        return ""
    # Lowercase only the first letter while preserving the rest
    return pascal[0].lower() + pascal[1:] if pascal else ""


def title_case(value: Any) -> str:
    """Convert string to Title Case.

    Capitalizes the first letter of each word and replaces separators with spaces.

    Args:
        value: The value to convert (will be coerced to string)

    Returns:
        The Title Case string

    Example:
        {{ 'my variable name' | title_case }} → 'My Variable Name'
        {{ 'my_class_name' | title_case }} → 'My Class Name'
    """
    value_str = str(value).strip()

    # Insert spaces before uppercase letters (for camelCase or PascalCase)
    value_str = re.sub(r"([a-z])([A-Z])", r"\1 \2", value_str)

    # Replace underscores and hyphens with spaces
    value_str = re.sub(r"[\s\-_]+", " ", value_str)

    # Remove multiple consecutive spaces
    value_str = re.sub(r" +", " ", value_str)

    # Capitalize each word
    return value_str.title()


def indent(value: Any, width: int = 4, first: bool = False) -> str:
    """Indent text by N spaces.

    Adds spaces to the beginning of each line. Useful for indenting code blocks.

    Args:
        value: The text to indent (will be coerced to string)
        width: Number of spaces to indent (default: 4)
        first: Whether to indent the first line (default: False)

    Returns:
        The indented text

    Example:
        {{ 'def foo():\n    pass' | indent(8) }} → '        def foo():\\n            pass'
        {{ 'code' | indent(2, first=true) }} → '  code'
    """
    value_str = str(value)
    indent_str = " " * width

    lines = value_str.split("\n")

    if not lines:
        return value_str

    # Determine starting index based on 'first' parameter
    start_idx = 0 if first else 1

    # Indent each line
    for i in range(start_idx, len(lines)):
        lines[i] = indent_str + lines[i]

    return "\n".join(lines)


def pluralize(value: Any, count: int | None = None) -> str:
    """Simple pluralization - add 's' or 'es' based on count.

    This is a simple pluralization filter. For more complex pluralization needs,
    consider using a dedicated library like 'inflect'.

    Args:
        value: The word to pluralize (will be coerced to string)
        count: The count that determines if pluralization is needed.
               If not provided, always pluralizes. If provided and == 1, returns singular.

    Returns:
        The pluralized (or original) word

    Example:
        {{ 'file' | pluralize }} → 'files'
        {{ 'box' | pluralize }} → 'boxes'
        {{ 'file' | pluralize(count=1) }} → 'file'
        {{ 'file' | pluralize(count=5) }} → 'files'
    """
    value_str = str(value).strip()

    # If count is provided and equals 1, return singular form
    if count is not None and count == 1:
        return value_str

    # Simple pluralization rules (can be extended as needed)
    if value_str.endswith(("s", "x", "z", "ch", "sh")):
        return value_str + "es"
    elif value_str.endswith("y") and len(value_str) > 1 and value_str[-2] not in "aeiou":
        return value_str[:-1] + "ies"
    else:
        return value_str + "s"


def register_custom_filters(environment: Any) -> None:
    """Register all custom filters with a Jinja2 environment.

    Args:
        environment: A Jinja2 Environment instance
    """
    environment.filters["kebab_case"] = kebab_case
    environment.filters["snake_case"] = snake_case
    environment.filters["pascal_case"] = pascal_case
    environment.filters["camel_case"] = camel_case
    environment.filters["title_case"] = title_case
    environment.filters["indent"] = indent
    environment.filters["pluralize"] = pluralize
