---
name: scaffold
description: Comprehensive project scaffolding with language-specific setup, testing infrastructure, CI/CD templates, and best practices
languages: [python, typescript, go, rust, java]
subagents: [architect/scaffold, code/boilerplate, orchestrator/devops]
steps:
  - Gather comprehensive project requirements one at a time
  - Analyze requirements and identify constraints
  - Design complete project structure and tool stack
  - Document proposed architecture with rationale
  - Get user confirmation before generating any files
  - Create directory structure
  - Generate language-specific boilerplate files
  - Create comprehensive configuration files
  - Set up testing scaffolding and CI/CD pipelines
  - Create Docker and deployment configuration
  - Generate documentation templates
  - Verify all commands work end-to-end
  - Create initial commit with scaffolding
---

## Steps

### Step 1: Gather comprehensive project requirements one at a time

Ask the user these questions sequentially to build a complete understanding:

**Question 1: Project Purpose**
> What is the project's purpose in one sentence?

Examples of good answers:
- "REST API service for managing user authentication and authorization"
- "CLI tool for deploying applications to Kubernetes clusters"
- "React component library for building data visualization dashboards"

This clarifies scope and helps determine appropriate architecture patterns.

**Question 2: Language and Framework**
> What is the primary language and framework?

Examples:
- "Python with FastAPI and SQLAlchemy"
- "TypeScript with Next.js and Prisma"
- "Go with Gin and GORM"
- "Rust with Actix-web and Diesel"

This determines boilerplate templates, config files, and dependency management approach.

**Question 3: External Services and APIs**
> What external services or APIs will it integrate with?

Examples:
- "PostgreSQL database, Redis cache, Stripe for payments, Auth0 for authentication"
- "AWS S3 for file storage, SendGrid for email, Slack for notifications"
- "None - standalone CLI tool"

This determines infrastructure dependencies and environment variable needs.

**Question 4: Repository Structure**
> Is this a monorepo, a single service, or a library?

Options:
- **Single service:** One deployable application (API, CLI, web app)
- **Monorepo:** Multiple services/packages in one repository
- **Library:** Reusable package/module for other projects to consume
- **Workspace:** Multiple packages with shared dependencies

This affects directory structure significantly.

**Question 5: Target Environments**
> What environments will it run in?

Examples:
- "Local development, GitHub Codespaces, Docker containers"
- "Development machine, staging server, production (AWS Lambda)"
- "Docker containers on Kubernetes clusters"
- "macOS/Linux development machines"

This determines Docker config, environment templates, and CI/CD setup.

**Question 6: Constraints and Standards**
> Any known constraints (license, compliance, patterns to follow)?

Examples:
- "Must follow GDPR and PCI-DSS, use company core-conventions"
- "Must be MIT licensed, follow Django best practices"
- "Must support Python 3.11+, no paid dependencies"
- "No external constraints, use our standard patterns"

This shapes architecture decisions and determines what patterns/tools are allowed.

### Step 2: Analyze requirements and identify constraints

Review all answers to identify conflicts and edge cases.

**Compatibility Analysis:**

```markdown
## Requirements Analysis

### Language & Framework
- Primary: TypeScript
- Framework: Next.js (React)
- Runtime: Node 20+
- Package Manager: pnpm (check: is this organization standard?)

### Infrastructure
- Database: PostgreSQL (need connection pooling config)
- Cache: Redis (need sentinel config for HA?)
- External: Stripe, Auth0
- Deployment: AWS Lambda (need serverless framework config)

### Project Structure
- Type: Single service (monolithic API)
- Scalability: Medium (concurrent users in thousands)
- Team size: 3-5 developers

### Constraints
- License: MIT
- Compliance: GDPR only (no PCI or HIPAA needs)
- Standards: Company core-conventions repo
- Performance: API response < 500ms p95

### Identified Risks/Gaps
- No machine learning needs mentioned (ok)
- Real-time features? Not mentioned (assume REST polling)
- Mobile app? Not mentioned (assume web only)
- Rate limiting? Not mentioned (should add)
```

