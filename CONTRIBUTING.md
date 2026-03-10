# Contributing to Promptosaurus

Welcome! This guide covers how to contribute to Promptosaurus.

## Getting Started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) for package management

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/promptosaurus.git
   cd promptosaurus
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   # or with uv
   uv pip install -e .
   ```

4. Install development dependencies:
   ```bash
   uv sync --dev
   ```

## Development Workflow

### Running Tests

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit

# With coverage
pytest --cov=promptosaurus --cov-report=html
```

### Linting and Formatting

We use Ruff for linting and formatting:

```bash
# Check for issues
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
ruff format .

# Type checking
pyright
```

### Adding a New Mode

1. Add the mode to `MODES` in `promptosaurus/registry.py`
2. Add prompt files to `MODE_FILES[mode]`
3. Add builder outputs in `promptosaurus/builders/`
4. Run `promptosaurus validate` to verify

### Adding a New Prompt File

1. Create the `.md` file in `promptosaurus/prompts/agents/{mode}/`
2. Add to `MODE_FILES[mode]` in `promptosaurus/registry.py`
3. Add `CONCAT_ORDER` entry if it should appear in Cline/Cursor/Copilot
4. Run `promptosaurus validate` to confirm

## Branch Naming

- `feat/*` — New features
- `bugfix/*` — Bug fixes
- `hotfix/*` — Urgent production fixes
- `docs/*` — Documentation only
- `refactor/*` — Code refactoring

## Commit Messages

Use clear, descriptive commit messages:
- `feat: add new mode for security reviews`
- `fix: resolve missing import in registry`
- `docs: update installation instructions`

## Pull Requests

1. Create a feature branch from `main`
2. Make your changes
3. Run tests and linting locally
4. Push and create a PR
5. Ensure CI passes

## Code Style

- Follow PEP 8
- Use type hints
- Use Ruff for formatting
- Keep lines under 100 characters when practical
