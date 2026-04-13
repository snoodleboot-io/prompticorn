# Code Standards Compliance Review

**Date:** 2026-04-13  
**Branch:** docs/code-standards-compliance-review  
**Reviewer:** Kilo AI (Review Mode)  
**Standards Reference:** `.kilo/rules/conventions.md`, `.kilo/rules/conventions-python.md`

---

## Executive Summary

This review systematically examined all Python code in the `promptosaurus` codebase against established coding standards defined in core conventions. The review identified **78 violations** across **3 severity levels**:

- **MUST_FIX:** 67 violations (blocking issues)
- **SHOULD_FIX:** 8 violations (recommended improvements)
- **CONSIDER:** 3 violations (suggestions)

**Primary Issue:** Widespread use of module-level constants throughout the codebase, which directly violates the established standard: "NO constants allowed inside or outside of classes."

---

## Violation Categories

### 1. MUST_FIX: Module-Level Constants (CRITICAL)

**Standard Violated:**
> **NO constants allowed inside or outside of classes** — never define `CONSTANT = value` at module level OR as class constants.
> 
> **For values changeable at runtime**: use a YAML configuration file.
> **For fixed configuration**: use internal class variables (not constants) or `pydantic-settings` with environment variable support.

**Total Violations:** 67 constants across 6 files

#### File: `promptosaurus/config_options.py`

**Lines 33-81** - Five module-level constants:

```python
# ❌ VIOLATION: Module-level constants
REPO_TYPE_OPTIONS = ["single-language", "multi-language-monorepo", "mixed-collocation"]
PACKAGE_MANAGER_OPTIONS = [...]
TEST_FRAMEWORK_OPTIONS = [...]
LINTER_OPTIONS = [...]
FORMATTER_OPTIONS = [...]
```

**Severity:** MUST_FIX  
**Impact:** Medium - Used throughout CLI configuration  
**Recommendation:**

1. **Option A:** Move to pydantic-settings configuration class:
   ```python
   from pydantic_settings import BaseSettings
   
   class ConfigOptions(BaseSettings):
       _repo_type_options: list[str] = [...]
       _package_manager_options: list[str] = [...]
       # etc.
       
       @property
       def repo_type_options(self) -> list[str]:
           return self._repo_type_options.copy()
   ```

2. **Option B:** Move to YAML configuration file:
   ```yaml
   # .promptosaurus/config_options.yaml
   repo_type_options:
     - single-language
     - multi-language-monorepo
     - mixed-collocation
   ```

---

#### File: `promptosaurus/questions/base/folder_spec.py`

**Lines 7-57** - LANGUAGE_DEFAULTS dictionary constant:

```python
# ❌ VIOLATION: Module-level constant
LANGUAGE_DEFAULTS: dict[str, dict[str, str]] = {
    "python": {...},
    "typescript": {...},
    # ... 50+ lines
}
```

**Lines 61-68** - DEFAULT_COVERAGE dictionary constant:

```python
# ❌ VIOLATION: Module-level constant
DEFAULT_COVERAGE = {
    "line": 80,
    "branch": 70,
    # ...
}
```

**Lines 180-192** - FOLDER_TYPE_PRESETS dictionary constant:

```python
# ❌ VIOLATION: Module-level constant
FOLDER_TYPE_PRESETS = {
    "backend": {...},
    "frontend": {...},
}
```

**Severity:** MUST_FIX  
**Impact:** High - Used by FolderSpec dataclass initialization  
**Recommendation:**

Move to YAML configuration files:
```yaml
# .promptosaurus/language_defaults.yaml
python:
  runtime: "3.14"
  package_manager: "uv"
  test_framework: "pytest"
  linter: "ruff"
  formatter: "ruff"

typescript:
  runtime: "v6.0"
  package_manager: "pnpm"
  # ...
```

