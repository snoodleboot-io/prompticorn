"""UI package for prompticorn - antifragile pipeline-based interactive components.

This package provides an interactive command-line UI system for prompticorn,
allowing users to select options, confirm actions, and navigate through
configuration questions.

The UI is built on a pipeline architecture that separates:
- Input: Platform-specific input handling (Windows, Unix, fallback)
- Processing: State management and command processing
- Rendering: Multiple output layouts (vertical, columns, explain mode)

Architecture:
    ┌─────────────────┐
    │  InputProvider  │  ← Platform-specific keyboard input
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │     Command     │  ← Parse keypresses into commands
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │ SelectionState  │  ← Track selected options
    └────────┬────────┘
             │
             ▼
    ┌─────────────────┐
    │    Renderer     │  ← Display options to user
    └─────────────────┘

Classes:
    UIFactory: Factory for creating platform-appropriate UI components.
    select_option_with_explain: Main entry point for interactive selection.
    confirm_interactive: Yes/no confirmation dialog.
    prompt_with_default: Input prompt with default value.
"""

from prompticorn.ui._selector import (
    confirm_interactive,
    prompt_with_default,
    select_option_with_explain,
)

__all__ = [
    "select_option_with_explain",
    "confirm_interactive",
    "prompt_with_default",
]
