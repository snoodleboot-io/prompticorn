# Test Conventions & Coverage Requirements

**Version:** 1.0  
**Date:** April 11, 2026  
**Status:** Active Standard  
**Applies To:** All Python code in promptosaurus/

---

## 1. Test Organization Conventions

### Current State vs. Requirements

**What EXISTS (✅):**
```
tests/
├── unit/                    # Unit tests (fast, isolated)
│   ├── agents/             # Agent tests by domain
│   ├── builders/           # Builder implementation tests
│   ├── ir/                 # IR model/loader/parser tests
│   ├── questions/          # Question handler tests
│   ├── registry/           # Registry lookup tests
│   ├── skills/             # Skill content tests
│   ├── subagents/          # Subagent content tests
│   ├── ui/                 # UI component tests
│   ├── validation/         # Schema/content validation tests
│   └── workflows/          # Workflow content tests
├── integration/            # Integration tests (multi-component)
├── slow/                   # Slow/expensive tests
└── security/               # Security-focused tests
```

**What SHOULD Exist (Convention):**

```
tests/
├── unit/
│   ├── [package]/
│   │   ├── test_[module].py        ← Test file for each module
│   │   └── [subpackage]/
│   │       └── test_[module].py
│   └── __init__.py                 ← Package marker
├── integration/
│   ├── test_[feature]_integration.py
│   └── conftest.py                 ← Shared fixtures
├── slow/
│   └── test_[feature]_slow.py
├── security/
│   └── test_[feature]_security.py
├── conftest.py                     ← Root fixtures
└── __init__.py                     ← Package marker
```

### Convention Rules

