<!-- path: promptosaurus/prompts/agents/core/core-conventions-php.md -->
# Core Conventions PHP

Language:             {{config.language}}           e.g., PHP 8.3
Runtime:              {{config.runtime}}            e.g., PHP-FPM, Laravel Octane
Package Manager:      {{config.package_manager}}        e.g., Composer
Linter:               {{config.linter}}             e.g., PHP CS Fixer, Pint
Formatter:           {{config.formatter}}          e.g., Pint, PHP CS Fixer

### Naming Conventions

Files:               snake_case
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase or snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## PHP-Specific Rules

### Type System
- Use strict types (`declare(strict_types=1);`)
- Use return type declarations
- Use nullable types (?Type)
- Avoid mixed type

### Error Handling
- Use exceptions for error handling
- Never disable error reporting in production
- Use try/catch for exception handling

### Code Style
- Follow PSR-12 coding standard
- Use namespacing
- Follow Laravel conventions if using Laravel

### Testing

#### Coverage Targets
Line:           {{config.coverage.line}}          e.g., 80%
Branch:         {{config.coverage.branch}}        e.g., 70%
Function:       {{config.coverage.function}}       e.g., 90%
Statement:      {{config.coverage.statement}}      e.g., 85%
Path:           {{config.coverage.path}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use PHPUnit for testing
- Use Mockery for mocking
- Test one class/method in isolation

##### Integration Tests
- Test at service boundary
- Use in-memory databases for testing

##### Browser Tests
- Use Pest or Laravel Dusk for browser testing

#### Framework & Tools
Framework:       {{config.testing_framework}}        e.g., PHPUnit, Pest
Mocking:        {{config.mocking_library}}              e.g., Mockery, PHP-Mock
Coverage tool:  {{config.coverage_tool}}              e.g., Xdebug, PCOV

#### Scaffolding

```bash
# Install
composer require --dev phpunit/phpunit pest/pest mockery/mockery

# Run tests
./vendor/bin/phpunit
./vendor/bin/pest
./vendor/bin/phpunit --coverage
```