**Ask Clarifying Questions if Needed:**

If anything is unclear:
- "You mentioned PostgreSQL and Redis. Do you need connection pooling config?"
- "You said AWS Lambda. Should we scaffold serverless framework config or vanilla Node?"
- "Need real-time features? This affects websocket setup."

### Step 3: Design complete project structure and tool stack

Design the full scaffold based on requirements.

**For Python API Service:**

```
project-name/
├── src/
│   ├── __init__.py
│   ├── main.py                    # Application entry point
│   ├── config.py                  # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py              # API route definitions
│   │   ├── dependencies.py        # Route dependencies (auth, db)
│   │   └── schemas.py             # Request/response schemas
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py              # Core business models
│   │   ├── services.py            # Business logic
│   │   └── repositories.py        # Data access layer
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── database.py            # Database connection
│   │   ├── cache.py               # Redis cache
│   │   └── external_services.py   # Stripe, Auth0, etc.
│   └── shared/
│       ├── __init__.py
│       ├── exceptions.py          # Custom exceptions
│       ├── utils.py               # Utility functions
│       └── logging.py             # Logging configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_repositories.py
│   ├── integration/
│   │   ├── test_api_routes.py
│   │   ├── test_database.py
│   │   └── test_external_services.py
│   └── fixtures/
│       ├── test_data.py
│       └── factories.py
├── scripts/
│   ├── setup_db.py                # Database initialization
│   ├── migrate.py                 # Database migrations
│   └── seed.py                    # Seed test data
├── docs/
│   ├── API.md                     # API documentation
│   ├── ARCHITECTURE.md            # Architecture overview
│   ├── DATABASE.md                # Database schema
│   └── SETUP.md                   # Local setup guide
├── .github/
│   └── workflows/
│       ├── ci.yml                 # Test and lint workflow
│       ├── deploy.yml             # Deployment workflow
│       └── security.yml           # Security scanning
├── docker/
│   ├── Dockerfile                 # Production image
│   ├── Dockerfile.dev             # Development image
│   └── docker-compose.yml         # Local development stack
├── .env.example                   # Environment variables template
├── .env.development               # Local dev environment
├── .gitignore
├── .editorconfig
├── pyproject.toml                 # Package config
├── poetry.lock                    # Dependency lock file
├── pytest.ini                     # Test configuration
├── .pylintrc                      # Linter configuration
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE

**For TypeScript/Next.js Web App:**

```
project-name/
├── src/
│   ├── app/
│   │   ├── layout.tsx             # Root layout
│   │   ├── page.tsx               # Home page
│   │   ├── api/
│   │   │   └── [route].ts         # API routes
│   │   └── [page]/
│   │       └── page.tsx           # Pages
│   ├── components/                # Reusable components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Header.tsx
│   ├── lib/
│   │   ├── api.ts                 # API client
│   │   ├── auth.ts                # Authentication
│   │   └── utils.ts               # Utilities
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   └── useLocalStorage.ts
│   ├── types/
│   │   └── index.ts               # TypeScript types
│   └── styles/
│       └── globals.css
├── tests/
│   ├── unit/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   ├── integration/
│   │   └── pages/
│   ├── e2e/
│   │   └── [test].spec.ts
│   └── fixtures/
├── public/
│   ├── images/
│   ├── icons/
│   └── favicon.ico
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── e2e.yml
│       └── deploy.yml
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── .env.example
├── tsconfig.json
├── next.config.js
├── package.json
├── pnpm-lock.yaml
├── vitest.config.ts               # Unit test config
├── playwright.config.ts           # E2E test config
├── .eslintrc.json
├── .prettierrc
├── README.md
├── CONTRIBUTING.md
└── LICENSE
```

**Tool Stack Decision Matrix:**

| Aspect | Option A | Option B | Recommendation |
|--------|----------|----------|-----------------|
| Language | Python | Go | Based on team expertise |
| Framework | FastAPI | Django | FastAPI for APIs, Django for full-stack |
| Database | PostgreSQL | MongoDB | PostgreSQL for relational, Mongo for docs |
| Testing | pytest | unittest | pytest is more readable |
| Linting | ruff | black | ruff is faster, all-in-one |
| Type Checking | pyright | mypy | pyright is stricter |
| Container | Docker | Podman | Docker is industry standard |
| CI/CD | GitHub Actions | GitLab CI | Based on repository host |

### Step 4: Document proposed architecture with rationale

Present the complete design to user for review:

```markdown
## Scaffolding Proposal: Chat API Service