#### Rule 1: Mirror Source Structure
**Every module in promptosaurus/ should have corresponding test in tests/unit/**

**Current violations:**
```
❌ promptosaurus/ui/_selector.py           → No tests/unit/ui/test_selector.py
❌ promptosaurus/ui/input/unix.py          → No tests/unit/ui/input/test_unix.py
❌ promptosaurus/ui/input/windows.py       → No tests/unit/ui/input/test_windows.py
❌ promptosaurus/ui/pipeline/orchestrator.py → No tests/unit/ui/pipeline/test_orchestrator.py
❌ promptosaurus/registry.py               → tests/unit/registry/ exists but incomplete
```

#### Rule 2: Test File Naming
- **Test file:** `test_[module].py` (module is filename without .py)
- **Test class:** `Test[ClassName]` (for testing a specific class)
- **Test method:** `test_[method]_[scenario]`

**Examples:**
```python
# File: tests/unit/ui/test_selector.py
class TestSelectOptionWithExplain:
    def test_returns_selected_option_on_valid_input(self):
        pass
    
    def test_raises_on_user_cancel(self):
        pass

class TestConfirmInteractive:
    def test_returns_true_on_yes(self):
        pass
```

#### Rule 3: Test Class Organization
**One test class per tested class/function**

```
promptosaurus/ui/_selector.py contains:
  - select_option_with_explain()
  - confirm_interactive()
  - prompt_with_default()

tests/unit/ui/test_selector.py contains:
  - class TestSelectOptionWithExplain
  - class TestConfirmInteractive
  - class TestPromptWithDefault
```

#### Rule 4: Fixture Organization
**Shared fixtures in conftest.py, module-specific in test file**

```python
# tests/conftest.py (root level)
@pytest.fixture
def temp_dir():
    """Shared fixture for all tests."""
    pass

# tests/unit/ui/conftest.py (UI module level)
@pytest.fixture
def mock_curses():
    """UI-specific fixture."""
    pass

# tests/unit/ui/test_selector.py (test file level)
class TestSelectOptionWithExplain:
    @pytest.fixture
    def context(self):
        """Fixture used only in this test class."""
        pass
```

#### Rule 5: Test Type Markers
**Use pytest marks to categorize tests**

```python
@pytest.mark.unit              # Fast, isolated unit tests
@pytest.mark.integration       # Multi-component tests
@pytest.mark.slow              # Expensive operations (>1s)
@pytest.mark.security          # Security-focused tests
@pytest.mark.parametrize       # Data-driven tests
@pytest.mark.skip("reason")    # Disabled tests with reason
```

---

## 2. Coverage Requirements

### Standard: 90% per class/function

**Metric Definition:**
- **90% coverage** = 90 lines of code executed per 100 lines written
- **Per class** = Each class must achieve 90%
- **Per module** = Each module should aim for 90%+
- **Overall project** = Target 85%+ (allows edge cases to be untested)

**Current State:**
```
❌ Overall: 64.3% (below target of 85%)
❌ UI Module: 20-53% (critical gaps)
❌ Registry: 53% (critical gaps)
```

### Coverage Calculation

```
Total Lines in Class = 45
Lines Executed = 40
Coverage % = (40 / 45) * 100 = 88.9%
Status = FAIL (need 90%)
```

### Coverage Targets by Module

| Module | Current | Target | Gap | Priority |
|--------|---------|--------|-----|----------|
| agents/ | 98% | 90% | ✅ PASS | - |
| builders/ | 97% | 90% | ✅ PASS | - |
| ir/ | 96% | 90% | ✅ PASS | - |
| registry/ | 53% | 90% | ❌ -37% | HIGH |
| ui/selector | 32% | 90% | ❌ -58% | HIGH |
| ui/input/unix | 20% | 90% | ❌ -70% | HIGH |
| ui/input/windows | 25% | 90% | ❌ -65% | HIGH |
| ui/pipeline | 24% | 90% | ❌ -66% | HIGH |
| **Overall** | **64%** | **85%** | ❌ -21% | HIGH |

---

## 3. Missing Test Files (Priority Order)

### CRITICAL (>50% gap)

#### 1. tests/unit/ui/test_selector.py
**File:** promptosaurus/ui/_selector.py (138 lines, 32% coverage)  
**Classes to test:**
- `select_option_with_explain()` - 60 lines, 0% covered
- `confirm_interactive()` - 20 lines, 50% covered
- `prompt_with_default()` - 15 lines, 80% covered

**Tests needed:** 8-10 test methods
**Effort:** 1 day
**Coverage target:** 90%+

```python
# tests/unit/ui/test_selector.py
class TestSelectOptionWithExplain:
    def test_returns_selected_option_on_single_select(self): ...
    def test_returns_list_on_multi_select(self): ...
    def test_raises_on_user_cancel(self): ...
    def test_handles_explain_option(self): ...
    def test_handles_default_option(self): ...

class TestConfirmInteractive:
    def test_returns_true_on_yes(self): ...
    def test_returns_false_on_no(self): ...
    def test_uses_default_on_enter(self): ...

class TestPromptWithDefault:
    def test_returns_user_input_when_non_empty(self): ...
    def test_returns_default_when_empty(self): ...
```

#### 2. tests/unit/ui/input/test_unix.py
**File:** promptosaurus/ui/input/unix.py (66 lines, 20% coverage)  
**Classes to test:**
- `UnixInputProvider.events` - 15 lines, 0% covered
- `UnixInputProvider._parse_key()` - 31 lines, 10% covered

**Tests needed:** 12-15 test methods  
**Effort:** 2 days (requires termios mocking)
**Coverage target:** 90%+

```python
# tests/unit/ui/input/test_unix.py
class TestUnixInputProvider:
    @pytest.fixture
    def provider(self, mock_termios):
        return UnixInputProvider()
    
    def test_yields_enter_event_on_return(self): ...
    def test_yields_quit_event_on_q(self): ...
    def test_yields_up_event_on_escape_a(self): ...
    def test_yields_down_event_on_escape_b(self): ...
    
    @pytest.mark.parametrize("key,expected", [
        ("1", InputEventType.NUMBER),
        ("a", InputEventType.NUMBER),
        ("e", InputEventType.EXPLAIN),
    ])
    def test_parse_key_variants(self, key, expected): ...
```

#### 3. tests/unit/ui/input/test_windows.py
**File:** promptosaurus/ui/input/windows.py (62 lines, 25% coverage)  
**Classes to test:**
- `WindowsInputProvider.events`
- `WindowsInputProvider._parse_key()`

**Tests needed:** 12-15 test methods  
**Effort:** 2 days (requires msvcrt mocking)
**Coverage target:** 90%+

#### 4. tests/unit/ui/pipeline/test_orchestrator.py
**File:** promptosaurus/ui/pipeline/orchestrator.py (41 lines, 24% coverage)  
**Classes to test:**
- `PipelineOrchestrator.run()` - Complex state machine

**Tests needed:** 6-8 test methods  
**Effort:** 1 day
**Coverage target:** 90%+

```python
# tests/unit/ui/pipeline/test_orchestrator.py
class TestPipelineOrchestrator:
    def test_runs_render_state_update_cycle(self): ...
    def test_handles_user_quit_event(self): ...
    def test_propagates_selection_through_pipeline(self): ...
    def test_cleanup_called_on_exit(self): ...
```

#### 5. tests/unit/test_registry.py (EXPAND)
**File:** promptosaurus/registry.py (117 lines, 53% coverage)  
**Missing coverage:**
- Error cases (agent not found, workflow not found)
- Edge cases (empty registries, invalid lookups)

**Tests needed:** 8-10 additional test methods  
**Effort:** 1 day
**Coverage target:** 90%+

```python
# Expand tests/unit/registry/test_registry.py
class TestAgentRegistry:
    def test_raises_on_missing_agent(self): ...
    def test_returns_all_agents(self): ...
    def test_handles_agent_with_no_subagents(self): ...

class TestWorkflowRegistry:
    def test_raises_on_missing_workflow(self): ...
    def test_filters_by_variant(self): ...
```

### HIGH (30-50% gap)

#### 6. tests/unit/ui/test_commands.py (NEW)
**Files:** promptosaurus/ui/commands/*.py  
**Commands needing tests:**
- `confirm.py` - 35% coverage
- `result.py` - 43% coverage
- `select.py` - 60% coverage

**Tests needed:** 8-12  
**Effort:** 1 day

#### 7. tests/unit/ui/test_input_fallback.py (NEW)
**File:** promptosaurus/ui/input/fallback.py (29% coverage)  
**Tests needed:** 6-8  
**Effort:** 0.5 days

---

## 4. Creating Missing Tests

### Step-by-Step Process

#### 1. Create test file with proper naming
```bash
# Create missing test file
touch tests/unit/ui/test_selector.py
```

#### 2. Import what you're testing
```python
# tests/unit/ui/test_selector.py
import pytest
from promptosaurus.ui._selector import (
    select_option_with_explain,
    confirm_interactive,
    prompt_with_default,
)
```

#### 3. Create test classes (one per function/class)
```python
class TestSelectOptionWithExplain:
    """Tests for select_option_with_explain function."""
    pass

class TestConfirmInteractive:
    """Tests for confirm_interactive function."""
    pass
```

#### 4. Add fixtures for shared setup
```python
@pytest.fixture
def mock_pipeline(mocker):
    """Mock PipelineOrchestrator."""
    return mocker.patch("promptosaurus.ui._selector.PipelineOrchestrator")

class TestSelectOptionWithExplain:
    def test_creates_context_correctly(self, mock_pipeline):
        # Test implementation
        pass
```

#### 5. Write test methods covering happy path + edge cases
```python
def test_returns_selected_option_on_single_select(self):
    """Single selection returns string."""
    # Setup
    # Execute
    # Assert

def test_returns_list_on_multi_select(self):
    """Multi-select returns list of strings."""
    # Setup
    # Execute
    # Assert

def test_raises_on_user_cancel(self):
    """Cancellation raises UserCancelledError."""
    # Setup
    # Execute with pytest.raises()
    # Assert
```

#### 6. Run coverage report
```bash
pytest tests/unit/ui/test_selector.py --cov=promptosaurus.ui._selector
```

#### 7. Verify 90%+ coverage achieved
```
promptosaurus/ui/_selector.py  125  12  90.4%  ✅ PASS
```

---

## 5. Testing Interactive Code (UI Components)

### Challenge: Testing Code That Requires Terminal Input

**Problem:** _selector.py, unix.py, windows.py all need user input/terminal

**Solutions:**

#### A. Mock the Input Provider
```python
class TestSelectOptionWithExplain:
    @pytest.fixture
    def mock_input_provider(self, mocker):
        provider = mocker.MagicMock()
        # Simulate key presses
        provider.events = iter([
            InputEvent(event_type=InputEventType.NUMBER, value=1),
            InputEvent(event_type=InputEventType.ENTER),
        ])
        return provider
    
    def test_with_mock_input(self, mock_input_provider):
        result = select_option_with_explain(...)
        assert result == "option_1"
```

#### B. Mock Terminal Library (termios, msvcrt)
```python
@pytest.fixture
def mock_termios(mocker):
    return mocker.patch("termios.tcgetattr", return_value=[1, 2, 3, 4, 5, 6, 7])

class TestUnixInputProvider:
    def test_unix_input(self, mock_termios):
        provider = UnixInputProvider()
        # Test input parsing
```

#### C. Use Pexpect for End-to-End Terminal Testing
```python
import pexpect

class TestSelectorE2E:
    def test_interactive_flow(self):
        proc = pexpect.spawn("pytest --interactive-mode")
        proc.expect("Select an option:")
        proc.sendline("1")
        proc.expect("Your selection: 1")
```

---

## 6. Coverage Gaps Action Plan

### Week 1: Critical Gaps (5 days)
- [ ] Create test_selector.py (1 day)
- [ ] Create test_unix.py (1.5 days)
- [ ] Create test_windows.py (1.5 days)
- [ ] Create test_orchestrator.py (1 day)

**Target:** Registry + UI coverage from 20-53% → 85%+

### Week 2: High Priority Gaps (3 days)
- [ ] Expand registry tests (1 day)
- [ ] Create test_commands.py (1 day)
- [ ] Create test_input_fallback.py (0.5 days)
- [ ] Fix edge cases in existing tests (0.5 days)

**Target:** Overall coverage from 64% → 75%+

### Week 3: Fine-Tuning (2 days)
- [ ] Run full coverage report
- [ ] Find remaining uncovered paths
- [ ] Add missing edge case tests
- [ ] Verify 90% per-class compliance

**Target:** Overall coverage from 75% → 85%+

---

## 7. Verification Commands

```bash
# Check coverage by module
pytest --cov=promptosaurus --cov-report=term-missing

# Check coverage for specific module
pytest tests/unit/ui/ --cov=promptosaurus.ui --cov-report=html

# List modules below 90% coverage
pytest --cov=promptosaurus --cov-report=term | grep -v "100.0%"

# Test one class
pytest tests/unit/ui/test_selector.py::TestSelectOptionWithExplain -v

# Run with coverage thresholds
pytest --cov=promptosaurus --cov-fail-under=90
```

---

## 8. Summary

### Convention Rules (MUST FOLLOW)
1. ✅ Test file `test_[module].py` mirrors source structure
2. ✅ One test class per tested class/function
3. ✅ Test method naming: `test_[function]_[scenario]`
4. ✅ Use pytest marks (@pytest.mark.unit, etc.)
5. ✅ Fixtures in conftest.py or at test class level

### Coverage Requirements (MUST ACHIEVE)
- ✅ **90% per class/function** (non-negotiable)
- ✅ **85% per module** minimum
- ✅ **Overall 85%** project target

### Priority (DO THIS FIRST)
1. Create 5 missing test files (Week 1)
2. Expand registry tests (Week 2)
3. Achieve 85% overall coverage (Week 3)
4. Then proceed with Phase 3 expansion

---

**Next Step:** Begin creating missing test files in order of priority
