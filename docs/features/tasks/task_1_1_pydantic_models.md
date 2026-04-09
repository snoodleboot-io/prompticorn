# Task 1.1: Create Pydantic IR Models

**Task ID:** 1.1  
**Story:** Story 1 - Infrastructure & Foundation  
**Status:** Ready to Start  
**Effort:** XS (3-4 hours)  
**Owner:** TBD

---

## Overview

Implement the six tool-agnostic Pydantic models that form the Intermediate Representation (IR) for agents, skills, workflows, tools, rules, and project configuration.

## Description

Create Pydantic data classes that model the core concepts used across all AI tools. These models are tool-agnostic and form the foundation for all builders.

## Deliverables

### Models to Create

1. **Agent** (`src/ir/models/agent.py`)
   - Fields: name, description, system_prompt, tools, skills, workflows, subagents
   - Full type hints
   - Validation logic

2. **Skill** (`src/ir/models/skill.py`)
   - Fields: name, description, instructions, tools_needed
   - Full type hints
   - Validation logic

3. **Workflow** (`src/ir/models/workflow.py`)
   - Fields: name, description, steps (list of strings)
   - Full type hints
   - Validation logic

4. **Tool** (`src/ir/models/tool.py`)
   - Fields: name, description, parameters (JSON schema)
   - Full type hints
   - Validation logic

5. **Rules** (`src/ir/models/rules.py`)
   - Fields: constraints, guidelines, patterns
   - Flexible structure for different use cases
   - Full type hints

6. **Project** (`src/ir/models/project.py`)
   - Fields: registry settings, verbosity preference, builder configs
   - Full type hints
   - Validation logic

## Acceptance Criteria

### Functional
- [ ] Agent model created with all required fields (name, description, system_prompt, tools, skills, workflows, subagents)
- [ ] Skill model created (name, description, instructions, tools_needed)
- [ ] Workflow model created (name, description, steps)
- [ ] Tool model created (name, description, parameters)
- [ ] Rules model created (flexible structure)
- [ ] Project model created (registry, verbosity, builder configs)
- [ ] All models have full type hints (no `Any` types)
- [ ] All models have docstrings explaining purpose and usage
- [ ] Validation logic for required fields
- [ ] Validation logic for constraints (e.g., non-empty names)

### Code Quality
- [ ] All models in separate files (one per file)
- [ ] Models inherit from Pydantic BaseModel
- [ ] No external dependencies beyond Pydantic
- [ ] Models are immutable (frozen=True)
- [ ] Models have helpful error messages

### Testing
- [ ] Unit tests cover all models: `tests/unit/ir/test_models.py`
- [ ] Tests cover happy path (valid data)
- [ ] Tests cover edge cases (empty strings, None values, etc.)
- [ ] Tests cover validation errors (invalid data)
- [ ] Coverage: 100% on all models
- [ ] All tests passing

### Type Safety
- [ ] pyright strict mode passes (no type errors)
- [ ] No `Any` types without justification

## Files to Create

```
src/ir/
└── models/
    ├── __init__.py
    ├── agent.py         (Agent model + validation)
    ├── skill.py         (Skill model + validation)
    ├── workflow.py      (Workflow model + validation)
    ├── tool.py          (Tool model + validation)
    ├── rules.py         (Rules model + validation)
    └── project.py       (Project model + validation)

tests/unit/ir/
└── test_models.py       (Unit tests for all models)
```

## Example Model Structure

```python
# src/ir/models/agent.py

from pydantic import BaseModel, Field
from typing import List

class Agent(BaseModel):
    """Tool-agnostic agent model."""
    
    name: str = Field(..., description="Agent name (e.g., 'code')")
    description: str = Field(..., description="One-sentence description")
    system_prompt: str = Field(..., description="System prompt text")
    tools: List[str] = Field(default_factory=list, description="Tool names")
    skills: List[str] = Field(default_factory=list, description="Skill names")
    workflows: List[str] = Field(default_factory=list, description="Workflow names")
    subagents: List[str] = Field(default_factory=list, description="Subagent names")
    
    class Config:
        frozen = True  # Immutable
```

## Test Coverage

Unit tests should cover:
- Valid agent creation
- Missing required fields (raises ValidationError)
- Empty strings for name (raises ValidationError)
- Valid skill creation
- Invalid tool references
- Workflow steps as list
- Project configuration loading
- Rules constraints validation

## Definition of Done

- [ ] All 6 models created and complete
- [ ] All type hints added (no `Any`)
- [ ] All docstrings added
- [ ] All validation logic implemented
- [ ] Unit tests written (100% coverage)
- [ ] All tests passing (locally + CI)
- [ ] pyright strict mode passing
- [ ] Code review approved

## Dependencies

**None** - This is the foundation.

## Related Tasks

- Task 1.2: Parser infrastructure (will read into these models)
- Task 1.3: Registry discovery (will load these models from files)
- All builder tasks (will use these models as input)

---

**Related Documents:**
- Story: `docs/features/stories/story_1_foundation.md`
- Comprehensive: `docs/PHASE2A_FEATURES_STORIES_TASKS.md` (Task 1.1 section)
- Feature: `docs/features/FEATURE_001_...md`
