"""Tests for RenderStage multi-line explanation rendering."""

from unittest.mock import MagicMock, Mock

from prompticorn.ui.domain.context import PipelineContext, QuestionContext
from prompticorn.ui.pipeline.render_stage import RenderStage
from prompticorn.ui.state.single_selection_state import SingleSelectionState


class TestRenderStageMultilineExplanation:
    """Tests for multi-line explanation rendering in RenderStage."""

    def test_render_single_line_explanation(self):
        """Test rendering a single-line explanation."""
        # Create a mock stdscr
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (30, 80)

        # Create a question with single-line explanation
        question = QuestionContext(
            question="What is your preference?",
            options=["Option A", "Option B"],
            explanations={"Option A": "Explanation A"},
            question_explanation="This is a single line explanation.",
            default_index=0,
            default_indices={0},
            allow_multiple=False,
            none_index=None,
        )

        # Create state and context
        state = SingleSelectionState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="select")

        # Create render stage and inject mock stdscr
        renderer_selector = Mock(return_value=Mock(render=Mock(return_value="")))
        stage = RenderStage(renderer_selector)
        stage._stdscr = mock_stdscr
        stage._initialized = True

        # Render
        stage._render_with_curses(context)

        # Verify the explanation was rendered with addstr (single call)
        calls = mock_stdscr.addstr.call_args_list
        explanation_calls = [c for c in calls if "single line explanation" in str(c)]
        assert len(explanation_calls) == 1

    def test_render_multiline_explanation(self):
        """Test rendering a multi-line explanation splits correctly."""
        # Create a mock stdscr
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (30, 80)

        # Create a question with multi-line explanation (like PythonRuntimeQuestion)
        multiline_explanation = """Python runtime affects package compatibility, performance, and available features.

- Newer versions have better performance but may have compatibility issues
- Some packages only support specific versions
- match statements require 3.10+, walrus operator requires 3.8+"""

        question = QuestionContext(
            question="What Python runtime version do you want to use?",
            options=["3.11", "3.12", "3.13"],
            explanations={"3.11": "Stable", "3.12": "Latest", "3.13": "Cutting edge"},
            question_explanation=multiline_explanation,
            default_index=1,
            default_indices={1},
            allow_multiple=False,
            none_index=None,
        )

        # Create state and context
        state = SingleSelectionState(selected=1, max_index=2)
        context = PipelineContext(question=question, state=state, mode="select")

        # Create render stage and inject mock stdscr
        renderer_selector = Mock(return_value=Mock(render=Mock(return_value="")))
        stage = RenderStage(renderer_selector)
        stage._stdscr = mock_stdscr
        stage._initialized = True

        # Render
        stage._render_with_curses(context)

        # Verify multi-line explanation was split and rendered line by line
        calls = mock_stdscr.addstr.call_args_list

        # Should have multiple calls for the explanation lines
        # The explanation has 5 lines (separated by newlines)
        explanation_lines = multiline_explanation.split("\n")
        for exp_line in explanation_lines:
            if exp_line:  # Skip empty lines
                matching_calls = [c for c in calls if exp_line in str(c)]
                assert len(matching_calls) >= 1, f"Expected to find call with line: {exp_line}"

    def test_render_multiline_explanation_respects_terminal_height(self):
        """Test that multi-line explanation rendering respects terminal height limits."""
        # Create a mock stdscr with small height
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (10, 80)  # Only 10 lines tall

        # Create a question with multi-line explanation
        multiline_explanation = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5\nLine 6\nLine 7"

        question = QuestionContext(
            question="Question?",
            options=["A", "B"],
            explanations={"A": "Exp A"},
            question_explanation=multiline_explanation,
            default_index=0,
            default_indices={0},
            allow_multiple=False,
            none_index=None,
        )

        state = SingleSelectionState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="select")

        # Create render stage
        renderer_selector = Mock(return_value=Mock(render=Mock(return_value="")))
        stage = RenderStage(renderer_selector)
        stage._stdscr = mock_stdscr
        stage._initialized = True

        # Render - should not raise
        stage._render_with_curses(context)

        # Verify no assertion errors from y < max_y checks
        assert mock_stdscr.addstr.called


class TestRenderStageEmptyExplanation:
    """Tests for edge cases with explanations."""

    def test_render_empty_explanation(self):
        """Test rendering with empty explanation."""
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (30, 80)

        question = QuestionContext(
            question="What is your preference?",
            options=["Option A", "Option B"],
            explanations={},
            question_explanation="",
            default_index=0,
            default_indices={0},
            allow_multiple=False,
            none_index=None,
        )

        state = SingleSelectionState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="select")

        renderer_selector = Mock(return_value=Mock(render=Mock(return_value="")))
        stage = RenderStage(renderer_selector)
        stage._stdscr = mock_stdscr
        stage._initialized = True

        # Should not raise
        stage._render_with_curses(context)
        assert mock_stdscr.addstr.called

    def test_render_explanation_with_trailing_newlines(self):
        """Test rendering explanation with trailing newlines."""
        mock_stdscr = MagicMock()
        mock_stdscr.getmaxyx.return_value = (30, 80)

        question = QuestionContext(
            question="Question?",
            options=["A", "B"],
            explanations={},
            question_explanation="Line 1\nLine 2\n\n",  # Trailing newlines
            default_index=0,
            default_indices={0},
            allow_multiple=False,
            none_index=None,
        )

        state = SingleSelectionState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="select")

        renderer_selector = Mock(return_value=Mock(render=Mock(return_value="")))
        stage = RenderStage(renderer_selector)
        stage._stdscr = mock_stdscr
        stage._initialized = True

        # Should not raise - trailing newlines create empty strings when split
        stage._render_with_curses(context)
        assert mock_stdscr.addstr.called