### Project Overview
- **Purpose:** Real-time chat application API
- **Language:** Python 3.12+
- **Framework:** FastAPI with WebSockets
- **Deployment:** Docker on Kubernetes

### Architecture Layers

**API Layer** (`src/api/`)
- Handles HTTP requests and WebSocket connections
- Manages request validation and response formatting
- Responsible for routing and middleware

**Domain Layer** (`src/domain/`)
- Contains pure business logic (no frameworks)
- Defines core models: User, Chat, Message
- Implements business rules and constraints
- Testable in isolation

**Infrastructure Layer** (`src/infrastructure/`)
- Database access (PostgreSQL)
- Cache layer (Redis)
- External service integration
- Logging and monitoring

### Key Design Decisions

1. **Layered architecture** - Separation of concerns, testability
2. **FastAPI for async** - Handles concurrent connections efficiently
3. **PostgreSQL + Redis** - Persistent + in-memory caching
4. **Pydantic for validation** - Type-safe request/response handling
5. **Docker containerization** - Consistent across environments
6. **GitHub Actions CI/CD** - Integrated with repository

### Dependency Choices

```toml
[dependencies]
fastapi = "^0.104.0"
uvicorn = "^0.24.0"
sqlalchemy = "^2.0.0"
psycopg2-binary = "^2.9.0"
redis = "^5.0.0"
pydantic = "^2.0.0"
python-jose = "^3.3.0"  # JWT tokens
stripe = "^7.0.0"
```

### Testing Strategy

- Unit tests: Fast, isolated, domain logic only (pytest)
- Integration tests: Database + API together (pytest with fixtures)
- E2E tests: Full API requests (pytest with test client)
- Coverage target: 80%+

### Environment Configuration

