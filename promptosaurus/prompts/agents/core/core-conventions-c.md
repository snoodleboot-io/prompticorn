<!-- path: promptosaurus/prompts/agents/core/core-conventions-c.md -->
# Core Conventions C

Language:             {{config.language}}           e.g., C17, C23
Compiler:            {{config.runtime}}            e.g., GCC, Clang, MSVC
Package Manager:      {{config.package_manager}}        e.g., CMake, make
Linter:               {{config.linter}}             e.g., cppcheck, clang-tidy
Formatter:           {{config.formatter}}          e.g., clang-format

### Naming Conventions

Files:               snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case or PascalCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## C-Specific Rules

### Memory Management
- Always pair malloc with free
- Use valgrind for memory leak detection
- Check return values of memory allocation
- Use static analysis tools

### Error Handling
- Use error codes return values
- Check all return values
- Use errno for system errors
- Never ignore warnings

### Code Style
- Follow MISRA C guidelines for safety-critical code
- Use const for read-only data
- Prefer static functions over globals
- Initialize all variables

### Testing

#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Path:           {{config.coverage.path}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use Unity or Check framework
- Test one function in isolation
- Use mocks for hardware/OS dependencies

##### Integration Tests
- Test component interactions
- Test with real hardware when needed

##### Static Analysis
- Use cppcheck, clang-tidy
- Run in CI pipeline

#### Framework & Tools
Framework:       {{config.testing_framework}}        e.g., Unity, Check, CMocka
Coverage tool:  {{config.coverage_tool}}              e.g., lcov, gcov
Static analysis: {{config.lint_tool}}           e.g., cppcheck, clang-tidy

#### Scaffolding

```bash
# Install
apt-get install cppcheck clang-tidy lcov

# Run tests
make test                    # Run tests
gcov -r *.c                 # Coverage
cppcheck --enable=all .     # Static analysis

# Configuration (.clang-format)
BasedOnStyle: Google
IndentWidth: 4
```
