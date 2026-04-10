# Phase 2 Architecture Summary

**Status:** Design Complete ✅  
**Date:** 2026-04-08  
**Commits:** `52decd6` (Phase 2 SOLID architecture with IR models, builders, minimal/verbose strategy)

---

## WHAT WE ALIGNED ON

### 1. ✅ SOLID Registry Architecture
- **IR (Intermediate Representation)**: Promptosaurus configs are the universal language
- **Adapters**: Each tool gets a builder that translates IR → tool-native format
- **Single Source of Truth**: Write once in Promptosaurus, deploy to any tool
- **No Factory Nesting**: Use sweet_tea directly (max power, min complexity)

### 2. ✅ Interface Segregation with Mixins
```
PromptosaurusBuilder (base - all tools implement)
├── SupportsSkills (Kilo, Copilot, Claude)
├── SupportsWorkflows (Kilo, Copilot, Claude)
├── SupportsHooks (Copilot only)
└── SupportsRules (Kilo, Cursor, Cline)
```
Tools only implement what they support. Liskov-compliant.

### 3. ✅ Minimal/Verbose Strategy (Built Into IR)
**Dual fields in every content model:**
- `prompt` + `prompt_verbose` (Agent)
- `instructions` + `instructions_verbose` (Skill)
- `steps` (implied minimal/verbose) (Workflow)

**How it works:**
- Users define both minimal and verbose in YAML
- IR models have `get_prompt(verbose: bool)` methods
- Builders call `get_prompt(verbose=False)` for production use
- Phase 2B can add auto-expansion (minimal → verbose via LLM)

### 4. ✅ Pydantic Validation (IR Parser + Builders)
```
User Input (YAML/Markdown)
    ↓ [PromptosaurusParser]
Pydantic Models (validates)
    ↓ [BuilderFactory.create()]
Tool-Specific Builder
    ↓ [builder.validate_agent()]
Tool-native format
```

**Validation happens twice:**
1. **Parser**: Pydantic ensures IR is structurally valid
2. **Builder**: Tool-specific constraints (e.g., Kilo requires snake_case names)

### 5. ✅ Sweet_Tea Factory (Following Existing Patterns)
```python
# Register implementations
Registry.register("kilo", KiloBuilder, library="promptosaurus")
Registry.register("copilot", CopilotBuilder, library="promptosaurus")
# ... etc

# Get builder at runtime
builder = BuilderFactory.create("kilo")  # Returns PromptosaurusBuilder

# Use it (same interface for all tools)
built = builder.build_agent(ir_agent)
```

**Why sweet_tea?** It handles registry, lifecycle, DI. Don't wrap it.

### 6. ✅ All 6 Tools Supported
| Tool | Supported | Builder Complexity | Status |
|------|-----------|-------------------|--------|
| Kilo | ✅ Yes | High (all features) | Documented |
| Copilot | ✅ Yes | Medium-High (skills + hooks) | Documented |
| Cursor | ✅ Yes | Low (rules only) | Documented |
| Cline | ✅ Yes | Unknown (bundled skills) | Documented |
| Claude | ✅ Yes | Medium (system_prompt + tools) | Partially documented |

---

## WHAT WE DESIGNED

### Core Pydantic IR Models
```python
PromptosaurusAgent(
    name: str,
    description: str,
    prompt: str,
    prompt_verbose: Optional[str],
    skills: List[str],
    tags: List[str],
)

PromptosaurusSkill(
    name: str,
    description: str,
    instructions: str,
    instructions_verbose: Optional[str],
    scope: str,  # shared | per-agent | bundled
    tags: List[str],
)

PromptosaurusWorkflow(
    name: str,
    description: str,
    steps: List[str],
    target_tools: List[str],
)

PromptosaurusRules(
    name: str,
    description: str,
    file_pattern: Optional[str],
    scope: str,  # global | per-agent | per-file
    instructions: str,
)

PromptosaurusProject(
    agents: List[PromptosaurusAgent],
    skills: List[PromptosaurusSkill],
    workflows: List[PromptosaurusWorkflow],
    rules: List[PromptosaurusRules],
)
```

### Builder Interface (SOLID)
```python
class PromptosaurusBuilder(ABC):
    @abstractmethod
    def build_agent(self, agent: PromptosaurusAgent) -> dict:
        """IR → tool-native agent"""
        pass
    
    @abstractmethod
    def validate_agent(self, agent: PromptosaurusAgent) -> list[str]:
        """Validate against tool constraints"""
        pass
    
    @property
    @abstractmethod
    def tool_name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def supported_features(self) -> dict[str, bool]:
        """Which capabilities this tool supports"""
        pass
```

Plus mixin protocols:
- `SupportsSkills` (build_skill, validate_skill)
- `SupportsWorkflows` (build_workflow)
- `SupportsHooks` (build_hook)
- `SupportsRules` (build_rules)

