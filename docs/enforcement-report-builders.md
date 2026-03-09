# Builder Code Enforcement Report

**Date:** 2026-03-08  
**Scope:** `promptosaurus/builders/` directory + `promptosaurus/registry.py`  
**Mode:** enforcement  
**Branch:** main (review only)

---

## Executive Summary

The builders code has significant convention violations across multiple categories. The most critical issues are:
1. **Module-level constants** violating the "NO constants outside classes" rule
2. **Deeply nested logic** in `_make_dest_filename` function
3. **Duplicated code** across builder classes
4. **Missing shared utilities** for repeated patterns
5. **Large inline strings** that should be separate files

**Compliance Rate:** ~45% (significant work needed)

---

## Violation Details

### MUST_FIX Items

#### 1. Module-Level Constants in [`kilo.py`](promptosaurus/builders/kilo.py:59-60)

**Rule Violated:** "NO constants allowed inside or outside of classes — never define `CONSTANT = value` at module level"

**Severity:** MUST_FIX  
**Location:** [`kilo.py:59-60`](promptosaurus/builders/kilo.py:59)

**Current Code:**
```python
_KILO_MODES: dict[str, Any] = _load_kilo_modes_from_yaml()
_LANGUAGE_FILE_MAP: dict[str, str] = _load_language_file_map_from_yaml()
```

**Violation:** These are module-level "constants" (loaded at import time) that should be class-level or in a configuration module.

**Suggested Fix:** Move to class-level properties in `KiloCodeBuilder` or create a separate `KiloConfig` class.

---

#### 2. Deeply Nested Logic in [`kilo_ide.py:21-90`](promptosaurus/builders/kilo_ide.py:21)

**Rule Violated:** SOLID principles - code should be readable and maintainable

**Severity:** MUST_FIX  
**Location:** [`_make_dest_filename()`](promptosaurus/builders/kilo_ide.py:21)

**Current Code:** 70-line function with 6+ levels of nesting

**Violation:** The function has deeply nested if/elif/else chains that make it hard to read and maintain.

**Suggested Fix:** Refactor into a `DestinationFilenameStrategy` class with separate methods for each transformation rule.

---

#### 3. Hardcoded Agent Prefixes in [`kilo_ide.py:68-85`](promptosaurus/builders/kilo_ide.py:68)

**Rule Violated:** Maintainability - hardcoded values should be extracted

**Severity:** MUST_FIX  
**Location:** [`kilo_ide.py:68-85`](promptosaurus/builders/kilo_ide.py:68)

**Current Code:**
```python
for agent_prefix in [
    "code-",
    "test-",
    "refactor-",
    "document-",
    # ... 11 more
]:
```

**Violation:** Hardcoded list of 15 agent prefixes that should come from the registry or configuration.

**Suggested Fix:** Use `registry.modes.keys()` or load from `kilo_modes.yaml`.

---

### SHOULD_FIX Items

#### 4. Duplicated `_build_ignore` Method

