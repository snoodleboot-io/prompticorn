# Agent Skills & Workflows Implementation Plan

## Problem Analysis

### Current System Architecture

1. **Agent Source Files** (`prompticorn/agents/{agent}/prompt.md`):
   - Contain ONLY: name, description, mode, permissions
   - Do NOT contain: skills or workflows

2. **Language Mapping** (`language_skill_mapping.yaml`):
   - Maps LANGUAGES (python, typescript, etc.) to skills/workflows
   - Has some language+agent combinations (e.g., `python/code`, `python/test`)
   - The `python` entry currently lists ALL 36 skills and ALL 66 workflows

3. **Build Process** (`prompticorn/prompt_builder.py`):
   - Method `_filter_agent_for_language()` loads language_skill_mapping.yaml
   - Creates a FILTERED Agent IR model with skills/workflows from the mapping
   - Passes filtered Agent to builder (KiloBuilder, ClaudeBuilder, etc.)
   - Builder outputs the skills/workflows from the Agent IR model

### Root Cause

The `python` entry in `language_skill_mapping.yaml` (lines 27-139) lists:
- **ALL 36 skills** (lines 28-67)
- **ALL 66 workflows** (lines 68-139)

When ANY agent is built with `language=python`, it gets all these skills/workflows.

The language+agent combinations (e.g., `python/code`, `python/architect`) exist but are INCOMPLETE - they only have a few skills/workflows each, not the full set needed for each agent.

---

## Solution Options

### Option 1: Update language_skill_mapping.yaml (NOT RECOMMENDED)

**Approach**: Modify the existing `language_skill_mapping.yaml` to have complete agent-specific mappings.

**Changes Required**:

1. **Remove global python skills/workflows**:
   - Delete lines 28-139 (the massive `python:` entry)

2. **Add complete agent-specific mappings**:
   - Add `python/architect`, `python/code`, `python/ask`, etc. for ALL 25 agents
   - Repeat for `typescript/architect`, `typescript/code`, etc.
   - Repeat for `javascript/architect`, `javascript/code`, etc.
   - Repeat for ALL languages (7+ languages × 25 agents = **175+ entries**)

**Example of duplication**:
```yaml
python/architect:
  skills:
    - architecture-documentation
    - data-model-discovery
    - mermaid-erd-creation
    # ... 5 more
  workflows:
    - scaffold-workflow
    - data-model-workflow
    # ... 4 more

typescript/architect:
  skills:
    - architecture-documentation   # DUPLICATE
    - data-model-discovery          # DUPLICATE
    - mermaid-erd-creation          # DUPLICATE
    # ... 5 more (all duplicates)
  workflows:
    - scaffold-workflow             # DUPLICATE
    - data-model-workflow           # DUPLICATE
    # ... 4 more (all duplicates)

javascript/architect:
  skills:
    - architecture-documentation   # DUPLICATE
    - data-model-discovery          # DUPLICATE
    # ... (SAME DUPLICATES AGAIN)

# ... repeat for go, rust, java, csharp = MASSIVE DUPLICATION
```

**Pros**:
- Uses existing infrastructure
- No new code required

**Cons**:
- ❌ **MASSIVE DUPLICATION**: 175+ near-identical entries (7 languages × 25 agents)
- ❌ **Maintenance nightmare**: Updating architect skills requires changing 7+ entries
- ❌ **Error-prone**: Easy to have inconsistencies across languages
- ❌ **Doesn't make logical sense**: architect skills are language-agnostic

---

### Option 2: Create agent_skill_mapping.yaml (RECOMMENDED)

**Approach**: Create a new `agent_skill_mapping.yaml` that maps agents directly (language-agnostic).

**Rationale**: 
- Most skills/workflows are **agent-specific**, NOT **language-specific**
- The `architect` agent needs the same skills whether working on Python, TypeScript, or Go
- The `security` agent needs the same security skills regardless of language
- Only a few edge cases might need language-specific overrides (handled via language_skill_mapping.yaml)

**Changes Required**:

#### 1. Create new file `agent_skill_mapping.yaml`:
```yaml
# Agent-Skill-Workflow Mapping Registry
# Maps agents to their skills and workflows (language-agnostic)
# Language-specific overrides can be added in language_skill_mapping.yaml

architect:
  skills:
    - architecture-documentation
    - data-model-discovery
    - mermaid-erd-creation
    - technical-decision-making
    - problem-decomposition
    - feature-planning
    - technical-communication
    - post-implementation-checklist
  workflows:
    - scaffold-workflow
    - data-model-workflow
    - decision-log-workflow
    - architecture-documentation
    - task-breakdown-workflow
    - strategy-workflow

code:
  skills:
    - feature-planning
    - incremental-implementation
    - code-review-practices
    - test-coverage-categories
    - post-implementation-checklist
    - technical-debt-management
    - quality-assurance
  workflows:
    - code-workflow
    - feature-workflow
    - boilerplate-workflow
    - house-style-workflow
    - refactor-workflow
    - testing-workflow

security:
  skills:
    - code-review-practices
    - quality-assurance
    - technical-decision-making
    - problem-decomposition
  workflows:
    - security-hardening-checklist
    - threat-modeling-workflow
    - vulnerability-scanning-workflow
    - security-testing-workflow
    - security-code-review
    - penetration-testing-guide
    - workflow-security-in-workflows

# ... all 25 agents (ONE entry per agent, not duplicated per language)
```

