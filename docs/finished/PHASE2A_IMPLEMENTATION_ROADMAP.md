# Phase 2A Implementation Roadmap

**Status:** Ready to Begin  
**Execution Models Research:** 4/6 HIGH CONFIDENCE (complete for MVP)  
**IR Design:** Finalized (PHASE2A_IR_MODELS_AND_BUILDERS.md)  
**Builders Prioritized:** KiloBuilder, ClineBuilder, ClaudeBuilder  
**Timeline:** 6-8 weeks (estimated)  

---

## Executive Summary

Phase 2A builds the CORE infrastructure for unified agent management across 3 primary tools (Kilo, Cline, Claude). Phase 2B (later) adds Copilot, Cursor, and Kilo CLI.

**Phase 2A MVP Scope:**
- Pydantic IR models (agents, skills, workflows, rules)
- Parser (YAML/Markdown → Pydantic)
- Registry/Factory pattern (builder discovery)
- 3 initial builders: KiloBuilder, ClineBuilder, ClaudeBuilder
- Test suite with real file generation
- Documentation + examples

**Success Criteria:**
1. Parser correctly loads agents/skills from YAML
2. KiloBuilder writes `.kilocode/rules-{mode}/` structure
3. ClineBuilder writes `.agents/skills/` + focus chain config
4. ClaudeBuilder generates tool JSON schemas
5. All tests pass with 80%+ coverage
6. Real integration tests with actual file I/O

---

## Week-by-Week Implementation Plan

### Week 1: Foundation (Pydantic IR Models + Parser)

**Goal:** Establish IR models and parsing infrastructure

#### Week 1.1 - Monday-Tuesday (2 days)

**Task 1.1.1:** Implement Pydantic IR Models
- Location: `promptosaurus/models/`
- Files:
  - `agent.py` - PromptosaurusAgent model with get_prompt()
  - `skill.py` - PromptosaurusSkill model with get_instructions()
  - `workflow.py` - PromptosaurusWorkflow model
  - `rules.py` - PromptosaurusRules model
  - `project.py` - PromptosaurusProject (root model)
- Acceptance Criteria:
  - [ ] All models pass Pydantic validation
  - [ ] Dual fields (prompt/prompt_verbose) implemented
  - [ ] get_prompt(verbose=bool) methods work
  - [ ] JSON schema generation works (pydantic schema_json())
  - [ ] Unit tests for each model (happy path + validation errors)

**Task 1.1.2:** Create Parser Infrastructure
- Location: `promptosaurus/parsers/`
- Files:
  - `base.py` - ParserInterface (ABC)
  - `yaml_parser.py` - YAML parsing → Pydantic models
  - `markdown_parser.py` - Markdown frontmatter parsing
  - `validation.py` - Validation helpers
- Acceptance Criteria:
  - [ ] Parse YAML agent definitions
  - [ ] Parse YAML skill definitions
  - [ ] Handle validation errors gracefully
  - [ ] Tests for valid + invalid input

#### Week 1.2 - Wednesday-Thursday (2 days)

**Task 1.2.1:** Create Registry + Factory Pattern
- Location: `promptosaurus/registry/`
- Files:
  - `builder_registry.py` - BuilderRegistry (singleton)
  - `builder_factory.py` - BuilderFactory (creates builders)
  - `loader.py` - Discovers and registers builders
- Acceptance Criteria:
  - [ ] Registry registers builders by name
  - [ ] Factory creates builders with correct parameters
  - [ ] Auto-discovery of builder modules
  - [ ] Tests for registration and instantiation

**Task 1.2.2:** Define Builder Base Classes
- Location: `promptosaurus/builders/`
- Files:
  - `base.py` - PromptosaurusBuilder (ABC)
  - `interfaces.py` - Mixin protocols (SupportsSkills, SupportsWorkflows, etc)
  - `errors.py` - BuilderError, ValidationError
- Acceptance Criteria:
  - [ ] Abstract build_agent() method
  - [ ] Abstract validate_agent() method
  - [ ] Mixin protocols defined
  - [ ] Error hierarchy established

#### Week 1.3 - Friday (1 day + Buffer)

**Task 1.3.1:** Unit Tests + Integration Tests
- Location: `tests/unit/models/`, `tests/integration/parser/`
- Coverage:
  - [ ] Pydantic models: 90%+ coverage
  - [ ] Parser: 85%+ coverage
  - [ ] Registry/Factory: 80%+ coverage
- Real Testing:
  - [ ] Create test YAML files
  - [ ] Parse and validate
  - [ ] Verify Pydantic models match

**Deliverables (Week 1):**
- 5 Pydantic models (agent, skill, workflow, rules, project)
- Parser infrastructure (YAML + Markdown)
- Registry + Factory pattern
- 120+ unit tests (coverage 80%+)

---

