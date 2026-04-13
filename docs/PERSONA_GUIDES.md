# Quick Reference by Persona

Find the right resources for your role.

## 🏗️ Architect / Tech Lead

**Goal:** Understand system design and plan implementation

**Start here:**
1. [RELATIONSHIPS_MATRIX.md](./RELATIONSHIPS_MATRIX.md) - See how all components fit together
2. [ADVANCED_PATTERNS.design.md](./design/ADVANCED_PATTERNS.design.md) - Architecture decisions
3. Check the LIBRARY_INDEX.md for all available resources

**Key documents:**
- Design decisions: `docs/design/*.design.md`
- Planning docs: `planning/current/*.plan.md`

**Questions answered:**
- What agents exist and why? → LIBRARY_INDEX.md
- How do they work together? → RELATIONSHIPS_MATRIX.md
- What was the design thinking? → docs/design/
- What resources are available? → LIBRARY_INDEX.md

---

## 👨‍💻 Backend Developer

**Goal:** Get backend-specific guidance and patterns

**Start here:**
1. Find "backend" in [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
2. Read `promptosaurus/agents/backend/` for full context
3. Explore related workflows: database design, API development, performance optimization

**Key agents:**
- **Backend Engineer** - Main backend role
- **Database Engineer** - Schema design, query optimization
- **Performance Engineer** - Optimization and benchmarking
- **DevOps Engineer** - Infrastructure and deployment

**Key workflows:**
- Search LIBRARY_INDEX.md for: "backend", "database", "API", "performance"
- Read minimal variants first (quick reference)
- Deep dive with verbose variants when needed

**Key skills:**
- SQL optimization
- Database design patterns
- API design principles
- Performance tuning

---

## 🎨 Frontend Developer

**Goal:** Get frontend-specific guidance and component patterns

**Start here:**
1. Find "frontend" in [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
2. Read `promptosaurus/agents/frontend/` for full context
3. Explore related workflows: component design, testing, accessibility

**Key agents:**
- **Frontend Engineer** - Main frontend role
- **Testing Engineer** - QA and test automation
- **Performance Engineer** - Frontend optimization
- **UI/UX Specialist** - Design system guidance

**Key workflows:**
- Search LIBRARY_INDEX.md for: "frontend", "component", "testing", "accessibility"
- Read workflow guides for common patterns
- Check skills for deep dives into specific technologies

**Key skills:**
- React/Vue patterns
- CSS methodologies
- Testing strategies
- Accessibility (a11y)

---

## 🔧 DevOps / SRE

**Goal:** Get infrastructure and operations guidance

**Start here:**
1. Find "devops" in [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
2. Read `promptosaurus/agents/devops-engineer/` for full context
3. Explore infrastructure workflows

**Key agents:**
- **DevOps Engineer** - Main DevOps role
- **Incident Response Engineer** - Emergency procedures
- **Observability Engineer** - Monitoring and logging
- **Performance Engineer** - Capacity planning

**Key workflows:**
- Search LIBRARY_INDEX.md for: "devops", "kubernetes", "monitoring", "incident", "deployment"
- Read infrastructure setup guides
- Check incident response procedures

**Key skills:**
- Kubernetes operations
- CI/CD pipeline design
- Infrastructure as Code (Terraform)
- Monitoring and alerting
- Incident response

---

## 🧪 QA / Test Engineer

**Goal:** Get testing strategies and QA patterns

**Start here:**
1. Find "testing" in [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
2. Read `promptosaurus/agents/qa-tester/` for full context
3. Explore testing workflows

**Key agents:**
- **Testing Engineer** - Main QA role
- **Backend Developer** - Integration testing
- **Frontend Developer** - E2E testing
- **Performance Engineer** - Load testing

**Key workflows:**
- Search LIBRARY_INDEX.md for: "testing", "test", "automation", "coverage", "quality"
- Read testing strategy guides
- Check test automation patterns

**Key skills:**
- Unit testing patterns
- Integration testing
- E2E testing strategies
- Test automation frameworks
- Coverage analysis

---

## 📊 Data / ML Engineer

**Goal:** Get data pipeline and ML guidance

**Start here:**
1. Find "data" in [LIBRARY_INDEX.md](./LIBRARY_INDEX.md)
2. Read `promptosaurus/agents/data-engineer/` for full context
3. Explore data workflow guides

**Key agents:**
- **Data Engineer** - Main data role
- **ML Engineer** - Machine learning guidance
- **Database Engineer** - Data storage patterns
- **Observability Engineer** - Data quality monitoring

**Key workflows:**
- Search LIBRARY_INDEX.md for: "data", "pipeline", "warehouse", "ml", "analytics"
- Read pipeline design guides
- Check data quality patterns

**Key skills:**
- Data pipeline design
- SQL optimization
- Data warehouse patterns
- ML model serving
- Data quality frameworks

---

## 📈 Product / Manager Role

**Goal:** Understand project status and planning

**Start here:**
1. [QUICKSTART.md](./QUICKSTART.md) - Overview of what exists
2. [QUALITY_METRICS.md](./QUALITY_METRICS.md) - Project quality dashboard
3. 4. [LIBRARY_INDEX.md](./LIBRARY_INDEX.md) - Feature catalog

**Key documents:**
- Quality metrics: QUALITY_METRICS.md
- Technical debt: TECHNICAL_DEBT.md

**Questions answered:**
- What's the quality level? → QUALITY_METRICS.md
- What's left to do? → TECHNICAL_DEBT.md

---

## 🚀 DevOps / Infrastructure Lead

**Goal:** Deploy and maintain the system

**Start here:**
1. [TOOL_CONFIGURATION_EXAMPLES.reference.md](./reference/TOOL_CONFIGURATION_EXAMPLES.reference.md) - Deployment options
2. `docs/design/ADVANCED_PATTERNS.design.md` - System architecture
3. `promptosaurus/agents/devops-engineer/` - DevOps guidance

**Key resources:**
- Deployment guides: `docs/reference/TOOL_CONFIGURATION_EXAMPLES.reference.md`
- Infrastructure code: `docs/design/`
- Monitoring setup: Search LIBRARY_INDEX.md for "observability"
- Incident response: Search for "incident-response"

---

## 🤖 AI Tool Developer

**Goal:** Integrate Promptosaurus into your AI tool

**Start here:**
1. [GETTING_STARTED.reference.md](./reference/GETTING_STARTED.reference.md) - Setup guide
2. [TOOL_CONFIGURATION_EXAMPLES.reference.md](./reference/TOOL_CONFIGURATION_EXAMPLES.reference.md) - Tool-specific setup
3. [API_REFERENCE.reference.md](./reference/API_REFERENCE.reference.md) - Technical reference

**Integration points:**
- Kilo (CLI): `promptosaurus/agents/` directory structure
- Cline: `.clinerules` file generation
- Cursor: `.cursor/rules/` directory
- Copilot: `.github/copilot-instructions.md` format

**Key resources:**
- Reference guides: `docs/reference/*.reference.md`
- Design decisions: `docs/design/TOOL_INTEGRATION_GUIDE.design.md`
- Examples: `docs/builders/*.builder.md`

---

## 🔍 Code Reviewer / QA Lead

**Goal:** Validate quality and completeness

**Start here:**
1. [QUALITY_METRICS.md](./QUALITY_METRICS.md) - Quality dashboard
2. [TECHNICAL_DEBT.md](./TECHNICAL_DEBT.md) - Known issues
3. `_temp/validation/` - Validation reports

**Key documents:**
- Test coverage: QUALITY_METRICS.md
- Known issues: TECHNICAL_DEBT.md
- Validation reports: `_temp/validation/`
- Code structure: [DIRECTORY_STRUCTURE.reference.md](./reference/DIRECTORY_STRUCTURE.reference.md)

**Questions answered:**
- What's the test coverage? → QUALITY_METRICS.md
- Are there known issues? → TECHNICAL_DEBT.md
- How's the code quality? → _temp/validation/
- Is everything documented? → LIBRARY_INDEX.md

---

## How to Use This Guide

1. **Find your role** in the list above
2. **Follow the "Start here" links** in order
3. **Use "Key documents"** as reference during work
4. **Check "Questions answered"** when stuck

All guides link back to the central [LIBRARY_INDEX.md](./LIBRARY_INDEX.md), which is searchable and comprehensive.