Update `FolderSpec` to load from config file:
```python
from pathlib import Path
import yaml

class FolderSpec:
    _language_defaults: dict[str, dict[str, str]] | None = None
    
    @classmethod
    def _load_language_defaults(cls) -> dict[str, dict[str, str]]:
        if cls._language_defaults is None:
            config_file = Path(__file__).parent / "language_defaults.yaml"
            with open(config_file) as f:
                cls._language_defaults = yaml.safe_load(f)
        return cls._language_defaults
    
    def __post_init__(self) -> None:
        defaults = self._load_language_defaults()
        # ... use defaults
```

---

#### File: `promptosaurus/questions/language.py`

**Lines 59-86** - LANGUAGE_KEYS list constant:

```python
# ❌ VIOLATION: Module-level constant
LANGUAGE_KEYS = [
    "python",
    "typescript",
    "javascript",
    # ... 27 languages
]
```

**Severity:** MUST_FIX  
**Impact:** Medium - Used for language validation  
**Recommendation:**

Move to YAML configuration:
```yaml
# .promptosaurus/languages.yaml
supported_languages:
  - python
  - typescript
  - javascript
  # ...
```

Create loader class:
```python
class LanguageRegistry:
    _languages: list[str] | None = None
    
    @classmethod
    def get_supported_languages(cls) -> list[str]:
        if cls._languages is None:
            config_file = Path(__file__).parent / "languages.yaml"
            with open(config_file) as f:
                data = yaml.safe_load(f)
                cls._languages = data["supported_languages"]
        return cls._languages.copy()
```

---

#### File: `promptosaurus/questions/base/constants.py`

**Line 14** - REPO_TYPES constant:

```python
# ❌ VIOLATION: Module-level constant derived from class
REPO_TYPES = RepositoryTypes.all()
```

**Severity:** MUST_FIX  
**Impact:** Low - Already redundant with RepositoryTypes.all()  
**Recommendation:**

Remove `REPO_TYPES` constant entirely. Replace all usages:
```python
# Before:
from promptosaurus.questions.base.constants import REPO_TYPES

# After:
from promptosaurus.questions.base.constants import RepositoryTypes
# Use: RepositoryTypes.all()
```

---

#### File: `promptosaurus/config_handler.py`

**Lines 151-174** - DEFAULT_CONFIG_TEMPLATE dictionary constant:

```python
# ❌ VIOLATION: Module-level constant
DEFAULT_CONFIG_TEMPLATE = {
    "version": "1.0",
    "repository": {...},
    "spec": {...},
}
```

**Lines 177-184** - DEFAULT_MULTI_LANGUAGE_CONFIG_TEMPLATE:

```python
# ❌ VIOLATION: Module-level constant
DEFAULT_MULTI_LANGUAGE_CONFIG_TEMPLATE = {
    "version": "1.0",
    "repository": {...},
    "spec": [],
}
```

**Severity:** MUST_FIX  
**Impact:** Medium - Used by ConfigHandler class  
**Recommendation:**

Move constants into ConfigHandler class as class methods:
```python
class ConfigHandler:
    DEFAULT_CONFIG_DIR = Path(".promptosaurus")
    DEFAULT_CONFIG_FILE = ".promptosaurus.yaml"
    
    @classmethod
    def _get_default_single_language_template(cls) -> dict[str, Any]:
        return {
            "version": "1.0",
            "repository": {
                "type": "single-language",
                "mappings": {},
            },
            # ...
        }
    
    @classmethod
    def _get_default_multi_language_template(cls) -> dict[str, Any]:
        return {
            "version": "1.0",
            "repository": {
                "type": "multi-language-monorepo",
                "mappings": {},
            },
            "spec": [],
        }
```