### Week 2: KiloBuilder Implementation

**Goal:** Build and test KiloBuilder with real file I/O

#### Week 2.1 - Monday-Tuesday (2 days)

**Task 2.1.1:** Implement KiloBuilder Core
- Location: `promptosaurus/builders/kilo/`
- Files:
  - `kilo_builder.py` - Main KiloBuilder class
  - `agent_builder.py` - Agent → .kilocode/ directory
  - `skill_builder.py` - Skill → .kilocode/skills/
- Implementation:
  ```python
  # KiloBuilder extends PromptosaurusBuilder
  class KiloBuilder(PromptosaurusBuilder):
      def build_agent(self, agent: PromptosaurusAgent) -> dict:
          """Build agent → .kilocode/rules-{mode}/ structure"""
          # 1. Create directory: .kilocode/rules-{agent.slug}/
          # 2. Write: instructions.md (agent.get_prompt(verbose=False))
          # 3. Write: instructions-verbose.md (agent.get_prompt(verbose=True))
          # 4. Write: metadata.yaml (agent metadata)
          # 5. Return: {"path": "...", "files": [...]}
  ```
- Acceptance Criteria:
  - [ ] Agent directory created with correct structure
  - [ ] instructions.md contains minimal prompt
  - [ ] instructions-verbose.md contains detailed prompt
  - [ ] metadata.yaml written correctly
  - [ ] validate_agent() catches schema errors

#### Week 2.2 - Wednesday (1 day)

**Task 2.2.1:** Implement SupportsSkills Mixin for Kilo
- Implementation:
  - Extract skills from agent
  - Write skill files to `.kilocode/skills/{skill_name}/`
  - Format: `instructions.md` + `metadata.yaml`
- Acceptance Criteria:
  - [ ] Skills written to correct directory
  - [ ] Metadata properly formatted
  - [ ] validate_skill() checks for conflicts

#### Week 2.3 - Thursday-Friday (2 days)

**Task 2.3.1:** Real Integration Tests for KiloBuilder
- Location: `tests/integration/builders/kilo/`
- Tests:
  - [ ] Create test agent → write to temporary .kilocode/
  - [ ] Verify directory structure matches expected
  - [ ] Verify files are readable markdown
  - [ ] Verify metadata YAML is valid
  - [ ] Test skill extraction and writing
  - [ ] Test error handling (invalid paths, permissions)
- Real File System:
  - [ ] Use `tempfile` for isolated test directories
  - [ ] Actually write files
  - [ ] Verify with `os.path.exists()` + read content
  - [ ] Clean up in teardown

**Task 2.3.2:** KiloBuilder Documentation
- Files:
  - `docs/builders/KILO_BUILDER.md` - Usage guide
  - `docs/builders/examples/kilo-agent-example.yaml` - Example agent config
- Content:
  - How KiloBuilder works
  - Configuration options
  - Example YAML input
  - Expected output structure

**Deliverables (Week 2):**
- KiloBuilder (350 LOC)
- 40+ integration tests
- Real file I/O tests
- Documentation with examples

---

### Week 3: ClineBuilder Implementation

**Goal:** Build ClineBuilder with focus chain support

#### Week 3.1 - Monday-Tuesday (2 days)

**Task 3.1.1:** Implement ClineBuilder Core
- Location: `promptosaurus/builders/cline/`
- Files:
  - `cline_builder.py` - Main ClineBuilder
  - `agent_builder.py` - Agent → system prompt
  - `skill_builder.py` - Skill → .agents/skills/ + metadata
- Implementation:
  - Agent → System prompt (similar to Claude but with focus chain)
  - Skills → `.agents/skills/{skill_name}/SKILL.md`
  - Include: `SkillMetadata` interface
- Acceptance Criteria:
  - [ ] Agent generates system prompt with tools
  - [ ] Focus chain instructions included
  - [ ] Skills written to correct directory
  - [ ] Metadata matches Cline interface

#### Week 3.2 - Wednesday-Thursday (2 days)

**Task 3.2.1:** Implement Focus Chain Support
- Files:
  - `focus_chain_builder.py` - Focus chain configuration
  - `workflow_builder.py` - Workflow → .clinerules/workflows/
- Implementation:
  - Generate focus chain instructions
  - Configure reminder intervals
  - Write workflow toggle files
- Acceptance Criteria:
  - [ ] Focus chain instructions in system prompt
  - [ ] Reminder intervals configurable
  - [ ] Workflows written with toggles

#### Week 3.3 - Friday (1 day + Buffer)

**Task 3.3.1:** Integration Tests + Documentation
- Tests:
  - [ ] Agent → system prompt with focus chain
  - [ ] Skills → .agents/skills/ directory
  - [ ] Workflows → .clinerules/ directory
  - [ ] File watcher compatibility
