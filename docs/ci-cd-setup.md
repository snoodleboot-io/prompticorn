# CI/CD Pipeline Documentation

## Overview

This document describes the GitHub Actions CI/CD pipeline for the `promptcli` package. The pipeline implements comprehensive testing, building, and publishing workflows with semantic versioning.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CI/CD Pipeline                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Phase 1   │───▶│   Phase 2   │───▶│   Phase 3   │───▶│   Phase 4   │  │
│  │    TEST     │    │    BUILD    │    │   PUBLISH   │    │   VERIFY    │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
│         │                  │                  │                  │          │
│    ┌────┴────┐        ┌────┴────┐       ┌────┴────┐       ┌────┴────┐      │
│    ▼         ▼        ▼         ▼       ▼         ▼       ▼         ▼      │
│  Lint    Unit Tests  Build   Install   Test    Verify   Install   Test     │
│           (Py      Package  Test      PyPI     PyPI    from      Package   │
│         3.10-3.14)          Package   Publish  Publish  Index              │
│  Integration                                                                │
│  Tests                                                                      │
│  Security                                                                   │
│  Tests                                                                      │
│  Slow Tests                                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Phase 1: Test

### Lint & Format Check
- **Trigger**: All pushes and PRs
- **Python Version**: 3.11
- **Tools**:
  - `ruff check` - Linting
  - `ruff format --check` - Format verification
  - `mypy` - Type checking

### Unit Tests
- **Trigger**: All pushes and PRs
- **Matrix Strategy**: Python 3.10, 3.11, 3.12, 3.13, 3.14
- **Parallelization**: Tests run in parallel across Python versions (fail-fast disabled)
- **Artifacts**: Test results, coverage reports (XML and HTML)
- **Coverage**: Uploaded to Codecov for Python 3.11 run

### Integration Tests
- **Trigger**: After lint and unit tests pass
- **Python Version**: 3.11
- **Scope**: Integration test suite in `tests/integration/`

### Security Tests
- **Trigger**: After lint and unit tests pass
- **Python Version**: 3.11
- **Scope**: Security-focused tests in `tests/security/`

### Slow Tests
- **Trigger**: Only on `main` and `feat/*` branches
- **Python Version**: 3.11
- **Scope**: Long-running tests in `tests/slow/`

## Phase 2: Build

