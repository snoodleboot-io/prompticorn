<!-- path: promptosaurus/prompts/core-conventions-kotlin.md -->
# Kotlin Conventions

Language:             {{LANGUAGE}}           e.g., Kotlin 1.9
Runtime:              {{RUNTIME}}            e.g., JVM 21, Kotlin/JS, Kotlin/Native
Package Manager:      {{PACKAGE_MANAGER}}        e.g., Gradle, Maven
Linter:               {{LINTER}}             e.g., ktlint, detekt
Formatter:           {{FORMATTER}}          e.g., ktlint

## Kotlin-Specific Rules

### Null Safety
- Use nullable types (?) for values that can be null
- Use safe call operator (?.) and elvis operator (?:)
- Prefer val over var
- Avoid null checks, use built-in operators

### Error Handling
- Use Result for fallible operations
- Use exceptions for truly exceptional cases
- Use sealed classes for error types

### Coroutines
- Use suspend functions for async operations
- Use structured concurrency
- Use Flow for streams of data

### Testing

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests
- Use JUnit 5 or Kotest
- Use MockK for mocking
- Test one function/class in isolation

##### Integration Tests
- Use Spring Boot Test for integration
- Use Testcontainers for databases

##### Property Tests
- Use Kotest property-based testing

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., JUnit 5, Kotest
Mocking:        {{MOCKING_LIBRARY}}              e.g., MockK
Property tool:   {{PROPERTY_TOOL}}        e.g., Kotest
Coverage tool:  {{COVERAGE_TOOL}}              e.g., JaCoCo

#### Scaffolding

```kotlin
// build.gradle.kts
dependencies {
    testImplementation("io.kotest:kotest-runner-junit5:5.8.0")
    testImplementation("io.kotest:kotest-property:5.8.0")
    testImplementation("io.mockk:mockk:1.13.8")
}

// Run tests
././gradlew testgradlew test
 -Pcoverage=true
```

##### CI Integration
```yaml
# GitHub Actions
- name: Run tests
  run: ./gradlew test
```