**Rule Violated:** DRY principle (Don't Repeat Yourself)

**Severity:** SHOULD_FIX  
**Location:** 
- [`cline.py:48-59`](promptosaurus/builders/cline.py:48)
- [`cursor.py:63-74`](promptosaurus/builders/cursor.py:63)
- [`kilo.py:195-206`](promptosaurus/builders/kilo.py:195)

**Current Code:** Nearly identical `_build_ignore` methods in 3+ files.

**Violation:** Same pattern repeated - generate ignore file, check dry_run, write or return preview.

**Suggested Fix:** Create interface method in base `Builder` class or create `IgnoreFileBuilder` utility class.

---

#### 5. Duplicated Header Stripping Logic

**Rule Violated:** DRY principle

**Severity:** SHOULD_FIX  
**Locations:**
- [`kilo.py:229-240`](promptosaurus/builders/kilo.py:229) (in `_create_base_md`)
- [`kilo.py:290-301`](promptosaurus/builders/kilo.py:290) (in `_create_collapsed_mode_md`)
- [`registry.py:29-36`](promptosaurus/registry.py:29)

**Current Code:** Same 6-line logic to strip header comments repeated 3+ times.

**Violation:** Identical code for stripping header comments appears in multiple places.

**Suggested Fix:** Create a `HeaderStripper` utility class or function in a shared module.

---

#### 6. Large Inline String in [`kilo_cli.py:90-151`](promptosaurus/builders/kilo_cli.py:90)

**Rule Violated:** Code organization - large strings should be in separate files

**Severity:** SHOULD_FIX  
**Location:** [`_get_agents_md_content()`](promptosaurus/builders/kilo_cli.py:90)

**Current Code:** 60-line multi-line string returned directly in method.

**Violation:** AGENTS.md content (a user-facing document) is embedded as a string literal in code.

**Suggested Fix:** Move AGENTS.md content to a separate `.md` file and read it at runtime.

---

#### 7. Similar Pattern in [`copilot.py:48-136`](promptosaurus/builders/copilot.py:48)

**Rule Violated:** Missing shared utilities - similar patterns should be consolidated

**Severity:** SHOULD_FIX  
**Location:** Multiple `_build_*` methods

**Current Code:**
- `_build_always_on` (lines 48-74)
- `_build_mode` (lines 76-110)
- `_build_copilotignore` (lines 112-123)
- `_build_gitignore` (lines 125-136)

**Violation:** These methods follow similar patterns (check dry_run, create content, write or return preview) but aren't consolidated.

**Suggested Fix:** Create a base `_generate_file` method that handles the common pattern.

---

#### 8. Module-Level Functions in [`kilo.py:19-40`](promptosaurus/builders/kilo.py:19)

**Rule Violated:** Organization - related functions should be in classes

**Severity:** SHOULD_FIX  
**Location:** 
- [`_load_kilo_modes_from_yaml()`](promptosaurus/builders/kilo.py:19)
- [`_load_language_file_map_from_yaml()`](promptosaurus/builders/kilo.py:42)

**Current Code:** Two module-level functions for loading YAML data.

**Violation:** These are factory/loading functions that should be class methods or in a `ConfigLoader` class.

**Suggested Fix:** Move to a `KiloConfig` class as class methods or static methods.

---

#### 9. Module-Level Functions in [`registry.py:23-47`](promptosaurus/registry.py:23)

**Rule Violated:** Organization - related functions should be in classes

**Severity:** SHOULD_FIX  
**Location:**
- [`_prompt_body_cached()`](promptosaurus/registry.py:23)
- [`_dest_name()`](promptosaurus/registry.py:39)

**Current Code:** Helper functions at module level.

**Violation:** These are helper functions that could be methods in a utility class.

**Suggested Fix:** Consider creating a `PromptFileHandler` class or keep as module-level (acceptable for small utilities).

---

### CONSIDER Items

#### 10. Abstract Method Not Decorated in [`builder.py:13-16`](promptosaurus/builders/builder.py:13)

**Rule Violated:** Best practice for interface methods

**Severity:** ~~CONSIDER~~ N/A (already correct interface pattern)  
**Location:** [`Builder.build()`](promptosaurus/builders/builder.py:13)

**Current Code:**
```python
def build(self, output: Path, config: dict[str, Any] | None = None, dry_run: bool = False) -> list[str]:
    raise NotImplementedError("Subclasses must implement build()")
```

**Violation:** ~~Method raises `NotImplementedError` but isn't decorated with `@abstractmethod`.~~

**Status:** N/A - This is CORRECT. Uses interface pattern (NotImplementedError) per conventions - no ABC.

---

#### 11. TODO Comments in [`registry.py:99, 119`](promptosaurus/registry.py:99)

**Rule Violated:** "No TODOs without issue references"

**Severity:** CONSIDER  
**Location:**
- [`registry.py:99`](promptosaurus/registry.py:99): "TODO: Discover This"
- [`registry.py:119`](promptosaurus/registry.py:119): "TODO: This should be auto-discoverable"

**Violation:** TODO comments without issue ticket references.

**Suggested Fix:** Either create tickets or remove TODOs if not actionable.

---

#### 12. Inline String Literals in [`kilo_ide.py:149-199`](promptosaurus/builders/kilo_ide.py:149)

**Rule Violated:** Code organization

**Severity:** CONSIDER  
**Location:** [`_get_agents_md_content()`](promptosaurus/builders/kilo_ide.py:149)

**Current Code:** 50-line AGENTS.md content as inline string.

**Violation:** Same issue as #6 - document content in code.

**Suggested Fix:** Move to separate file.

---

#### 13. Singleton Pattern Comment in [`registry.py:445-447`](promptosaurus/registry.py:445)

**Rule Violated:** Code quality - excuses in comments

**Severity:** CONSIDER  
**Location:** [`registry.py:445-447`](promptosaurus/registry.py:445)

**Current Code:**
```python
# Yes - this is not a proper singleton - but it works for the current needs and
#       avoids hoop jumping from using pydantic
registry = Registry()
```

**Violation:** Comment explaining why a pattern isn't properly implemented.

**Suggested Fix:** Either implement proper singleton or remove the comment.

---

## Missing Abstractions

The following interfaces are missing and should be created:

1. **`IgnoreFileGenerator`** - Shared class for generating ignore files
   - Used by: ClineBuilder, CursorBuilder, KiloCodeBuilder
   - Methods: `generate_gitignore()`, `generate_clineignore()`, etc.

2. **`HeaderStripper`** - Utility for stripping file headers
   - Used by: kilo.py (2 places), registry.py

3. **`KiloConfig`** - Configuration loader class
   - Replaces: `_KILO_MODES`, `_LANGUAGE_FILE_MAP`, YAML loading functions
   - Location: New file `promptosaurus/builders/config.py`

4. **`DestinationFilenameStrategy`** - Filename transformation strategy
   - Replaces: `_make_dest_filename()` in kilo_ide.py
   - Methods: each transformation rule as separate method

---

### 14. Import Forwarding Violation in [`__init__.py`](promptosaurus/builders/__init__.py:6)

**Rule Violated:** "NEVER use import forwarding — do not re-export imported symbols"

**Severity:** MUST_FIX  
**Location:** [`__init__.py:6-17`](promptosaurus/builders/__init__.py:6)

**Current Code:**
```python
from promptosaurus.builders.kilo import KiloCodeBuilder
from promptosaurus.builders.kilo_cli import KiloCLIBuilder
from promptosaurus.builders.kilo_ide import KiloIDEBuilder

KiloBuilder = KiloCLIBuilder

__all__ = [
    "KiloCodeBuilder",
    "KiloCLIBuilder",
    "KiloIDEBuilder",
    "KiloBuilder",
]
```

**Violation:** This is exactly the anti-pattern - importing from submodules and re-exporting at package level.

**Suggested Fix:** Define public API explicitly OR remove re-exports entirely (import directly from submodules).

---

## Summary

### Files Scanned: 10

| File | Lines | Violations |
|------|-------|------------|
| kilo.py | 330 | 3 MUST_FIX, 2 SHOULD_FIX |
| kilo_ide.py | 199 | 2 MUST_FIX, 2 SHOULD_FIX |
| kilo_cli.py | 151 | 1 SHOULD_FIX |
| registry.py | 448 | 2 SHOULD_FIX, 2 CONSIDER |
| copilot.py | 136 | 1 SHOULD_FIX |
| cline.py | 59 | 1 SHOULD_FIX |
| cursor.py | 83 | 1 SHOULD_FIX |
| builder.py | 27 | 1 CONSIDER |
| _concat.py | 43 | 0 (acceptable) |
| __init__.py | 18 | 0 |

### Total Violations: 19
- **MUST_FIX:** 6
- **SHOULD_FIX:** 12
- **CONSIDER:** 1 (TODO comments - deferred)

### Priority Actions

1. **Immediate (MUST_FIX):**
   - [ ] Move `_KILO_MODES` and `_LANGUAGE_FILE_MAP` to class-level in `KiloCodeBuilder`
   - [ ] Refactor `_make_dest_filename()` to reduce nesting
   - [ ] Extract hardcoded agent prefixes to configuration
   - [ ] Fix import forwarding in `__init__.py`

2. **Soon (SHOULD_FIX):**
   - [ ] Create `IgnoreFileBuilder` interface
   - [ ] Create `HeaderStripper` utility
   - [ ] Move large inline strings to separate files

---

## Plan for Refactoring

### Phase 1: Extract Configuration (MUST_FIX)
1. Move `_KILO_MODES` and `_LANGUAGE_FILE_MAP` to class-level in `KiloCodeBuilder`
2. Convert `_load_*_from_yaml` functions to class methods
3. Create `promptosaurus/builders/config.py` for configuration loading

### Phase 2: Simplify Nested Logic (MUST_FIX)
1. Refactor `_make_dest_filename()` into `DestinationFilenameStrategy` class
2. Use early returns to reduce nesting
3. Extract agent prefix list to use `registry.modes.keys()`

### Phase 3: Consolidate Duplication (SHOULD_FIX)
1. Create `IgnoreFileGenerator` base class
2. Create `HeaderStripper` utility
3. Consolidate file writing patterns in builders

### Phase 4: Extract Large Strings (SHOULD_FIX)
1. Create `promptosaurus/builders/templates/agents_md.py` or separate `.md` files
2. Update builders to read from files

---

**Status:** NON_COMPLIANT  
**Next Step:** Switch to **refactor** mode to begin fixes, or provide feedback on priorities.
