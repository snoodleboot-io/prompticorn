"""Public UI API - main entry point for interactive selection."""

from promptcli.ui._factory import UIFactory
from promptcli.ui.domain.context import QuestionContext
from promptcli.ui.pipeline.orchestrator import PipelineOrchestrator
from promptcli.ui.pipeline.render_stage import RenderStage
from promptcli.ui.pipeline.state_update_stage import StateUpdateStage


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

    Backwards-compatible with existing code - same signature as before.
    Internally uses the new pipeline architecture.
    """
    context = QuestionContext(
        question=question,
        options=options,
        explanations=explanations,
        question_explanation=question_explanation,
        default_index=default_index,
        allow_multiple=allow_multiple,
    )

    input_provider = UIFactory.create_input_provider()
    render_stage = RenderStage(renderer_selector=UIFactory.create_renderer)
    state_update = StateUpdateStage()

    pipeline = PipelineOrchestrator(
        input_provider=input_provider,
        render_stage=render_stage,
        state_update_stage=state_update,
    )

    return pipeline.run(context)


def confirm_interactive(prompt: str, default: bool = True) -> bool:
    """Yes/no confirmation."""
    result = select_option_with_explain(
        question=prompt,
        options=["Yes", "No"],
        explanations={"Yes": "Confirm", "No": "Cancel"},
        question_explanation=prompt,
        default_index=0 if default else 1,
    )
    return result == "Yes"


def prompt_with_default(prompt: str, default: str) -> str:
    """Prompt with default value."""
    suffix = f" [{default}]" if default else ""
    response = input(f"{prompt}{suffix}: ").strip()
    return response if response else default
