# PRIMARY_AGENTS_LIST Template Variable - Root Cause & Fix

## Problem

The `{{PRIMARY_AGENTS_LIST}}` template variable was not being populated in the built orchestrator prompt.

## Root Cause Analysis

### Issue 1: Wrong Base Class

**File:** `promptosaurus/builders/template_handlers/primary_agents_handler.py`

**Problem:**
```python
from promptosaurus.builders.template_handlers.template_handler import TemplateVariableHandler

class PrimaryAgentsHandler(TemplateVariableHandler):  # ❌ WRONG
```

**Issue:** Implemented the Protocol directly instead of extending the ABC base class.

**Why this failed:**
- `TemplateVariableHandler` is a Protocol (interface definition)
- `TemplateHandler` is the ABC base class with default implementations
- All other handlers (LanguageHandler, RuntimeHandler, etc.) extend `TemplateHandler`
- The Protocol defines the interface, but the ABC provides the required default methods

**Fix:**
```python
from promptosaurus.builders.template_handlers.template_handler import TemplateHandler

class PrimaryAgentsHandler(TemplateHandler):  # ✅ CORRECT
```

---

### Issue 2: Missing from known_variables List

**File:** `promptosaurus/builders/builder.py`

**Problem:** The `_substitute_template_variables` method has a hardcoded list of known variables:

```python
def _substitute_template_variables(self, content: str, config: dict[str, Any] | None = None) -> str:
    known_variables = [
        "LANGUAGE",
        "RUNTIME",
        "PACKAGE_MANAGER",
        "LINTER",
        # ... etc
        "MUTATION_TOOL",
        # PRIMARY_AGENTS_LIST was missing here! ❌
    ]
    for var_name in known_variables:
        handler = self._template_handler_registry.get_handler_for_variable(var_name)
        if handler:
            context[var_name] = handler.handle(var_name, spec_config)
```

**Why this failed:**
- Only variables in the `known_variables` list get looked up
- `PRIMARY_AGENTS_LIST` wasn't in the list
- Even though the handler was registered, it was never queried

**Fix:**
```python
known_variables = [
    "LANGUAGE",
    "RUNTIME",
    # ... existing variables ...
    "MUTATION_TOOL",
    "PRIMARY_AGENTS_LIST",  # ✅ Added
    "LINE_COVERAGE_%",
    # ... rest of variables ...
]
```

---

## Complete Fix Summary

### Changes Made

1. **promptosaurus/builders/template_handlers/primary_agents_handler.py**
   - Changed: `class PrimaryAgentsHandler(TemplateVariableHandler):`
   - To: `class PrimaryAgentsHandler(TemplateHandler):`
   - Reason: Extend ABC base class, not Protocol

2. **promptosaurus/builders/builder.py** (Line ~293)
   - Added: `"PRIMARY_AGENTS_LIST",` to known_variables list
   - Reason: Variable must be in list to be looked up

3. **promptosaurus/builders/builder.py** (Line ~30)
   - Added: `from promptosaurus.builders.template_handlers.primary_agents_handler import PrimaryAgentsHandler`
   - Reason: Import the handler

4. **promptosaurus/builders/builder.py** (Line ~365)
   - Added: `PrimaryAgentsHandler(),` to fallback_handlers list
   - Reason: Register handler in default registry

### How Template Variables Work

1. **Template File Contains Variable**
   - `orchestrator/prompt.md` has `{{PRIMARY_AGENTS_LIST}}`

2. **Builder Reads Template**
   - `_substitute_template_variables()` is called on content

3. **Variable Lookup**
   - Iterates through `known_variables` list
   - For each variable, asks registry: `get_handler_for_variable(var_name)`

4. **Handler Discovery**
   - Registry checks each registered handler
   - Calls `handler.can_handle(var_name)`
   - Returns first handler that returns True

5. **Variable Substitution**
   - Calls `handler.handle(var_name, config)`
   - Handler returns replacement string
   - Jinja2 renderer substitutes `{{var_name}}` with returned value

6. **Result**
   - Template variable is replaced with generated content

### Key Learnings

**Two Requirements for Template Variables:**

1. **Handler must be registered** in `_get_default_template_handler_registry()`
   - Adds handler to the registry so it can be discovered

2. **Variable must be in known_variables list** in `_substitute_template_variables()`
   - Only variables in this list are looked up during substitution

**Without BOTH:** Template variable remains unreplaced!

---

## Testing

To verify the fix works:

```bash
# Build the config
promptosaurus build kilo ./output

# Check orchestrator prompt
cat output/.kilo/agents/orchestrator.md | grep -A 20 "Available primary agents"

# Should see:
# - **architect**: System design, architecture planning...
# - **ask**: General questions and exploratory analysis...
# - **backend**: Backend development and API implementation...
# ... (all 17+ agents listed)
```

---

## Future Improvement

Consider making variable registration more dynamic:

**Option A: Auto-discover variables**
```python
# Instead of hardcoded known_variables list:
known_variables = []
for handler in self._template_handler_registry.get_handlers():
    known_variables.extend(handler.get_variable_names())
```

**Option B: Handler provides variable names**
```python
class PrimaryAgentsHandler(TemplateHandler):
    def get_variable_names(self) -> list[str]:
        return ["PRIMARY_AGENTS_LIST"]
```

This would eliminate the need to manually update the known_variables list.