Required variables (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `JWT_SECRET` - Secret for JWT signing
- `STRIPE_API_KEY` - Stripe API credential
- `LOG_LEVEL` - Debug/Info/Warning/Error

### CI/CD Pipeline

1. **Test** - Run pytest with coverage (must pass)
2. **Lint** - Run ruff linter (must pass)
3. **Type check** - Run pyright (must pass)
4. **Build** - Docker image build
5. **Push** - Push to container registry
6. **Deploy** - Deploy to staging/production

### Directory Rationale

- `src/api/` - API layer, isolated from business logic
- `src/domain/` - Pure domain logic, testable without frameworks
- `src/infrastructure/` - Framework-specific code, database, external services
- `tests/` - Test files mirror source layout for easy navigation
- `scripts/` - Operational scripts (setup, migrate, seed)
- `docs/` - Architecture and usage documentation
- `.github/workflows/` - CI/CD pipeline definitions
- `docker/` - Container configuration

### Questions for You

- Does this structure match your mental model?
- Any adjustments needed to dependencies or tools?
- Should we add any additional subdirectories (e.g., `events/` for event handling)?
- Any compliance/audit requirements we should scaffold for?

Ready to proceed? [YES / NO / REVISE]
```

### Step 5: Get user confirmation before generating any files

Do NOT create any files until user confirms.

**Confirmation Checkpoint:**

```
You've designed the scaffold. Now ask:

"The proposal above shows the directory structure, tool stack, 
and design decisions. Does everything look good to proceed with file generation?

Please confirm:
[ ] Directory structure matches your needs
[ ] Language/framework choices are correct
[ ] Dependencies look reasonable
[ ] Testing approach makes sense
[ ] CI/CD strategy aligns with goals

Answer: YES, proceed with generation
        NO, let me revise something
        REVISE: Specific changes needed
"
```

**If User Revises:**
- Update the proposal in Step 3
- Highlight the changes made
- Get re-confirmation before proceeding

### Step 6: Create directory structure

Once confirmed, create all directories:

```bash
# Core directories
mkdir -p src/{api,domain,infrastructure,shared}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p scripts docs

# Configuration directories
mkdir -p .github/workflows docker config

# Create all subdirectories for organization
mkdir -p src/{api,domain,infrastructure,shared}
mkdir -p tests/{unit,integration,e2e,fixtures}
mkdir -p docs/{architecture,guides,api}

# Development planning structure
mkdir -p planning/{current,complete,backlog}/{adrs,execution-plans,features,prds}
mkdir -p planning/research
mkdir -p _temp
```

**Verification:**
```bash
find . -type d -name __pycache__ -prune -o -type d -print | sort
# Should show complete structure matching proposal
```

### Step 7: Generate language-specific boilerplate files

Create core boilerplate with TODO comments for user implementation.

**Python Example - `src/main.py`:**

```python
"""
Application entry point.

This module initializes and runs the FastAPI application.

TODO: Update application metadata below
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api.routes import router as api_router
from src.config import settings
from src.infrastructure.database import init_db, close_db
from src.shared.exceptions import APIError

# Configure logging
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    await init_db()
    logger.info("Application started")
    yield
    # Shutdown
    await close_db()
    logger.info("Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="TODO: Your Project Name",
    description="TODO: Your project description",
    version="0.1.0",
    lifespan=lifespan,
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.exception_handler(APIError)
async def api_error_handler(request, exc: APIError):
    """Handle application errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.message},
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
```

**Python Example - `src/domain/models.py`:**

```python
"""
Core domain models.

These models represent the core business entities and should contain
only pure business logic, no framework-specific code.

TODO: Define your domain models here
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """User domain model."""
    
    id: str
    email: str
    name: str
    created_at: datetime
    updated_at: datetime
    
    # TODO: Add user-specific fields
    # TODO: Add business logic methods


@dataclass
class Chat:
    """Chat domain model."""
    
    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    
    # TODO: Add chat-specific fields


@dataclass
class Message:
    """Message domain model."""
    
    id: str
    chat_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime
```

**Generate similar files for:**
- `src/api/routes.py` - Route definitions with TODO endpoints
- `src/api/schemas.py` - Pydantic request/response models
- `src/domain/services.py` - Business logic service stubs
- `src/infrastructure/database.py` - Database connection setup
- `tests/unit/test_models.py` - Example unit test
- `tests/conftest.py` - Pytest fixtures

### Step 8: Create comprehensive configuration files

Set up all configuration and tooling files.

**`pyproject.toml` (Python):**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "chat-api"
version = "0.1.0"
description = "TODO: Your project description"
readme = "README.md"
license = {text = "MIT"}
authors = [
    {name = "TODO: Your Name", email = "TODO: your.email@example.com"},
]
requires-python = ">=3.12"

dependencies = [
    "fastapi==0.104.0",
    "uvicorn[standard]==0.24.0",
    "sqlalchemy==2.0.0",
    "psycopg2-binary==2.9.0",
    "redis==5.0.0",
    "pydantic==2.0.0",
    "pydantic-settings==2.0.0",
    "python-jose[cryptography]==3.3.0",
    "python-multipart==0.0.6",
    "stripe==7.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest==7.4.0",
    "pytest-cov==4.1.0",
    "pytest-asyncio==0.21.0",
    "pytest-mock==3.11.0",
    "ruff==0.1.0",
    "pyright==1.1.300",
    "black==23.0.0",
    "isort==5.12.0",
    "pre-commit==3.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--cov=src",
    "--cov-report=html",
    "--cov-report=term-missing:skip-covered",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
]

[tool.ruff]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "UP",   # pyupgrade
]
ignore = ["E501"]  # Line length handled by formatter
line-length = 100
target-version = "py312"

[tool.black]
line-length = 100
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 100

[tool.pyright]
include = ["src"]
exclude = ["**/__pycache__", "tests"]
typeCheckingMode = "strict"
reportUnnecessaryIsInstance = false
reportPrivateUsage = false
```

**`package.json` (TypeScript/Next.js):**

```json
{
  "name": "chat-web",
  "version": "0.1.0",
  "description": "TODO: Your project description",
  "type": "module",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "test": "vitest run --coverage",
    "test:watch": "vitest --watch",
    "lint": "eslint . --ext .ts,.tsx",
    "type-check": "tsc --noEmit",
    "format": "prettier --write ."
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "next": "^14.0.0",
    "axios": "^1.6.0",
    "zustand": "^4.4.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^6.0.0",
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0",
    "@vitest/coverage-v8": "^1.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "prettier": "^3.0.0",
    "playwright": "^1.40.0"
  },
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=8.0.0"
  }
}
```

**Create `.env.example`:**

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/chat_db

# Cache
REDIS_URL=redis://localhost:6379/0

# Security
JWT_SECRET=TODO-CHANGE-THIS-IN-PRODUCTION-VERY-LONG-RANDOM-STRING
JWT_EXPIRATION_HOURS=24

# External Services
STRIPE_API_KEY=sk_test_TODO_YOUR_KEY
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=TODO_YOUR_CLIENT_ID

# Application
LOG_LEVEL=INFO
DEBUG=False
ENVIRONMENT=development
```

### Step 9: Set up testing scaffolding and CI/CD pipelines

Create test structure and GitHub Actions workflows.

**`tests/conftest.py` (Pytest Fixtures):**

```python
"""
Pytest configuration and shared fixtures.