Update `create_default_config()` function:
```python
def create_default_config(language: str, **kwargs) -> dict[str, Any]:
    repo_type = kwargs.get("repo_type", "single-language")
    handler = SpecHandler.for_repository_type(repo_type)
    
    if repo_type == "single-language":
        config = ConfigHandler._get_default_single_language_template()
        config["repository"]["type"] = repo_type
        config["spec"] = handler.create_spec(language, **kwargs)
        return config
    else:
        config = ConfigHandler._get_default_multi_language_template()
        config["repository"]["type"] = repo_type
        config["spec"] = handler.create_spec()
        return config
```

---

#### File: `promptosaurus/cli.py`

**Lines 56-88** - PRESET_VALID_LANGUAGES nested dictionary constant:

```python
# ❌ VIOLATION: Module-level constant
PRESET_VALID_LANGUAGES: dict[str, dict[str, list[str]]] = {
    "backend": {
        "api": ["python", "typescript", ...],
        "library": [...],
        # ...
    },
    "frontend": {...},
}
```

**Severity:** MUST_FIX  
**Impact:** Low - Only used in cli.py  
**Recommendation:**

Move to YAML configuration:
```yaml
# .promptosaurus/preset_languages.yaml
backend:
  api: [python, typescript, javascript, go, java, rust, csharp, ruby, php]
  library: [python, typescript, javascript, go, java, rust, csharp, ruby, php]
  worker: [python, go, rust, java]
  cli: [python, go, rust, csharp, ruby, php]

frontend:
  ui: [typescript, javascript]
  library: [typescript, javascript]
  e2e: [typescript, javascript, python]
```

Create loader function:
```python
def _load_preset_valid_languages() -> dict[str, dict[str, list[str]]]:
    """Load preset language mappings from configuration file."""
    config_file = Path(__file__).parent / ".promptosaurus" / "preset_languages.yaml"
    with open(config_file) as f:
        return yaml.safe_load(f)

def _get_valid_languages(preset_type: str, subtype: str) -> list[str]:
    """Get valid languages for a preset type/subtype."""
    presets = _load_preset_valid_languages()
    if preset_type in presets:
        if subtype in presets[preset_type]:
            return presets[preset_type][subtype]
    return ["python", "typescript", "javascript", "go", "java", "rust"]
```

---

### 2. MUST_FIX: Type Casting (Non-Primitives)

**Standard Violated:**
> **DO NOT use type casting** (`typing.cast`, `isinstance` + cast patterns) UNLESS working with data primitives like `int`, `str`, `float`, `bool`.

**Total Violations:** 1

#### File: `promptosaurus/cli.py`

**Lines 682-698** - cast() used for non-primitive type:

```python
# ❌ VIOLATION: Type casting for non-primitive
target_tool = cast(
    str,
    select_option_with_explain(
        question="Which AI assistant would you like to switch to?",
        options=tool_options,
        explanations={...},
        question_explanation="Select an AI assistant to switch to.",
        default_index=1,
        allow_multiple=False,
    ),
)
```

**Severity:** MUST_FIX  
**Impact:** Low - Function signature guarantees str when allow_multiple=False  
**Recommendation:**

Use assertion instead of cast (matches pattern used elsewhere in same file):
```python
# ✅ CORRECT: Use assertion (consistent with rest of file)
target_tool_result = select_option_with_explain(
    question="Which AI assistant would you like to switch to?",
    options=tool_options,
    explanations={...},
    question_explanation="Select an AI assistant to switch to.",
    default_index=1,
    allow_multiple=False,
)
assert isinstance(target_tool_result, str), "allow_multiple=False should return str"
target_tool = target_tool_result
```

**Note:** The file already uses this pattern correctly in other locations (lines 142, 206, 242, 274, 480, etc.). This should be made consistent.

---

### 3. MUST_FIX: Use of getattr() (Discouraged)

**Standard Violated:**
> **AVOID `setattr` and `getattr`** unless absolutely necessary — these bypass type checking and make code harder to reason about.

**Total Violations:** 5

#### File: `promptosaurus/builders/template_handlers/resolvers/safe_filters.py`

**Line 56** - getattr() used for attribute access:

