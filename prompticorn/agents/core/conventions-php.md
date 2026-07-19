<!-- path: prompticorn/prompts/agents/core/core-conventions-php.md -->
# Core Conventions PHP

Language:             {{ language or "e.g., PHP 8.3" }}
Runtime:              {{ runtime or "e.g., PHP-FPM, Laravel Octane" }}
Package Manager:      {{ package_manager or "e.g., Composer" }}
Linter:               {{ linter or "e.g., PHP CS Fixer, Pint" }}
Formatter:           {{ formatter or "e.g., Pint, PHP CS Fixer" }}

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
Line:           {{ coverage_targets.get('line', '') or "e.g., 80%" }}
Branch:         {{ coverage_targets.get('branch', '') or "e.g., 70%" }}
Function:       {{ coverage_targets.get('function', '') or "e.g., 90%" }}
Statement:      {{ coverage_targets.get('statement', '') or "e.g., 85%" }}
Path:           {{ coverage_targets.get('path', '') or "e.g., 60%" }}

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
Framework:       {{ test_framework or "e.g., PHPUnit, Pest" }}
Mocking:        {{ mocking_library or "e.g., Mockery, PHP-Mock" }}
Coverage tool:  {{ coverage_tool or "e.g., Xdebug, PCOV" }}

#### Scaffolding

```bash
# Install
composer require --dev phpunit/phpunit pest/pest mockery/mockery

# Run tests
./vendor/bin/phpunit
./vendor/bin/pest
./vendor/bin/phpunit --coverage
```
