---
type: subagent
agent: orchestrator
name: devops
variant: verbose
version: 1.0.0
description: CI/CD, Docker, env config, deployment automation with examples
tools: [read]
---

# DevOps Orchestration (Verbose)

Complete guide for generating CI/CD pipelines, Dockerfiles, environment configuration, and deployment checklists.

---

## CI/CD Pipeline Generation

### Before Generating

**Ask these questions if not provided:**
1. CI platform: GitHub Actions, GitLab CI, CircleCI, Buildkite?
2. Deployment target: AWS (Lambda, ECS, EC2), GCP (Cloud Run, GKE), Vercel, Netlify?
3. Environment strategy: staging + production? Feature branch deployments?

**Read project structure:**
- Package manager (from pyproject.toml, package.json, go.mod)
- Test framework (pytest, vitest, go test)
- Build artifacts (Docker image, static bundle, binary)

### Pipeline Structure

**Include these stages:**

1. **Install Dependencies (with caching)**
   - Cache based on lock file hash
   - Restore from cache before install
   - Save cache after successful install

2. **Lint + Type Check**
   - Run in parallel with tests
   - Use project-specific linter config

3. **Unit Tests**
   - Run with coverage reporting
   - Fail if coverage below threshold

4. **Integration Tests (if applicable)**
   - Use test database or mocked services
   - Run after unit tests pass

5. **Build**
   - Docker image OR static bundle OR binary
   - Tag with commit SHA

6. **Deploy (if on main/staging branch)**
   - Deploy to appropriate environment
   - Use environment-specific secrets

### GitHub Actions Example (Python with pytest)

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      
      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
          restore-keys: |
            ${{ runner.os }}-pip-
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov ruff
      
      - name: Lint with ruff
        run: ruff check .
      
      - name: Type check with pyright
        run: pyright
      
      - name: Run tests with coverage
        run: pytest --cov=src --cov-report=xml --cov-branch
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
          fail_ci_if_error: true

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker image
        run: docker build -t myapp:${{ github.sha }} .
      
      - name: Push to registry
        run: |
          echo "${{ secrets.DOCKER_PASSWORD }}" | docker login -u "${{ secrets.DOCKER_USERNAME }}" --password-stdin
          docker push myapp:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to AWS Lambda
        run: |
          aws lambda update-function-code \
            --function-name my-function \
            --image-uri myapp:${{ github.sha }}
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          AWS_REGION: us-east-1
```

### Common Pitfalls

❌ **Don't hardcode secrets:**
```yaml
env:
  DATABASE_URL: "postgresql://user:password@host/db"  # ❌ NEVER
```

✅ **Use CI secrets:**
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}  # ✅ Correct
```

❌ **Don't run expensive tests on every PR:**
```yaml
- name: Run all tests
  run: pytest tests/  # ❌ Includes slow integration tests
```

✅ **Separate fast and slow tests:**
```yaml
- name: Run unit tests
  run: pytest tests/unit/  # ✅ Fast tests on every PR

- name: Run integration tests
  if: github.ref == 'refs/heads/main'
  run: pytest tests/integration/  # ✅ Slow tests on main only
```

---

## Dockerfile Generation

### Multi-Stage Build Pattern

**Why multi-stage?**
- Smaller final image (no build tools)
- Faster deployments
- Better security (fewer attack surfaces)

### Python Example

```dockerfile
# Stage 1: Builder
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY requirements.txt .

# Install Python dependencies to /install
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.12-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Add local bin to PATH
ENV PATH=/root/.local/bin:$PATH

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### .dockerignore

```
# Version control
.git/
.gitignore

# Python
__pycache__/
*.py[cod]
*$py.class
.pytest_cache/
.coverage
htmlcov/

# Virtual environments
venv/
env/
.venv/

# IDE
.vscode/
.idea/
*.swp

# CI/CD
.github/
.gitlab-ci.yml

# Documentation
docs/
*.md

# Tests
tests/

# Environment files
.env
.env.local
```

### Common Mistakes

❌ **Running as root:**
```dockerfile
# ❌ Security risk
CMD ["python", "app.py"]
```

✅ **Create and use non-root user:**
```dockerfile
# ✅ Secure
RUN useradd -m appuser
USER appuser
CMD ["python", "app.py"]
```

❌ **Installing everything in final image:**
```dockerfile
# ❌ Large image with build tools
RUN apt-get install gcc make cmake
```

✅ **Multi-stage to exclude build tools:**
```dockerfile
# ✅ Build tools only in builder stage
FROM python:3.12 AS builder
RUN apt-get install gcc

FROM python:3.12-slim
# No gcc in final image
```

---

## Environment Configuration

### .env.example Template

```bash
# ======================
# Database Configuration
# ======================
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10

