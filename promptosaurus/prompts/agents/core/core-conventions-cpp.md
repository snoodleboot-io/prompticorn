<!-- path: promptosaurus/prompts/agents/core/core-conventions-cpp.md -->
# Core Conventions C++

Language:             {{config.language}}           e.g., C++20, C++23
Compiler:            {{config.runtime}}            e.g., GCC, Clang, MSVC
Package Manager:      {{config.package_manager}}        e.g., CMake, vcpkg, Conan
Linter:               {{config.linter}}             e.g., clang-tidy, cppcheck
Formatter:           {{config.formatter}}          e.g., clang-format

### Naming Conventions

Files:               snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          PascalCase or snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## C++-Specific Rules

### Modern C++
- Use C++20 or later when possible
- Use RAII for resource management (no raw new/delete)
- Use smart pointers (unique_ptr, shared_ptr)
- Use std::vector, std::string, std::array

### Type System
- Use strong typing - avoid raw pointers where possible
- Use constexpr for compile-time computation
- UseConcepts for constraints

### Error Handling
- Use exceptions for error handling (not error codes)
- No new without delete (use smart pointers)
- Use std::optional for optional values
- Use std::expected (C++23) for fallible operations

### Testing

#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Path:           {{config.coverage.path}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use Google Test, Catch2, or doctest
- Test one class/function in isolation
- Use mocks with Google Mock

##### Integration Tests
- Test component interactions
- Test with real dependencies

##### Fuzz Tests
- Use libFuzzer or AFL
- Test parsers and input validation

#### Framework & Tools
Framework:       {{config.testing_framework}}        e.g., Google Test, Catch2, doctest
Mocking:        {{config.mocking_library}}              e.g., Google Mock, Trompeloeil
Coverage tool:  {{config.coverage_tool}}              e.g., lcov, gcov, llvm-cov

#### Scaffolding

```bash
# Install
apt-get install cmake g++ cppcheck clang-tidy

# Run tests
cmake --build . --target test
gcov -r *.cpp

# Static analysis
clang-tidy -checks=* src/*.cpp
cppcheck --enable=all src/

# Configuration (CMakeLists.txt)
enable_testing()
find_package(GTest CONFIG REQUIRED)
add_test(NAME tests COMMAND tests)
```
