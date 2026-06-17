# Template Substitution Fix for KiloBuilder

**Status:** ✅ COMPLETE  
**Date:** 2026-04-12  
**Issue:** Template variables like `{{PRIMARY_AGENTS_LIST}}` were not being substituted in KiloBuilder output

---

## Problem

The `KiloBuilder` class (used to generate Kilo IDE agent configuration files) was NOT performing template variable substitution when building agent files. This meant that template variables like `{{PRIMARY_AGENTS_LIST}}` in the orchestrator agent's prompt remained unreplaced in the final output.

### Root Cause

**Architecture issue:** Two builder classes existed with different inheritance:
1. `Builder` (in `builder.py`) - has `_substitute_template_variables()` method
2. `KiloBuilder` (in `kilo_builder.py`) - extends `AbstractBuilder` (NOT `Builder`)

Result: `KiloBuilder.build()` directly used `agent.system_prompt` without calling template substitution.

---

## Solution Implemented

### 1. Modified `KiloBuilder.__init__()` 

Added initialization of `Builder` instance for template substitution:

```python
def __init__(self, agents_dir: Path | str = "agents") -> None:
    self.agents_dir = agents_dir
    self.core_loader = CoreFilesLoader()
    # Initialize Builder for template variable substitution
    self._builder = Builder()  # ← ADDED
```

### 2. Modified `KiloBuilder.build()` 

Added template substitution call before using system_prompt:

```python
# Use agent system prompt directly (no variants for top-level agents)
system_prompt = agent.system_prompt

# Apply template variable substitution if config is provided
if config:
    system_prompt = self._builder._substitute_template_variables(system_prompt, config)
```

### 3. Fixed `PrimaryAgentsHandler`

The handler was using the wrong registry. Updated to:
- Use `agent_registry.Registry` instead of old `prompticorn.registry`
- Try multiple possible paths for agent discovery
- Filter agents by `mode='primary'`
- Return formatted markdown list

### 4. Added import

Added `from prompticorn.builders.builder import Builder` to imports.

---

## Files Modified

| File | Change |
|------|--------|
| `prompticorn/builders/kilo_builder.py` | Added `Builder` import, initialized `_builder` in `__init__`, called `_substitute_template_variables()` in `build()` |
| `prompticorn/builders/template_handlers/primary_agents_handler.py` | Fixed to use `agent_registry.Registry`, improved path discovery, fixed filtering logic |

---

## Verification

### Test Results

**Template substitution test:**
```bash
$ python /tmp/test_real_agents2.py
✅ Orchestrator prompt DOES contain {{PRIMARY_AGENTS_LIST}} template variable
✅ Template variable was removed from build output
✅ PASS: Template was substituted with agent list!
```

**Output sample:**
```markdown
**Available primary agents for delegation:**
- **architect**: System design, architecture planning, and technical decision making
- **ask**: Answer questions and provide explanations
- **backend**: Design scalable backend systems, APIs, microservices, and distributed architectures
- **compliance**: SOC 2, ISO 27001, GDPR, HIPAA, PCI-DSS compliance
...
(17 total primary agents listed)
```

**Unit tests:**
```bash
$ pytest tests/unit/builders/test_kilo_builder.py
42/43 tests passed (1 pre-existing failure unrelated to this change)
```

---

## Impact

### Before Fix
- `{{PRIMARY_AGENTS_LIST}}` remained unreplaced in orchestrator agent output
- Users would see template syntax instead of actual agent list
- Orchestrator couldn't know which agents are available

### After Fix
- Template variable is correctly substituted with formatted list of all primary agents
- Orchestrator agent file shows complete, up-to-date list of 17 primary agents
- Dynamic discovery - list updates automatically as new agents are added

---

## Design Decisions

### Why not make KiloBuilder extend Builder?

**Considered but rejected.** `AbstractBuilder` and `Builder` serve different purposes:
- `AbstractBuilder` - Interface for tool-specific builders (Kilo, Claude, Cline, etc.)
- `Builder` - Implementation with legacy concat_order and sweet-tea registry dependencies

Making `KiloBuilder` extend `Builder` would:
- Couple it to legacy systems
- Break the abstraction layer
- Force inheritance of unused methods

**Chosen approach:** Composition over inheritance - `KiloBuilder` uses a `Builder` instance internally for template substitution only.

### Why try multiple paths in PrimaryAgentsHandler?

Template handlers are called during build, which may happen:
1. From project root directory
2. From within a subdirectory
3. From test environment
4. From package installation

Multiple path attempts ensure discovery works in all contexts.

---

## Future Improvements

### 1. Extract template substitution to utility module

Currently `KiloBuilder` depends on `Builder` just for `_substitute_template_variables()`. Could extract to:
```python
# prompticorn/builders/template_utils.py
def substitute_template_variables(content: str, config: dict) -> str:
    ...
```

Then both `Builder` and `KiloBuilder` could use it without coupling.

### 2. Registry path configuration

Instead of trying multiple paths, could:
- Accept `agents_dir` as constructor parameter to PrimaryAgentsHandler
- Pass via config dict: `config['agents_dir']`
- Use environment variable: `PROMPTICORN_AGENTS_DIR`

### 3. Template variable documentation

Document all available template variables in one place:
- `PRIMARY_AGENTS_LIST` - List of primary agents
- `LANGUAGE` - Programming language
- `RUNTIME` - Runtime version
- etc.

---

## Related

- **Template variable system:** `prompticorn/builders/builder.py` lines 280-306
- **Handler registry:** `prompticorn/builders/template_handlers/`
- **Original issue:** `planning/current/PRIMARY_AGENTS_LIST_FIX.md` (root cause analysis)
- **Orchestrator agent:** `prompticorn/agents/orchestrator/prompt.md`
