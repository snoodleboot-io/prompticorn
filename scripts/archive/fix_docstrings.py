#!/usr/bin/env python3
"""
Script to fix docstring formatting issues in Python files.

This script scans Python files for docstrings that are missing their closing triple quotes
and fixes them by adding the proper closing quotes with correct indentation.
"""

import re
from pathlib import Path


def fix_docstring_issues(file_path: Path) -> bool:
    """Fix docstring formatting issues in a single file.

    Args:
        file_path: Path to the Python file to fix

    Returns:
        True if the file was modified, False otherwise
    """
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Find all docstrings that might be missing closing quotes
    # Look for triple-quoted strings that start with """ and don't end with """
    lines = content.split("\n")
    fixed_lines = []
    i = 0
    modified = False

    while i < len(lines):
        line = lines[i]

        # Check if this line starts a docstring (contains """ at the beginning)
        if '"""' in line and not line.strip().startswith('"""'):
            # Find the start of the docstring
            start_quote_match = re.search(r'"""', line)
            if start_quote_match:
                # Look ahead to find where this docstring should end
                docstring_start = i
                j = i + 1

                # Skip docstring content until we find the end
                while j < len(lines):
                    if '"""' in lines[j]:
                        # Found a closing quote, this docstring is properly closed
                        break
                    j += 1

                if j >= len(lines) or '"""' not in lines[j]:
                    # Docstring is not properly closed, we need to close it
                    # Find the indentation level by looking at the previous line
                    # or the current line's indentation
                    indent_match = re.match(r"^(\s*)", lines[docstring_start])
                    indent = indent_match.group(1) if indent_match else ""

                    # Insert the closing quote after the last docstring line
                    # For now, just add it after the current line
                    lines.insert(j, f'{indent}"""')
                    modified = True
                    i = j  # Skip to after the inserted line

        fixed_lines.append(line)
        i += 1

    if modified:
        new_content = "\n".join(fixed_lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True

    return False


def main():
    """Main function to scan and fix all Python files."""
    project_root = Path(".")
    python_files = list(project_root.rglob("*.py"))

    # Skip venv and common directories
    skip_dirs = {".venv", "__pycache__", ".git", ".promptosaurus", "node_modules"}

    fixed_files = []

    for py_file in python_files:
        # Skip files in directories we don't want to touch
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue

        if fix_docstring_issues(py_file):
            fixed_files.append(str(py_file))
            print(f"Fixed: {py_file}")

    print(f"\nFixed {len(fixed_files)} files:")
    for file in fixed_files:
        print(f"  - {file}")


if __name__ == "__main__":
    main()