- Documentation:
  - `docs/builders/CLINE_BUILDER.md`
  - Example configurations

**Deliverables (Week 3):**
- ClineBuilder (400 LOC)
- Focus chain integration
- 45+ integration tests
- Documentation

---

### Week 4: ClaudeBuilder + Base Infrastructure

**Goal:** Build ClaudeBuilder and foundational infrastructure

#### Week 4.1 - Monday-Tuesday (2 days)

**Task 4.1.1:** Implement ClaudeBuilder
- Location: `promptosaurus/builders/claude/`
- Files:
  - `claude_builder.py` - Agent → Claude API format
  - `tool_builder.py` - Skill → Tool JSON schema
- Implementation:
  ```python
  # Skills → Anthropic Tool format
  {
      "name": "skill_name",
      "description": "...",
      "input_schema": {
          "type": "object",
          "properties": {...},
          "required": [...]
      }
  }
  ```
- Acceptance Criteria:
  - [ ] Generate valid OpenAI/Anthropic tool schemas
  - [ ] Tool input validation
  - [ ] Error handling for invalid schemas

#### Week 4.2 - Wednesday-Thursday (2 days)

**Task 4.2.1:** CLI Tool + Management Scripts
- Location: `promptosaurus/cli/`
- Commands:
  - `promptosaurus build --agent agent.yaml --builder kilo`
  - `promptosaurus validate agent.yaml`
  - `promptosaurus list --type agents|skills|workflows`
  - `promptosaurus init --type project|agent|skill`
- Acceptance Criteria:
  - [ ] Commands work end-to-end
  - [ ] Error messages are clear
  - [ ] Help text complete

**Task 4.2.2:** Configuration Defaults
- Files:
  - `promptosaurus/config.py` - Default settings
  - `.promptosaurusrc` - User config template
- Content:
  - Default output directories
  - Verbose/minimal setting
  - Builder preferences
  - Tool configurations

#### Week 4.3 - Friday (1 day + Buffer)

**Task 4.3.1:** Documentation Completion
- Files created:
  - `docs/PHASE2A_GETTING_STARTED.md` - Quick start guide
  - `docs/builders/CLAUDE_BUILDER.md` - Claude builder docs
  - `docs/API.md` - Pydantic model API reference
- Content:
  - [ ] Installation instructions
  - [ ] Quick start examples
  - [ ] API reference
  - [ ] Troubleshooting guide

**Deliverables (Week 4):**
- ClaudeBuilder (250 LOC)
- CLI tool (150 LOC)
- Configuration system
- Comprehensive documentation

---

### Week 5: Testing, Integration, Polish

**Goal:** High test coverage, real integration scenarios, production readiness

#### Week 5.1 - Monday-Tuesday (2 days)

**Task 5.1.1:** Comprehensive Testing
- Unit tests:
  - [ ] All builders: 85%+ coverage
  - [ ] Parser/Registry: 85%+ coverage
  - [ ] Models: 90%+ coverage
  - Target total: 85%+ across codebase
- Integration tests:
  - [ ] Real file I/O with cleanup
  - [ ] Multi-builder workflows (agent + skills + workflows)
  - [ ] Error scenarios (invalid input, permissions, etc)
  - [ ] Tool compatibility verification

#### Week 5.2 - Wednesday-Thursday (2 days)

**Task 5.2.1:** End-to-End Scenarios
- Scenario 1: Feature implementation workflow
  - Create agent (architect) → create skill (feature-impl) → create workflow
  - Build all 3 builders (Kilo, Cline, Claude)
  - Verify outputs match expected structure
- Scenario 2: Multi-agent project
  - Create 5 agents (architect, code, test, review, debug)
  - Create shared skills (testing, documentation)
  - Build all builders
  - Verify no conflicts or overwrites

#### Week 5.3 - Friday (1 day + Buffer)

**Task 5.3.1:** Performance + Security
- Performance:
  - [ ] Parser handles 100+ agents in < 1s
  - [ ] Builder writes 100+ files in < 5s
  - [ ] No memory leaks on large projects
- Security:
  - [ ] Path traversal protection (no `../` in paths)
  - [ ] Permission checks for file writes
  - [ ] No secrets in generated files

**Deliverables (Week 5):**
- 85%+ test coverage across codebase
- 5+ end-to-end integration tests
- Performance benchmarks
- Security audit pass

---

### Week 6: Phase 2B Planning + Documentation

**Goal:** Prepare for Phase 2B (additional builders) and finalize Phase 2A

#### Week 6.1 - Monday (1 day)

**Task 6.1.1:** Phase 2A Release Preparation
- Files:
  - `PHASE2A_RELEASE_NOTES.md` - What's included, limitations
  - `PHASE2A_NEXT_STEPS.md` - Phase 2B planning
  - `CONTRIBUTING.md` - How to add new builders
