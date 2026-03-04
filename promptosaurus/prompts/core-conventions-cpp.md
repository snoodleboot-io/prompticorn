# C++ Conventions

Language:             {{LANGUAGE}}           e.g., C++20, C++23
Compiler:            {{RUNTIME}}            e.g., GCC, Clang, MSVC
Package Manager:      {{PACKAGE_MANAGER}}        e.g., CMake, vcpkg, Conan
Linter:               {{LINTER}}             e.g., clang-tidy, cppcheck
Formatter:           {{FORMATTER}}          e.g., clang-format

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

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
Framework:       {{TESTING_FRAMEWORK}}        e.g., Google Test, Catch2, doctest
Mocking:        {{MOCKING_LIBRARY}}              e.g., Google Mock, Trompeloeil
Coverage tool:  {{COVERAGE_TOOL}}              e.g., lcov, gcov, llvm-cov

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
