"""Render stage for UI pipeline."""

import curses
import sys
from collections.abc import Callable
from typing import Any

from promptosaurus.ui.domain.context import PipelineContext


class RenderStage:
    """Renders current state using curses for reliable terminal control.

    Uses Python's curses library for proper terminal state management,
    clearing, and cursor positioning. Curses is the standard, proven way
    to handle terminal operations reliably across all ANSI-compliant terminals.
    """

    def __init__(self, renderer_selector: Callable[[PipelineContext], object]):
        self.renderer_selector = renderer_selector
        self._stdscr: Any = None
        self._initialized: bool = False

    def _init_curses(self) -> None:
        """Initialize curses terminal control on first render.

        This is called once on the first render() call to set up
        the terminal for proper rendering. Subsequent calls reuse
        the same curses window.

        Note: We do NOT call curses.noecho(), curses.raw(), or curses.cbreak()
        here. The input provider (UnixInputProvider) handles terminal mode
        configuration. Curses is used only for rendering operations.

        We also do NOT call keypad(True) here. The UnixInputProvider handles
        arrow key parsing manually by reading raw escape sequences. Curses
        keypad mode interferes with this by changing how the terminal reports
        arrow keys, so we let the input provider have full control.
        """
        if self._initialized:
            return

        try:
            self._stdscr = curses.initscr()
            self._initialized = True
        except Exception:
            # Fallback to non-curses mode if initialization fails
            self._stdscr = None
            self._initialized = False

    def _cleanup_curses(self) -> None:
        """Clean up curses and release the window.

        Note: We do NOT restore terminal modes (echo, cbreak) here since
        we never set them in the first place. The input provider manages
        terminal modes independently.
        """
        if self._stdscr and self._initialized:
            try:
                curses.endwin()
            except Exception:
                pass  # Curses already cleaned up
            finally:
                self._stdscr = None
                self._initialized = False

    def render(self, context: PipelineContext) -> None:
        """Render current state to terminal.

        Uses curses for reliable terminal operations:
        - stdscr.clear() ensures complete clearing
        - stdscr.refresh() guarantees buffer flush
        - Proper cursor positioning throughout

        Args:
            context: The current pipeline context with question and state.
        """
        self._init_curses()

        if self._stdscr:
            # Use curses for rendering
            self._render_with_curses(context)
        else:
            # Fallback to simple print if curses unavailable
            self._render_simple(context)

    def _render_with_curses(self, context: PipelineContext) -> None:
        """Render using curses window management.

        Args:
            context: The current pipeline context.
        """
        if not self._stdscr:
            self._render_simple(context)
            return

        try:
            # Clear screen and move to top-left
            self._stdscr.clear()
            self._stdscr.move(0, 0)

            # Get terminal dimensions
            max_y, max_x = self._stdscr.getmaxyx()

            y = 0

            # Show question and explanation at the top
            question = context.question

            # Add blank line
            if y < max_y - 1:
                y += 1

            # Add question text
            if y < max_y - 1:
                question_text = question.question
                self._stdscr.addstr(y, 0, question_text)
                y += 1

            # Add blank line
            if y < max_y - 1:
                y += 1

            # Add explanation if present
            if question.question_explanation and y < max_y - 1:
                explanation_text = question.question_explanation
                self._stdscr.addstr(y, 0, explanation_text)
                y += 1

            # Add blank line
            if y < max_y - 1:
                y += 1

            # Render the options using the renderer
            renderer = self.renderer_selector(context)
            output = renderer.render(context)  # type: ignore[attr-defined]

            # Add renderer output (may span multiple lines)
            if output and y < max_y - 1:
                for line in output.split("\n"):
                    if y < max_y - 1:
                        self._stdscr.addstr(y, 0, line)
                        y += 1

            # Add controls section at bottom
            if context.mode == "select" and y < max_y - 3:
                y += 1  # Blank line

                selection_text = self._format_current_selection(context)
                selection_line = f"Current selection: {selection_text}"
                self._stdscr.addstr(y, 0, selection_line)
                y += 1

                y += 1  # Blank line

                controls_line = (
                    "Controls: Numbers to select, Enter to confirm, q to quit, ? for help"
                )
                self._stdscr.addstr(y, 0, controls_line)

            # Refresh to update display
            self._stdscr.refresh()
        except curses.error:
            # If curses operations fail, try simple rendering
            self._render_simple(context)

    def _render_simple(self, context: PipelineContext) -> None:
        """Fallback simple rendering using print().

        Used when curses is unavailable or fails.
        Uses ANSI escape codes for minimal clearing.

        Args:
            context: The current pipeline context.
        """
        # Move cursor to home and clear from cursor down
        # This is less aggressive than full reset but more reliable than reset codes
        sys.stdout.write("\033[H\033[J")
        sys.stdout.flush()

        # Show question and explanation at the top
        question = context.question
        print(f"\n{question.question}\n")
        if question.question_explanation:
            print(f"{question.question_explanation}\n")

        renderer = self.renderer_selector(context)
        output = renderer.render(context)  # type: ignore[attr-defined]
        print(output)

        if context.mode == "select":
            # Show current selection at bottom
            selection_text = self._format_current_selection(context)
            print(f"\nCurrent selection: {selection_text}")
            print("\nControls: Numbers to select, Enter to confirm, q to quit, ? for help")

    @staticmethod
    def _format_current_selection(context: PipelineContext) -> str:
        """Format the current selection for display.

        Args:
            context: The current pipeline context.

        Returns:
            Formatted selection string for display.
        """
        state = context.state
        options = context.question.options
        selection = state.current_selection

        if isinstance(selection, set):
            # Multi-select: show comma-delimited selections
            if selection:
                selected_options = [options[i] for i in sorted(selection) if 0 <= i < len(options)]
                return ", ".join(selected_options) if selected_options else "None"
            return "None"
        else:
            # Single select: show current selection
            if 0 <= selection < len(options):
                return options[selection]
            return "None"
