# Advanced Configuration Guide

Comprehensive guide to advanced configuration options in Promptosaurus.

## Table of Contents

- [Configuration File Schema](#configuration-file-schema)
- [Single-Language Projects](#single-language-projects)
- [Multi-Language Monorepos](#multi-language-monorepos)
- [Persona Configuration](#persona-configuration)
- [Variant Selection](#variant-selection)
- [Builder-Specific Settings](#builder-specific-settings)
- [Template Variables](#template-variables)
- [Ignore Files](#ignore-files)
- [Advanced Use Cases](#advanced-use-cases)

---

## Configuration File Schema

The `.promptosaurus.yaml` file is your project's configuration source.

### Required Fields

```yaml
version: "1.0"              # Config schema version
repository:
  type: "single-language"   # or "multi-language-monorepo"
spec: { }                   # Language/folder specifications (see below)
```

### Optional Fields

```yaml
variant: "minimal"          # or "verbose"
active_personas: []         # List of persona IDs
```

### Complete Schema Reference

```yaml
version: string               # "1.0" (required)
repository:
  type: string               # "single-language" | "multi-language-monorepo" (required)
spec:
  # For single-language:
  language: string           # "python", "typescript", "go", etc.
  runtime: string            # "3.12", "5.4", "1.21", etc.
  package_manager: string    # "uv", "npm", "go mod", etc.
  testing_framework: string  # "pytest", "vitest", "go test", etc.
  test_runner: string        # Same as testing_framework or custom
  linter: list[string]       # ["ruff", "mypy"] or single value
  formatter: list[string]    # ["black"] or single value
  coverage_tool: string      # "pytest-cov", "c8", etc.
  e2e_tool: string           # "playwright", "cypress", etc.
  mocking_library: string    # "unittest.mock", "vitest.mock", etc.
  mutation_tool: string      # "mutmut", "stryker", etc.
  abstract_class_style: string  # "abc", "Protocol", "interface"
  
  # For multi-language-monorepo:
  - folder: string           # Folder path (e.g., "backend/api")
    type: string             # "backend", "frontend", "custom"
    subtype: string          # "api", "ui", "library", etc.
    language: string         # Same as above
    runtime: string          # Same as above
    # ... (all language-specific fields above)

variant: string              # "minimal" | "verbose" (optional, default: "minimal")
active_personas: list[string]  # ["software_engineer", "qa_tester", ...] (optional)
```

---

## Single-Language Projects

For projects using one primary programming language.

### Minimal Configuration

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
```

This is enough to generate basic agent configurations.

### Complete Python Configuration

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
  testing_framework: "pytest"
  test_runner: "pytest"
  linter: ["ruff", "mypy"]
  formatter: ["black"]
  coverage_tool: "pytest-cov"
  coverage_target: 90
  e2e_tool: "playwright"
  mocking_library: "unittest.mock"
  mutation_tool: "mutmut"
  abstract_class_style: "abc"
variant: "minimal"
active_personas:
  - "software_engineer"
  - "qa_tester"
```

### Complete TypeScript Configuration

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "typescript"
  runtime: "5.4"
  package_manager: "npm"
  testing_framework: "vitest"
  test_runner: "npm test"
  linter: ["eslint", "@typescript-eslint"]
  formatter: ["prettier"]
  coverage_tool: "c8"
  coverage_target: 85
  e2e_tool: "playwright"
  mocking_library: "vitest.mock"
  mutation_tool: "stryker"
  abstract_class_style: "interface"
variant: "verbose"
active_personas:
  - "software_engineer"
  - "devops_engineer"
```

### Language-Specific Fields

#### Python

```yaml
spec:
  language: "python"
  runtime: "3.10" | "3.11" | "3.12" | "3.13" | "3.14"
  package_manager: "pip" | "poetry" | "uv"
  testing_framework: "pytest" | "unittest"
  linter: ["ruff", "pylint", "mypy", "flake8"]
  formatter: ["black", "ruff"]
  abstract_class_style: "abc" | "Protocol"
```

#### TypeScript/JavaScript

```yaml
spec:
  language: "typescript" | "javascript"
  runtime: "5.0" | "5.1" | "5.2" | "5.3" | "5.4"  # TypeScript version
  package_manager: "npm" | "yarn" | "pnpm" | "bun"
  testing_framework: "vitest" | "jest" | "mocha"
  linter: ["eslint", "@typescript-eslint"]
  formatter: ["prettier", "biome"]
  abstract_class_style: "class" | "interface"
```

#### Go

```yaml
spec:
  language: "go"
  runtime: "1.20" | "1.21" | "1.22"
  package_manager: "go mod"
  testing_framework: "go test"
  linter: ["golangci-lint", "staticcheck"]
  formatter: ["gofmt", "goimports"]
```

---

## Multi-Language Monorepos

For projects with multiple languages in different folders.

### Structure

```yaml
version: "1.0"
repository:
  type: "multi-language-monorepo"
spec:
  - folder: "backend/api"
    type: "backend"
    subtype: "api"
    language: "python"
    runtime: "3.12"
    package_manager: "uv"
    testing_framework: "pytest"
    # ... other Python-specific settings
  
  - folder: "frontend"
    type: "frontend"
    subtype: "ui"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"
    testing_framework: "vitest"
    # ... other TypeScript-specific settings
  
  - folder: "shared/utils"
    type: "library"
    subtype: "shared"
    language: "typescript"
    runtime: "5.4"
    package_manager: "npm"

variant: "minimal"
active_personas:
  - "software_engineer"
  - "devops_engineer"
```

### Standard Folder Types

#### Backend

```yaml
- folder: "backend/api"
  type: "backend"
  subtype: "api"        # API server
  language: "python"    # Default: python
  # ... language-specific settings
```

**Subtypes:**
- `api` - REST/GraphQL API server
- `worker` - Background worker/queue processor
- `library` - Shared backend library
- `cli` - Command-line tool

#### Frontend

```yaml
- folder: "frontend"
  type: "frontend"
  subtype: "ui"         # Web application
  language: "typescript"  # Default: typescript
  # ... language-specific settings
```

**Subtypes:**
- `ui` - Web application (React, Vue, etc.)
- `library` - Shared frontend library
- `e2e` - End-to-end tests

#### Custom

```yaml
- folder: "services/auth"
  type: "custom"
  subtype: "microservice"
  language: "go"
  # ... language-specific settings
```

### Hierarchical Paths

Folders can be nested:

```yaml
spec:
  - folder: "services/auth/api"
    type: "backend"
    subtype: "api"
    language: "go"
  
  - folder: "services/auth/worker"
    type: "backend"
    subtype: "worker"
    language: "go"
  
  - folder: "services/payment/api"
    type: "backend"
    subtype: "api"
    language: "python"
```

---

## Persona Configuration

Personas control which agents are generated.

### Available Personas

```yaml
active_personas:
  - "software_engineer"    # Core development
  - "qa_tester"            # Testing and QA
  - "devops_engineer"      # CI/CD and ops
  - "security_engineer"    # Security reviews
  - "architect"            # System design
  - "data_engineer"        # Data pipelines
  - "data_scientist"       # ML/AI
  - "technical_writer"     # Documentation
  - "product_manager"      # Product planning
```

### Universal Agents

These agents are **always generated** regardless of persona selection:
- `ask` - Q&A and decision logs
- `debug` - Debugging assistance
- `explain` - Code explanations
- `plan` - Planning and task breakdown
- `orchestrator` - Workflow coordination

### Agent Filtering Examples

#### Example 1: Solo Developer

```yaml
active_personas:
  - "software_engineer"
```

**Generated agents:**
- Universal: ask, debug, explain, plan, orchestrator
- Software Engineer: code, test, refactor, review, document

**Total:** ~10 agents

#### Example 2: Full-Stack Team

```yaml
active_personas:
  - "software_engineer"
  - "qa_tester"
  - "devops_engineer"
```

**Generated agents:**
- Universal: ask, debug, explain, plan, orchestrator
- Software Engineer: code, test, refactor, review, document
- QA/Tester: test, review (overlap with Software Engineer)
- DevOps: deployment, ci-cd, monitoring

**Total:** ~15 agents (with overlap)

#### Example 3: Enterprise Team

```yaml
active_personas:
  - "software_engineer"
  - "qa_tester"
  - "devops_engineer"
  - "security_engineer"
  - "architect"
```

**Generated agents:**
- All previous + architect, security, compliance

**Total:** ~20 agents

### Custom Persona Creation

Edit `promptosaurus/personas/personas.yaml`:

```yaml
personas:
  my_custom_persona:
    display_name: "My Custom Role"
    description: "Custom role for specific workflow"
    primary_agents:
      - "code"
      - "test"
    secondary_agents:
      - "review"
    workflows:
      - "feature"
    skills:
      - "debugging-methodology"
```

Then use in your config:

```yaml
active_personas:
  - "my_custom_persona"
```

---

## Variant Selection

Choose between **minimal** (efficient) or **verbose** (detailed) agent prompts.

### Minimal Variant

```yaml
variant: "minimal"
```

**Characteristics:**
- Concise prompts (50-200 lines)
- Essential instructions only
- Lower token usage
- Faster response times
- Best for: Cost-conscious projects, experienced developers

### Verbose Variant

```yaml
variant: "verbose"
```

**Characteristics:**
- Detailed prompts (200-800 lines)
- Extensive examples
- More context and explanations
- Higher token usage
- Best for: Learning, complex projects, junior developers

### Per-Agent Variant Override

Currently, variant is global. All agents use the same variant.

**Future feature:** Per-agent variant selection.

---

## Builder-Specific Settings

Different AI tools have different output formats.

### Kilo IDE

```yaml
# No builder-specific settings needed
# Outputs to: .kilo/agents/
```

**Output structure:**
```
.kilo/
├── agents/
│   ├── code.md
│   ├── test.md
│   └── ...
└── rules/
    ├── system.md
    └── conventions.md
```

### Kilo CLI

```yaml
# No builder-specific settings needed
# Outputs to: .opencode/rules/
```

**Output structure:**
```
.opencode/
└── rules/
    ├── always-on.md  (collapsed)
    └── modes.md      (collapsed)
```

### Cline

```yaml
# No builder-specific settings needed
# Outputs to: .clinerules
```

**Output:** Single concatenated file.

### Cursor

```yaml
# No builder-specific settings needed
# Outputs to: .cursor/rules/
```

**Output structure:**
```
.cursor/
└── rules/
    ├── code.mdc
    ├── test.mdc
    └── ...
```

Plus legacy `.cursorrules` file.

### GitHub Copilot

```yaml
# No builder-specific settings needed
# Outputs to: .github/copilot-instructions.md
```

**Output:** Single markdown file.

---

## Template Variables

See [TEMPLATE_SYSTEM.md](./TEMPLATE_SYSTEM.md) for complete documentation.

### Quick Reference

All variables in `.promptosaurus.yaml` `spec` section are available as templates:

```yaml
spec:
  language: "python"       # → {{LANGUAGE}}
  runtime: "3.12"          # → {{RUNTIME}}
  package_manager: "uv"    # → {{PACKAGE_MANAGER}}
  testing_framework: "pytest"  # → {{TESTING_FRAMEWORK}}
  # ... etc
```

### Usage in Custom Prompts

Create custom agent prompts using template variables:

```markdown
---
name: my-custom-agent
description: Custom agent for {{LANGUAGE}}
---

# System Prompt

You are a {{LANGUAGE}} {{RUNTIME}} expert.
Use {{PACKAGE_MANAGER}} for dependencies.
Test with {{TESTING_FRAMEWORK}}.
```

---

## Ignore Files

Promptosaurus can generate ignore files for various tools.

### .kiloignore

Generated for Kilo Code:

```
# Auto-generated by promptosaurus
node_modules/
.venv/
__pycache__/
*.pyc
.git/
```

### .gitignore Integration

Promptosaurus respects existing `.gitignore` and can generate additional patterns:

```gitignore
# Promptosaurus
.promptosaurus.yaml
.kilo/
.clinerules
.cursor/
```

### Custom Ignore Patterns

Add custom patterns to `.promptosaurus.yaml`:

```yaml
ignore_patterns:
  - "vendor/"
  - "dist/"
  - "*.log"
```

---

## Advanced Use Cases

### Use Case 1: Multiple AI Tools

Generate configs for all tools:

```bash
# Generate Kilo
promptosaurus init
# Select: Kilo IDE

# Generate Cline
promptosaurus switch
# Select: Cline

# Generate Cursor
promptosaurus switch
# Select: Cursor
```

**Result:** All three configs exist simultaneously.

### Use Case 2: Environment-Specific Configs

#### Development

`.promptosaurus.dev.yaml`:
```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
variant: "verbose"  # More detailed for development
```

#### Production

`.promptosaurus.prod.yaml`:
```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
variant: "minimal"  # Efficient for production
```

**Switch configs:**
```bash
cp .promptosaurus.dev.yaml .promptosaurus.yaml
promptosaurus init
```

### Use Case 3: Team Configurations

#### Backend Team

`.promptosaurus.backend.yaml`:
```yaml
active_personas:
  - "software_engineer"
  - "devops_engineer"
  - "security_engineer"
```

#### Frontend Team

`.promptosaurus.frontend.yaml`:
```yaml
active_personas:
  - "software_engineer"
  - "qa_tester"
```

### Use Case 4: CI/CD Integration

**GitHub Actions:**

```yaml
name: Generate AI Configs

on:
  push:
    branches: [main]

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install promptosaurus
      - run: promptosaurus validate
      - run: promptosaurus init --non-interactive
```

### Use Case 5: Monorepo with Shared Config

**Base config:** `.promptosaurus.base.yaml`

```yaml
version: "1.0"
variant: "minimal"
active_personas:
  - "software_engineer"
  - "qa_tester"
```

**Per-language overlays:**

```yaml
# backend/.promptosaurus.yaml
extends: "../.promptosaurus.base.yaml"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
```

**Note:** Config inheritance is a planned feature.

---

## Configuration Validation

### Validate Syntax

```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('.promptosaurus.yaml'))"
```

### Validate with Promptosaurus

```bash
promptosaurus validate
```

**Output:**
```
▶ Validating prompt registry...

  ✓ All good — no missing or orphaned files.
```

### Common Validation Errors

#### Invalid YAML Syntax

**Error:**
```
YAMLError: expected ':', but found '<stream end>'
```

**Cause:** Missing colon or incorrect indentation

**Fix:** Use spaces (not tabs), check colons

#### Unknown Language

**Error:**
```
ValueError: Unknown language 'pythn'
```

**Cause:** Language name misspelled

**Fix:** Use correct language name from supported list

#### Missing Required Fields

**Error:**
```
ValidationError: 'language' is required
```

**Cause:** Missing required field in spec

**Fix:** Add all required fields (language, runtime, package_manager at minimum)

---

## Migration and Upgrades

### Upgrading Config Version

Currently on version `1.0`. Future versions will have migration guides.

### Breaking Changes

Breaking changes will be documented in [MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md).

### Config Schema Versioning

```yaml
version: "1.0"  # Always specify version
```

When upgrading:
1. Read migration guide
2. Update `version` field
3. Run `promptosaurus validate`
4. Regenerate configs with `promptosaurus init`

---

## Best Practices

### 1. Use Version Control

**Commit** `.promptosaurus.yaml` to git:

```bash
git add .promptosaurus.yaml
git commit -m "Add promptosaurus config"
```

**Ignore** generated files:

```gitignore
.kilo/
.clinerules
.cursor/
.github/copilot-instructions.md
```

### 2. Start Minimal, Expand Later

Begin with minimal config:

```yaml
version: "1.0"
repository:
  type: "single-language"
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"
```

Add more fields as needed.

### 3. Document Custom Settings

Add comments to your config:

```yaml
spec:
  language: "python"
  runtime: "3.12"
  package_manager: "uv"  # Using uv for speed
  testing_framework: "pytest"  # Team standard
```

### 4. Use Personas Wisely

Don't select all personas - only those your team uses:

```yaml
# Good (focused)
active_personas:
  - "software_engineer"
  - "qa_tester"

# Bad (too many)
active_personas:
  - "software_engineer"
  - "qa_tester"
  - "devops_engineer"
  - "security_engineer"
  - "architect"
  - "data_engineer"
  - "data_scientist"
```

### 5. Validate After Changes

Always run validation after editing config:

```bash
# Edit config
vim .promptosaurus.yaml

# Validate
promptosaurus validate

# Regenerate if valid
promptosaurus init
```

---

## Reference

### Related Documentation

- [GETTING_STARTED.md](./user-guide/GETTING_STARTED.md) - Basic usage
- [TEMPLATE_SYSTEM.md](./TEMPLATE_SYSTEM.md) - Template variables
- [PERSONAS.md](./PERSONAS.md) - Persona system details
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - Common issues

---

**Last Updated:** 2026-04-13  
**Version:** 0.1.0
