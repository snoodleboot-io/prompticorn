<!-- path: promptosaurus/prompts/agents/core/core-conventions-rust.md -->
{%- import 'macros/testing_sections.jinja2' as testing -%}
{%- import 'macros/coverage_targets.jinja2' as coverage -%}
# Core Conventions Rust

Language:             {{config.language}}           e.g., Rust 1.75
Runtime:              {{config.runtime}}            e.g., Native, WASM
Package Manager:      {{config.package_manager}}        e.g., Cargo
Linter:               {{config.linter}}             e.g., Clippy
Formatter:           {{config.formatter}}          e.g., rustfmt

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

{{ testing.render_test_types('rust') }}

{{ coverage.render_coverage_table(
  line=config.coverage.line | default('80'),
  branch=config.coverage.branch | default('70'),
  function=config.coverage.function | default('90'),
  statement=config.coverage.statement | default('85'),
  mutation=config.coverage.mutation | default('80'),
  path=config.coverage.path | default('60')
) }}
