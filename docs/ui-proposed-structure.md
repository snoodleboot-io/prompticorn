# Proposed UI Module Structure

## Directory Layout

```
promptcli/
├── __init__.py               # sweet_tea auto-registration imports
├── cli.py                    # Entry points - unchanged
├── config.py                 # Configuration handling - unchanged
├── registry.py               # Prompt registry - unchanged
├── ui/                       # NEW: UI package (replaces ui.py)
│   ├── _selector.py          # Main select_option_with_explain implementation
│   ├── _factory.py           # UIFactory for component creation
│   │
│   ├── domain/               # Domain models (Pydantic BaseModel)
│   │   ├── events.py         # InputEvent, InputEventType
│   │   └── context.py        # QuestionContext, PipelineContext
│   │
│   ├── state/                # State management (Strategy Pattern)
│   │   ├── single.py         # SingleSelectState
│   │   └── multi.py          # MultiSelectState
│   │
│   ├── input/                # Input handling (Strategy Pattern)
│   │   ├── windows.py        # WindowsInputProvider
│   │   ├── unix.py           # UnixInputProvider
│   │   └── fallback.py       # FallbackInputProvider
│   │
│   ├── commands/             # Commands (Command Pattern)
│   │   ├── select.py         # SelectCommand
│   │   ├── navigate.py       # NavigateCommand
│   │   ├── confirm.py        # ConfirmCommand
│   │   ├── quit.py           # QuitCommand
│   │   ├── explain.py        # EnterExplainCommand
│   │   ├── noop.py           # NoOpCommand
│   │   └── result.py         # CommandResult
│   │
│   ├── render/               # Rendering (Strategy Pattern)
│   │   ├── columns.py        # ColumnLayoutRenderer
│   │   ├── vertical.py       # VerticalLayoutRenderer
│   │   └── explain.py        # ExplainRenderer
│   │
│   └── pipeline/             # Pipeline orchestration
│       ├── orchestrator.py   # PipelineOrchestrator
│       └── stages.py         # RenderStage, StateUpdateStage
│
└── questions/                # Existing - unchanged structure
    ├── __init__.py
    ├── language.py
    ├── question_pipelines.yaml
    ├── base/
    │   └── question.py       # Question ABC - already SOLID
    ├── handlers/
    │   └── handle_single_language_questions.py
    └── python/
        └── ...
```

## Key Files Explained

### `promptcli/__init__.py` - sweet_tea Auto-Registration

```python
"""PromptCLI package - sweet_tea auto-registers all imported classes."""

# Domain models
from promptcli.ui.domain.events import InputEvent, InputEventType
from promptcli.ui.domain.context import QuestionContext, PipelineContext

# State implementations
from promptcli.ui.state.single import SingleSelectState
from promptcli.ui.state.multi import MultiSelectState

# Input providers
from promptcli.ui.input.windows import WindowsInputProvider
from promptcli.ui.input.unix import UnixInputProvider
from promptcli.ui.input.fallback import FallbackInputProvider

# Renderers
from promptcli.ui.render.columns import ColumnLayoutRenderer
from promptcli.ui.render.vertical import VerticalLayoutRenderer
from promptcli.ui.render.explain import ExplainRenderer

# Commands
from promptcli.ui.commands.select import SelectCommand
from promptcli.ui.commands.navigate import NavigateCommand
from promptcli.ui.commands.confirm import ConfirmCommand
from promptcli.ui.commands.quit import QuitCommand
from promptcli.ui.commands.explain import EnterExplainCommand
from promptcli.ui.commands.noop import NoOpCommand

# Pipeline
from promptcli.ui.pipeline.orchestrator import PipelineOrchestrator

# sweet_tea automatically registers all imported classes - no manual registration needed
```

### `promptcli/ui/_selector.py` - Main Entry Point

```python
"""Public UI API - main entry point for interactive selection."""

from promptcli.ui.domain.context import QuestionContext
from promptcli.ui.pipeline.orchestrator import PipelineOrchestrator
from promptcli.ui._factory import UIFactory
from promptcli.ui.pipeline.stages import RenderStage, StateUpdateStage


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
```

### `promptcli/ui/_factory.py` - Component Factory