Fixtures defined here are available to all tests.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: Import your application models
# TODO: Create database fixtures
# TODO: Create mock service fixtures


@pytest.fixture(scope="session")
def db_engine():
    """Create test database engine."""
    # TODO: Use in-memory SQLite or test database
    # engine = create_engine("sqlite:///:memory:")
    # yield engine
    pass


@pytest.fixture
def db_session(db_engine):
    """Create database session for each test."""
    # TODO: Create tables
    # TODO: Provide session to test
    # TODO: Cleanup after test
    pass


@pytest.fixture
def client(db_session):
    """Create FastAPI test client."""
    # TODO: Import your app
    # TODO: Create test client with test db
    pass
```

**`.github/workflows/ci.yml` (GitHub Actions):**

```yaml

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: chat_db_test
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install poetry
          poetry install
      
      - name: Lint with ruff
        run: poetry run ruff check .
      
      - name: Type check with pyright
        run: poetry run pyright
      
      - name: Run tests
        run: poetry run pytest --cov
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/chat_db_test
          REDIS_URL: redis://localhost:6379/0
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

### Step 10: Create Docker and deployment configuration

Generate Docker-related configuration.

**`docker/Dockerfile` (Production):**

```dockerfile
# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install --no-dev --no-interaction --no-ansi

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /app/.venv .venv

# Copy application code
COPY src src

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**`docker/docker-compose.yml` (Local Development):**

```yaml
version: '3.9'

services:
  api:
    build:
      context: ..
      dockerfile: docker/Dockerfile.dev
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/chat_db
      - REDIS_URL=redis://redis:6379/0
      - DEBUG=True
      - LOG_LEVEL=DEBUG
    volumes:
      - ../src:/app/src
      - ../tests:/app/tests
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=chat_db
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### Step 11: Generate documentation templates

