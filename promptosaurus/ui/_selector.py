"""Public UI API - main entry point for interactive selection.

This module provides the primary functions for interactive command-line
selection, confirmation, and prompting. These functions are the main
public API for the promptosaurus UI system.

Functions:
    select_option_with_explain: Interactive selection with number keys and explain option.
    confirm_interactive: Yes/no confirmation dialog.
    prompt_with_default: Input prompt with default value.

Example:
    >>> from promptosaurus.ui import select_option_with_explain, confirm_interactive
    >>>
    >>> # Single selection
    >>> language = select_option_with_explain(
    ...     question="Choose a language:",
    ...     options=["Python", "TypeScript", "Go"],
    ...     explanations={
    ...         "Python": "Popular for data science and AI",
    ...         "TypeScript": "Type-safe JavaScript for web",
    ...         "Go": "Systems programming by Google"
    ...     },
    ...     question_explanation="Select your primary language"
    ... )
    >>>
    >>> # Confirmation
    >>> if confirm_interactive("Continue with installation?"):
    ...     print("Proceeding...")
"""

from promptosaurus.ui.domain.context import QuestionContext
from promptosaurus.ui.pipeline.orchestrator import PipelineOrchestrator
from promptosaurus.ui.pipeline.render_stage import RenderStage
from promptosaurus.ui.pipeline.state_update_stage import StateUpdateStage
from promptosaurus.ui.ui_factory import UIFactory


def select_option_with_explain(
    question: str,
    options: list[str],
    explanations: dict[str, str],
    question_explanation: str,
    default_index: int = 0,
    default_indices: set[int] | None = None,
    allow_multiple: bool = False,
    none_index: int | None = None,
) -> str | list[str]:
    """Interactive selection with number keys and explain option.

    This is the main entry point for interactive selection in promptosaurus.
    It presents options to the user with explanations and handles keyboard
    input for selection. The function uses the pipeline architecture
    internally but maintains backwards compatibility with existing code.

    Args:
        question: The main question/prompt to display to the user.
        options: List of available options to choose from.
        explanations: Dictionary mapping option strings to their explanations.
        question_explanation: Detailed explanation of what the question means.
        default_index: Index of the default option (used when user presses Enter).
        default_indices: Set of default indices for multi-select.
        allow_multiple: If True, allow selecting multiple options.
        none_index: Optional index for a "none of the above" option.

    Returns:
        If allow_multiple is False: The selected option string.
        If allow_multiple is True: List of selected option strings.

    Raises:
        UserCancelledError: If the user presses the quit key (typically 'q' or 'Escape').

    Example:
        >>> result = select_option_with_explain(
        ...     question="Choose a language:",
        ...     options=["Python", "TypeScript", "Go"],
        ...     explanations={
        ...         "Python": "Popular for data science",
        ...         "TypeScript": "Type-safe JavaScript",
        ...         "Go": "Systems programming"
        ...     },
        ...     question_explanation="Select your primary language",
        ...     default_index=0
        ... )
        >>> print(result)
        Python
    """
    context = QuestionContext(
        question=question,
        options=options,
        explanations=explanations,
        question_explanation=question_explanation,
        default_index=default_index,
        default_indices=default_indices if default_indices is not None else {default_index},
        allow_multiple=allow_multiple,
        none_index=none_index,
    )

    input_provider = UIFactory.create_input_provider()
    render_stage = RenderStage(renderer_selector=UIFactory.create_renderer)
    state_update = StateUpdateStage()

    pipeline = PipelineOrchestrator(
        input_provider=input_provider,
        render_stage=render_stage,
        state_update_stage=state_update,
    )

    return pipeline.run(context)


def confirm_interactive(prompt: str, default: bool = True) -> bool:
    """Yes/no confirmation dialog.

    Presents a simple yes/no confirmation to the user and returns
    their choice as a boolean.

    Args:
        prompt: The confirmation question to display.
        default: The default choice if user presses Enter (True for "Yes", False for "No").

    Returns:
        True if user confirmed ("Yes"), False if they declined ("No").

    Example:
        >>> if confirm_interactive("Install dependencies?"):
        ...     print("Installing...")
        >>> # Or with No as default
        >>> if not confirm_interactive("Delete files?", default=False):
        ...     print("Keeping files")
    """
    result = select_option_with_explain(
        question=prompt,
        options=["Yes", "No"],
        explanations={"Yes": "Confirm", "No": "Cancel"},
        question_explanation=prompt,
        default_index=0 if default else 1,
    )
    return result == "Yes"


def prompt_with_default(prompt: str, default: str) -> str:
    """Prompt with default value.

    Displays a prompt with a default value. If the user enters nothing,
    the default is returned.

    Args:
        prompt: The prompt text to display.
        default: The default value to use if input is empty.

    Returns:
        The user's input if non-empty, otherwise the default value.

    Example:
        >>> name = prompt_with_default("Enter your name", "Anonymous")
        >>> # If user presses Enter without typing: returns "Anonymous"
        >>> # If user types "John": returns "John"
    """
    suffix = f" [{default}]" if default else ""
    response = input(f"{prompt}{suffix}: ").strip()
    return response if response else default