```python
"""Factory for creating UI components via sweet_tea."""

import os
from sweet_tea.abstract_factory import AbstractFactory

from promptcli.ui.input.windows import WindowsInputProvider
from promptcli.ui.input.unix import UnixInputProvider
from promptcli.ui.input.fallback import FallbackInputProvider
from promptcli.ui.render.columns import ColumnLayoutRenderer
from promptcli.ui.render.vertical import VerticalLayoutRenderer
from promptcli.ui.render.explain import ExplainRenderer
from promptcli.ui.domain.context import PipelineContext


class UIFactory:
    """Factory for creating UI components via sweet_tea."""

    @staticmethod
    def create_input_provider() -> InputProvider:
        """Create appropriate input provider for current platform."""
        factory = AbstractFactory[InputProvider]

        try:
            if os.name == "nt":
                return factory.create("windows_input")
            else:
                return factory.create("unix_input")
        except Exception:
            return factory.create("fallback_input")

    @staticmethod
    def create_renderer(context: PipelineContext) -> Renderer:
        """Create appropriate renderer based on context."""
        factory = AbstractFactory[Renderer]

        if context.mode == "explain":
            return factory.create("explain_renderer")

        # Choose layout based on option count
        if len(context.display_options) > 8:
            return factory.create("column_layout")
        return factory.create("vertical_layout")
```

## Base Classes (No ABC)

### `promptcli/ui/state/single.py`

```python
"""Single selection state implementation."""


class SingleSelectState:
    """Single selection state - immutable."""

    def __init__(self, selected: int, max_index: int):
        self._selected = selected
        self._max = max_index

    @property
    def current_selection(self) -> int:
        """Get current selection."""
        return self._selected

    def select(self, index: int) -> "SingleSelectState":
        """Return new state after selection."""
        if 0 <= index <= self._max:
            return SingleSelectState(index, self._max)
        return self

    def navigate(self, direction: int) -> "SingleSelectState":
        """Return new state after navigation."""
        new_index = max(0, min(self._max, self._selected + direction))
        return SingleSelectState(new_index, self._max)

    def is_selected(self, index: int) -> bool:
        """Check if index is selected."""
        return index == self._selected
```

### `promptcli/ui/input/windows.py`

```python
"""Windows-specific input provider."""

from typing import Iterator
from promptcli.ui.domain.events import InputEvent, InputEventType


class WindowsInputProvider:
    """Windows-specific input using msvcrt."""

    def get_events(self) -> Iterator[InputEvent]:
        """Yield input events."""
        import msvcrt

        while True:
            key = msvcrt.getch()
            yield self._parse_key(key, msvcrt)

    def _parse_key(self, key: bytes, msvcrt) -> InputEvent:
        """Parse Windows key codes into events."""
        if key == b"\r":
            return InputEvent(event_type=InputEventType.ENTER)
        elif key == b"q":
            return InputEvent(event_type=InputEventType.QUIT)
        elif key == b"\xe0":
            arrow = msvcrt.getch()
            if arrow == b"H":
                return InputEvent(event_type=InputEventType.UP)
            elif arrow == b"P":
                return InputEvent(event_type=InputEventType.DOWN)
        elif key.isdigit():
            return InputEvent(event_type=InputEventType.NUMBER, value=int(key.decode()))
        return InputEvent(event_type=InputEventType.UNKNOWN, raw_key=key)

    def supports_raw(self) -> bool:
        """Whether raw input is supported."""
        return True
```

## Migration Strategy

### Step 1: Create Parallel Structure
```bash
# Create new package alongside existing ui.py
mkdir -p promptcli/ui/{domain,state,input,commands,render,pipeline}
# Create all files...
```

### Step 2: Update `promptcli/__init__.py`
Add imports for sweet_tea auto-registration:
```python
# Add these to existing imports
from promptcli.ui.domain.events import InputEvent, InputEventType
from promptcli.ui.domain.context import QuestionContext, PipelineContext
from promptcli.ui.state.single import SingleSelectState
from promptcli.ui.state.multi import MultiSelectState
from promptcli.ui.input.windows import WindowsInputProvider
from promptcli.ui.input.unix import UnixInputProvider
from promptcli.ui.input.fallback import FallbackInputProvider
from promptcli.ui.render.columns import ColumnLayoutRenderer
from promptcli.ui.render.vertical import VerticalLayoutRenderer
from promptcli.ui.render.explain import ExplainRenderer
from promptcli.ui.pipeline.orchestrator import PipelineOrchestrator
```

