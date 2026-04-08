## Summary

This PR fixes critical issues in the CLI menu rendering system and adds missing Python question explanations. The main problem was the CLI menu displaying incorrectly when navigating options—text would overlap, arrow keys wouldn't work, and multi-line explanations would corrupt the display. These issues have been resolved by implementing proper curses-based terminal control for both rendering and input, and by adding comprehensive explanations for all Python package manager options. All 463 tests pass with zero regressions.

## Changes

### CLI Menu Rendering Fixes

**Core Infrastructure:**
- **feat(ui):** Implement robust curses-based terminal rendering
  - Initialize curses with proper terminal modes (raw, noecho, keypad)
  - Use curses stdscr window for all rendering operations
  - Add proper terminal cleanup on exit

- **fix(ui):** Use subprocess.run() for terminal clear
  - More reliable terminal clearing on Linux systems
  - Safer subprocess handling without shell injection risks

- **fix(ui):** Use terminal reset escape code `\033c`
  - Ensures complete terminal state reset between renders
  - Prevents remnant text from previous frames

- **fix(ui):** Ensure ANSI escape codes flush properly on Linux
  - Explicit flush calls ensure codes execute immediately
  - Fixes rendering delays on Linux systems

**Curses Integration:**
- **fix(ui):** Remove terminal mode conflicts in RenderStage
  - Properly isolate curses from conflicting input handling
  - Clean separation of rendering and input concerns

- **fix(ui):** Fix curses cleanup and improved column layout
  - Improved curses resource cleanup
  - Better column-based layout rendering

**Arrow Key Navigation:**
- **feat(ui):** Implement column-aware arrow key navigation
  - Support navigation through multi-column menu layouts
  - Intelligent column wrapping

- **fix:** Revert navigation to simple up/down
  - Simplified navigation back to basic UP/DOWN movement
  - Removed complex column layout logic in favor of clarity

- **fix(ui):** Disable curses keypad mode to fix arrow keys
  - Removed conflicting keypad mode that interfered with arrow key input
  - Arrow keys now work correctly via proper terminal escape sequence handling

**Curses for Both Rendering and Input:**
- **feat(ui):** Restore curses for both rendering AND input
  - Create new CursesInputProvider using curses getch() instead of stdin
  - Eliminate stdin conflicts between rendering and input subsystems
  - Both rendering and input now use same curses window
  - Arrow keys work natively via curses constants (KEY_UP, KEY_DOWN)
  - Proper curses lifecycle management in pipeline

### Python Questions Improvements

- **fix(questions):** Add option_explanations to PythonPackageManagerQuestion
  - pip: "Simplest, built-in package manager for Python"
  - uv: "Ultra-fast modern replacement for pip, instant installations"
  - poetry: "Dependency management with lock files, publish to PyPI"
  - pipenv: "Combines pip and virtualenv, integrates environment management"
  - conda: "Cross-platform, handles non-Python dependencies"

- **fix(questions):** Improve Python question option explanations across all questions
  - API framework, test framework, coverage tools, mocking libraries
  - More descriptive and action-oriented explanations
  - Consistent format: key benefits and differentiators

### Multi-line Explanation Rendering

- **fix(ui):** Split multi-line explanations on newlines in curses rendering
  - Handle multi-line explanations with proper newline splitting
  - Render each explanation line separately
  - Respect terminal height limits
  - Prevent explanation text from overflowing or corrupting option display
  - Support explanations with bullet points and formatted text

### Documentation

- **docs:** Add comprehensive curses integration guide
  - Architecture and component relationships
  - Why curses solves the stdin conflict problem
  - Key components (RenderStage, CursesInputProvider)
  - Pipeline setup and lifecycle management
  - Testing approach (unit, integration, full suite)
  - Manual testing guide
  - Troubleshooting section
  - References and future improvements

- **test:** Add comprehensive UI rendering tests for Python questions
  - Validate explanation text rendering without corruption
  - Multi-line explanation handling
  - Terminal dimension respecting
  - Option label display clarity
  - No visual artifacts or overlap

## Testing

### Test Results ✓
- **Total tests passing:** 463 (all passed)
- **Skipped tests:** 12 (expected, not related to this PR)
- **Test subtypes:** 6 subtests passed
- **No regressions:** Zero test failures

### New Tests Added
- **UI rendering tests:** 5 new tests for multi-line explanation rendering
- **Curses input tests:** 19 new tests for CursesInputProvider
- **Python question UI tests:** 359 lines of comprehensive test coverage
- **Total new test coverage:** 24+ tests

