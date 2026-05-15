"""Unit tests for prompticorn.ui.pipeline.orchestrator.

This module tests the PipelineOrchestrator class which coordinates
the entire UI interaction flow. Tests focus on state transitions,
event handling, and proper pipeline execution.
"""

from unittest.mock import Mock

import pytest

from prompticorn.ui.domain.context import QuestionContext
from prompticorn.ui.pipeline.orchestrator import PipelineOrchestrator
from prompticorn.ui.state.multi_selection_state import MultiSelectionState
from prompticorn.ui.state.mutual_exclusion_multi_selection_state import (
    MutualExclusionMultiSelectionState,
)
from prompticorn.ui.state.single_selection_state import SingleSelectionState


class TestPipelineOrchestratorInit:
    """Tests for PipelineOrchestrator.__init__ method."""

    def test_initializes_with_required_components(self):
        """Should initialize with input_provider, render_stage, and state_update_stage."""
        # Arrange
        input_provider = Mock()
        render_stage = Mock()
        state_update_stage = Mock()

        # Act
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Assert
        assert orchestrator.input_provider == input_provider
        assert orchestrator.render_stage == render_stage
        assert orchestrator.state_update_stage == state_update_stage
        assert orchestrator.command_factory is not None

    def test_creates_command_factory_instance(self):
        """Should create a CommandFactory instance during initialization."""
        # Arrange
        input_provider = Mock()
        render_stage = Mock()
        state_update_stage = Mock()

        # Act
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Assert
        from prompticorn.ui.pipeline.command_factory import CommandFactory

        assert isinstance(orchestrator.command_factory, CommandFactory)


