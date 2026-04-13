# Visual Diagrams & Flows

Comprehensive visual documentation for Promptosaurus workflows.

## Table of Contents

- [Workflow Diagrams](#workflow-diagrams)
- [CLI Interaction Flows](#cli-interaction-flows)
- [Data Flow Diagrams](#data-flow-diagrams)
- [Configuration Flow](#configuration-flow)
- [Agent Discovery Flow](#agent-discovery-flow)
- [Builder Selection Flow](#builder-selection-flow)

---

## Workflow Diagrams

### Complete Promptosaurus Setup Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Runs CLI                            │
│                  promptosaurus init                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Select AI Assistant Tool                             │
│  (Kilo IDE, Kilo CLI, Cline, Cursor, Copilot)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Choose Repository Type                               │
│  (single-language or multi-language-monorepo)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Select Prompt Variant                                │
│  (minimal for efficiency or verbose for detail)             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Choose Active Personas                               │
│  (filters which agents are generated)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│    Answer Language-Specific Questions                        │
│  (runtime, package manager, testing framework, etc.)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Generate Tool-Specific Configurations                       │
│  (.kilo/, .clinerules, .cursor/, etc.)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Configuration Complete ✓                             │
│    Ready to use with AI Assistant                            │
└─────────────────────────────────────────────────────────────┘
```

---

## CLI Interaction Flows

### Init Command Flow

```
promptosaurus init
    │
    ├─ Step 1: Select AI Tool
    │   Options: Kilo IDE, Kilo CLI, Cline, Cursor, Copilot
    │   │
    │   └─ ✓ Selected: Kilo IDE
    │
    ├─ Step 2: Repository Type
    │   Options: single-language, multi-language-monorepo
    │   │
    │   └─ ✓ Selected: single-language
    │
    ├─ Step 3: Prompt Variant
    │   Options: minimal, verbose
    │   │
    │   └─ ✓ Selected: minimal
    │
    ├─ Step 4: Choose Personas
    │   Options: Multiple selection of roles
    │   │
    │   └─ ✓ Selected: software_engineer, qa_tester
    │
    ├─ Step 5: Language Questions
    │   (Python/TypeScript/Go/etc specific)
    │   ├─ Runtime version
    │   ├─ Package manager
    │   ├─ Testing framework
    │   └─ ... more options
    │   │
    │   └─ ✓ All answers collected
    │
    ├─ Save Configuration
    │   │
    │   └─ ✓ .promptosaurus.yaml created
    │
    └─ Generate Tool Outputs
        ├─ .kilo/agents/code.md
        ├─ .kilo/agents/test.md
        ├─ .kilo/agents/review.md
        ├─ .kilo/agents/...
        │
        └─ ✓ Setup complete!
```

### Switch Command Flow

```
Current State: .promptosaurus.yaml exists

promptosaurus switch
    │
    ├─ Check Configuration ✓
    │
    ├─ Select New Tool (interactive menu)
    │   Options: Kilo IDE, Kilo CLI, Cline, Cursor, Copilot
    │   │
    │   └─ ✓ Selected: Cline
    │
    ├─ Generate Cline Configuration
    │   │
    │   └─ ✓ .clinerules created
    │
    └─ ✓ Tool switch complete!
       (Keep existing .promptosaurus.yaml, now have both .kilo/ and .clinerules)
```

### Swap Command Flow

```
Current State: .promptosaurus.yaml exists with personas

promptosaurus swap
    │
    ├─ Check Configuration ✓
    │
    ├─ Select New Personas (interactive menu)
    │   Current: software_engineer, qa_tester
    │   Available: All personas
    │   │
    │   └─ ✓ Selected: software_engineer, devops_engineer, architect
    │
    ├─ Update Configuration
    │   .promptosaurus.yaml: active_personas = [software_engineer, devops_engineer, architect]
    │   │
    │   └─ ✓ Configuration updated
    │
    ├─ Regenerate All Outputs
    │   (with new persona filter applied)
    │   │
    │   └─ ✓ Agents regenerated for selected personas
    │
    └─ ✓ Persona swap complete!
```

---

## Data Flow Diagrams

### Agent Discovery and Build Flow

```
┌─────────────────────────────────────────────────────┐
│          Scan agents/ Directory                      │
│                                                     │
│  agents/                                            │
│  ├── code/                                         │
│  │   ├── minimal/prompt.md                         │
│  │   └── verbose/prompt.md                         │
│  ├── test/                                         │
│  │   └── minimal/prompt.md                         │
│  └── debug/                                        │
│      └── subagents/                                │
│          ├── rubber-duck/minimal/prompt.md         │
│          └── root-cause/minimal/prompt.md          │
└────────────┬──────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│     ComponentLoader Loads Files                      │
│  - YAML Frontmatter (metadata)                      │
│  - Markdown Content (system prompt)                 │
│  - Skills (optional)                               │
│  - Workflows (optional)                            │
└────────────┬──────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│   Parsers Extract Structured Data                    │
│  - YAMLParser: frontmatter → dict                   │
│  - MarkdownParser: sections → dict                  │
└────────────┬──────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│   Create Agent IR Models (Pydantic)                 │
│  - Validate with type hints                         │
│  - Freeze (immutable)                               │
│  - Cache in Registry                                │
└────────────┬──────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│   PersonaFilter (optional)                           │
│  Filter agents by selected personas                 │
│  - Keep universal agents (always)                   │
│  - Include persona-specific agents                  │
└────────────┬──────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│  Builder Selects & Transforms Agent IR              │
│  - Select variant (minimal/verbose)                 │
│  - Apply template substitution                      │
│  - Format for target tool                           │
└────────────┬──────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│   Write Tool-Specific Configuration Files           │
│  - .kilo/agents/code.md                             │
│  - .clinerules                                      │
│  - .cursor/rules/                                   │
│  - .github/copilot-instructions.md                  │
└─────────────────────────────────────────────────────┘
```

### Template Substitution Flow

```
Configuration (.promptosaurus.yaml)
    ├── language: "python"
    ├── runtime: "3.12"
    ├── package_manager: "uv"
    └── testing_framework: "pytest"
         │
         ▼
    ┌────────────────────────────┐
    │  Template String            │
    │  from Agent Prompt File:    │
    │  "Use {{LANGUAGE}}"         │
    │  "Runtime: {{RUNTIME}}"     │
    │  "Package: {{PACKAGE_MG}}"  │
    │  "Test: {{TESTING_FRAME}}"  │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │  TemplateHandler Chain      │
    │  ├─ LanguageHandler         │
    │  ├─ RuntimeHandler          │
    │  ├─ PackageManagerHandler   │
    │  └─ TestingFrameworkHandler │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │ Jinja2 Renderer            │
    │ - Variable substitution    │
    │ - Conditional logic        │
    │ - Custom filters           │
    │ - Error recovery           │
    └────────────┬───────────────┘
                 │
                 ▼
    ┌────────────────────────────┐
    │  Final Output              │
    │  "Use python"              │
    │  "Runtime: 3.12"           │
    │  "Package: uv"             │
    │  "Test: pytest"            │
    └────────────────────────────┘
```

---

## Configuration Flow

### Single-Language Setup

```
Repository Type: single-language

Config Generated:
    version: "1.0"
    repository:
      type: "single-language"
    spec:
      language: "python"
      runtime: "3.12"
      package_manager: "uv"
      testing_framework: "pytest"
      linter: ["ruff"]
      formatter: ["black"]
      (+ all other settings)
    variant: "minimal"
    active_personas: ["software_engineer", "qa_tester"]
```

### Multi-Language Monorepo Setup

```
Repository Type: multi-language-monorepo

Config Generated:
    version: "1.0"
    repository:
      type: "multi-language-monorepo"
    spec:
      - folder: "backend/api"
        type: "backend"
        subtype: "api"
        language: "python"
        runtime: "3.12"
        (+ python-specific settings)
      
      - folder: "frontend"
        type: "frontend"
        subtype: "ui"
        language: "typescript"
        runtime: "5.4"
        (+ typescript-specific settings)
      
      - folder: "shared/lib"
        type: "library"
        subtype: "shared"
        language: "typescript"
        runtime: "5.4"
        (+ typescript-specific settings)
    
    variant: "verbose"
    active_personas: ["software_engineer", "devops_engineer"]
```

---

## Agent Discovery Flow

```
┌──────────────────────────────┐
│ RegistryDiscovery            │
│ Scans: promptosaurus/agents/ │
└─────────────┬────────────────┘
              │
              ▼
    ┌─────────────────────────┐
    │ For each agent_name/:   │
    │ ├─ Look for minimal/    │
    │ ├─ Look for verbose/    │
    │ └─ Select variant       │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Load prompt.md          │
    │ (required)              │
    │ ├─ YAML frontmatter     │
    │ └─ Markdown body        │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Load optional files:    │
    │ ├─ skills.md           │
    │ └─ workflow.md         │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Create Agent IR         │
    │ (immutable model)       │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Look for subagents/     │
    │ (recursive discovery)   │
    └──────────┬──────────────┘
               │
               ▼
    ┌─────────────────────────┐
    │ Cache in Registry       │
    │ (with variant index)    │
    └─────────────────────────┘
```

---

## Builder Selection Flow

```
┌──────────────────────────────────┐
│ User selects tool during init    │
│ (Kilo IDE, Cline, Cursor, etc.)  │
└─────────────┬────────────────────┘
              │
              ▼
    ┌─────────────────────────────┐
    │ BuilderFactory.get_builder() │
    │ ("kilo-ide")                │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Returns:                    │
    │ KiloBuilder instance        │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ builder.build(agent, opts)  │
    │ ├─ Validate agent           │
    │ ├─ Build YAML frontmatter   │
    │ ├─ Build prompt section     │
    │ ├─ Build skills section     │
    │ ├─ Build workflows section  │
    │ └─ Compose markdown output  │
    └──────────┬──────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Output for Kilo:            │
    │ ├─ .kilo/agents/code.md    │
    │ ├─ .kilo/agents/test.md    │
    │ ├─ .kilo/agents/review.md  │
    │ └─ ... (per selected agent) │
    └─────────────────────────────┘
```

---

## Tool Output Locations

```
Tool Selection → Output Location

Kilo IDE        → .kilo/agents/
                  ├── code.md
                  ├── test.md
                  ├── review.md
                  ├── refactor.md
                  ├── document.md
                  └── ... (agent-specific)

Kilo CLI        → .opencode/rules/
                  ├── always-on.md
                  └── modes.md

Cline           → .clinerules (single file)

Cursor          → .cursor/rules/
                  ├── code.mdc
                  ├── test.mdc
                  └── ...
                  + .cursorrules (legacy)

GitHub Copilot  → .github/copilot-instructions.md
```

---

## Reference

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed component documentation
- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Step-by-step guide
- [ADVANCED_CONFIGURATION.md](./ADVANCED_CONFIGURATION.md) - Configuration reference