# ======================
# Authentication & Security
# ======================
# SECRET: Do not commit actual value
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32
# SECRET: Do not commit actual value
ENCRYPTION_KEY=generate-with-openssl-rand-hex-32

SESSION_TIMEOUT_MINUTES=30
PASSWORD_MIN_LENGTH=12

# ======================
# External Services
# ======================
# SECRET: Do not commit actual value
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# SECRET: Do not commit actual value
SENDGRID_API_KEY=SG....

# ======================
# Application Settings
# ======================
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=false

# ======================
# Feature Flags
# ======================
FEATURE_WEBHOOKS_ENABLED=true
FEATURE_BETA_UI=false
```

### Config Validation Module (Python)

```python
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    """Application settings with validation."""
    
    # Database
    database_url: str = Field(..., description="PostgreSQL connection string")
    database_pool_size: int = Field(default=20, ge=1, le=100)
    
    # Secrets
    jwt_secret_key: str = Field(..., min_length=32, description="JWT signing key")
    encryption_key: str = Field(..., min_length=32, description="Data encryption key")
    
    # External services
    stripe_secret_key: str | None = Field(default=None, description="Stripe API key")
    sendgrid_api_key: str | None = Field(default=None, description="SendGrid API key")
    
    # Application
    app_env: str = Field(default="development", pattern="^(development|staging|production)$")
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    debug: bool = Field(default=False)
    
    # Feature flags
    feature_webhooks_enabled: bool = Field(default=False)
    feature_beta_ui: bool = Field(default=False)
    
    @validator("jwt_secret_key", "encryption_key")
    def validate_secrets(cls, v):
        """Ensure secrets are not placeholder values."""
        if v in ("changeme", "secret", "test"):
            raise ValueError("Secret must not be a placeholder value")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

# Fail fast on startup if config is invalid
settings = Settings()
```

### Environment Differences

| Variable | Local | Staging | Production |
|----------|-------|---------|------------|
| `DATABASE_URL` | localhost | staging-db.internal | prod-db.internal |
| `DEBUG` | true | true | **false** |
| `LOG_LEVEL` | DEBUG | INFO | WARNING |
| `FEATURE_WEBHOOKS_ENABLED` | true | true | false (until tested) |
| `SESSION_TIMEOUT_MINUTES` | 60 | 30 | 15 |

---

## Deployment Checklist

### Pre-Deployment

**Code & Tests:**
- [ ] All tests passing in CI
- [ ] Code review approved
- [ ] No merge conflicts with main
- [ ] Coverage meets threshold (≥80%)

**Database:**
- [ ] Migration scripts reviewed
- [ ] Backward compatible (can roll back without data loss)
- [ ] No table locks on large tables
- [ ] Migration tested on staging with production-size data

**Configuration:**
- [ ] Environment variables documented in .env.example
- [ ] Secrets rotated if compromised
- [ ] Feature flags set correctly for environment

### Deployment

**Execute:**
- [ ] Run database migrations
- [ ] Deploy application code
- [ ] Verify health check endpoint responds
- [ ] Check logs for startup errors

**Smoke Tests (specific, not generic):**
- [ ] User can log in with valid credentials
- [ ] API endpoint `/api/users/me` returns 200
- [ ] Webhook delivery succeeds for test event
- [ ] Background job processes within 5 seconds

### Post-Deployment

**Observability:**
- [ ] Error rate < 1% (check logs/metrics)
- [ ] Response time p95 < 500ms
- [ ] No spike in 500 errors
- [ ] Database connection pool not exhausted

**Rollback Plan:**
- [ ] Rollback command documented: `git revert <commit> && deploy.sh`
- [ ] Database rollback script ready (if migration applied)
- [ ] Estimated rollback time: 5 minutes

### Migration-Specific Risks

❌ **Adding NOT NULL column without default:**
```sql
-- ❌ Will lock table and fail on existing rows
ALTER TABLE users ADD COLUMN phone VARCHAR(20) NOT NULL;
```

✅ **Add with default, then backfill:**
```sql
-- ✅ Safe: add with default
ALTER TABLE users ADD COLUMN phone VARCHAR(20) DEFAULT '';

-- ✅ Backfill in batches
UPDATE users SET phone = '' WHERE phone IS NULL;

-- ✅ Add constraint after backfill
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
```

❌ **Renaming column without backward compatibility:**
```sql
-- ❌ Breaks old code immediately
ALTER TABLE users RENAME COLUMN email TO email_address;
```

✅ **Gradual migration:**
```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN email_address VARCHAR(255);

-- Step 2: Backfill data
UPDATE users SET email_address = email;

-- Step 3: Deploy code using both columns
-- (Code reads from email_address, writes to both)

-- Step 4: Drop old column after deploy
ALTER TABLE users DROP COLUMN email;
```