class TestPipelineOrchestratorRun:
    """Tests for PipelineOrchestrator.run method."""

    @pytest.fixture
    def mock_components(self):
        """Create mock components for testing."""
        input_provider = Mock()
        render_stage = Mock()
        state_update_stage = Mock()
        return input_provider, render_stage, state_update_stage

    @pytest.fixture
    def single_select_question(self):
        """Create a single-selection question context."""
        return QuestionContext(
            question="Select an option",
            options=["Option 1", "Option 2", "Option 3"],
            explanations={},
            question_explanation="Select one option from the list",
            allow_multiple=False,
            default_index=0,
            default_indices={0},
            none_index=None,
        )

    @pytest.fixture
    def multi_select_question(self):
        """Create a multi-selection question context."""
        return QuestionContext(
            question="Select multiple options",
            options=["Option A", "Option B", "Option C"],
            explanations={},
            question_explanation="Select one or more options from the list",
            allow_multiple=True,
            default_index=0,
            default_indices={0, 1},
            none_index=None,
        )

    @pytest.fixture
    def mutual_exclusion_question(self):
        """Create a mutual exclusion multi-selection question context."""
        return QuestionContext(
            question="Select options or None",
            options=["Option X", "Option Y", "None"],
            explanations={},
            question_explanation="Select options or None for no selection",
            allow_multiple=True,
            default_index=0,
            default_indices={0},
            none_index=2,
        )

    def test_creates_single_selection_state_for_single_select(
        self, mock_components, single_select_question
    ):
        """Should create SingleSelectionState when allow_multiple is False."""
        # Arrange
        input_provider, render_stage, state_update_stage = mock_components
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Mock the event flow to complete immediately
        mock_event = Mock()
        input_provider.events = iter([mock_event])

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        mock_result = Mock(
            transition_to=None, new_state=None, continue_pipeline=False, output_value="Option 1"
        )
        state_update_stage.apply = Mock(return_value=mock_result)

        # Act
        result = orchestrator.run(single_select_question)

        # Assert
        # Verify that the context was created with SingleSelectionState
        call_args = render_stage.render.call_args[0][0]
        assert isinstance(call_args.state, SingleSelectionState)
        assert result == "Option 1"

    def test_creates_multi_selection_state_for_multi_select(
        self, mock_components, multi_select_question
    ):
        """Should create MultiSelectionState when allow_multiple is True and no none_index."""
        # Arrange
        input_provider, render_stage, state_update_stage = mock_components
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Mock the event flow to complete immediately
        mock_event = Mock()
        input_provider.events = iter([mock_event])

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        mock_result = Mock(
            transition_to=None,
            new_state=None,
            continue_pipeline=False,
            output_value=["Option A", "Option B"],
        )
        state_update_stage.apply = Mock(return_value=mock_result)

        # Act
        result = orchestrator.run(multi_select_question)

        # Assert
        # Verify that the context was created with MultiSelectionState
        call_args = render_stage.render.call_args[0][0]
        assert isinstance(call_args.state, MultiSelectionState)
        assert result == ["Option A", "Option B"]

    def test_creates_mutual_exclusion_state_when_none_index_present(
        self, mock_components, mutual_exclusion_question
    ):
        """Should create MutualExclusionMultiSelectionState when none_index is specified."""
        # Arrange
        input_provider, render_stage, state_update_stage = mock_components
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Mock the event flow
        mock_event = Mock()
        input_provider.events = iter([mock_event])

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        mock_result = Mock(
            transition_to=None, new_state=None, continue_pipeline=False, output_value=["Option X"]
        )
        state_update_stage.apply = Mock(return_value=mock_result)

        # Act
        result = orchestrator.run(mutual_exclusion_question)

        # Assert
        call_args = render_stage.render.call_args[0][0]
        assert isinstance(call_args.state, MutualExclusionMultiSelectionState)
        assert result == ["Option X"]

    def test_handles_state_transitions_during_pipeline(
        self, mock_components, single_select_question
    ):
        """Should update state when result contains new_state."""
        # Arrange
        input_provider, render_stage, state_update_stage = mock_components
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Create a sequence of events and results
        events = [Mock(), Mock(), Mock()]
        input_provider.events = iter(events)

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        # First two results continue pipeline with state updates
        new_state_1 = SingleSelectionState(1, 3)
        new_state_2 = SingleSelectionState(2, 3)

        results = [
            Mock(transition_to=None, new_state=new_state_1, continue_pipeline=True),
            Mock(transition_to=None, new_state=new_state_2, continue_pipeline=True),
            Mock(
                transition_to=None, new_state=None, continue_pipeline=False, output_value="Option 3"
            ),
        ]
        state_update_stage.apply = Mock(side_effect=results)

        # Act
        result = orchestrator.run(single_select_question)

        # Assert
        assert state_update_stage.apply.call_count == 3
        assert result == "Option 3"

    def test_handles_explain_mode_transition(self, mock_components, single_select_question):
        """Should transition to explain mode and back to select mode."""
        # Arrange
        input_provider, render_stage, state_update_stage = mock_components
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Create a sequence of events
        events = [Mock(), Mock(), Mock(), Mock()]
        input_provider.events = iter(events)

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        # First result triggers explain mode, then continue, then complete
        results = [
            Mock(transition_to="explain", new_state=None, continue_pipeline=True),
            Mock(transition_to=None, new_state=None, continue_pipeline=True),
            Mock(
                transition_to=None, new_state=None, continue_pipeline=False, output_value="Option 1"
            ),
        ]
        state_update_stage.apply = Mock(side_effect=results)

        # Act
        result = orchestrator.run(single_select_question)

        # Assert
        # Should render twice for explain mode (once in main loop, once in _handle_explain_mode)
        assert render_stage.render.call_count >= 3
        assert result == "Option 1"

    def test_continues_pipeline_until_completion(self, mock_components, single_select_question):
        """Should continue processing events until continue_pipeline is False."""
        # Arrange
        input_provider, render_stage, state_update_stage = mock_components
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Create multiple events
        events = [Mock() for _ in range(5)]
        input_provider.events = iter(events)

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        # Create results that continue pipeline 4 times, then complete
        results = [
            Mock(transition_to=None, new_state=None, continue_pipeline=True),
            Mock(transition_to=None, new_state=None, continue_pipeline=True),
            Mock(transition_to=None, new_state=None, continue_pipeline=True),
            Mock(transition_to=None, new_state=None, continue_pipeline=True),
            Mock(transition_to=None, new_state=None, continue_pipeline=False, output_value="Final"),
        ]
        state_update_stage.apply = Mock(side_effect=results)

        # Act
        result = orchestrator.run(single_select_question)

        # Assert
        assert state_update_stage.apply.call_count == 5
        assert orchestrator.command_factory.create_command.call_count == 5
        assert result == "Final"

    def test_uses_default_indices_fallback_for_multi_select(self, mock_components):
        """Should fallback to default_index when default_indices is None in multi-select."""
        # Arrange
        input_provider, render_stage, state_update_stage = mock_components
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Create a multi-select question without default_indices
        question = QuestionContext(
            question="Select options",
            options=["A", "B", "C"],
            explanations={},
            question_explanation="Select options from the list",
            allow_multiple=True,
            default_index=1,  # Fallback to this
            default_indices=set(),  # Empty set instead of None
            none_index=None,
        )

        # Mock the event flow
        mock_event = Mock()
        input_provider.events = iter([mock_event])

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        mock_result = Mock(
            transition_to=None, new_state=None, continue_pipeline=False, output_value=["B"]
        )
        state_update_stage.apply = Mock(return_value=mock_result)

        # Act
        result = orchestrator.run(question)

        # Assert
        # Verify the initial state was created with fallback to default_index
        call_args = render_stage.render.call_args[0][0]
        assert isinstance(call_args.state, MultiSelectionState)
        # The state should have been initialized with {1} (the default_index)
        assert result == ["B"]