Create starter documentation files.

**`README.md`:**

```markdown
# TODO: Your Project Name

> TODO: One-sentence description of what this project does.

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL 13+
- Redis 6+

### Local Development

1. Clone the repository
2. Create `.env` from `.env.example` and update values
3. Start services: `docker-compose up`
4. Install dependencies: `poetry install`
5. Run tests: `poetry run pytest`
6. Start API: `poetry run uvicorn src.main:app --reload`

The API will be available at http://localhost:8000

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test
poetry run pytest tests/unit/test_models.py -v
```

### Code Quality

```bash
# Lint code
poetry run ruff check .

# Type checking
poetry run pyright

# Format code
poetry run black .
```

## Project Structure

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed architecture overview.

- `src/` - Application source code
- `tests/` - Test files
- `docs/` - Documentation
- `scripts/` - Utility scripts
- `docker/` - Docker configuration

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT - See [LICENSE](LICENSE) for details.
```

**`docs/ARCHITECTURE.md`:**

```markdown
# Architecture

## Overview

This document describes the high-level architecture of the Chat API.

## Layers

### API Layer (`src/api/`)
Handles HTTP requests and responses.
- Routes: Endpoint definitions
- Schemas: Request/response validation
- Dependencies: Shared dependencies (database, auth)

### Domain Layer (`src/domain/`)
Pure business logic with no framework dependencies.
- Models: Core domain entities
- Services: Business logic
- Repositories: Data access

### Infrastructure Layer (`src/infrastructure/`)
External dependencies and framework integration.
- Database: PostgreSQL connection and ORM
- Cache: Redis connection
- External Services: Third-party integrations

## Data Flow

```
HTTP Request → API Layer → Validation → Domain Logic → 
Infrastructure → Response → HTTP Response
```

## Technology Stack

- **Runtime:** Python 3.12
- **Framework:** FastAPI
- **Database:** PostgreSQL
- **Cache:** Redis
- **Testing:** Pytest
- **Container:** Docker

## Design Decisions

See [docs/DECISIONS.md](DECISIONS.md) for detailed architectural decisions.
```

### Step 12: Verify all commands work end-to-end

Test that the scaffolded project actually builds and runs.

**Python Verification:**

```bash
# Test package manager works
uv sync

# Test linting
ruff check .

# Test type checking
pyright

# Test tests can run
pytest --collect-only

# Verify imports work
python -c "import src.main; print('Imports OK')"

# Start application (should fail without env setup, but that's ok)
python src/main.py 2>&1 | head -5
# Should see import errors about missing database, which is expected
```

**TypeScript Verification:**

```bash
# Install dependencies
pnpm install

# Check linting
pnpm lint

# Type check
pnpm type-check

# Build
pnpm build

# Run tests
pnpm test
```

**Verification Checklist:**

```markdown
- [ ] All directories created
- [ ] Package manager works (uv sync / npm install)
- [ ] Linting runs (ruff check / eslint)
- [ ] Type checking runs (pyright / tsc)
- [ ] Tests can be collected (pytest --collect-only)
- [ ] Docker builds successfully
- [ ] docker-compose up starts without errors
- [ ] Application runs (shows health check endpoint)
```

If any command fails, fix before proceeding to Step 13.

### Step 13: Create initial commit with scaffolding

Commit the complete scaffold with clear message.

**Commit Message:**

```
chore: scaffold project structure and configuration

## Project Setup
- Project: Chat API Service
- Language: Python 3.12 with FastAPI
- Database: PostgreSQL
- Cache: Redis
- Testing: Pytest

## Changes
- Created layered architecture:
  - api/ for routes and schemas
  - domain/ for business logic
  - infrastructure/ for databases and external services
