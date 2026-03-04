<!-- path: promptosaurus/prompts/core-conventions-r.md -->
# R Conventions

Language:             {{LANGUAGE}}           e.g., R 4.3+
Package Manager:      {{PACKAGE_MANAGER}}        e.g., renv, pacman
Linter:              {{LINTER}}             e.g., lintr
Formatter:           {{FORMATTER}}          e.g., styler, formatR

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use testthat for unit testing
- Test one function in isolation
- Use mocking with mockery

##### Integration Tests
- Test at function boundary
- Test data transformations

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., testthat, tinytest
Mocking:        {{MOCKING_LIBRARY}}              e.g., mockery, mockr
Coverage tool:  {{COVERAGE_TOOL}}              e.g., covr

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