- Content:
  - [ ] Summary of Phase 2A accomplishments
  - [ ] Known limitations (Copilot/Cursor not yet supported)
  - [ ] Phase 2B timeline and scope

#### Week 6.2 - Tuesday-Thursday (3 days)

**Task 6.2.1:** Phase 2B Architecture Design
- Document:
  - `docs/PHASE2B_ARCHITECTURE.md`
- Covers:
  - [ ] CopilotBuilder design (hook-based)
  - [ ] CursorBuilder design (instruction-based)
  - [ ] KiloCliBuilder design (step-based)
  - [ ] Estimated effort for each

#### Week 6.3 - Friday (1 day + Buffer)

**Task 6.3.1:** Retrospective + Lessons Learned
- File: `docs/PHASE2A_RETROSPECTIVE.md`
- Content:
  - [ ] What worked well
  - [ ] Challenges encountered
  - [ ] Recommendations for Phase 2B
  - [ ] Process improvements

**Deliverables (Week 6):**
- Phase 2A release documentation
- Phase 2B architecture design
- Contributing guide for new builders
- Retrospective document

---

## File Structure Summary

```
promptosaurus/
├── models/
│   ├── agent.py              # PromptosaurusAgent
│   ├── skill.py              # PromptosaurusSkill
│   ├── workflow.py           # PromptosaurusWorkflow
│   ├── rules.py              # PromptosaurusRules
│   └── project.py            # PromptosaurusProject
│
├── parsers/
│   ├── base.py               # ParserInterface
│   ├── yaml_parser.py        # YAML parsing
│   ├── markdown_parser.py    # Markdown parsing
│   └── validation.py         # Validation helpers
│
├── registry/
│   ├── builder_registry.py   # BuilderRegistry
│   ├── builder_factory.py    # BuilderFactory
│   └── loader.py             # Auto-discovery
│
├── builders/
│   ├── base.py               # PromptosaurusBuilder (ABC)
│   ├── interfaces.py         # Mixin protocols
│   ├── errors.py             # Error classes
│   ├── kilo/                 # KiloBuilder
│   │   ├── kilo_builder.py
│   │   ├── agent_builder.py
│   │   ├── skill_builder.py
│   │   └── workflow_builder.py
│   ├── cline/                # ClineBuilder
│   │   ├── cline_builder.py
│   │   ├── agent_builder.py
│   │   ├── skill_builder.py
│   │   ├── focus_chain_builder.py
│   │   └── workflow_builder.py
│   └── claude/               # ClaudeBuilder
│       ├── claude_builder.py
│       ├── tool_builder.py
│       └── schema_generator.py
│
├── cli/
│   ├── __main__.py           # Entry point
│   ├── commands/
│   │   ├── build.py          # Build command
│   │   ├── validate.py       # Validate command
│   │   ├── init.py           # Initialize command
│   │   └── list.py           # List command
│   └── config.py             # Configuration
│
└── tests/
    ├── unit/
    │   ├── models/           # Model tests
    │   ├── parsers/          # Parser tests
    │   ├── registry/         # Registry tests
    │   └── builders/         # Unit tests for builders
    └── integration/
        ├── builders/         # Integration tests with real I/O
        └── cli/              # CLI end-to-end tests
```

---

## Success Criteria (Phase 2A Complete)

- [ ] **IR Models:** 5 Pydantic models, 90%+ coverage
- [ ] **Parser:** YAML + Markdown parsing, 85%+ coverage
- [ ] **Registry:** Builder discovery and instantiation, 80%+ coverage
- [ ] **KiloBuilder:** Agent, Skill, Workflow support, real file I/O tests
- [ ] **ClineBuilder:** Agent, Skill, Focus chain, Workflow support
- [ ] **ClaudeBuilder:** Tool schema generation
- [ ] **CLI:** build, validate, init, list commands working
- [ ] **Tests:** 85%+ coverage, 100+ tests, E2E scenarios
- [ ] **Documentation:** API reference, builder guides, getting started
- [ ] **No regressions:** Existing Promptosaurus functionality unaffected

---

## Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|-----------|
| Builder validation too strict | Medium | Medium | Iterative testing with real projects |
| File I/O issues (permissions, paths) | Low | High | Early integration testing, edge case handling |
| Pydantic model changes | Low | Medium | Design finalized, minimal changes expected |
| Phase 2B scope creep | Medium | High | Document Phase 2A boundaries clearly |
| Builder interdependencies | Low | Medium | Mixin pattern isolates concerns |

---

## Next Steps

1. **Confirm scope and timeline** with stakeholders
2. **Set up test infrastructure** (pytest, coverage tools)
3. **Begin Week 1 implementation**
4. **Establish daily standup** for progress tracking
5. **Create Phase 2A project board** (GitHub Projects or similar)