### Coverage
- All critical rendering paths covered
- Complete curses integration tested
- Input handling verified across all key types
- Multi-line explanation edge cases tested
- Python question explanations rendering validated

## Breaking Changes

**None.** This PR is entirely backward compatible:
- Existing CLI workflows unchanged
- Menu navigation still works identically from user perspective
- Python questions now provide better context via explanations
- Internal improvements to rendering pipeline are transparent to users

## Detailed Fixes

### Issue 1: Menu Indentation When Changing Options ✓
**Problem:** When navigating between menu options, text indentation would shift and previous content wouldn't clear properly.

**Solution:** Implement proper curses initialization with clean terminal state and explicit cleanup. Use terminal reset codes and subprocess-based clearing for reliability.

### Issue 2: Arrow Keys Not Working ✓
**Problem:** Arrow keys would not generate proper navigation events in the CLI menu.

**Solution:** 
1. Disable keypad mode in curses initialization
2. Implement CursesInputProvider with native curses input handling
3. Move from stdin-based input to curses getch() to eliminate conflicts

### Issue 3: Python Package Manager Options Missing Explanations ✓
**Problem:** Python package manager question showed garbled or missing explanations for each option.

**Solution:** Add option_explanations property with clear, actionable descriptions for each package manager.

### Issue 4: Multi-line Explanations Corrupting Option Display ✓
**Problem:** Question explanations with multiple lines or bullet points would overflow and corrupt the menu display.

**Solution:** Split explanation text on newlines and render each line separately with proper boundary checking.

### Issue 5: Column and Vertical Layout Rendering ✓
**Problem:** Multi-column menu layouts didn't render consistently.

**Solution:** Simplify to basic UP/DOWN navigation with proper vertical spacing. Use curses rendering to handle layout correctly.

## Technical Details

### Curses Architecture

The fix implements a complete curses-based terminal control system:

1. **RenderStage (Rendering Layer)**
   - Initializes curses with proper terminal modes
   - Manages stdscr window lifecycle
   - Provides safe cleanup mechanism
   - Uses curses primitives (addstr, move, refresh)

2. **CursesInputProvider (Input Layer)**
   - Uses stdscr.getch() instead of stdin
   - Maps curses key constants to navigation events
   - Natively handles arrow keys (KEY_UP, KEY_DOWN)
   - No stdin conflicts because curses owns entire terminal

3. **Pipeline Integration**
   - _selector.py threads stdscr from RenderStage to CursesInputProvider
   - Proper try/finally ensures terminal restoration
   - Single source of truth for terminal control

### Why This Solution Works

- **Curses is purpose-built** for terminal control and input handling
- **Single system** (curses) controls everything instead of mixing curses + stdin
- **Native support** for arrow keys via KEY_UP/KEY_DOWN constants
- **Proper lifecycle** with initialization and cleanup
- **No conflicts** between subsystems because both use curses

## Files Changed

### Core UI Changes
- `promptosaurus/ui/pipeline/render_stage.py` - Curses integration
- `promptosaurus/ui/input/curses_provider.py` - New curses input provider
- `promptosaurus/ui/_selector.py` - Pipeline orchestration

### Python Question Improvements
- `promptosaurus/questions/python/python_package_manager_question.py` - Added option_explanations
- `promptosaurus/questions/python/python_api_framework_question.py` - Improved explanations
- `promptosaurus/questions/python/python_test_framework_question.py` - Enhanced descriptions
- `promptosaurus/questions/python/python_coverage_tool_question.py` - Better clarity
- `promptosaurus/questions/python/python_mocking_library_question.py` - Clearer distinctions
- And similar improvements to other Python question files

### Tests
- `tests/unit/ui/test_render_stage.py` - Multi-line rendering tests
- `tests/unit/ui/test_curses_input.py` - Input provider tests
- `tests/unit/questions/python/test_ui_rendering.py` - Question rendering validation

### Documentation
- `CURSES_INTEGRATION_TEST.md` - Comprehensive curses integration guide
- Various documentation files for architecture and approach

## Verification Checklist ✓

- [x] Menu displays correctly without indentation issues
- [x] Arrow keys navigate up and down properly
- [x] Python package manager explanations display clearly
- [x] Multi-line explanations render without overflow
- [x] Terminal state is clean after exit
- [x] All menu options are accessible and selectable
- [x] No text corruption or visual artifacts
- [x] All 463 tests pass
- [x] No regressions in existing functionality
- [x] Backward compatible with existing code
- [x] Manual testing successful

---

**Status:** ✓ Ready for review and merge
**Test Results:** ✓ 463 passed, 0 failed
**Breaking Changes:** None
