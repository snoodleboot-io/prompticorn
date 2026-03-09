<!-- path: promptosaurus/prompts/agents/core/core-conventions-ruby.md -->
# Core Conventions Ruby

Language:             {{LANGUAGE}}           e.g., Ruby 3.3
Runtime:              {{RUNTIME}}            e.g., MRI, JRuby
Package Manager:      {{PACKAGE_MANAGER}}        e.g., Bundler
Linter:               {{LINTER}}             e.g., RuboCop
Formatter:           {{FORMATTER}}          e.g., Rufo, RuboCop

### Naming Conventions

Files:              snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case (methods)
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Ruby-Specific Rules

### Type System
- Use RBS for type signatures (Ruby 3.0+)
- Use strict typing in critical code paths

### Error Handling
- Use exceptions for error handling
- Never rescue Exception (rescue StandardError instead)
- Use begin/rescue/ensure blocks

### Code Style
- Follow Ruby style guide (RuboCop)
- Use RuboCop for linting
- Use meaningful method names

### Testing

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Method:         {{METHOD_COVERAGE_%}}         e.g., 90%

#### Test Types

##### Unit Tests
- Use RSpec or Minitest
- Test one class/method in isolation
- Use doubles/mocks for external dependencies

##### Integration Tests
- Test at service boundary
- Use factory_bot for test data

##### System Tests
- Use Capybara for browser testing

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., RSpec, Minitest
Mocking:        {{MOCKING_LIBRARY}}              e.g., RSpec mocks, RR
Coverage tool:  {{COVERAGE_TOOL}}              e.g., SimpleCov

#### Scaffolding

```bash
# Install
gem install rspec simplecov

# Run tests
rspec                          # Run tests
rspec --format documentation  # Detailed output
rspec --coverage             # With coverage

# Configuration (.rspec)
--require spec_helper
--format documentation
--color
```
