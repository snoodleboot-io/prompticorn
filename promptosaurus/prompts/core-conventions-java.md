<!-- path: promptosaurus/prompts/core-conventions-java.md -->
# Java Conventions

Language:             {{LANGUAGE}}           e.g., Java 21
Runtime:              {{RUNTIME}}            e.g., JDK 21, OpenJDK
Package Manager:      {{PACKAGE_MANAGER}}        e.g., Maven, Gradle
Linter:               {{LINTER}}             e.g., Checkstyle, SpotBugs
Formatter:           {{FORMATTER}}          e.g., Google Java Format, Spotless

## Java-Specific Rules

### Type System
- Use strong typing - avoid raw types
- Prefer immutable objects where possible
- Use Optional for nullable return types
- Enable checker framework for null annotations

### Error Handling
- Use specific exception types, not generic Exception
- Never catch Exception or Throwable unless rethrowing
- Use try-with-resources for all Closeable resources
- Log at the boundary where the error is handled

### Imports & Packages
- Use standard package structure (com.company.module)
- Group imports: java → javax → third-party → internal
- Never use wildcard imports (*)

### Testing

#### Coverage Targets
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Mutation:       {{MUTATION_COVERAGE_%}}       e.g., 80%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

#### Test Types

##### Unit Tests
- One class or method in isolation
- Use JUnit 5 (Jupiter) for testing
- Mock external dependencies with Mockito
- Test behavior, not implementation

##### Integration Tests
- Test at service or component boundary
- Use Testcontainers for database testing
- Use Spring Boot Test for integration tests

##### E2E Tests
- Use Selenium or Playwright for browser testing
- Test critical user flows end-to-end

##### Mutation Tests
- Use Pitest for mutation testing

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., JUnit 5, TestNG
Mocking library: {{MOCKING_LIBRARY}}              e.g., Mockito, EasyMock
Coverage tool:  {{COVERAGE_TOOL}}              e.g., JaCoCo, Cobertura
Mutation tool:  {{MUTATION_TOOL}}          e.g., Pitest

#### Scaffolding

```bash
# Maven
mvn test                          # Run tests
mvn test -Dcoverage=true         # With coverage
mvn org.pitest:pitest-maven:mutationCoverage  # Mutation testing

# Gradle
gradle test                      # Run tests
gradle test --coverage           # With coverage
gradle pitest                   # Mutation testing

# Dependencies (Maven)
<dependencies>
    <dependency>
        <groupId>org.junit.jupiter</groupId>
        <artifactId>junit-jupiter</artifactId>
        <version>5.10.0</version>
        <scope>test</scope>
    </dependency>
    <dependency>
        <groupId>org.mockito</groupId>
        <artifactId>mockito-core</artifactId>
        <version>5.8.0</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

##### CI Integration
```yaml
# GitHub Actions
- name: Run tests
  run: mvn verify -DskipITs

- name: Mutation tests
  run: mvn org.pitest:pitest-maven:mutationCoverage
```
