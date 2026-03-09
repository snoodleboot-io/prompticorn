"""Pipeline orchestrator for UI interactions."""

from promptosaurus.ui.domain.context import PipelineContext, QuestionContext
from promptosaurus.ui.pipeline.command_factory import CommandFactory
from promptosaurus.ui.state.multi_selection_state import MultiSelectionState
from promptosaurus.ui.state.mutual_exclusion_multi_selection_state import (
    MutualExclusionMultiSelectionState,
)
from promptosaurus.ui.state.selection_state import SelectionState
from promptosaurus.ui.state.single_selection_state import SingleSelectionState


class PipelineOrchestrator:
    """Orchestrates the complete UI pipeline."""

    def __init__(self, input_provider, render_stage, state_update_stage):
        """Initialize with pipeline components."""
        self.input_provider = input_provider
        self.render_stage = render_stage
        self.state_update_stage = state_update_stage
        self.command_factory = CommandFactory()

    def run(self, question: QuestionContext) -> str | list[str]:
        """Run the complete pipeline for a question."""
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
        """Handle explain mode - wait for any key."""
        self.render_stage.render(context)
        next(events)  # Wait for any key
