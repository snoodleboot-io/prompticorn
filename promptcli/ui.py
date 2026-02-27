"""Interactive UI components for CLI with number-based selection."""

import os
import sys

# Check if we're in a interactive terminal
IS_TTY = sys.stdin.isatty()


def format_options_columns(
    options: list[str],
    items_per_column: int = 8,
    column_width: int = 20,
) -> str:
    """
    Format options into columns for display.

    Fills columns left-to-right, top-to-bottom (1-8 in col 1, 9-16 in col 2, etc.)
    Example with items_per_column=8 and column_width=20:
        1. python            9. php
        2. typescript       10. swift
        ...

    Args:
        options: List of option strings
        items_per_column: Number of items per column (default 8)
        column_width: Width reserved for each column (default 20)

    Returns:
        Formatted string with options in columns
    """
    if not options:
        return ""

    num_items = len(options)
    num_columns = (num_items + items_per_column - 1) // items_per_column
    lines: list[str] = []

    for row in range(items_per_column):
        line_parts = []
        for col in range(num_columns):
            idx = col * items_per_column + row
            if idx < num_items:
                # Format: " 1. optionname        " (padded to column_width)
                num_str = f"{idx + 1}."
                # Content is: num + space + option
                content = f"{num_str:>3} {options[idx]}"
                # Pad to column_width
                part = content.ljust(column_width)
                line_parts.append(part)

        if line_parts:
            lines.append("".join(line_parts))

    return "\n".join(lines)


