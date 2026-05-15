<!-- path: prompticorn/prompts/agents/core/core-conventions-python.md -->
{%- import 'macros/naming_conventions.jinja2' as naming -%}
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
{%- import 'macros/code_examples.jinja2' as examples -%}
# Core Conventions Python

Language:             {{ language }} e.g., Python 3.11+
Runtime:              {{ runtime }} e.g., CPython 3.11, PyPy
Package Manager:      {{ package_manager }} e.g., poetry, pip, uv
Linter:               {{ linter }} e.g., Ruff, flake8
Formatter:           {{ formatter }} e.g., Ruff, Black
Abstract Class Style: {{ abstract_class_style }} e.g., abc, interface

### Naming Conventions

Files:               snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE (discouraged - use pydantic-settings)
Classes/Types:      PascalCase
Functions:          snake_case
Database tables:     snake_case
Environment vars:    UPPER_SNAKE_CASE always

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

[Dynamic content - see template]

TODO

[Dynamic content - see template]

[Dynamic content - see template]

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

[Dynamic content - see template]

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

[Dynamic content - see template]

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

Selected Style: **{{ abstract_class_style }}**

{% if config.abstract_class_style == "abc" %}
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
{% endif %}

{% if config.abstract_class_style == "interface" %}
#### Using Interface Pattern (Traditional OOP Interfaces)
- Interfaces are base classes with standard `__init__` containing base details repeated across classes
- Interface methods raise `NotImplementedError` for methods that must be implemented by subclasses
- Used as roots of inheritance trees to define contracts through inheritance
- Provides clear inheritance hierarchies and explicit contracts
- Better for internal APIs where inheritance is expected

```python
class Repository:
    """Interface for repository implementations.
    
    Base class providing common initialization and defining the interface
    that all repository implementations must follow.
    """
    
    def __init__(self, connection_string: str, timeout: int = 30):
        """Initialize repository with connection details.
        
        Args:
            connection_string: Database connection string
            timeout: Connection timeout in seconds
        """
        self.connection_string = connection_string
        self.timeout = timeout
    
    def get(self, id: str) -> Entity | None:
        """Retrieve entity by ID. Must be overridden by subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement get()")
    
    def save(self, entity: Entity) -> None:
        """Save entity to storage. Must be overridden by subclasses."""
        raise NotImplementedError(f"{self.__class__.__name__} must implement save()")
    
    def delete(self, id: str) -> bool:
        """Delete entity by ID. Must be overridden by subclasses.""" 
        raise NotImplementedError(f"{self.__class__.__name__} must implement delete()")

# Implementation - explicit inheritance required
class SqlRepository(Repository):
    def __init__(self, connection_string: str, timeout: int = 30):
        super().__init__(connection_string, timeout)
        # Additional SQL-specific initialization
        self._engine = create_engine(connection_string)
    
    def get(self, id: str) -> Entity | None:
        return self._session.query(Entity).get(id)
    
    def save(self, entity: Entity) -> None:
        self._session.add(entity)
        self._session.commit()
    
    def delete(self, id: str) -> bool:
        entity = self.get(id)
        if entity:
            self._session.delete(entity)
            self._session.commit()
            return True
        return False

# Usage - inheritance provides the interface
def process_data(repo: Repository) -> None:
    entity = repo.get("123")
    if entity:
        repo.save(entity)
```

**When to use Interface pattern:**
- Creating base classes with shared initialization logic
- Building inheritance hierarchies for internal APIs
- When you want explicit contracts through inheritance
- For classes that will be instantiated and need base behavior
- When runtime type checking with inheritance is important

{% endif %}
