<!-- path: prompticorn/prompts/agents/core/core-conventions-r.md -->
# Core Conventions R

Language:             {{ language or "e.g., R 4.3+" }}
Package Manager:      {{ package_manager or "e.g., renv, pacman" }}
Linter:               {{ linter or "e.g., lintr" }}
Formatter:           {{ formatter or "e.g., styler, formatR" }}

### Naming Conventions

Files:              snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## R-Specific Rules

### Type System
- Use vectors instead of loops where possible
- Prefer tidyverse for data manipulation
- Use tibbles instead of data.frames

### Error Handling
- Use tryCatch for error handling
- Use stop() for raising errors
- Never swallow errors silently

### Code Style
- Follow tidyverse style guide
- Use pipes (%>%) for readability
- Name functions with verbs

### Testing

#### Coverage Targets
Line:           {{ coverage_targets.get('line', '') or "e.g., 80%" }}
Branch:         {{ coverage_targets.get('branch', '') or "e.g., 70%" }}
Function:       {{ coverage_targets.get('function', '') or "e.g., 90%" }}
Statement:      {{ coverage_targets.get('statement', '') or "e.g., 85%" }}
Path:           {{ coverage_targets.get('path', '') or "e.g., 60%" }}

#### Test Types

##### Unit Tests
- Use testthat for unit testing
- Test one function in isolation
- Use mocking with mockery

##### Integration Tests
- Test at function boundary
- Test data transformations

#### Framework & Tools
Framework:       {{ test_framework or "e.g., testthat, tinytest" }}
Mocking:        {{ mocking_library or "e.g., mockery, mockr" }}
Coverage tool:  {{ coverage_tool or "e.g., covr" }}

#### Scaffolding

```r
# Install
install.packages("testthat")
install.packages("covr")

# Run tests
devtools::test()
covr::report()

# Configuration
# tests/testthat.R
library(testthat)
devtools::test()

# testthat example
test_that("function works", {
  expect_equal(my_func(1), 2)
  expect_error(my_func("a"))
})
```