- Set up testing structure with unit, integration, and fixtures
- Configured pytest, ruff, pyright, black
- Created Dockerfile for production image
- Created docker-compose.yml for local development
- Generated GitHub Actions CI/CD pipeline
- Created documentation templates (README, ARCHITECTURE, etc)
- Generated .env.example with required variables

## Scaffolding Status
All commands verified working:
- ✓ uv sync (dependency installation)
- ✓ ruff check (linting)
- ✓ pyright (type checking)
- ✓ pytest --collect-only (test discovery)
- ✓ docker build (image creation)
- ✓ docker-compose up (local dev stack)

## Getting Started
1. Copy .env.example to .env and update values
2. Run: docker-compose up
3. Run: uv sync && poetry install
4. Run: pytest to verify tests work
5. Implement core domain models in src/domain/models.py

## Next Steps
- Implement User, Chat, Message domain models
- Create API routes in src/api/routes.py
- Implement business logic in src/domain/services.py
- Create database models and migrations
- Write tests as features are implemented

## References
- Architecture: docs/ARCHITECTURE.md
- Setup guide: docs/SETUP.md
- Contributing: CONTRIBUTING.md
```

**Push to repository:**

```bash
git add .
git commit -m "chore: scaffold project structure and configuration" --no-verify
git push origin main  # Or feature branch
```

---

## Common Mistakes & How to Avoid Them

### ❌ Pitfall 1: Scaffolding Before Requirements Are Clear
**What:** Starting to generate files without understanding project needs
**Risk:** Wrong structure/tools chosen, have to refactor later
**Solution:** Always complete Step 1 (gather requirements) first

### ❌ Pitfall 2: Generating Without User Confirmation
**What:** Creating files without asking for approval of proposed structure
**Risk:** Structure doesn't match user's vision, frustration
**Solution:** Always get confirmation in Step 5 before any file generation

### ❌ Pitfall 3: Not Verifying Scaffold Actually Works
**What:** Creating files but not testing they build/run
**Risk:** User gets broken scaffold, waste time debugging
**Solution:** Always do Step 12 verification before committing

### ❌ Pitfall 4: Over-Scaffolding Complex Features
**What:** Generating code for features not yet approved (like authentication)
**Risk:** User doesn't need it, adds complexity
**Solution:** Only scaffold structure and minimal examples, no feature logic

### ❌ Pitfall 5: Inconsistent Across Language/Framework Choices
**What:** Scaffold doesn't follow language/framework conventions
**Risk:** Generated code looks foreign to team familiar with that ecosystem
**Solution:** Study language conventions before scaffolding (see core-conventions)

### ❌ Pitfall 6: Forgetting Environment Configuration
**What:** Not creating .env.example with all required variables
**Risk:** User doesn't know what configuration is needed
**Solution:** Document every environment variable required

### ❌ Pitfall 7: Not Including CI/CD from the Start
**What:** Scaffolding without GitHub Actions / CI configuration
**Risk:** Team has to set up pipelines separately
**Solution:** Always include basic CI/CD template

---

## Language-Specific Scaffolding Patterns

### Python (FastAPI)
- Use layered architecture: api → domain → infrastructure
- Include async/await support
- Use Pydantic for validation
- Include both poetry and uv support

### TypeScript (Next.js)
- Use App Router (not Pages Router)
- Include React hooks and context
- Set up testing with Vitest
- Include E2E testing with Playwright

### Go
- Use standard library patterns
- Include dependency injection
- Set up interfaces for mockability
- Include Makefile for common tasks

### Rust
- Use workspaces for multi-crate projects
- Include error handling with thiserror
- Set up logging with tracing
- Include both unit and integration tests

---

## Performance Optimization

### For Large Scaffolds
- Generate structure in parallel where possible
- Cache template content
- Minimize file I/O operations

### For Complex Projects
- Break monolithic scaffold into smaller phases
- Allow user to select which parts to generate
- Provide --minimal and --full options

