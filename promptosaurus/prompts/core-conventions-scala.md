<!-- path: promptosaurus/prompts/core-conventions-scala.md -->
# Scala Conventions

Language:             {{LANGUAGE}}           e.g., Scala 3.4
Runtime:              {{RUNTIME}}            e.g., JVM 21
Package Manager:      {{PACKAGE_MANAGER}}        e.g., sbt, mill
Linter:              {{LINTER}}             e.g., Scalafmt, Scalafix
Formatter:           {{FORMATTER}}          e.g., Scalafmt

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
Line:           {{LINE_COVERAGE_%}}          e.g., 80%
Branch:         {{BRANCH_COVERAGE_%}}        e.g., 70%
Function:       {{FUNCTION_COVERAGE_%}}       e.g., 90%
Statement:      {{STATEMENT_COVERAGE_%}}      e.g., 85%
Path:           {{PATH_COVERAGE_%}}           e.g., 60%

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
Framework:       {{TESTING_FRAMEWORK}}        e.g., ScalaTest, MUnit, specs2
Mocking:        {{MOCKING_LIBRARY}}              e.g., ScalaMock, Mockito
Property tool:   {{PROPERTY_TOOL}}        e.g., ScalaCheck
Coverage tool:  {{COVERAGE_TOOL}}              e.g., scoverage

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