#### 2. Create new loader `AgentSkillMappingLoader`:

Location: `prompticorn/ir/loaders/agent_skill_mapping_loader.py`

```python
class AgentSkillMappingLoader:
    """Loads agent to skills/workflows mapping from YAML registry.
    
    Provides resolution of which skills and workflows apply to a given agent.
    Language-agnostic - same skills/workflows apply regardless of language.
    """
    
    def __init__(self, mapping_file: Path | str = "agent_skill_mapping.yaml"):
        self.mapping_file = Path(mapping_file)
        if not self.mapping_file.exists():
            raise FileNotFoundError(f"Mapping file not found: {self.mapping_file}")
        self._mapping = None
    
    @property
    def mapping(self) -> dict:
        if self._mapping is None:
            with open(self.mapping_file, encoding="utf-8") as f:
                self._mapping = yaml.safe_load(f) or {}
        return self._mapping
    
    def get_skills_for_agent(self, agent_name: str) -> list[str]:
        """Get skills for an agent.
        
        Args:
            agent_name: Agent name (e.g., 'code', 'architect')
        
        Returns:
            List of skill names for this agent
        """
        if agent_name in self.mapping and "skills" in self.mapping[agent_name]:
            return self.mapping[agent_name]["skills"]
        return []
    
    def get_workflows_for_agent(self, agent_name: str) -> list[str]:
        """Get workflows for an agent.
        
        Args:
            agent_name: Agent name (e.g., 'code', 'architect')
        
        Returns:
            List of workflow names for this agent
        """
        if agent_name in self.mapping and "workflows" in self.mapping[agent_name]:
            return self.mapping[agent_name]["workflows"]
        return []
```

#### 3. Update `prompt_builder.py`:

```python
# Add to __init__:
self.agent_skill_loader = AgentSkillMappingLoader("agent_skill_mapping.yaml")

# Update _filter_agent_for_language method:
def _filter_agent_for_language(
    self, agent: Agent, language: Optional[str], agent_name: Optional[str] = None
) -> Agent:
    """Filter agent skills/workflows based on agent and language.
    
    Priority resolution:
    1. agent_skill_mapping.yaml - Agent-specific (language-agnostic)
    2. language_skill_mapping.yaml - Language+agent overrides
    3. Original agent skills/workflows (if no mappings found)
    """
    # Get agent-level skills/workflows (language-agnostic)
    agent_skills = self.agent_skill_loader.get_skills_for_agent(agent.name)
    agent_workflows = self.agent_skill_loader.get_workflows_for_agent(agent.name)
    
    # Get language-specific overrides (if any)
    if language and self.language_skill_loader:
        subagent_path = agent_name if agent_name and "/" in agent_name else None
        language_skills = self.language_skill_loader.get_skills_for_language(
            language, subagent=subagent_path
        )
        language_workflows = self.language_skill_loader.get_workflows_for_language(
            language, subagent=subagent_path
        )
        
        # Merge: agent mapping + language overrides
        # Language overrides take precedence if they exist
        final_skills = language_skills if language_skills else agent_skills
        final_workflows = language_workflows if language_workflows else agent_workflows
    else:
        # No language specified, use agent mapping only
        final_skills = agent_skills
        final_workflows = agent_workflows
    
    # Create filtered Agent IR model
    return Agent(
        name=agent.name,
        description=agent.description,
        mode=agent.mode,
        system_prompt=agent.system_prompt,
        tools=agent.tools,
        skills=final_skills,
        workflows=final_workflows,
        subagents=agent.subagents,
        permissions=agent.permissions,
    )
```

#### 4. Clean up `language_skill_mapping.yaml`:

```yaml
# Remove the massive python: entry (lines 27-139)
# Remove python/code, python/test, etc. (now handled by agent_skill_mapping.yaml)
# Keep ONLY language-specific overrides (if any exist)

# Example: IF a language has unique needs, keep those
# But for most cases, the agent mapping is sufficient

all:
  skills: []  # No global defaults, handled by agent mapping
  workflows: []
```

**Pros**:
- ✅ **Zero duplication**: One entry per agent (25 entries total, not 175+)
- ✅ **Language-agnostic**: Same skills for architect whether Python, TypeScript, or Go
- ✅ **Easy to maintain**: Update architect skills in ONE place
- ✅ **Logically correct**: Skills are tied to agent role, not language
- ✅ **Flexible**: Can still add language-specific overrides if needed via language_skill_mapping.yaml

**Cons**:
- Requires new loader class (~100 lines of code)
- Requires updating prompt_builder.py (~30 lines changed)
- New file to maintain

---

## Recommended Implementation: Option 2