### Step 3: Feature Flag Migration
```python
# In cli.py, use feature flag
import os

if os.environ.get("USE_NEW_UI"):
    from promptcli.ui._selector import select_option_with_explain
else:
    from promptcli.ui_legacy import select_option_with_explain
```

### Step 4: Replace Old UI
```bash
# Once tested, rename files
mv promptcli/ui.py promptcli/ui_old.py  # Backup
# Update imports to use new ui/ package
```

### Step 5: Clean Up
```bash
# Remove backup after confidence
rm promptcli/ui_old.py
```

## Testing Strategy (unittest)

```python
# tests/unit/ui/test_state.py
import unittest
from promptcli.ui.state.single import SingleSelectState
from promptcli.ui.state.multi import MultiSelectState


class TestSingleSelectState(unittest.TestCase):
    """Single selection state machine tests."""

    def test_initial_selection(self):
        state = SingleSelectState(0, 5)
        self.assertEqual(state.current_selection, 0)

    def test_select_valid_index(self):
        state = SingleSelectState(0, 5)
        new_state = state.select(3)
        self.assertEqual(new_state.current_selection, 3)
        self.assertEqual(state.current_selection, 0)

    def test_select_out_of_bounds(self):
        state = SingleSelectState(2, 5)
        new_state = state.select(10)
        self.assertEqual(new_state.current_selection, 2)

    def test_navigate_up(self):
        state = SingleSelectState(2, 5)
        new_state = state.navigate(-1)
        self.assertEqual(new_state.current_selection, 1)

    def test_navigate_up_at_boundary(self):
        state = SingleSelectState(0, 5)
        new_state = state.navigate(-1)
        self.assertEqual(new_state.current_selection, 0)

    def test_navigate_down(self):
        state = SingleSelectState(2, 5)
        new_state = state.navigate(1)
        self.assertEqual(new_state.current_selection, 3)

    def test_navigate_down_at_boundary(self):
        state = SingleSelectState(4, 5)
        new_state = state.navigate(1)
        self.assertEqual(new_state.current_selection, 4)


class TestMultiSelectState(unittest.TestCase):
    """Multi-selection state machine tests."""

    def test_initial_selection(self):
        state = MultiSelectState({0, 2}, 5)
        self.assertEqual(state.current_selection, {0, 2})

    def test_toggle_add(self):
        state = MultiSelectState({0}, 5)
        new_state = state.select(2)
        self.assertTrue(new_state.is_selected(0))
        self.assertTrue(new_state.is_selected(2))

    def test_toggle_remove(self):
        state = MultiSelectState({0, 2}, 5)
        new_state = state.select(2)
        self.assertTrue(new_state.is_selected(0))
        self.assertFalse(new_state.is_selected(2))


if __name__ == "__main__":
    unittest.main()
```

## Benefits of This Structure

| Aspect | Old ui.py | New Structure |
|--------|-----------|---------------|
| **Lines per file** | 350+ | ~50-100 each |
| **Testability** | Difficult (mixed concerns) | Easy (isolated components) |
| **Platform branches** | 2 large if/else blocks | Separate classes |
| **Adding new input** | Modify existing code | New class + auto-registration |
| **Adding new layout** | Modify existing code | New class + auto-registration |
| **Understanding** | Read entire file | Read relevant module only |
| **Parallel work** | Conflicts likely | Clean module boundaries |
| **Base classes** | ABC with abstractmethod | Regular classes with NotImplementedError |
| **Data models** | dataclass | Pydantic BaseModel |
| **__init__.py** | Re-exports | sweet_tea auto-registration imports only |
| **Registry** | Manual registration | sweet_tea auto-registration from root __init__.py |
| **Tests** | pytest | unittest |

## Design Pattern Summary

| Pattern | Used In | Purpose |
|---------|---------|---------|
| **Pipeline** | `pipeline/` | Orchestrate user interaction flow |
| **Strategy** | `input/`, `render/`, `state/` | Swappable implementations |
| **Command** | `commands/` | Encapsulate user actions |
| **State Machine** | `state/` | Manage selection state immutably |
| **Factory** | `_factory.py` | Create components via sweet_tea |
| **Abstract Factory** | sweet_tea | Type-safe component creation |
