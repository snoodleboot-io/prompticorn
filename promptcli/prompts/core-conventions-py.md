# Python Conventions

Language:             {{LANGUAGE}}           e.g., Python 3.11+
Runtime:              {{RUNTIME}}            e.g., CPython 3.11, PyPy
Package Manager:      {{PACKAGE_MANAGER}}        e.g., poetry, pip, uv
Linter:               {{LINTER}}             e.g., Ruff, flake8
Formatter:           {{FORMATTER}}          e.g., Ruff, Black
Abstract Class Style: {{ABSTRACT_CLASS_STYLE}}  e.g., abc, interface

## Python-Specific Rules

### Type Hints
- Type hints required on all public functions (use `pyright` or `mypy` to enforce)
- Use `dataclasses` or `pydantic` for data shapes, not raw dicts
- Use `T | None` instead of `typing.Optional[T]`. This is the standard for modern python
- Use `typing.TypeAlias` for complex type aliases

### Error Handling
- Use exception hierarchies — don't raise generic `Exception`
- Use `Result` pattern from `returns` library or custom Result type
- Never swallow errors silently — always log or re-raise with context
- Use `contextlib.contextmanager` for resource management

### Async
- Use `asyncio` — no mixing sync/async without explicit bridging
- Use `asyncpg` for async database access, not synchronous drivers
- Use `httpx` for async HTTP requests

### Imports
- Use absolute imports (no relative `..` imports)
- Group imports: stdlib → third-party → local (blank lines between)
- Use `__all__` to define public API

### Testing

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Mutation:       {{MUTATION_COVERAGE_%}}       e.g., 80%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests
- One function or method in isolation
- Mock all external dependencies (database, API calls, filesystem)
- Use `pytest` fixtures for setup/teardown
- Use `pytest.mark.parametrize` for table-driven tests
- Use `pytest.raises` for exception testing

##### Integration Tests
- Test at service or module boundary
- Use real database (testcontainers) or in-memory alternatives
- Test API endpoints, database queries, file operations
- Clean up test data after each test

##### Mutation Tests
- Use `mutmut` or `pytest-mutmut` to verify test quality
- Run after unit tests pass
- Aim to kill mutations in core business logic

##### Property-Based Tests
- Use `hypothesis` for generative testing
- Test edge cases automatically generated

#### Framework & Tools
Framework:         {{TESTING_FRAMEWORK}}       e.g., pytest
Mocking library:   {{MOCKING_LIBRARY}}             e.g., unittest.mock, pytest-mock
Coverage tool:    {{COVERAGE_TOOL}}             e.g., pytest-cov, coverage.py
Mutation tool:    {{MUTATION_TOOL}}        e.g., mutmut, pytest-mutmut

#### Scaffolding

```bash
# Install
pip install pytest pytest-cov pytest-mock hypothesis mutmut

# Run tests
pytest                          # Run all tests
pytest --cov                    # With coverage
pytest --cov --cov-branch       # Line + branch coverage
pytest --cov-report=html        # HTML report

# Mutation testing
mutmut run
mutmut report

# Configuration (pyproject.toml)
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --strict-markers"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if __name__ == .__main__.:",
    "raise NotImplementedError",
]
```

##### CI Integration
```yaml
# GitHub Actions example
- name: Run tests
  run: pytest --cov --cov-branch --cov-report=xml

- name: Mutation tests
  run: |
    pip install mutmut
    mutmut run
    mutmut html > mutation_report.html
```

### Code Style
- Follow PEP 8 (enforced by Ruff)
- Use f-strings for string formatting
- Use `dataclasses` for simple data containers
- Use `pydantic` for complex validation
- Unless the code is a framework layer or there is a strong necessity - DO NOT use setattr or getattr.

### Abstract Classes and Interfaces

Selected Style: **{{ABSTRACT_CLASS_STYLE}}**

{{#if ABSTRACT_CLASS_STYLE == "abc"}}
#### Using Abstract Base Classes (abc module)
- Inherit from `abc.ABC` for abstract base classes
- Use `@abstractmethod` decorator for methods that must be implemented
- Use `@abstractclassmethod` and `@abstractstaticmethod` where appropriate
- Type checkers will catch incomplete implementations at static analysis time

```python
from abc import ABC, abstractmethod

class Repository(ABC):
    @abstractmethod
    def get(self, id: str) -> Entity | None:
        """Retrieve entity by ID. Must be implemented by subclasses."""
        ...

class SqlRepository(Repository):
    def get(self, id: str) -> Entity | None:
        # Concrete implementation
        return self.session.query(Entity).get(id)
```
{{/if}}

{{#if ABSTRACT_CLASS_STYLE == "interface"}}
#### Using NotImplementedError (Informal Interfaces)
- Raise `NotImplementedError` in methods that must be overridden
- Document expected behavior in docstrings
- Rely on runtime checks and duck typing
- Simpler for cases where strict enforcement isn't needed

```python
class Repository:
    def get(self, id: str) -> Entity | None:
        """Retrieve entity by ID. Must be overridden by subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement get()")

class SqlRepository(Repository):
    def get(self, id: str) -> Entity | None:
        # Concrete implementation
        return self.session.query(Entity).get(id)
```
{{/if}}
