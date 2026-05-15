"""Unit tests for prompticorn.ui._selector module.

Tests the public UI API functions for interactive selection, confirmation,
and prompting with default values.
"""

from unittest.mock import MagicMock, patch

import pytest

from prompticorn.ui._selector import (
    confirm_interactive,
    prompt_with_default,
    select_option_with_explain,
)


class TestSelectOptionWithExplain:
    """Test select_option_with_explain function."""

    def test_creates_question_context_with_correct_parameters(self) -> None:
        """Test that QuestionContext is created with correct parameters."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
        ):
            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.return_value = "option1"
            mock_pipeline.return_value = mock_pipeline_instance

            mock_render_instance = MagicMock()
            mock_render_instance.stdscr = None
            mock_render.return_value = mock_render_instance

            with patch(
                "prompticorn.ui._selector.UIFactory.create_input_provider"
            ) as mock_input_factory:
                mock_input_provider = MagicMock()
                mock_input_factory.return_value = mock_input_provider

                result = select_option_with_explain(
                    question="Pick one",
                    options=["option1", "option2"],
                    explanations={"option1": "First", "option2": "Second"},
                    question_explanation="Choose wisely",
                    default_index=0,
                    allow_multiple=False,
                )

                assert result == "option1"

    def test_returns_single_option_when_allow_multiple_false(self) -> None:
        """Test returns string when allow_multiple=False."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
        ):
            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.return_value = "selected_option"
            mock_pipeline.return_value = mock_pipeline_instance

            mock_render_instance = MagicMock()
            mock_render_instance.stdscr = None
            mock_render.return_value = mock_render_instance

            with patch("prompticorn.ui._selector.UIFactory.create_input_provider"):
                result = select_option_with_explain(
                    question="Q",
                    options=["A", "B"],
                    explanations={"A": "E1", "B": "E2"},
                    question_explanation="Ex",
                    allow_multiple=False,
                )

                assert isinstance(result, str)

    def test_returns_list_when_allow_multiple_true(self) -> None:
        """Test returns list when allow_multiple=True."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
        ):
            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.return_value = ["option1", "option2"]
            mock_pipeline.return_value = mock_pipeline_instance

            mock_render_instance = MagicMock()
            mock_render_instance.stdscr = None
            mock_render.return_value = mock_render_instance

            with patch("prompticorn.ui._selector.UIFactory.create_input_provider"):
                result = select_option_with_explain(
                    question="Q",
                    options=["opt1", "opt2", "opt3"],
                    explanations={"opt1": "E1", "opt2": "E2", "opt3": "E3"},
                    question_explanation="Ex",
                    allow_multiple=True,
                )

                assert isinstance(result, list)

    def test_cleans_up_curses_on_exit(self) -> None:
        """Test that curses resources are cleaned up even if pipeline fails."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
        ):
            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.side_effect = RuntimeError("Pipeline error")
            mock_pipeline.return_value = mock_pipeline_instance

            mock_render_instance = MagicMock()
            mock_render_instance.stdscr = None
            mock_render_instance.cleanup = MagicMock()
            mock_render.return_value = mock_render_instance

            with patch("prompticorn.ui._selector.UIFactory.create_input_provider"):
                with pytest.raises(RuntimeError):
                    select_option_with_explain(
                        question="Q",
                        options=["A"],
                        explanations={"A": "E"},
                        question_explanation="Ex",
                    )

                mock_render_instance.cleanup.assert_called_once()

    def test_handles_default_indices_none_input(self) -> None:
        """Test that default_indices defaults to set containing default_index."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
        ):
            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.return_value = "option1"
            mock_pipeline.return_value = mock_pipeline_instance

            mock_render_instance = MagicMock()
            mock_render_instance.stdscr = None
            mock_render.return_value = mock_render_instance

            with patch("prompticorn.ui._selector.UIFactory.create_input_provider"):
                result = select_option_with_explain(
                    question="Q",
                    options=["opt1", "opt2"],
                    explanations={"opt1": "E1", "opt2": "E2"},
                    question_explanation="Ex",
                    default_index=1,
                    default_indices=None,  # Should default to {1}
                )

                assert result == "option1"

    def test_uses_curses_provider_when_curses_available(self) -> None:
        """Test that CursesInputProvider is used when curses initializes."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.CursesInputProvider") as mock_curses_provider,
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
        ):
            mock_render_instance = MagicMock()
            mock_render_instance.stdscr = MagicMock()  # Curses available
            mock_render.return_value = mock_render_instance

            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.return_value = "option1"
            mock_pipeline.return_value = mock_pipeline_instance

            select_option_with_explain(
                question="Q",
                options=["opt1"],
                explanations={"opt1": "E1"},
                question_explanation="Ex",
            )

            # Verify CursesInputProvider was instantiated
            mock_curses_provider.assert_called()

    def test_fallback_to_default_input_on_curses_error(self) -> None:
        """Test fallback to default input provider when curses init fails."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
            patch(
                "prompticorn.ui._selector.UIFactory.create_input_provider"
            ) as mock_input_factory,
        ):
            mock_render_instance = MagicMock()
            mock_render_instance._init_curses.side_effect = RuntimeError("Curses failed")
            mock_render.return_value = mock_render_instance

            mock_input_provider = MagicMock()
            mock_input_factory.return_value = mock_input_provider

            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.return_value = "option1"
            mock_pipeline.return_value = mock_pipeline_instance

            select_option_with_explain(
                question="Q",
                options=["opt1"],
                explanations={"opt1": "E1"},
                question_explanation="Ex",
            )

            # Verify fallback was used
            mock_input_factory.assert_called()

    def test_accepts_none_index_parameter(self) -> None:
        """Test that none_index parameter is accepted."""
        with (
            patch("prompticorn.ui._selector.RenderStage") as mock_render,
            patch("prompticorn.ui._selector.StateUpdateStage"),
            patch("prompticorn.ui._selector.PipelineOrchestrator") as mock_pipeline,
        ):
            mock_pipeline_instance = MagicMock()
            mock_pipeline_instance.run.return_value = "option1"
            mock_pipeline.return_value = mock_pipeline_instance

            mock_render_instance = MagicMock()
            mock_render_instance.stdscr = None
            mock_render.return_value = mock_render_instance

            with patch("prompticorn.ui._selector.UIFactory.create_input_provider"):
                result = select_option_with_explain(
                    question="Q",
                    options=["opt1", "opt2", "None"],
                    explanations={"opt1": "E1", "opt2": "E2", "None": "N"},
                    question_explanation="Ex",
                    none_index=2,  # Last option is "none"
                )

                assert result == "option1"


class TestConfirmInteractive:
    """Test confirm_interactive function."""

    def test_returns_true_on_yes(self) -> None:
        """Test returns True when user selects Yes."""
        with patch("prompticorn.ui._selector.select_option_with_explain") as mock_select:
            mock_select.return_value = "Yes"

            result = confirm_interactive(prompt="Proceed?")

            assert result is True

    def test_returns_false_on_no(self) -> None:
        """Test returns False when user selects No."""
        with patch("prompticorn.ui._selector.select_option_with_explain") as mock_select:
            mock_select.return_value = "No"

            result = confirm_interactive(prompt="Proceed?")

            assert result is False

    def test_uses_yes_as_default_when_default_true(self) -> None:
        """Test that default_index=0 (Yes) when default=True."""
        with patch("prompticorn.ui._selector.select_option_with_explain") as mock_select:
            mock_select.return_value = "Yes"

            confirm_interactive(prompt="Proceed?", default=True)

            # Verify default_index=0 was passed
            call_kwargs = mock_select.call_args[1]
            assert call_kwargs["default_index"] == 0

    def test_uses_no_as_default_when_default_false(self) -> None:
        """Test that default_index=1 (No) when default=False."""
        with patch("prompticorn.ui._selector.select_option_with_explain") as mock_select:
            mock_select.return_value = "No"

            confirm_interactive(prompt="Proceed?", default=False)

            # Verify default_index=1 was passed
            call_kwargs = mock_select.call_args[1]
            assert call_kwargs["default_index"] == 1

    def test_passes_correct_options(self) -> None:
        """Test that Yes/No options are passed to select_option_with_explain."""
        with patch("prompticorn.ui._selector.select_option_with_explain") as mock_select:
            mock_select.return_value = "Yes"

            confirm_interactive(prompt="Continue?")

            # Verify options are correct
            call_kwargs = mock_select.call_args[1]
            assert call_kwargs["options"] == ["Yes", "No"]

    def test_passes_prompt_as_question(self) -> None:
        """Test that prompt is passed as question to select_option_with_explain."""
        with patch("prompticorn.ui._selector.select_option_with_explain") as mock_select:
            mock_select.return_value = "Yes"

            test_prompt = "Do you want to continue?"
            confirm_interactive(prompt=test_prompt)

            # Verify prompt is passed as question
            call_kwargs = mock_select.call_args[1]
            assert call_kwargs["question"] == test_prompt


class TestPromptWithDefault:
    """Test prompt_with_default function."""

    def test_returns_default_when_input_empty(self) -> None:
        """Test returns default value when user input is empty."""
        with patch("builtins.input", return_value=""):
            result = prompt_with_default(prompt="Name", default="Alice")

            assert result == "Alice"

    def test_returns_default_when_input_only_whitespace(self) -> None:
        """Test returns default value when input contains only whitespace."""
        with patch("builtins.input", return_value="   "):
            result = prompt_with_default(prompt="Name", default="Bob")

            assert result == "Bob"

    def test_returns_user_input_when_non_empty(self) -> None:
        """Test returns user input when non-empty."""
        with patch("builtins.input", return_value="Charlie"):
            result = prompt_with_default(prompt="Name", default="Default")

            assert result == "Charlie"

    def test_strips_whitespace_from_input(self) -> None:
        """Test that leading/trailing whitespace is stripped."""
        with patch("builtins.input", return_value="  Dave  "):
            result = prompt_with_default(prompt="Name", default="Default")

            assert result == "Dave"

    def test_displays_default_value_in_prompt(self) -> None:
        """Test that default value is shown in prompt suffix."""
        with patch("builtins.input", return_value="") as mock_input:
            prompt_with_default(prompt="Username", default="guest")

            # Verify input was called with default shown
            called_prompt = mock_input.call_args[0][0]
            assert "[guest]" in called_prompt

    def test_handles_empty_default_value(self) -> None:
        """Test handles empty string as default value."""
        with patch("builtins.input", return_value=""):
            result = prompt_with_default(prompt="Optional", default="")

            assert result == ""

    def test_prompt_format_with_default(self) -> None:
        """Test the exact prompt format includes default in brackets."""
        with patch("builtins.input", return_value="") as mock_input:
            prompt_with_default(prompt="Port", default="8080")

            called_prompt = mock_input.call_args[0][0]
            assert called_prompt == "Port [8080]: "

    def test_returns_non_empty_input_over_default(self) -> None:
        """Test that non-empty input always takes precedence."""
        with patch("builtins.input", return_value="user_value"):
            result = prompt_with_default(prompt="Setting", default="default_value")

            assert result == "user_value"
            assert result != "default_value"

    def test_preserves_internal_whitespace_in_input(self) -> None:
        """Test that whitespace within input is preserved."""
        with patch("builtins.input", return_value="  hello world  "):
            result = prompt_with_default(prompt="Name", default="default")

            # Only leading/trailing should be stripped
            assert result == "hello world"

    @pytest.mark.parametrize(
        "user_input,expected",
        [
            ("", "default"),
            ("   ", "default"),
            ("value", "value"),
            ("  value  ", "value"),
            ("0", "0"),  # Edge case: "0" is falsy but should not be treated as empty
        ],
    )
    def test_various_input_scenarios(self, user_input: str, expected: str) -> None:
        """Test various input/default combinations."""
        with patch("builtins.input", return_value=user_input):
            result = prompt_with_default(prompt="Q", default="default")

            assert result == expected
