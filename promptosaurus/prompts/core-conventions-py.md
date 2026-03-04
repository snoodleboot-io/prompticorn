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
- **NEVER use import forwarding** — do not re-export imported symbols (e.g., `from module import X` then exposing `X` at package level). This is an anti-pattern and NOT allowed. Define public API explicitly.

### Code Structure & Patterns

#### Constants & Configuration (CRITICAL)
- **NO constants allowed inside or outside of classes** — never define `CONSTANT = value` at module level OR as class constants
- **For values changeable at runtime**: use a YAML configuration file
- **For fixed configuration**: use internal class variables (not constants) or `pydantic-settings` with environment variable support
- **Never have const values outside of a class** — always use a settings file (`pydantic-settings`) for configurable values
- When asked to create constants, redirect to the appropriate configuration approach

#### Dynamic Attribute Access
- **AVOID `setattr` and `getattr`** unless absolutely necessary — these bypass type checking and make code harder to reason about
- Before using: ask yourself if there's a type-safe alternative (dataclass, pydantic model, explicit properties)
- If present: ask the user if they are creating core/framework code or generally reusable code — only acceptable for core framework code that MUST handle dynamic structures

#### Module Structure
- **ALL modules MUST have `__init__.py`** — every package directory must include an `__init__.py` file
- Verify `__init__.py` exists before adding new modules
- No implicit namespace packages allowed

#### Type Casting
- **DO NOT use type casting** (`typing.cast`, `isinstance` + cast patterns) UNLESS working with data primitives like `int`, `str`, `float`, `bool`
- Primitive conversions (e.g., `int()`, `str()`, `float()`) are acceptable
- Use proper type narrowing with `isinstance` checks instead of casting for complex types
- Design APIs to return correct types rather than requiring casts

#### Type Checking Enforcement
- **ENFORCE the use of `pyright`** while coding — run continuously during development
- Treat type errors as blocking issues
- All code must pass pyright strict mode before commit
- No commits with type errors or `Any` types without explicit justification

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

### Python Styling and Conventions

#### Properties Over Direct Access
- **Use properties** for attribute access control - never access fields directly when get/set logic is needed
- Use `@property` decorator with getters/setters instead of `get_x()` / `set_x()` methods
- Use `@property.deleter` when cleanup logic is needed on attribute deletion
- Prevent setting when inappropriate by raising `AttributeError` or `TypeError` in setters

```python
# GOOD - property with controlled access
class Temperature:
    def __init__(self, celsius: float = 0.0) -> None:
        self._celsius = celsius

    @property
    def celsius(self) -> float:
        return self._celsius

    @celsius.setter
    def celsius(self, value: float) -> None:
        if value < -273.15:
            raise ValueError("Temperature below absolute zero is not possible")
        self._celsius = value

    @celsius.deleter
    def celsius(self) -> None:
        self._celsius = 0.0

# BAD - direct field access or getter/setter methods
class Temperature:
    def __init__(self) -> None:
        self.celsius = 0.0  # Direct access - no validation

    def get_celsius(self) -> float:  # Old-style getter
        return self._celsius

    def set_celsius(self, value: float) -> None:  # Old-style setter
        self._celsius = value
```

#### Public/Protected/Private Scoping
- Use single underscore `_` prefix for protected/internal attributes and methods
- Use double underscore `__` prefix for private attributes (name mangling when needed)
- Protected methods should not be called from outside the class hierarchy

```python
class DataProcessor:
    def __init__(self) -> None:
        self.public_field: str = "visible"
        self._internal_state: dict = {}  # Protected
        self.__private_cache: dict = {}  # Private (name mangled)

    def public_method(self) -> None:
        """Part of public API."""
        pass

    def _helper_method(self) -> None:
        """Protected - for subclass use only."""
        pass

    def __internal_cleanup(self) -> None:
        """Private - internal use only."""
        pass
```

#### Decorators and Design Patterns
- Use `@staticmethod` for functions that don't access instance state
- Use `@classmethod` for factory methods and alternate constructors
- Use `@property` for computed attributes without side effects
- Use `@functools.cached_property` for expensive computations that should be cached
- Use `@functools.wraps` when creating decorators
- Use `@contextlib.contextmanager` for creating context managers

```python
from functools import cached_property, wraps
from contextlib import contextmanager
from typing import Iterator

class ExpensiveComputation:
    @cached_property
    def heavy_result(self) -> dict:
        """Computed once and cached."""
        return self._expensive_operation()

    @staticmethod
    def utility_function(x: int) -> int:
        """Doesn't need self."""
        return x * 2

    @classmethod
    def from_config(cls, config: dict) -> "ExpensiveComputation":
        """Factory method."""
        return cls(**config)

def my_decorator(func):
    @wraps(func)  # Preserves function metadata
    def wrapper(*args, **kwargs):
        print("Before call")
        return func(*args, **kwargs)
    return wrapper
```

#### Asynchrony and Async Constructs
- Use `async`/`await` for I/O-bound operations
- Use `asyncio` for concurrency - never mix sync/async without explicit bridging
- Use `async with` for async context managers
- Use `async for` for async iterators
- Never use `time.sleep()` in async code - use `await asyncio.sleep()`

```python
import asyncio
from contextlib import asynccontextmanager

class AsyncResource:
    async def fetch(self) -> bytes:
        """Async operation."""
        await asyncio.sleep(0.1)  # Never use time.sleep() in async code
        return b"data"

    async def __aenter__(self) -> "AsyncResource":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.disconnect()

@asynccontextmanager
async def managed_resource() -> Iterator[AsyncResource]:
    """Async context manager using decorator."""
    resource = AsyncResource()
    await resource.connect()
    try:
        yield resource
    finally:
        await resource.disconnect()
```

#### Context Managers (sync and async)
- **ALWAYS use context managers** for resource management (files, connections, locks)
- Use `contextlib.contextmanager` for simple sync context managers
- Use `contextlib.asynccontextmanager` for async context managers
- Never manually manage `connect()`/`disconnect()` or `open()`/`close()` without context managers
- Use `contextlib.closing()` for objects with close() but no context manager

```python
from contextlib import contextmanager, asynccontextmanager, closing
from typing import Iterator
import sqlite3

@contextmanager
def database_connection(db_path: str) -> Iterator[sqlite3.Connection]:
    """Sync context manager for database connections."""
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()

# Usage - always use context managers
with database_connection("app.db") as conn:
    conn.execute("SELECT * FROM users")

# For objects with close() but no context manager
from urllib.request import urlopen
with closing(urlopen("https://example.com")) as response:
    data = response.read()
```

#### No Nested Class/Function Definitions
- **NEVER nest class or function definitions** unless:
  1. It is a documented design decision
  2. It is marked with `#design-decision-override` comment
  3. It solves a specific scoping or closure problem that cannot be solved otherwise
- Define classes and functions at module level for testability and readability
- Use factories or partial functions instead of closures when state capture is needed

```python
# BAD - nested function (hard to test, unclear scope)
def process_data(data: list) -> list:
    def transform(item: int) -> int:
        return item * 2
    return [transform(x) for x in data]

# GOOD - module-level function (testable, clear scope)
def transform(item: int) -> int:
    return item * 2

def process_data(data: list) -> list:
    return [transform(x) for x in data]

# Acceptable - nested with explicit design decision override
def create_handler(config: dict):
    #design-decision-override: closure captures config without exposing it
    def handler(event: dict) -> None:
        if event["type"] in config["allowed_types"]:
            process_event(event, config["handler_type"])
    return handler
```

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