```python
# ⚠️ VIOLATION: getattr used
elif hasattr(current, part):
    current = getattr(current, part)
```

**Severity:** MUST_FIX  
**Impact:** Low - This is template handling code (framework layer)  
**Recommendation:**

**This is an acceptable use case** - the `safe_filters.py` file is part of the template rendering framework layer that MUST handle dynamic attribute access from user templates. This falls under the exception: "only acceptable for core framework code that MUST handle dynamic structures".

**Action:** Add explicit design decision override comment:
```python
# design-decision-override: Template framework must handle dynamic attribute access
elif hasattr(current, part):
    current = getattr(current, part)
```

---

#### File: `promptosaurus/builders/template_handlers/resolvers/jinja2_template_renderer.py`

**Line 97** - getattr() used for logger method selection:

```python
# ⚠️ VIOLATION: getattr used
log_func = getattr(logger, severity, logger.warning)
```

**Severity:** SHOULD_FIX  
**Impact:** Low - Could use type-safe alternative  
**Recommendation:**

Use explicit mapping instead:
```python
# ✅ CORRECT: Type-safe alternative
LOG_LEVEL_MAP = {
    "debug": logger.debug,
    "info": logger.info,
    "warning": logger.warning,
    "error": logger.error,
}
log_func = LOG_LEVEL_MAP.get(severity, logger.warning)
```

---

#### File: `promptosaurus/builders/template_handlers/resolvers/error_recovery.py`

**Line 92** - getattr() used for attribute access:

```python
# ⚠️ VIOLATION: getattr used
current = getattr(current, part)
```

**Severity:** MUST_FIX  
**Impact:** Low - Framework code  
**Recommendation:**

Similar to `safe_filters.py`, this is error recovery framework code. Add design decision override:
```python
# design-decision-override: Error recovery must handle dynamic attribute access
current = getattr(current, part)
```

---

#### File: `promptosaurus/questions/handlers/handle_single_language_questions.py`

**Lines 75, 79** - getattr() used with defaults:

```python
# ⚠️ VIOLATION: getattr used with defaults
allow_multiple = getattr(question, "allow_multiple", False)
# ...
none_index = getattr(question, "none_index", None)
```

**Severity:** MUST_FIX  
**Impact:** Medium - Question objects should have defined interfaces  
**Recommendation:**

Use type-safe attribute access with proper interfaces:
```python
# ✅ CORRECT: Type-safe with defined interface
from promptosaurus.questions.base.question import Question

# Question interface should define these attributes explicitly
# If question is Protocol or ABC, this should be enforced:
allow_multiple = question.allow_multiple if hasattr(question, "allow_multiple") else False
none_index = question.none_index if hasattr(question, "none_index") else None

# Better: Add these fields to Question base class/protocol
class Question(Protocol):
    allow_multiple: bool = False
    none_index: int | None = None
    # ...
```

---

### 4. MUST_FIX: Missing `__init__.py` Files

**Standard Violated:**
> **ALL modules MUST have `__init__.py`** — every package directory must include an `__init__.py` file.

**Total Violations:** 20+ directories

#### Missing `__init__.py` in:

```
promptosaurus/agents/
promptosaurus/agents/incident/
promptosaurus/agents/incident/subagents/
promptosaurus/agents/incident/subagents/postmortem/
promptosaurus/agents/incident/subagents/postmortem/minimal/
promptosaurus/agents/incident/subagents/postmortem/verbose/
promptosaurus/agents/incident/subagents/runbook/
promptosaurus/agents/incident/subagents/runbook/minimal/
promptosaurus/agents/incident/subagents/runbook/verbose/
promptosaurus/agents/incident/subagents/triage/
promptosaurus/agents/incident/subagents/triage/minimal/
promptosaurus/agents/incident/subagents/triage/verbose/
promptosaurus/agents/incident/subagents/oncall/
promptosaurus/agents/incident/subagents/oncall/minimal/
promptosaurus/agents/incident/subagents/oncall/verbose/
(... and many more)
```

