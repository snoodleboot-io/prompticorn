# Visual Diagrams & Flows

Comprehensive visual documentation for Promptosaurus workflows using Mermaid diagrams.

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

```mermaid
flowchart TD
    A["User Runs CLI<br/>promptosaurus init"] --> B["Select AI Assistant Tool<br/>(Kilo IDE, Kilo CLI, Cline, Cursor, Copilot)"]
    B --> C["Choose Repository Type<br/>(single-language or multi-language-monorepo)"]
    C --> D["Select Prompt Variant<br/>(minimal for efficiency or verbose for detail)"]
    D --> E["Choose Active Personas<br/>(filters which agents are generated)"]
    E --> F["Answer Language-Specific Questions<br/>(runtime, package manager, testing framework, etc.)"]
    F --> G["Generate Tool-Specific Configurations<br/>(.kilo/, .clinerules, .cursor/, etc.)"]
    G --> H["Configuration Complete ✓<br/>Ready to use with AI Assistant"]
    
    style A fill:#e1f5ff
    style H fill:#c8e6c9
```

---

## CLI Interaction Flows

### Init Command Flow

```mermaid
flowchart TD
    A["promptosaurus init"] --> B["Step 1: Select AI Tool"]
    B --> B1["Options: Kilo IDE, Kilo CLI, Cline, Cursor, Copilot"]
    B1 --> B2["✓ Selected: Kilo IDE"]
    
    B2 --> C["Step 2: Repository Type"]
    C --> C1["Options: single-language, multi-language-monorepo"]
    C1 --> C2["✓ Selected: single-language"]
    
    C2 --> D["Step 3: Prompt Variant"]
    D --> D1["Options: minimal, verbose"]
    D1 --> D2["✓ Selected: minimal"]
    
    D2 --> E["Step 4: Choose Personas"]
    E --> E1["Options: Multiple selection of roles"]
    E1 --> E2["✓ Selected: software_engineer, qa_tester"]
    
    E2 --> F["Step 5: Language Questions"]
    F --> F1["Python/TypeScript/Go specific"]
    F1 --> F2["Runtime version<br/>Package manager<br/>Testing framework<br/>...more options"]
    F2 --> F3["✓ All answers collected"]
    
    F3 --> G["Save Configuration"]
    G --> G1["✓ .promptosaurus/.promptosaurus.yaml created"]
    
    G1 --> H["Generate Tool Outputs"]
    H --> H1[".kilo/agents/code.md<br/>.kilo/agents/test.md<br/>.kilo/agents/review.md<br/>..."]
    H1 --> I["✓ Setup complete!"]
    
    style A fill:#e1f5ff
    style I fill:#c8e6c9
```

### Switch Command Flow

```mermaid
flowchart TD
    A["Current State: .promptosaurus/.promptosaurus.yaml exists"] --> B["promptosaurus switch"]
    B --> C["Check Configuration ✓"]
    C --> D["Select New Tool<br/>(interactive menu)"]
    D --> D1["Options: Kilo IDE, Kilo CLI, Cline, Cursor, Copilot"]
    D1 --> D2["✓ Selected: Cline"]
    
    D2 --> E["Generate Cline Configuration"]
    E --> E1["✓ .clinerules created"]
    
    E1 --> F["✓ Tool switch complete!<br/>(Keep existing .promptosaurus/.promptosaurus.yaml,<br/>now have both .kilo/ and .clinerules)"]
    
    style A fill:#fff3e0
    style F fill:#c8e6c9
```

### Swap Command Flow

```mermaid
flowchart TD
    A["Current State: .promptosaurus/.promptosaurus.yaml exists with personas"] --> B["promptosaurus swap"]
    B --> C["Check Configuration ✓"]
    C --> D["Select New Personas<br/>(interactive menu)"]
    D --> D1["Current: software_engineer, qa_tester<br/>Available: All personas"]
    D1 --> D2["✓ Selected: software_engineer, devops_engineer, architect"]
    
    D2 --> E["Update Configuration"]
    E --> E1[".promptosaurus/.promptosaurus.yaml:<br/>active_personas = [...]"]
    E1 --> E2["✓ Configuration updated"]
    
    E2 --> F["Regenerate All Outputs<br/>(with new persona filter applied)"]
    F --> F1["✓ Agents regenerated for selected personas"]
    
    F1 --> G["✓ Persona swap complete!"]
    
    style A fill:#fff3e0
    style G fill:#c8e6c9
```

---

## Data Flow Diagrams

### Agent Discovery and Build Flow

```mermaid
flowchart TD
    A["Scan agents/ Directory<br/>(agents/code/, agents/test/, agents/debug/, etc.)"] --> B["ComponentLoader Loads Files<br/>(YAML Frontmatter + Markdown Content)"]
    B --> C["Parsers Extract Structured Data<br/>(YAMLParser, MarkdownParser)"]
    C --> D["Create Agent IR Models<br/>(Pydantic - immutable)"]
    D --> E["PersonaFilter<br/>(optional filter by selected personas)"]
    E --> F["Builder Selects & Transforms Agent IR<br/>(variant selection + template substitution)"]
    F --> G["Write Tool-Specific Configuration Files<br/>(.kilo/agents/code.md, .clinerules, .cursor/rules/, etc.)"]
    
    style A fill:#e1f5ff
    style G fill:#c8e6c9
```