**Rationale**:
1. **Skills are agent-centric, not language-centric**: The `architect` agent needs architecture skills regardless of language
2. **Eliminates massive duplication**: 25 entries instead of 175+
3. **Maintainability**: Update skills in ONE place instead of 7+ places
4. **Separation of concerns**: Agent responsibilities vs language specifics
5. **Follows DRY principle**: Don't Repeat Yourself

**When to use each mapping**:
- `agent_skill_mapping.yaml`: Default skills/workflows for each agent (language-agnostic)
- `language_skill_mapping.yaml`: Language-specific overrides (rare, only when needed)

---

## Implementation Steps

### Step 1: Create agent_skill_mapping.yaml

Using the mappings from `planning/current/skill_mappings.json` and `planning/current/workflow_mappings.json`:

1. Create new file `agent_skill_mapping.yaml` at project root
2. Add header documentation explaining purpose
3. For each of the 25 agents:
   - Add `{agent}:` section
   - Add `skills:` with the agent's skills from skill_mappings.json
   - Add `workflows:` with the agent's workflows from workflow_mappings.json
4. Total: 25 agent entries (not 175+)

**Script**: `scripts/generate_agent_mapping.py`

### Step 2: Create AgentSkillMappingLoader

1. Create `prompticorn/ir/loaders/agent_skill_mapping_loader.py`
2. Implement loader class (similar to LanguageSkillMappingLoader)
3. Add unit tests in `tests/unit/ir/test_agent_skill_mapping_loader.py`
4. Update `prompticorn/ir/loaders/__init__.py` to export new loader

### Step 3: Update prompt_builder.py

1. Import `AgentSkillMappingLoader`
2. Add `self.agent_skill_loader` to `__init__`
3. Update `_filter_agent_for_language()` to use agent mapping first
4. Implement priority resolution: agent_mapping > language_mapping > original

### Step 4: Clean up language_skill_mapping.yaml

1. Remove `python:` section (lines 27-139)
2. Remove `python/code`, `python/test`, etc. (now redundant)
3. Keep only true language-specific overrides (if any)
4. Update header comments to explain new structure

### Step 5: Verify & Test

1. Run build command: `uv run prompt build kilo`
2. Check `.kilo/agents/*.md` files
3. Verify each agent has ONLY its assigned skills/workflows
4. Compare to `planning/current/PROPOSED_SKILLS_WORKFLOWS_MAPPING.md`
5. Test with different languages (python, typescript, go)
6. Ensure all languages get same skills per agent

### Step 6: Update Documentation

1. Document the two-tier system in README
2. Add examples of when to use agent_skill_mapping vs language_skill_mapping
3. Create migration guide for adding new agents
4. Update contributing guidelines

---

## Resolution Priority (Final Design)

When building an agent, skills/workflows are resolved in this order:

1. **agent_skill_mapping.yaml**: Base skills for agent (e.g., `architect: [8 skills]`)
2. **language_skill_mapping.yaml override**: IF language-specific entry exists (rare)
3. **Fallback**: Original agent.skills/workflows (if no mappings found)

**Example**:
```yaml
# agent_skill_mapping.yaml
architect:
  skills:
    - architecture-documentation
    - data-model-discovery
    - mermaid-erd-creation
    # ... 5 more (applies to ALL languages)

# language_skill_mapping.yaml (only if override needed)
rust/architect:
  skills:
    - architecture-documentation
    - data-model-discovery
    - mermaid-erd-creation
    - rust-specific-skill  # ONLY added for Rust architect
```

---

## Questions for User

1. **Approve Option 2?** Creating `agent_skill_mapping.yaml` as the primary mapping system?
2. **Loader location**: `prompticorn/ir/loaders/agent_skill_mapping_loader.py` - correct?
3. **File location**: `agent_skill_mapping.yaml` at project root (prompticorn/configurations/ directory) - correct?
4. **Backwards compatibility**: The existing `python/code`, `python/test` entries in language_skill_mapping.yaml will be removed. Is this acceptable?
5. **Validation**: Should we add validation to ensure every agent (all 25) has an entry in agent_skill_mapping.yaml?
6. **Language overrides**: Can you think of any cases where a language WOULD need different skills for the same agent? (If not, we can remove language-specific agent entries entirely)

---

## File Outputs (if approved)

### New Files:
1. **`agent_skill_mapping.yaml`** - 25 agent entries with skills/workflows
2. **`prompticorn/ir/loaders/agent_skill_mapping_loader.py`** - Loader class
3. **`tests/unit/ir/test_agent_skill_mapping_loader.py`** - Unit tests
4. **`scripts/generate_agent_mapping.py`** - Generator script
5. **`scripts/validate_agent_mappings.py`** - Validation script

### Modified Files:
1. **`prompticorn/prompt_builder.py`** - Add agent_skill_loader, update filtering logic
2. **`prompticorn/ir/loaders/__init__.py`** - Export new loader
3. **`language_skill_mapping.yaml`** - Remove python section, clean up redundant entries
4. **`README.md`** - Document the two-tier mapping system

### Documentation:
1. **Migration guide** - How to add new agents
2. **Architecture decision record** - Why we chose this approach
3. **Examples** - When to use agent_mapping vs language_mapping

