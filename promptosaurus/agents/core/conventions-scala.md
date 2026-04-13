<!-- path: promptosaurus/prompts/agents/core/core-conventions-scala.md -->
# Core Conventions Scala

Language:             {{ language }} e.g., Scala 3.4
Runtime:              {{ runtime }} e.g., JVM 21
Package Manager:      {{ package_manager }} e.g., sbt, mill
Linter:               {{ linter }} e.g., Scalafmt, Scalafix
Formatter:           {{ formatter }} e.g., Scalafmt

### Naming Conventions

Files:               PascalCase
Variables:          camelCase
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          camelCase
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Scala-Specific Rules

### Type System
- Use Scala 3 features (enums, given/using, union types)
- Prefer immutability (val over var)
- Use case classes for immutable data
- Use Option, Either, Try for absence/errors

### Error Handling
- Use Try for exceptions
- Use Either for custom error types
- Use cats-effect for async error handling

### Code Style
- Follow Scala style guide (run scalafmt)
- Use extension methods
- Use pattern matching extensively

### Testing

#### Coverage Targets
Line:           [Template variable]          e.g., 80%
Branch:         [Template variable]        e.g., 70%
Function:       [Template variable]       e.g., 90%
Statement:      [Template variable]      e.g., 85%
Path:           [Template variable]           e.g., 60%

#### Test Types

##### Unit Tests
- Use ScalaTest or MUnit
- Test one function/method in isolation
- Use ScalaMock for mocking

##### Integration Tests
- Test at service/component boundary
- Use testcontainers for databases

##### Property Tests
- Use ScalaCheck for property-based testing

#### Framework & Tools
Framework:       [Template variable]        e.g., ScalaTest, MUnit, specs2
Mocking:        [Template variable]              e.g., ScalaMock, Mockito
Property tool:   [Template variable]        e.g., ScalaCheck
Coverage tool:  [Template variable]              e.g., scoverage

#### Scaffolding

```scala
// build.sbt
libraryDependencies ++= Seq(
  "org.scalatest" %% "scalatest" % "3.2.17" % Test,
  "org.scalacheck" %% "scalacheck" % "1.17.0" % Test
)

// Run tests
sbt test
sbt coverage test
sbt coverageReport
```

##### CI Integration
```yaml
# GitHub Actions
- name: Run tests
  run: |
    sbt test
    sbt coverageReport
```
