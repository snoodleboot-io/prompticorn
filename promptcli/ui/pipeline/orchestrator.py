"""Pipeline orchestrator for UI interactions."""

from promptcli.ui.domain.context import PipelineContext, QuestionContext
from promptcli.ui.pipeline.stages import CommandFactory
from promptcli.ui.state.multi import MultiSelectState
from promptcli.ui.state.single import SelectionState, SingleSelectState


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
        if question.allow_multiple:
            initial_state: SelectionState = MultiSelectState(
                {question.default_index}, len(question.options)
            )
        else:
            initial_state = SingleSelectState(question.default_index, len(question.options))

        context = PipelineContext(
            question=question,
            state=initial_state,
            mode="select",
        )

        # Create event generator
        events = self.input_provider.get_events()

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
