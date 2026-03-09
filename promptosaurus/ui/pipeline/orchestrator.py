"""Pipeline orchestrator for UI interactions.

This module provides the PipelineOrchestrator class which coordinates
the entire UI interaction flow. It ties together input handling,
state management, and rendering into a cohesive user experience.

Classes:
    PipelineOrchestrator: Orchestrates the complete UI pipeline.

Example:
    >>> from promptosaurus.ui.pipeline.orchestrator import PipelineOrchestrator
    >>> from promptosaurus.ui.domain.context import QuestionContext
    >>> from promptosaurus.ui.input.fallback import FallbackInputProvider
    >>> from promptosaurus.ui.pipeline.render_stage import RenderStage
    >>> from promptosaurus.ui.pipeline.state_update_stage import StateUpdateStage
    >>> from promptosaurus.ui.ui_factory import UIFactory
    >>>
    >>> # Create components
    >>> input_provider = FallbackInputProvider()
    >>> render_stage = RenderStage(renderer_selector=UIFactory.create_renderer)
    >>> state_update = StateUpdateStage()
    >>>
    >>> # Create orchestrator
    >>> orchestrator = PipelineOrchestrator(
    ...     input_provider=input_provider,
    ...     render_stage=render_stage,
    ...     state_update_stage=state_update
    ... )
"""

from promptosaurus.ui.domain.context import PipelineContext, QuestionContext
from promptosaurus.ui.pipeline.command_factory import CommandFactory
from promptosaurus.ui.state.multi_selection_state import MultiSelectionState
from promptosaurus.ui.state.mutual_exclusion_multi_selection_state import (
    MutualExclusionMultiSelectionState,
)
from promptosaurus.ui.state.selection_state import SelectionState
from promptosaurus.ui.state.single_selection_state import SingleSelectionState


class PipelineOrchestrator:
    """Orchestrates the complete UI pipeline.

    This class coordinates the entire interactive selection flow by:
    1. Initializing the appropriate selection state based on question type
    2. Running the event loop that processes user input
    3. Managing state transitions (select mode <-> explain mode)
    4. Returning the final selection result

    The orchestrator follows a pipeline architecture where:
    - InputProvider yields keyboard events
    - CommandFactory converts events to commands
    - StateUpdateStage applies commands to state
    - RenderStage displays current state to user

    Attributes:
        input_provider: Source of keyboard input events.
        render_stage: Handles rendering the UI.
        state_update_stage: Applies commands to state.
        command_factory: Creates commands from events.

    Example:
        >>> orchestrator = PipelineOrchestrator(
        ...     input_provider=my_input_provider,
        ...     render_stage=my_render_stage,
        ...     state_update_stage=my_state_update
        ... )
        >>> result = orchestrator.run(question_context)
    """

    def __init__(self, input_provider, render_stage, state_update_stage):
        """Initialize with pipeline components.

        Args:
            input_provider: InputProvider instance for keyboard events.
            render_stage: RenderStage instance for UI display.
            state_update_stage: StateUpdateStage instance for state management.
        """
        self.input_provider = input_provider
        self.render_stage = render_stage
        self.state_update_stage = state_update_stage
        self.command_factory = CommandFactory()

    def run(self, question: QuestionContext) -> str | list[str]:
        """Run the complete pipeline for a question.

        This is the main entry point that executes the entire interactive
        selection flow. It:
        1. Creates the appropriate initial state (single/multi/mutual-exclusion)
        2. Creates the pipeline context
        3. Enters the event loop
        4. Returns the final selection(s)

        Args:
            question: The QuestionContext containing the question details.

        Returns:
            If allow_multiple is False: The selected option string.
            If allow_multiple is True: List of selected option strings.

        Raises:
            UserCancelledError: If the user quits the interaction.

        Example:
            >>> from promptosaurus.ui.domain.context import QuestionContext
            >>> qc = QuestionContext(
            ...     question="Choose:",
            ...     options=["A", "B", "C"],
            ...     explanations={"A": "First", "B": "Second", "C": "Third"},
            ...     question_explanation="Pick one"
            ... )
            >>> result = orchestrator.run(qc)
            >>> print(result)
            A
        """
        # Initialize state based on question type
        initial_state: SelectionState
        if question.allow_multiple:
            # Use default_indices for multi-select, fall back to default_index
            default_selections = question.default_indices or {question.default_index}

            # Choose the appropriate multi-selection state class
            if question.none_index is not None:
                # Use mutual exclusion multi-select when none_index is specified
                initial_state = MutualExclusionMultiSelectionState(
                    default_selections, len(question.options), question.none_index
                )
            else:
                # Use standard multi-select
                initial_state = MultiSelectionState(default_selections, len(question.options))
        else:
            initial_state = SingleSelectionState(question.default_index, len(question.options))

        context = PipelineContext(
            question=question,
            state=initial_state,
            mode="select",
        )

        # Get event generator
        events = self.input_provider.events

        while True:
            # Render current state
            self.render_stage.render(context)

            # Get next event and convert to command
            event = next(events)
            command = self.command_factory.create_command(event)

            # Execute command
            result = self.state_update_stage.apply(command, context)

            # Handle transitions
            if result.transition_to:
                context.mode = result.transition_to
                if result.transition_to == "explain":
                    self._handle_explain_mode(context, events)
                    context.mode = "select"
                    if result.new_state:
                        context.state = result.new_state
                continue

            # Update state
            if result.new_state:
                context.state = result.new_state

            # Check for completion
            if not result.continue_pipeline:
                return result.output_value  # type: ignore[no-any-return]

    def _handle_explain_mode(self, context: PipelineContext, events) -> None:
        """Handle explain mode - wait for any key.

        This method is called when entering explain mode. It renders
        the explanation and waits for any key press before returning
        to select mode.

        Args:
            context: The current PipelineContext.
            events: The event generator.
        """
        self.render_stage.render(context)
        next(events)  # Wait for any key