def select_option_with_explain(
    question: str,
    options: list[str],
    explanations: dict[str, str],
    question_explanation: str,
    default_index: int = 0,
    allow_multiple: bool = False,
) -> str | list[str]:
    """
    Interactive selection with number keys and explain option.

    Args:
        question: The question to display
        options: List of available options
        explanations: Dict mapping option -> explanation
        question_explanation: Explanation of what the question is asking
        default_index: Index of default selection
        allow_multiple: Whether multiple selections are allowed

    Returns:
        The selected option (str) or list of selected options (list)
    """
    # Add "Explain" as the last option (only if not already there)
    all_options = list(options)
    if "Explain" not in all_options:
        all_options.append("Explain")

    selected: int | set[int] = {default_index} if allow_multiple else default_index

    while True:
        # Clear screen
        print("\033[2J\033[H", end="")

        print(f"\n{question}\n")
        print("=" * len(question))
        print(f"\n{question_explanation}\n")

        # Check if we should use columns (more than 8 options)
        use_columns = len(all_options) > 8

        if use_columns:
            # Use column layout
            col_width = 20
            print(format_options_columns(all_options, items_per_column=8, column_width=col_width))
        else:
            # Use regular vertical list
            if allow_multiple:
                print("Enter numbers to toggle selection, Enter to confirm:\n")
            else:
                print("Enter a number to select:\n")

            for i, opt in enumerate(all_options):
                num = f"{i + 1}."
                if allow_multiple:
                    # Check if this option is selected
                    is_selected = i in selected if isinstance(selected, set) else i == selected
                    marker = "[*]" if is_selected else "[ ]"
                else:
                    marker = "→" if i == selected else " "
                    if i == default_index:
                        default_tag = " (default)"
                    else:
                        default_tag = ""

                # Show explanation for selected option OR for Explain
                if allow_multiple:
                    show_exp = i in selected if isinstance(selected, set) else i == selected
                else:
                    show_exp = i == selected

                if show_exp:
                    if opt == "Explain":
                        exp = "Learn more about this question"
                    else:
                        exp = explanations.get(opt, "")
                    if exp:
                        print(f"  {marker} {num} {opt}{default_tag}")
                        print(f"       └─ {exp}")
                    else:
                        print(f"  {marker} {num} {opt}{default_tag}")
                else:
                    print(f"  {marker} {num} {opt}")

        print("\nControls: Numbers to select, Enter to confirm, q to quit")

        try:
            if os.name == "nt":
                import msvcrt

                key = msvcrt.getch()
                if key == b"\r":  # Enter - confirm
                    # If explain selected, show full explanation
                    if allow_multiple:
                        explain_idx = len(all_options) - 1
                        if explain_idx in selected:
                            selected.remove(explain_idx)
                            print("\033[2J\033[H", end="")
                            print(f"\n{question}\n")
                            print("=" * len(question))
                            print(f"\n{question_explanation}\n")
                            print("Available options:\n")
                            for opt in options:
                                exp = explanations.get(opt, "")
                                print(f"  • {opt}")
                                if exp:
                                    print(f"    {exp}")
                                print()
                            print("\nPress any key to return...")
                            msvcrt.getch()
                            continue

                        # Return list of selected options (excluding Explain)
                        return [options[i] for i in sorted(selected) if i < len(options)]
                    else:
                        if selected == len(all_options) - 1:
                            # Explain selected, show full explanation
                            print("\033[2J\033[H", end="")
                            print(f"\n{question}\n")
                            print("=" * len(question))
                            print(f"\n{question_explanation}\n")
                            print("Available options:\n")
                            for opt in options:
                                exp = explanations.get(opt, "")
                                print(f"  • {opt}")
                                if exp:
                                    print(f"    {exp}")
                                print()
                            print("\nPress any key to return...")
                            msvcrt.getch()
                        else:
                            return options[selected]
                elif key == b"q":
                    if allow_multiple:
                        return [options[default_index]]
                    return options[default_index]
                elif key == b"\xe0":  # Arrow key prefix on Windows
                    key2 = msvcrt.getch()
                    if key2 == b"H":  # Up
                        if allow_multiple:
                            # Not using arrows for multi-select
                            pass
                        else:
                            selected = max(0, selected - 1)
                    elif key2 == b"P":  # Down
                        if allow_multiple:
                            pass
                        else:
                            selected = min(len(all_options) - 1, selected + 1)
                else:
                    # Number keys
                    try:
                        num = int(key.decode()) - 1
                        if 0 <= num < len(all_options):
                            if allow_multiple:
                                # Toggle selection
                                if num in selected:
                                    selected.remove(num)
                                else:
                                    selected.add(num)
                            else:
                                selected = num
                    except (ValueError, UnicodeDecodeError):
                        pass
            else:
                # Unix-like systems
                import termios
                import tty

                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    key = sys.stdin.read(1)
                    if key == "\r":  # Enter
                        if allow_multiple:
                            explain_idx = len(all_options) - 1
                            if explain_idx in selected:
                                selected.remove(explain_idx)
                                print("\033[2J\033[H", end="")
                                print(f"\n{question}\n")
                                print("=" * len(question))
                                print(f"\n{question_explanation}\n")
                                print("Available options:\n")
                                for opt in options:
                                    exp = explanations.get(opt, "")
                                    print(f"  • {opt}")
                                    if exp:
                                        print(f"    {exp}")
                                    print()
                                print("\nPress any key to return...")
                                sys.stdin.read(1)
                                continue

                            return [options[i] for i in sorted(selected) if i < len(options)]
                        else:
                            if selected == len(all_options) - 1:
                                # Explain
                                print("\033[2J\033[H", end="")
                                print(f"\n{question}\n")
                                print("=" * len(question))
                                print(f"\n{question_explanation}\n")
                                print("Available options:\n")
                                for opt in options:
                                    exp = explanations.get(opt, "")
                                    print(f"  • {opt}")
                                    if exp:
                                        print(f"    {exp}")
                                    print()
                                print("\nPress any key to return...")
                                sys.stdin.read(1)
                            else:
                                return options[selected]
                    elif key == "q":
                        if allow_multiple:
                            return [options[default_index]]
                        return options[default_index]
                    elif key == "\x1b":  # Escape
                        next1 = sys.stdin.read(1)
                        if next1 == "[":
                            next2 = sys.stdin.read(1)
                            if next2 == "A":  # Up
                                if not allow_multiple:
                                    selected = max(0, selected - 1)
                            elif next2 == "B":  # Down
                                if not allow_multiple:
                                    selected = min(len(all_options) - 1, selected + 1)
                    else:
                        # Number keys
                        try:
                            num = int(key) - 1
                            if 0 <= num < len(all_options):
                                if allow_multiple:
                                    if num in selected:
                                        selected.remove(num)
                                    else:
                                        selected.add(num)
                                else:
                                    selected = num
                        except ValueError:
                            pass
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        except Exception:
            # Fallback
            print("\nEnter number(s) comma-separated:")
            choice = input(f" [{default_index + 1}]: ").strip()
            if not choice:
                return options[default_index]
            try:
                if allow_multiple:
                    # Parse comma-separated numbers
                    indices = [int(x.strip()) - 1 for x in choice.split(",")]
                    result = [options[i] for i in indices if 0 <= i < len(options)]
                    if result:
                        return result
                else:
                    idx = int(choice) - 1
                    if 0 <= idx < len(all_options):
                        if idx == len(all_options) - 1:
                            print(f"\n{question_explanation}\n")
                            input("Press Enter to continue...")
                        else:
                            return options[idx]
            except ValueError:
                pass
            return options[default_index]


def confirm_interactive(prompt: str, default: bool = True) -> bool:
    """Yes/no confirmation."""
    suffix = " [Y/n]" if default else " [y/N]"
    while True:
        response = input(f"{prompt}{suffix}: ").strip().lower()
        if not response:
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter y or n")


def prompt_with_default(prompt: str, default: str) -> str:
    """Prompt with default."""
    suffix = f" [{default}]" if default else ""
    response = input(f"{prompt}{suffix}: ").strip()
    return response if response else default
