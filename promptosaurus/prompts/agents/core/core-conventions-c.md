<!-- path: promptosaurus/prompts/agents/core/core-conventions-c.md -->
# Core Conventions C

Language:             {{LANGUAGE}}           e.g., C17, C23
Compiler:            {{RUNTIME}}            e.g., GCC, Clang, MSVC
Package Manager:      {{PACKAGE_MANAGER}}        e.g., CMake, make
Linter:               {{LINTER}}             e.g., cppcheck, clang-tidy
Formatter:           {{FORMATTER}}          e.g., clang-format

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

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
Framework:       {{TESTING_FRAMEWORK}}        e.g., Unity, Check, CMocka
Coverage tool:  {{COVERAGE_TOOL}}              e.g., lcov, gcov
Static analysis: {{LINT_TOOL}}           e.g., cppcheck, clang-tidy

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
