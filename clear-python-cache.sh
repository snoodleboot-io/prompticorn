#!/bin/bash
# Clear all Python bytecode cache recursively

echo "Removing Python bytecode cache..."

# Remove __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove .pyc files
find . -type f -name "*.pyc" -delete 2>/dev/null

# Remove .pyo files
find . -type f -name "*.pyo" -delete 2>/dev/null

# Remove any installed packages from venv
if [ -d ".venv/lib" ]; then
    rm -rf .venv/lib/python*/site-packages/promptosaurus* 2>/dev/null
fi

echo "✓ Python cache cleared"
