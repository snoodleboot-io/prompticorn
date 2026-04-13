# Promptosaurus Documentation

**Version:** 0.1.0  
**Status:** Active Development  
**Last Updated:** April 13, 2026

---

## Getting Started

New to Promptosaurus? Start here:

1. **[QUICKSTART.md](./QUICKSTART.md)** — 5-minute overview of core concepts
2. **[user-guide/GETTING_STARTED.md](./user-guide/GETTING_STARTED.md)** — Installation and setup
3. **[PERSONA_GUIDES.md](./PERSONA_GUIDES.md)** — Find resources for your role

---

## Core Documentation

### User Guides
Located in [`user-guide/`](./user-guide/):
- **GETTING_STARTED.md** — Installation, configuration, and first steps
- **CLI_REFERENCE.md** — Complete command reference
- **TOOL_CONFIGURATION_EXAMPLES.md** — Setup for different AI tools

### Reference Documentation
Located in [`reference/`](./reference/):
- **API_REFERENCE.reference.md** — Python API documentation
- **MIGRATION_GUIDE.md** — Upgrading from previous versions
- **DIRECTORY_STRUCTURE.reference.md** — Project layout and organization

### System Architecture
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** — Complete system design with diagrams
- **[TEMPLATE_SYSTEM.md](./TEMPLATE_SYSTEM.md)** — How templates and substitution work
- **[ADVANCED_CONFIGURATION.md](./ADVANCED_CONFIGURATION.md)** — Power user configuration

### Developer Guides
Located in [`developer-guide/`](./developer-guide/):
- Builder implementation guides
- Extension patterns
- Testing strategies

### Design Documentation
Located in [`design/`](./design/):
- Architecture Decision Records (ADRs)
- Design patterns and rationale
- Advanced patterns and implementation details

### Building & Extending
Located in [`builders/`](./builders/):
- Guide for each supported AI tool
- Builder API reference
- Implementation examples

---

## Troubleshooting & Operations

- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** — Common issues and solutions
- **[DIAGRAMS_GUIDE.md](./DIAGRAMS_GUIDE.md)** — Visual workflows and architecture diagrams
- **[INTEGRATION_GUIDES.md](./INTEGRATION_GUIDES.md)** — CI/CD and tool integration
- **[INTERACTIVE_WALKTHROUGH.md](./INTERACTIVE_WALKTHROUGH.md)** — Step-by-step examples
- **[MAINTENANCE_WORKFLOW.md](./MAINTENANCE_WORKFLOW.md)** — Maintenance and operational procedures

---

## Planning & Decisions

Development planning and architectural decisions:
- **[decisions/](./decisions/)** — Architectural Decision Records
- **[../planning/current/](../planning/current/)** — Active development plans (internal)
- **[PERSONAS.md](./PERSONAS.md)** — Agent personas and roles

---

## Quality & Metrics

Project quality and status:
- **[RELATIONSHIPS_MATRIX.md](./RELATIONSHIPS_MATRIX.md)** — Agent and workflow relationships
- **[LIBRARY_INDEX.md](./LIBRARY_INDEX.md)** — Searchable catalog of all agents

---

## Organization

Documentation is organized by intent, with filename suffixes indicating content type:

- `.md` — Main documentation
- `.reference.md` — Reference guides and how-to
- `.design.md` — Architecture and design decisions  
- `.builder.md` — Builder tool guides
- `.plan.md` — Execution plans and checklists (planning/)
- `.validation.md` — Test results and reports

---

## For Different Audiences

### I'm new to Promptosaurus
Start with [QUICKSTART.md](./QUICKSTART.md) then [user-guide/GETTING_STARTED.md](./user-guide/GETTING_STARTED.md)

### I want to understand the architecture
Read [ARCHITECTURE.md](./ARCHITECTURE.md) and [TEMPLATE_SYSTEM.md](./TEMPLATE_SYSTEM.md)

### I'm implementing a builder
See [builders/](./builders/) and [reference/API_REFERENCE.reference.md](./reference/API_REFERENCE.reference.md)

### I need to troubleshoot something
Check [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

### I'm integrating with CI/CD
See [INTEGRATION_GUIDES.md](./INTEGRATION_GUIDES.md)

### I want to contribute
Read [CONTRIBUTING.md](../CONTRIBUTING.md) in the project root

---

## Table of Contents by Directory

```
docs/
├── README.md (this file)
├── user-guide/          → Getting started and CLI usage
├── reference/           → API and reference documentation
├── design/              → Architecture and design decisions
├── builders/            → Builder implementation guides
├── developer-guide/     → Development practices and patterns
├── architecture/        → Detailed architecture documents
├── components/          → Component-specific documentation
├── decisions/           → Architectural Decision Records
├── misc/                → Miscellaneous documentation
│
├── QUICKSTART.md                    → 5-minute overview
├── ARCHITECTURE.md                  → Full system architecture
├── TEMPLATE_SYSTEM.md               → Template system documentation
├── ADVANCED_CONFIGURATION.md        → Power user guide
├── TROUBLESHOOTING.md               → Common issues and solutions
├── DIAGRAMS_GUIDE.md                → Visual diagrams and workflows
├── INTEGRATION_GUIDES.md            → CI/CD and tool integration
├── INTERACTIVE_WALKTHROUGH.md       → Step-by-step examples
├── PERSONAS.md                      → Agent personas and roles
├── PERSONA_GUIDES.md                → Resources by role
├── LIBRARY_INDEX.md                 → Searchable agent catalog
├── RELATIONSHIPS_MATRIX.md          → Agent/workflow relationships
├── MIGRATION_GUIDE.md               → Upgrade instructions
├── MAINTENANCE_WORKFLOW.md          → Operational procedures
└── INDEX.md                         → Documentation index
```

---

## Building & Contributing

To build documentation:
```bash
# Validate all links
python3 scripts/validate_docs.py

# Generate API docs from source
python3 scripts/generate_api_docs.py
```

To contribute documentation:
1. Follow the naming conventions (see "Organization" above)
2. Place in appropriate directory
3. Update this README if adding new top-level documents
4. Validate links before submitting

---

For questions or issues, see [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) or open an issue on GitHub.