class TestHandleExplainMode:
    """Tests for PipelineOrchestrator._handle_explain_mode method."""

    def test_renders_context_in_explain_mode(self):
        """Should render the context when in explain mode."""
        # Arrange
        input_provider = Mock()
        render_stage = Mock()
        state_update_stage = Mock()
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        context = Mock(mode="explain")
        events = iter([Mock()])  # Single event to consume

        # Act
        orchestrator._handle_explain_mode(context, events)

        # Assert
        render_stage.render.assert_called_once_with(context)

    def test_waits_for_any_key_in_explain_mode(self):
        """Should consume exactly one event in explain mode."""
        # Arrange
        input_provider = Mock()
        render_stage = Mock()
        state_update_stage = Mock()
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        context = Mock(mode="explain")
        consumed_event = Mock()
        remaining_event = Mock()
        events = iter([consumed_event, remaining_event])

        # Act
        orchestrator._handle_explain_mode(context, events)

        # Assert
        # Should only consume one event
        # If we try to get the next event, it should be the remaining_event
        assert next(events) == remaining_event

    def test_handles_explain_mode_with_state_update(self):
        """Should handle explain mode when result includes new_state."""
        # Arrange
        input_provider = Mock()
        render_stage = Mock()
        state_update_stage = Mock()
        orchestrator = PipelineOrchestrator(input_provider, render_stage, state_update_stage)

        # Create question context
        question = QuestionContext(
            question="Test",
            options=["A", "B"],
            explanations={"A": "Explanation A", "B": "Explanation B"},
            question_explanation="Test question with explanations",
            allow_multiple=False,
            default_index=0,
            default_indices={0},
            none_index=None,
        )

        # Mock events
        events = [Mock(), Mock(), Mock()]
        input_provider.events = iter(events)

        mock_command = Mock()
        orchestrator.command_factory.create_command = Mock(return_value=mock_command)

        # Create new state for after explain mode
        new_state = SingleSelectionState(1, 2)

        # Results: transition to explain with new state, then complete
        results = [
            Mock(transition_to="explain", new_state=new_state, continue_pipeline=True),
            Mock(transition_to=None, new_state=None, continue_pipeline=False, output_value="B"),
        ]
        state_update_stage.apply = Mock(side_effect=results)

        # Act
        result = orchestrator.run(question)

        # Assert
        assert result == "B"
        # Verify state was updated after explain mode
        assert state_update_stage.apply.call_count == 2
