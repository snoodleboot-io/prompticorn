# Python Conventions

Language:             {{LANGUAGE}}           e.g., Python 3.11+
Runtime:              {{RUNTIME}}            e.g., CPython 3.11, PyPy
Package Manager:      {{PKG_MANAGER}}        e.g., poetry, pip, uv
Linter:               {{LINTER}}             e.g., Ruff, flake8
Formatter:           {{FORMATTER}}          e.g., Ruff, Black

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
Framework:           {{TEST_FRAMEWORK}}     e.g., pytest
Coverage target:      {{COVERAGE_%}}         e.g., 80%
Mocking library:     {{MOCK_LIB}}           e.g., unittest.mock, pytest-mock

- Use `pytest` fixtures for setup/teardown
- Use `pytest.mark.parametrize` for table-driven tests
- Use `pytest.raises` for exception testing
- Unit tests: one function or method in isolation
- Integration tests: at the service or module boundary

### Code Style
- Follow PEP 8 (enforced by Ruff)
- Use f-strings for string formatting
- Use `dataclasses` for simple data containers
- Use `pydantic` for complex validation
- Unless the code is a framework layer or there is a strong necessity - DO NOT use setattr or getattr.