### Parser
```python
class PromptosaurusParser:
    @staticmethod
    def parse_file(path: Path) -> PromptosaurusAgent:
        """YAML/Markdown → PromptosaurusAgent (with Pydantic validation)"""
        pass
    
    @staticmethod
    def parse_project(root: Path) -> PromptosaurusProject:
        """Load entire project → PromptosaurusProject"""
        pass
```

### Factory
```python
class BuilderFactory:
    @staticmethod
    def create(tool_name: str) -> PromptosaurusBuilder:
        """Get builder for tool (via sweet_tea)"""
        pass
    
    @staticmethod
    def list_tools() -> list[str]:
        """Available tools"""
        pass
```

---

## FILE STRUCTURE (TO BE CREATED)

```
promptosaurus/
├── models/
│   ├── __init__.py
│   ├── agent.py
│   ├── skill.py
│   ├── workflow.py
│   ├── rules.py
│   └── project.py
├── parser/
│   ├── __init__.py
│   ├── parser.py
│   └── loaders.py
├── builders/
│   ├── __init__.py
│   ├── interface.py      # Base + mixins
│   ├── factory.py        # sweet_tea registration
│   ├── kilo.py
│   ├── copilot.py
│   ├── cursor.py
│   ├── cline.py
│   └── claude_api.py
└── tests/
    ├── unit/
    │   ├── models/
    │   ├── parser/
    │   └── builders/
    └── integration/
```

---

## IMPLEMENTATION ROADMAP (7 WEEKS)

### Week 1: Foundation
- [ ] Pydantic IR models (Agent, Skill, Workflow, Rules, Project)
- [ ] Add minimal/verbose fields + get_*() methods
- [ ] YAML examples for all model types
- [ ] Pydantic validation tests

### Week 2: Parser & Factory
- [ ] PromptosaurusParser (YAML → IR)
- [ ] BuilderFactory with sweet_tea registration
- [ ] Parser roundtrip tests
- [ ] Factory instantiation tests

### Week 3: KiloBuilder
- [ ] Implement KiloBuilder (highest priority)
- [ ] build_agent() → .kilo/agents/name.md
- [ ] Validation (snake_case names, skill existence, etc.)
- [ ] Test: IR → valid Kilo structure

### Week 4: CopilotBuilder
- [ ] Research Copilot Agent API
- [ ] Implement CopilotBuilder (skills + hooks)
- [ ] Test: IR → valid Copilot API format
- [ ] Test: skill IR → per-agent skill attachment

### Week 5: ClaudeBuilder (API)
- [ ] Complete Claude API research (tools, workflows, etc.)
- [ ] Implement ClaudeAPIBuilder (system_prompt + tools)
- [ ] Test: IR → valid Claude API call
- [ ] Test: skill IR → Claude tool JSON schema

### Week 6: CursorBuilder + ClaudeBuilder (Cline)
- [ ] Implement CursorBuilder (rules)
- [ ] Implement ClaudeBuilder (directory-based)
- [ ] Full test coverage

### Week 7: Validation & Documentation
- [ ] Comprehensive validation tests
- [ ] IR model documentation
- [ ] Builder capability matrix
- [ ] Example projects

---

## KEY BENEFITS

✅ **SOLID Principles**: Each principle properly applied  
✅ **Extensible**: Add new tool without modifying existing builders  
✅ **Type-Safe**: Pydantic validates IR structure  
✅ **Dual Validation**: Parser + Builder validation  
✅ **Minimal/Verbose Built-In**: Dual fields, not post-processing  
✅ **Tool-Agnostic**: Single source, many targets  
✅ **Sweet_Tea Power**: Direct use, no nesting  
✅ **Interface Segregation**: Tools implement only what they need  

---

## STILL TO RESEARCH

### Claude API
1. Tool definition format (JSON schema required?)
2. Tool calling workflow (how Claude invokes tools)
3. Sessions/context management
4. Error handling for tool execution
5. Multi-turn conversations

### Cline
1. Explicit documentation on skills/workflows model
2. Exact structure of `.agents/skills/` and `.clinerules/`

### Cursor
1. Exact structure of rules
2. Can rules be agent-specific or global?

---

## DOCUMENTATION CREATED

1. **PHASE2_REGISTRY_ARCHITECTURE.md**: SOLID design, IR + adapter pattern, sweet_tea factory
2. **PHASE2A_IR_MODELS_AND_BUILDERS.md**: Pydantic models, builders, validation, implementation roadmap

Both in: `docs/ard/`

---

## NEXT STEPS

### If Starting Phase 2A Now
1. Review IR Pydantic models (finalize constraints)
2. Create models/ directory with BaseModel definitions
3. Create parser/ directory with PromptosaurusParser
4. Create builders/interface.py with base class + mixins
5. Register sweet_tea factory
6. Start KiloBuilder (highest priority)

### If Waiting for User Go-Ahead
- Documents are ready for implementation
- No blockers identified
- Architecture is SOLID and extensible
- 7-week roadmap is feasible

---

## BRANCH INFO

**Branch:** `feat/prompt-system-redesign`  
**Latest Commit:** `52decd6`  
**Changes:** Phase 2 architecture documentation (2 ADRs)  
**Status:** Ready for implementation review