### Package Build
- **Trigger**: After integration and security tests pass
- **Steps**:
  1. Calculate semantic version (see [Versioning Strategy](#versioning-strategy))
  2. Update `pyproject.toml` with calculated version
  3. Build wheel and sdist using `uv build`
  4. Upload build artifacts
  5. Test package installability in isolated venv
  6. Verify CLI entry point (`prompt --help`)
  7. Verify package import

## Phase 3: Publish

### Test PyPI (feat/* branches)
- **Trigger**: Successfully built package from `feat/*` branch
- **Environment**: `testpypi`
- **Authentication**: OIDC Trusted Publishing (no API tokens)
- **Behavior**: Skip existing versions (allows re-runs)

### PyPI (main branch)
- **Trigger**: Successfully built package from `main` branch
- **Environment**: `pypi`
- **Authentication**: OIDC Trusted Publishing (no API tokens)
- **Behavior**: Fail on duplicate versions (prevents overwrites)

## Phase 4: Verify

### Post-Publish Verification
- **Trigger**: After successful publish
- **Steps**:
  1. Wait for package index propagation (30-60 seconds)
  2. Install package from respective index
  3. Verify CLI functionality
  4. Verify package import

## Versioning Strategy

The pipeline implements automatic semantic versioning based on event type:

| Event Type | Version Format | Example | Publishes | Description |
|------------|----------------|---------|-----------|-------------|
| Push to non-main branch | `MAJOR.MINOR.PATCH.devN+SHA` | `0.1.1.dev42+abc1234` | No | Dev build for local testing |
| Pull Request | `MAJOR.MINOR.PATCHrcN` | `0.1.1rc42` | TestPyPI | Release candidate with patch bump |
| Push to `main` (merge) | `MAJOR.MINOR.0` | `0.2.0` | PyPI | Stable release with minor bump |

### Version Calculation

The version is calculated by `.github/scripts/calculate_version.py`:

1. **MAJOR**: Configured via `MAJOR_VERSION` env var in workflow (default: 0)
2. **MINOR**: Read from `pyproject.toml`, incremented on main merge
3. **PATCH**: Read from `pyproject.toml`, incremented on PR builds
4. **Build Number**: Based on `GITHUB_RUN_NUMBER`

### Major Version Configuration

The major version is configured in `.github/workflows/ci-cd.yml`:

```yaml
env:
  MAJOR_VERSION: "0"  # Change this for breaking releases
```

When `MAJOR_VERSION` is changed, the minor version resets to 0:
- pyproject.toml: `0.5.3` with `MAJOR_VERSION=1` → Release: `1.0.0`

### Base Version Management

The `pyproject.toml` version serves as the base for calculating next versions:
- `version = "0.1.0"` → PR builds: `0.1.1rcN`, Main builds: `0.2.0`

To prepare for a new release cycle, update `pyproject.toml`:
```bash
# For minor release: keep as-is, CI will increment
# For major release: update MAJOR_VERSION env var in workflow
```

## Configuration

### Required Repository Secrets

The following secrets should be configured in GitHub:

| Secret | Required For | Description |
|--------|--------------|-------------|
| `CODECOV_TOKEN` | Coverage upload | Token for Codecov.io integration |

### PyPI Trusted Publishing Setup

No API tokens are required! The pipeline uses OIDC (OpenID Connect) for secure publishing:

#### Test PyPI Configuration

1. Go to [Test PyPI](https://test.pypi.org/manage/account/publishing/)
2. Add a new pending publisher:
   - **PyPI Project Name**: `promptcli`
   - **Owner**: Your GitHub username/organization
   - **Repository**: `promptcli`
   - **Workflow name**: `ci-cd.yml`
   - **Environment name**: `testpypi`

#### Production PyPI Configuration

1. Go to [PyPI](https://pypi.org/manage/account/publishing/)
2. Add a new pending publisher:
   - **PyPI Project Name**: `promptcli`
   - **Owner**: Your GitHub username/organization
   - **Repository**: `promptcli`
   - **Workflow name**: `ci-cd.yml`
   - **Environment name**: `pypi`

### GitHub Environments

Create two environments in your GitHub repository settings:

1. **`testpypi`**:
   - Protection rules: None required for test
   - URL: `https://test.pypi.org/p/promptcli`

2. **`pypi`**:
   - Protection rules: Recommended to require approval
   - URL: `https://pypi.org/p/promptcli`

## Workflow Triggers

```yaml
on:
  push:
    branches:
      - main        # Triggers full pipeline with PyPI publish (minor bump)
  pull_request:
    branches:
      - main        # Triggers full pipeline with TestPyPI publish (patch bump)
```

### Publish Behavior Matrix

| Event | Branch | Version Type | Publishes To |
|-------|--------|--------------|--------------|
| `push` | `main` | Stable (minor bump) | PyPI |
| `push` | other | Dev build (.devN+SHA) | Nowhere (build only) |
| `pull_request` | any | RC (patch bump) | TestPyPI |

## Concurrency Control

The pipeline uses concurrency groups to prevent overlapping runs:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

This ensures:
- Only one run per branch at a time
- Older runs are cancelled when new commits are pushed
- Main branch runs are never interrupted by other branches

## Artifact Retention

| Artifact Type | Retention | Purpose |
|---------------|-----------|---------|
| Test Results | 30 days | Debugging and audit trails |
| Coverage Reports | 30 days | Coverage analysis |
| Build Artifacts | 7 days | Short-term for verification |

## Local Testing

To test the pipeline locally:

```bash
# Install dependencies
uv sync --dev

# Run linting
uv run ruff check .
uv run ruff format --check .

# Run tests
uv run pytest tests/unit -v
uv run pytest tests/integration -v

# Build package
uv build

# Test install
pip install dist/*.whl
prompt --help
```

## Troubleshooting

### Build Failures

1. **Version conflicts**: Ensure base version in `pyproject.toml` is updated when releasing new MINOR versions
2. **Missing dependencies**: Check `pyproject.toml` dependencies and dev dependencies
3. **Import errors**: Verify package structure matches `tool.hatch.build.targets.wheel` config

### Publish Failures

1. **Trusted Publishing**: Verify OIDC configuration on PyPI/Test PyPI
2. **Environment protection**: Check GitHub environment settings
3. **Version already exists**: feat branches use `skip-existing: true`, main does not

### Test Failures

1. **Matrix failures**: Check Python version compatibility
2. **Slow tests**: Ensure proper test markers are applied
3. **Coverage upload**: Verify `CODECOV_TOKEN` secret is set

## Security Considerations

1. **No hardcoded secrets**: All authentication uses OIDC
2. **Environment protection**: PyPI environment requires approval
3. **Artifact retention**: Short retention limits exposure
4. **Concurrency**: Prevents race conditions in publishing

## Future Enhancements

Potential improvements to consider:

1. **Automatic changelog generation** from conventional commits
2. **Release notes automation** using GitHub releases
3. **Docker image building** and publishing
4. **Performance regression testing**
5. **Documentation deployment** to GitHub Pages