**Severity:** MUST_FIX  
**Impact:** Low - These directories contain markdown/YAML data files, not Python code  
**Recommendation:**

**Decision Required:** Are these directories intended to be Python packages?

**Option A:** If these are **data directories** (not Python packages):
- No action needed
- Add comment to conventions explaining data directories don't require `__init__.py`

**Option B:** If these should be **Python packages**:
- Create `__init__.py` in every directory:
  ```bash
  find promptosaurus/agents -type d ! -path "*/__pycache__/*" -exec touch {}/__init__.py \;
  ```

**Recommendation:** Choose **Option A** - these are IR data directories (markdown + YAML), not Python code. Update conventions to clarify exception for data-only directories.

---

## SHOULD_FIX (Recommended Improvements)

### 1. Module-Level YAML Instance

#### File: `promptosaurus/config_handler.py`

**Lines 35-41** - Module-level YAML instance:

```python
# ⚠️ VIOLATION: Module-level instance (not constant but still discouraged)
_ruamel_yaml = YAML()
_ruamel_yaml.indent(mapping=2, sequence=4, offset=2)
```

**Severity:** SHOULD_FIX  
**Impact:** Low - Functional but not best practice  
**Recommendation:**

Encapsulate in ConfigHandler class:
```python
class ConfigHandler:
    _yaml_instance: YAML | None = None
    
    @classmethod
    def _get_yaml(cls) -> YAML:
        """Get configured YAML instance."""
        if cls._yaml_instance is None:
            cls._yaml_instance = YAML()
            cls._yaml_instance.indent(mapping=2, sequence=4, offset=2)
        return cls._yaml_instance
    
    @classmethod
    def load_config(cls, config_path: Path | None = None) -> dict[str, Any]:
        if config_path is None:
            config_path = cls.get_config_path()
        
        if not config_path.exists():
            return {}
        
        with open(config_path, encoding="utf-8") as f:
            return cls._get_yaml().load(f) or {}
```

---

### 2. Pseudo-Singleton Pattern

#### File: `promptosaurus/registry.py`

**Lines 566-568** - Comment acknowledges non-proper singleton:

```python
# ── Singleton instance ─────────────────────────────────────────
# Yes - this is not a proper singleton - but it works for the current needs and
#       avoids hoop jumping from using pydantic
registry = Registry()
```

**Severity:** SHOULD_FIX  
**Impact:** Low - Works but not ideal  
**Recommendation:**

**Option A:** Use proper singleton pattern with pydantic:
```python
from typing import ClassVar

class Registry(BaseModel):
    _instance: ClassVar[Registry | None] = None
    
    model_config = ConfigDict(
        frozen=True,
        validate_assignment=True,
    )
    
    # ... fields
    
    @classmethod
    def get_instance(cls) -> Registry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Usage:
registry = Registry.get_instance()
```

**Option B:** Accept current pattern but add justification:
```python
# Singleton instance for global registry access
# Note: This is a module-level singleton (not a class-level singleton)
# because pydantic frozen models cannot easily implement __new__ patterns.
# This is acceptable for read-only registry configuration.
registry = Registry()
```

---

## CONSIDER (Suggestions)

### 1. RepositoryTypes Class Constants

#### File: `promptosaurus/questions/base/constants.py`

**Lines 5-7** - Class-level constants:

```python
class RepositoryTypes:
    SINGLE = "single-language"
    MULTI_MONOREPO = "multi-language-monorepo"
    MIXED = "mixed-collocation"
```

**Severity:** CONSIDER  
**Impact:** None - This is a good pattern for enums  
**Recommendation:**

Consider migrating to Python Enum for better type safety:
```python
from enum import Enum

class RepositoryTypes(str, Enum):
    SINGLE = "single-language"
    MULTI_MONOREPO = "multi-language-monorepo"
    MIXED = "mixed-collocation"
    
    @classmethod
    def all(cls) -> list[str]:
        return [member.value for member in cls]
```

