"""Tests for UI renderers."""

import pytest

from promptcli.ui.domain.context import PipelineContext, QuestionContext
from promptcli.ui.domain.renderer import Renderer
from promptcli.ui.render.columns import ColumnLayoutRenderer
from promptcli.ui.render.explain import ExplainRenderer
from promptcli.ui.render.vertical import VerticalLayoutRenderer
from promptcli.ui.state.multi import MultiSelectState
from promptcli.ui.state.single_select_state import SingleSelectState


class TestRendererBaseClass:
    """Tests for the Renderer base class."""

    def test_renderer_is_base_class(self):
        """Renderer should be a base class (not abstract)."""
        # Should be able to instantiate (though render will raise)
        renderer = Renderer()
        assert isinstance(renderer, Renderer)

    def test_renderer_render_raises_not_implemented(self):
        """Base Renderer.render should raise NotImplementedError."""
        renderer = Renderer()
        from unittest.mock import Mock

        context = Mock()

        with pytest.raises(NotImplementedError):
            renderer.render(context)


class TestColumnLayoutRenderer:
    """Tests for ColumnLayoutRenderer."""

    def test_inherits_from_renderer(self):
        """ColumnLayoutRenderer should inherit from Renderer."""
        assert issubclass(ColumnLayoutRenderer, Renderer)

    def test_renders_options_in_columns(self):
        """Should render options in column layout."""
        renderer = ColumnLayoutRenderer()
        question = QuestionContext(
            question="Test?",
            options=[str(i) for i in range(10)],
            explanations={},
            question_explanation="",
        )
        state = SingleSelectState(selected=0, max_index=9)
        context = PipelineContext(question=question, state=state, mode="select")

        output = renderer.render(context)

        assert isinstance(output, str)
        # Should contain numbered options
        assert "1." in output
        assert "10." in output


class TestVerticalLayoutRenderer:
    """Tests for VerticalLayoutRenderer."""

    def test_inherits_from_renderer(self):
        """VerticalLayoutRenderer should inherit from Renderer."""
        assert issubclass(VerticalLayoutRenderer, Renderer)

    def test_renders_single_selection(self):
        """Should render single selection with arrow marker."""
        renderer = VerticalLayoutRenderer()
        question = QuestionContext(
            question="Test?",
            options=["Option A", "Option B"],
            explanations={},
            question_explanation="",
            default_index=0,
        )
        state = SingleSelectState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="select")

        output = renderer.render(context)

        assert isinstance(output, str)
        assert "Option A" in output
        assert "Option B" in output
        assert "→" in output  # Selection marker

    def test_renders_multi_selection(self):
        """Should render multi selection with checkboxes."""
        renderer = VerticalLayoutRenderer()
        question = QuestionContext(
            question="Test?",
            options=["Option A", "Option B"],
            explanations={},
            question_explanation="",
            allow_multiple=True,
        )
        state = MultiSelectState(selected={0}, max_index=1)
        context = PipelineContext(question=question, state=state, mode="select")

        output = renderer.render(context)

        assert isinstance(output, str)
        assert "[*]" in output  # Checked box
        assert "[ ]" in output  # Unchecked box


class TestExplainRenderer:
    """Tests for ExplainRenderer."""

    def test_inherits_from_renderer(self):
        """ExplainRenderer should inherit from Renderer."""
        assert issubclass(ExplainRenderer, Renderer)

    def test_renders_explanation(self):
        """Should render question with explanation."""
        renderer = ExplainRenderer()
        question = QuestionContext(
            question="What is your preference?",
            options=["Option A", "Option B"],
            explanations={"Option A": "This is option A", "Option B": "This is option B"},
            question_explanation="This is the question explanation",
        )
        state = SingleSelectState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="explain")

        output = renderer.render(context)

        assert isinstance(output, str)
        assert "What is your preference?" in output
        assert "This is the question explanation" in output
        assert "Option A" in output
        assert "This is option A" in output
        assert "Press any key to return" in output