### Template Substitution Flow

```mermaid
flowchart LR
    A["Configuration<br/>language: python<br/>runtime: 3.12<br/>package_manager: uv<br/>testing_framework: pytest"] --> B["Template String<br/>from Agent Prompt File<br/>Use {{LANGUAGE}}<br/>Runtime: {{RUNTIME}}<br/>Package: {{PACKAGE_MG}}<br/>Test: {{TESTING_FRAME}}"]
    B --> C["TemplateHandler Chain<br/>LanguageHandler<br/>RuntimeHandler<br/>PackageManagerHandler<br/>TestingFrameworkHandler"]
    C --> D["Jinja2 Renderer<br/>Variable substitution<br/>Conditional logic<br/>Custom filters<br/>Error recovery"]
    D --> E["Final Output<br/>Use python<br/>Runtime: 3.12<br/>Package: uv<br/>Test: pytest"]
    
    style A fill:#fff3e0
    style E fill:#c8e6c9
```

---

## Configuration Flow

### Single-Language Setup

```mermaid
flowchart TD
    A["Repository Type: single-language"] --> B["Config Generated"]
    B --> C["version: 1.0<br/>repository.type: single-language<br/>language: python<br/>runtime: 3.12<br/>package_manager: uv<br/>testing_framework: pytest<br/>...(all other settings)<br/>variant: minimal<br/>active_personas: [software_engineer, qa_tester]"]
    
    style A fill:#e1f5ff
    style C fill:#f3e5f5
```

### Multi-Language Monorepo Setup

```mermaid
flowchart TD
    A["Repository Type: multi-language-monorepo"] --> B["Config Generated"]
    B --> C["version: 1.0<br/>repository.type: multi-language-monorepo"]
    C --> C1["Folder: backend/api<br/>type: backend<br/>language: python<br/>runtime: 3.12"]
    C1 --> C2["Folder: frontend<br/>type: frontend<br/>language: typescript<br/>runtime: 5.4"]
    C2 --> C3["Folder: shared/lib<br/>type: library<br/>language: typescript<br/>runtime: 5.4"]
    C3 --> D["variant: verbose<br/>active_personas: [software_engineer, devops_engineer]"]
    
    style A fill:#e1f5ff
    style D fill:#f3e5f5
```

---

## Agent Discovery Flow

```mermaid
flowchart TD
    A["RegistryDiscovery<br/>Scans: promptosaurus/agents/"] --> B["For each agent_name/:<br/>Look for minimal/<br/>Look for verbose/<br/>Select variant"]
    B --> C["Load prompt.md<br/>(required)<br/>YAML frontmatter<br/>Markdown body"]
    C --> D["Load optional files:<br/>skills.md<br/>workflow.md"]
    D --> E["Create Agent IR<br/>(immutable model)"]
    E --> F["Look for subagents/<br/>(recursive discovery)"]
    F --> G["Cache in Registry<br/>(with variant index)"]
    
    style A fill:#e1f5ff
    style G fill:#c8e6c9
```

---

## Builder Selection Flow

```mermaid
flowchart TD
    A["User selects tool during init<br/>(Kilo IDE, Cline, Cursor, etc.)"] --> B["BuilderFactory.get_builder<br/>(kilo-ide)"]
    B --> C["Returns: KiloBuilder instance"]
    C --> D["builder.build<br/>(agent, opts)"]
    D --> E["Validate agent<br/>Build YAML frontmatter<br/>Build prompt section<br/>Build skills section<br/>Build workflows section<br/>Compose markdown output"]
    E --> F["Output for Kilo:<br/>.kilo/agents/code.md<br/>.kilo/agents/test.md<br/>.kilo/agents/review.md<br/>...per selected agent"]
    
    style A fill:#e1f5ff
    style F fill:#c8e6c9
```

---

## Tool Output Locations

```mermaid
graph TD
    A["Tool Selection"] --> B["Kilo IDE"]
    A --> C["Kilo CLI"]
    A --> D["Cline"]
    A --> E["Cursor"]
    A --> F["GitHub Copilot"]
    
    B --> B1[".kilo/agents/<br/>├── code.md<br/>├── test.md<br/>├── review.md<br/>├── refactor.md<br/>├── document.md<br/>└── ...agent-specific"]
    
    C --> C1[".opencode/rules/<br/>├── always-on.md<br/>└── modes.md"]
    
    D --> D1[".clinerules<br/>(single file)"]
    
    E --> E1[".cursor/rules/<br/>├── code.mdc<br/>├── test.mdc<br/>└── ...<br/>+ .cursorrules (legacy)"]
    
    F --> F1[".github/<br/>copilot-instructions.md"]
    
    style A fill:#e1f5ff
    style B1 fill:#c8e6c9
    style C1 fill:#c8e6c9
    style D1 fill:#c8e6c9
    style E1 fill:#c8e6c9
    style F1 fill:#c8e6c9
```

---

## Reference

- [ARCHITECTURE.md](./ARCHITECTURE.md) - Detailed component documentation
- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Step-by-step guide
- [ADVANCED_CONFIGURATION.md](./ADVANCED_CONFIGURATION.md) - Configuration reference
