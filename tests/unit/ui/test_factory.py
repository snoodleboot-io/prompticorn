"""Tests for UI factory."""

import pytest
from sweet_tea.abstract_factory import AbstractFactory
from sweet_tea.sweet_tea_error import SweetTeaError

from prompticorn.ui.domain.context import PipelineContext, QuestionContext
from prompticorn.ui.domain.renderer import Renderer
from prompticorn.ui.render.columns import ColumnLayoutRenderer
from prompticorn.ui.render.explain import ExplainRenderer
from prompticorn.ui.render.vertical import VerticalLayoutRenderer
from prompticorn.ui.state.single_selection_state import SingleSelectionState
from prompticorn.ui.ui_factory import UIFactory


class TestUIFactory:
    """Tests for UIFactory."""

    def test_create_renderer_returns_renderer_subclass(self):
        """Factory should return instances of Renderer base class."""
        question = QuestionContext(
            question="Test?",
            options=["a", "b"],
            explanations={},
            question_explanation="",
        )
        state = SingleSelectionState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="select")

        renderer = UIFactory.create_renderer(context)

        assert isinstance(renderer, Renderer)

    def test_create_renderer_selects_vertical_for_few_options(self):
        """Factory should return VerticalLayoutRenderer for <= 8 options."""
        question = QuestionContext(
            question="Test?",
            options=[str(i) for i in range(5)],
            explanations={},
            question_explanation="",
        )
        state = SingleSelectionState(selected=0, max_index=4)
        context = PipelineContext(question=question, state=state, mode="select")

        renderer = UIFactory.create_renderer(context)

        assert isinstance(renderer, VerticalLayoutRenderer)

    def test_create_renderer_selects_column_for_many_options(self):
        """Factory should return ColumnLayoutRenderer for > 8 options."""
        question = QuestionContext(
            question="Test?",
            options=[str(i) for i in range(10)],
            explanations={},
            question_explanation="",
        )
        state = SingleSelectionState(selected=0, max_index=9)
        context = PipelineContext(question=question, state=state, mode="select")

        renderer = UIFactory.create_renderer(context)

        assert isinstance(renderer, ColumnLayoutRenderer)

    def test_create_renderer_selects_explain_for_explain_mode(self):
        """Factory should return ExplainRenderer for explain mode."""
        question = QuestionContext(
            question="Test?",
            options=["a", "b"],
            explanations={},
            question_explanation="Test explanation",
        )
        state = SingleSelectionState(selected=0, max_index=1)
        context = PipelineContext(question=question, state=state, mode="explain")

        renderer = UIFactory.create_renderer(context)

        assert isinstance(renderer, ExplainRenderer)


class TestRendererRegistration:
    """Tests that renderers are properly registered with sweet_tea."""

    def test_column_layout_renderer_registered(self):
        """ColumnLayoutRenderer should be registered with snake_case key."""
        factory = AbstractFactory[Renderer]
        renderer = factory.create("column_layout_renderer")
        assert isinstance(renderer, ColumnLayoutRenderer)

    def test_vertical_layout_renderer_registered(self):
        """VerticalLayoutRenderer should be registered with snake_case key."""
        factory = AbstractFactory[Renderer]
        renderer = factory.create("vertical_layout_renderer")
        assert isinstance(renderer, VerticalLayoutRenderer)

    def test_explain_renderer_registered(self):
        """ExplainRenderer should be registered with snake_case key."""
        factory = AbstractFactory[Renderer]
        renderer = factory.create("explain_renderer")
        assert isinstance(renderer, ExplainRenderer)

    def test_unregistered_key_raises_error(self):
        """Accessing unregistered key should raise SweetTeaError."""
        factory = AbstractFactory[Renderer]
        with pytest.raises(SweetTeaError):
            factory.create("nonexistent_renderer")
