# Documentation Index

prompticorn documentation is organized by intent and purpose.

prompticorn generates AI coding-assistant configs from a shared prompt library:
**25 primary agents**, **~100 workflows**, **~95 skills**, and conventions for
**29 languages**, targeting Kilo, Cline, Claude, Cursor, Copilot, Roo Code, Junie, Zed, Gemini CLI, Amazon Q, Windsurf, Continue.dev, and Aider.

## Getting Started (Pick Your Path)

### 🚀 Quick Start
- **[QUICKSTART.md](./QUICKSTART.md)** — 5-minute overview and the full `init` walkthrough (start here)
- **[PERSONAS.md](./PERSONAS.md)** — how persona-based filtering works
- **[PERSONA_GUIDES.md](./PERSONA_GUIDES.md)** — find resources for your role (architect, developer, QA, etc.)
- **[LIBRARY_INDEX.md](./LIBRARY_INDEX.md)** — searchable catalog of agents, workflows, and skills

## Navigation by Purpose

### 📊 Overview & Relationships
- **[RELATIONSHIPS_MATRIX.md](./RELATIONSHIPS_MATRIX.md)** — how agents, workflows, and skills relate

### 📖 Reference & How-To Guides
See `docs/reference/`:
- [GETTING_STARTED.reference.md](./reference/GETTING_STARTED.reference.md)
- [API_REFERENCE.reference.md](./reference/API_REFERENCE.reference.md)
- [TOOL_CONFIGURATION_EXAMPLES.reference.md](./reference/TOOL_CONFIGURATION_EXAMPLES.reference.md)
- [DIRECTORY_STRUCTURE.reference.md](./reference/DIRECTORY_STRUCTURE.reference.md)

### 🏗️ Design Decisions & Architecture
See `docs/design/`:
- [ADVANCED_PATTERNS.design.md](./design/ADVANCED_PATTERNS.design.md)
- [LANGUAGE_INTEGRATION_DESIGN.design.md](./design/LANGUAGE_INTEGRATION_DESIGN.design.md)
- [VARIANT_DIFFERENTIATION_STRATEGY.design.md](./design/VARIANT_DIFFERENTIATION_STRATEGY.design.md)
- [WORKFLOW_HANDLING_ANALYSIS.design.md](./design/WORKFLOW_HANDLING_ANALYSIS.design.md)

### 🛠️ Builder Documentation
See `docs/builders/` for per-tool builder guides (Kilo, Cline, Claude, Cursor, Copilot, Roo Code, Junie, Zed, Gemini CLI, Amazon Q, Windsurf, Continue.dev, Aider)
plus the builder API reference and implementation guide.

## CLI Commands

| Command | Description |
|---------|-------------|
| `prompticorn init` | Interactive setup: assistant, repo type, variant, personas, language and project questions. |
| `prompticorn list` | List discovered agents, subagents, and prompt variants. |
| `prompticorn validate` | Validate the `agents/` structure and that agents load cleanly. |
| `prompticorn switch [tool]` | Switch assistants and regenerate from the saved config. |
| `prompticorn swap` | Change active personas and regenerate. |
| `prompticorn update` | Update saved configuration options interactively. |

`init` writes its configuration to `.prompticorn/.prompticorn.yaml`.

## File Naming Conventions

Intent is encoded in filename suffixes:

- `.design.md` — architecture and design decisions
- `.reference.md` — reference guides and how-to documentation
- `.builder.md` — builder tool documentation
- `.research.md` — investigation and research findings

## Content Layout

In `prompticorn/`:

- `agents/<agent>/prompt.md` — primary agent instructions
- `agents/<agent>/subagents/<sub>/{minimal,verbose}/prompt.md` — subagent prompt variants
- `agents/core/conventions-*.md` — per-language conventions
- `workflows/.../{minimal,verbose}/workflow.md` — workflow guides
- `skills/<skill>/{minimal,verbose}/SKILL.md` — specialized skills
- `configurations/source_layouts.yaml` — per-language source-tree layouts
