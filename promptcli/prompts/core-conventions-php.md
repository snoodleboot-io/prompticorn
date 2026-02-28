# PHP Conventions

Language:             {{LANGUAGE}}           e.g., PHP 8.3
Runtime:              {{RUNTIME}}            e.g., PHP-FPM, Laravel Octane
Package Manager:      {{PACKAGE_MANAGER}}        e.g., Composer
Linter:               {{LINTER}}             e.g., PHP CS Fixer, Pint
Formatter:           {{FORMATTER}}          e.g., Pint, PHP CS Fixer

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

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
Framework:       {{TESTING_FRAMEWORK}}        e.g., PHPUnit, Pest
Mocking:        {{MOCKING_LIBRARY}}              e.g., Mockery, PHP-Mock
Coverage tool:  {{COVERAGE_TOOL}}              e.g., Xdebug, PCOV

#### Scaffolding

```bash
# Install
composer require --dev phpunit/phpunit pest/pest mockery/mockery

# Run tests
./vendor/bin/phpunit
./vendor/bin/pest
./vendor/bin/phpunit --coverage
```