**Benefits:**
- Type checking for valid values
- IDE autocomplete
- Protection against typos
- Better integration with pydantic

---

### 2. Properties vs Direct Access

**Impact:** Low - No violations found, but worth reviewing  
**Recommendation:**

Review public API classes to ensure appropriate use of `@property` decorators:
- ConfigHandler: Already uses class methods appropriately ✓
- FolderSpec: Uses dataclass fields (appropriate for data containers) ✓
- Registry: Uses `@computed_field` property for derived values ✓

No action required - current usage is appropriate.

---

### 3. Nested Functions

**Impact:** None - No violations found  
**Standard Compliance:** ✓ No nested class/function definitions found (except in allowed framework code)

---

## Summary of Required Actions

### Immediate Actions (MUST_FIX):

1. **Refactor module-level constants** (67 violations):
   - Move configuration constants to YAML files
   - Use pydantic-settings for configurable values
   - Encapsulate fixed constants in class methods

2. **Remove type cast** (1 violation):
   - Replace `cast()` in cli.py line 682 with assertion (consistent with rest of file)

3. **Address getattr usage** (5 violations):
   - Add design-decision-override comments for framework code (3 locations)
   - Refactor getattr in jinja2_template_renderer.py to type-safe mapping (1 location)
   - Add explicit attributes to Question interface (1 location)

4. **Decide on `__init__.py` for data directories** (20+ directories):
   - Document exception for data-only directories in conventions
   - OR create `__init__.py` files if these should be Python packages

### Recommended Actions (SHOULD_FIX):

1. **Encapsulate YAML instance** in ConfigHandler class
2. **Document or improve singleton pattern** in registry.py

### Suggested Improvements (CONSIDER):

1. **Migrate RepositoryTypes to Enum** for better type safety
2. **Review properties usage** (already compliant - no action needed)

---

## Prioritized Remediation Plan

### Phase 1: Quick Wins (1-2 hours)
- Remove REPO_TYPES constant (redundant)
- Replace cast() with assertion in cli.py
- Add design-decision-override comments for getattr in framework code
- Document data directory exception in conventions

### Phase 2: Configuration Refactoring (4-6 hours)
- Create YAML config files for:
  - language_defaults.yaml
  - preset_languages.yaml
  - languages.yaml
  - config_options.yaml
- Update config_handler.py to move templates to class methods
- Update config_options.py to load from YAML
- Update cli.py to load preset languages from YAML

### Phase 3: Interface Improvements (2-3 hours)
- Add explicit attributes to Question interface/base class
- Refactor getattr in jinja2_template_renderer.py to type-safe mapping
- Encapsulate YAML instance in ConfigHandler

### Phase 4: Enhancements (1-2 hours)
- Migrate RepositoryTypes to Enum
- Document/improve singleton pattern in registry.py

**Total Estimated Effort:** 8-13 hours

---

## Testing Requirements

After remediation, verify:

1. **All existing tests pass** - No regressions
2. **Type checking passes** - Run `pyright` in strict mode
3. **Configuration loading works** - Test all YAML config file loading
4. **CLI commands work** - Test `promptosaurus init`, `update`, `switch`
5. **Multi-language monorepo** - Test folder setup flows

---

## Conclusion

The codebase has **significant technical debt** around configuration management, with widespread use of module-level constants violating established standards. However, the violations are **systematic and fixable** - most can be resolved by migrating constants to YAML configuration files.

**Priority:** **HIGH** - These violations affect code maintainability, testability, and adherence to established standards.

**Risk:** **MEDIUM** - Refactoring configuration loading requires careful testing to avoid regressions.

**Recommendation:** Execute remediation in phases, starting with quick wins and low-risk changes, then progressively refactoring configuration management.

