# Curses Integration Test Guide

## Overview

The UI system now uses curses for **both rendering and input**, eliminating the stdin conflicts that occurred when mixing curses rendering with manual stdin reading.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   select_option_with_explain                │
│                    (_selector.py entry point)                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ├─ Initialize RenderStage with renderer
                   │
                   ├─ Call render_stage._init_curses()
                   │  └─ curses.initscr() - creates stdscr
                   │  └─ curses.raw() - raw input mode
                   │  └─ stdscr.keypad(True) - enable arrow keys
                   │
                   ├─ Create CursesInputProvider(stdscr)
                   │  └─ Uses stdscr.getch() for input
                   │
                   ├─ Create PipelineOrchestrator
                   │
                   └─ Run orchestrator with try/finally
                      └─ Finally: render_stage.cleanup()
                         └─ curses.endwin() - restore terminal
```

## Key Components

### 1. RenderStage (prompt osaurus/ui/pipeline/render_stage.py)

- Initializes and manages curses window (stdscr)
- Uses stdscr.addstr() for all output
- Exposes stdscr via property
- Provides cleanup() method to restore terminal

**Key methods:**
- `_init_curses()` - Initialize curses on first call
- `render()` - Render current state using curses
- `cleanup()` - Restore terminal to normal state
- `stdscr` property - Access curses window

### 2. CursesInputProvider (promptosaurus/ui/input/curses_provider.py)

- NEW: Replaces UnixInputProvider for curses-enabled terminals
- Uses stdscr.getch() for keyboard input
- Natively handles arrow keys via curses constants
- No stdin reading - no conflicts with curses rendering

**Key methods:**
- `__init__(stdscr)` - Store reference to curses window
- `events` property - Generator yielding InputEvents
- `_parse_key(key)` - Parse curses key codes to events

### 3. Pipeline Setup (_selector.py)

```python
# 1. Create render stage
render_stage = RenderStage(renderer_selector=UIFactory.create_renderer)

# 2. Initialize curses early
render_stage._init_curses()

# 3. Create input provider with curses window
input_provider = CursesInputProvider(render_stage.stdscr)

# 4. Create orchestrator
pipeline = PipelineOrchestrator(
    input_provider=input_provider,
    render_stage=render_stage,
    state_update_stage=state_update,
)

# 5. Run with proper cleanup
try:
    return pipeline.run(context)
finally:
    render_stage.cleanup()  # Restore terminal
```

## Why This Works

### Problem: stdin Conflicts

**Old approach (broken):**
- RenderStage used ANSI escape codes
- UnixInputProvider read directly from stdin
- Both compete for stdin control
- Arrow key parsing fails intermittently

**Root cause:**
- Curses and manual stdin reading don't mix
- They interfere with terminal state

### Solution: Unified Curses Control

**New approach:**
- RenderStage initializes curses and owns stdscr
- CursesInputProvider uses stdscr.getch()
- ONE system (curses) controls entire terminal
- Arrow keys work correctly via curses constants

**Benefits:**
1. **No conflicts** - Single terminal controller
2. **Reliable arrow keys** - Curses handles them natively
3. **Proper cleanup** - RenderStage manages lifecycle
4. **Standard approach** - Curses is designed for this

## Testing

### Unit Tests

Run curses input provider tests:
```bash
pytest tests/unit/ui/test_curses_input.py -v
```

**Coverage:**
- Arrow key parsing (UP, DOWN)
- Number and letter key parsing
- Special key handling (Enter, Quit, Explain, Help)
- Unknown key handling
- Generator/events property

### Integration Tests

The full pipeline is tested via:
```bash
pytest tests/unit/ui/ -v
```

All 38 UI tests pass, including:
- Factory tests
- State management tests
- Renderer tests

### Full Test Suite

```bash
pytest tests/ --tb=short -q
```

**Results:** 448 passed, 12 skipped

## Manual Testing

To manually test the curses integration:

```python
from promptosaurus.ui._selector import select_option_with_explain

# Test basic selection
result = select_option_with_explain(
    question="Which option?",
    options=["Option A", "Option B", "Option C"],
    explanations={
        "Option A": "Explanation for A",
        "Option B": "Explanation for B",
        "Option C": "Explanation for C",
    },
    question_explanation="Choose one of these options",
)
print(f"Selected: {result}")
```

**Try these interactions:**
- Use arrow keys (UP, DOWN) to navigate
- Use numbers (0, 1, 2) to jump to option
- Use letters (a, b, c) to jump to option
- Press 'e' or '?' to show explanation
- Press 'Enter' to confirm
- Press 'q' to quit

### What Should Work

✓ Arrow key navigation (UP/DOWN)
✓ Number selection (0-9)
✓ Letter selection (a-d)
✓ Explanation mode (e, E, ?)
✓ Confirmation (Enter)
✓ Quit (q, Q, Ctrl+C)
✓ Terminal layout preserved
✓ Proper terminal cleanup on exit

## Implementation Details

### Curses Key Constants

CursesInputProvider uses:
- `curses.KEY_UP` = 259
- `curses.KEY_DOWN` = 258
- Standard ASCII codes for letters/numbers
- Special handling for Ctrl+C, Enter, etc.

### Terminal Modes

RenderStage configures:
```python
curses.noecho()         # Don't echo input to screen
curses.raw()            # Raw input mode (no buffering)
stdscr.keypad(True)     # Enable special keys (arrows, etc)
```

### Cleanup

Terminal restoration on exit:
```python
curses.echo()           # Re-enable echo
curses.nocbreak()       # Back to normal buffering
stdscr.keypad(False)    # Disable special key mode
curses.endwin()         # Clean up curses
```

## Troubleshooting

### Terminal Corrupted After Exit

If terminal appears corrupted, run:
```bash
reset
```

This shouldn't happen with proper try/finally cleanup, but if it does:
```bash
stty sane
echo -e "\033c"  # Full terminal reset
```

### Arrow Keys Not Working

Check that:
1. RenderStage is initialized before input provider
2. `stdscr.keypad(True)` was called in `_init_curses()`
3. CursesInputProvider received correct stdscr reference

### Input Not Appearing

Check that:
1. `curses.noecho()` is called
2. You're not looking at stdout (curses manages the screen)
3. Terminal is in raw mode

## Future Improvements

1. **Windows Support** - Add `WindowsCursesInputProvider` if needed
2. **Color Support** - Add curses color pairs for syntax highlighting
3. **Mouse Support** - Add curses mouse event handling
4. **Alternative Inputs** - Add support for other input methods (e.g., wheel scroll)

## References

- Python curses documentation: https://docs.python.org/3/library/curses.html
- Curses programming guide: https://tldp.org/HOWTO/NCURSES-Programming-HOWTO/
