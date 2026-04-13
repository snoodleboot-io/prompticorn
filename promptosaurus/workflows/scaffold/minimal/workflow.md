---
name: scaffold
description: Generate project boilerplate structure with proper organization and configuration
languages: [all]
subagents: [architect/scaffold, code/boilerplate]
steps:
  - Gather project requirements and parameters
  - Design directory structure and configuration
  - Propose folder layout and tooling setup
  - Generate boilerplate files and directory structure
  - Create initial configuration files
  - Verify build and test commands work
  - Create initial commit with scaffolding
---

## Steps

### Step 1: Gather project requirements and parameters

Ask the user these questions one at a time to understand the project scope:

1. **What is the project's purpose in one sentence?**
   - Example: "API service for managing user authentication"

2. **What is the primary language and framework?**
   - Example: "Python with FastAPI" or "TypeScript with Next.js"

3. **What external services or APIs will it integrate with?**
   - Example: "PostgreSQL database, Redis cache, Stripe payments"

4. **Is this a monorepo, a single service, or a library?**
   - Example: "Single service, will be deployed to AWS Lambda"

5. **What environments will it run in?**
   - Example: "Local dev, staging, production"

6. **Any known constraints (license, compliance, patterns to follow)?**
   - Example: "Must follow GDPR, use our core-conventions"

### Step 2: Design directory structure and configuration

Based on answers from Step 1, design the folder structure.

**Typical structure for a service:**
```
project-name/
├── src/                  # Source code
│   ├── api/              # API endpoints/routes
│   ├── domain/           # Core business logic
│   ├── infrastructure/   # Database, external services
│   └── main.py           # Entry point
├── tests/                # Test files
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/                 # Documentation
├── scripts/              # Utility scripts
├── config/               # Configuration files
├── .github/              # GitHub workflows (CI/CD)
├── docker/               # Docker configuration
├── pyproject.toml        # Python project config
├── pytest.ini            # Test configuration
├── .env.example          # Environment variables template
├── README.md             # Project overview
├── CONTRIBUTING.md       # Contribution guidelines
└── Dockerfile            # Container definition
```

**Configuration files to create:**
- Package manager config (pyproject.toml, package.json, go.mod, etc.)
- Linting/formatting config (.flake8, .eslintrc, etc.)
- Testing config (pytest.ini, jest.config.js, etc.)
- Development tools (.editorconfig, .gitignore, etc.)
- CI/CD workflows (.github/workflows/*.yml)

### Step 3: Propose folder layout and tooling setup

Present the designed structure to the user for approval:

**Proposed Structure:**
```markdown
## Directory Layout

**Core Directories:**
- `/src` - All application source code
- `/tests` - All test files (unit, integration, E2E)
- `/docs` - Documentation and guides
- `/scripts` - Build, deployment, utility scripts

**Configuration:**
- `pyproject.toml` - Python package and tool configs
- `.github/workflows/` - CI/CD pipelines
- `.env.example` - Environment variables template
- `Dockerfile` - Container image definition

**Tooling Stack:**
- Language: Python 3.12+
- Package Manager: uv
- Framework: FastAPI
- Testing: pytest
- Linting: ruff
- Type Checking: pyright
- Container: Docker
- CI/CD: GitHub Actions

## Rationale
Each directory has a clear purpose. Config files at root for easy discovery.
src/ structure mirrors domain model. Tests mirror source layout.
```

**Ask for confirmation:** "Does this structure and tooling work for your project?"

### Step 4: Generate boilerplate files and directory structure

Create the directory structure and base files:

**Create directories:**
```bash
mkdir -p src/{api,domain,infrastructure}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p docs scripts config .github/workflows docker
```

**Create boilerplate files:**
- `src/main.py` - Entry point with TODO comments
- `src/api/routes.py` - API route stubs
- `src/domain/models.py` - Domain model stubs
- `tests/unit/test_example.py` - Example unit test
- `README.md` - Project overview
- `CONTRIBUTING.md` - Contribution guidelines
- `Dockerfile` - Multi-stage Docker build
- `.env.example` - Environment variables template

### Step 5: Create initial configuration files

Set up package manager and tool configurations:

**Python Example:**
```toml
# pyproject.toml
[project]
name = "project-name"
version = "0.1.0"
description = "Brief description"
requires-python = ">=3.12"
dependencies = [
    "fastapi==0.104.0",
    "uvicorn==0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.0",
    "pytest-cov==4.1.0",
    "ruff==0.1.0",
    "pyright==1.1.300",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=html"

[tool.ruff]
select = ["E", "F", "W"]
line-length = 100
```

**TypeScript Example:**
```json
{
  "name": "project-name",
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "test": "vitest run --coverage"
  },
  "dependencies": {
    "react": "18.2.0"
  }
}
```

### Step 6: Verify build and test commands work

Run initial build and test commands to verify scaffolding is correct:

**Python:**
```bash
# Install dependencies
uv sync

# Run tests
pytest --cov

# Run linting
ruff check .

# Type checking
pyright
```

**TypeScript:**
```bash
# Install dependencies
npm install

# Run tests
npm test

# Run build
npm run build
```

All commands should run without errors.

### Step 7: Create initial commit with scaffolding

Create a commit with the scaffolding setup:

```bash
git add .
git commit -m "chore: scaffold project structure and configuration

- Created src/ directory with domain, api, infrastructure layers
- Created tests/ directory with unit and integration subdirs
- Added pyproject.toml with dependencies and tool configs
- Added pytest, ruff, and pyright configurations
- Created Dockerfile for containerization
- Added .env.example with required variables
- Created README and CONTRIBUTING guidelines
- All build and test commands working

Next steps:
- Implement core domain models in src/domain/
- Create API routes in src/api/
- Write tests for implemented features
"
```

**Next Steps to Communicate:**

- Core domain models should be implemented next
- API routes can be built on top of domain models
- Tests should be written as features are implemented
- Documentation should be updated as implementation progresses

