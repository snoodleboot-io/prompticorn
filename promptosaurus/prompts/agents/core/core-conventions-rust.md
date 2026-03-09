<!-- path: promptosaurus/prompts/agents/core/core-conventions-rust.md -->
# Core Conventions Rust

Language:             {{LANGUAGE}}           e.g., Rust 1.75
Runtime:              {{RUNTIME}}            e.g., Native, WASM
Package Manager:      {{PACKAGE_MANAGER}}        e.g., Cargo
Linter:               {{LINTER}}             e.g., Clippy
Formatter:           {{FORMATTER}}          e.g., rustfmt

### Naming Conventions

Files:               snake_case
Variables:          snake_case
Constants:          UPPER_SNAKE
Classes/Types:      PascalCase
Functions:          snake_case
Database tables:    snake_case
Environment vars:   UPPER_SNAKE_CASE always

## Rust-Specific Rules

### Error Handling
- Use `Result<T, E>` for fallible operations - never panic in library code
- Use `?` operator for error propagation
- Use `thiserror` or `anyhow` for error handling
- Wrap errors with context using `map_err` or `with_context`

### Ownership & Borrowing
- Follow ownership rules - no use-after-free, no data races
- Use lifetimes when references must outlive their referents
- Prefer borrowing over cloning where possible
- Use `Arc` for shared ownership, `Rc` for single-threaded

### Traits & Generics
- Use traits for abstraction, not concrete types
- Prefer trait bounds over generic parameters
- Implement `Default`, `Clone`, `Debug`, `Display`, `Serialize`, `Deserialize` where appropriate

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
- Use `#[cfg(test)]` module with `#[test]` functions
- Test one function or method in isolation
- Use `#[should_panic]` for expected panics
- Use proptest or quickcheck for property-based tests

##### Integration Tests
- Create tests in `tests/` directory
- Test public API at module boundary
- Test with real dependencies

##### Doc Tests
- Use `#[doc = "..."]` examples in code
- Run with `cargo test --doc`

##### Fuzz Tests
- Use `cargo-fuzz` or ` AFL` for fuzz testing
- Test parsing and input validation

#### Framework & Tools
Framework:       {{TESTING_FRAMEWORK}}        e.g., built-in, rstest
Property tool:   {{PROPERTY_TOOL}}        e.g., proptest, quickcheck
Coverage tool:  {{COVERAGE_TOOL}}              e.g., tarpaulin, grcov
Fuzz tool:      {{FUZZ_TOOL}}            e.g., cargo-fuzz

#### Scaffolding

```bash
# Run tests
cargo test                     # Run all tests
cargo test --lib              # Library tests only
cargo test --doc              # Doc tests only
cargo test -- --nocapture    # Show output

# With coverage
cargo install cargo-tarpaulin
cargo tarpaulin --out Html

# Property-based testing
cargo add proptest
cargo add quickcheck

# Fuzzing
cargo install cargo-fuzz
cargo +nightly fuzz run my_fuzz_target
```

##### CI Integration
```yaml
# GitHub Actions
- name: Run tests
  run: |
    cargo test --all-features
    cargo test --doc

- name: Coverage
  run: |
    cargo install cargo-tarpaulin
    cargo tarpaulin --all-features --out Xml
```
