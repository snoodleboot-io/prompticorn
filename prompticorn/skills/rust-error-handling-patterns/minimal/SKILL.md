# Rust Error Handling Patterns (Minimal)

## Purpose
Model recoverable failures as `Result`, propagate with `?`, and reserve `panic!` for bugs and truly-impossible states.

## Core Techniques

### 1. Result for Recoverable, Panic for Bugs
```rust
use std::num::ParseIntError;

// Recoverable: the caller can reasonably handle it -> Result
fn parse_port(s: &str) -> Result<u16, ParseIntError> {
    s.parse::<u16>()
}

fn main() {
    // A violated invariant the programmer must fix -> panic
    let cfg = load_config().expect("config must exist at startup");
    assert!(cfg.workers > 0, "workers must be positive");
}
```
`Result` is for conditions the caller might recover from (bad input, missing file, network error). `panic!` (and `unwrap`/`expect`/`assert!`) is for programmer errors and broken invariants that should never occur in a correct program.

### 2. Propagate With `?`
```rust
use std::fs;
use std::io;

fn read_first_line(path: &str) -> Result<String, io::Error> {
    let contents = fs::read_to_string(path)?;   // return Err early on failure
    Ok(contents.lines().next().unwrap_or("").to_string())
}
```
`?` unwraps `Ok`, or returns the `Err` early. It also works on `Option` (returning `None`). The error type must convert into the function's declared error type via `From` — which is what makes the next two techniques compose.

### 3. Convert Errors With `From`
```rust
enum AppError {
    Io(std::io::Error),
    Parse(std::num::ParseIntError),
}

impl From<std::io::Error> for AppError {
    fn from(e: std::io::Error) -> Self { AppError::Io(e) }
}
impl From<std::num::ParseIntError> for AppError {
    fn from(e: std::num::ParseIntError) -> Self { AppError::Parse(e) }
}

fn load(path: &str) -> Result<i32, AppError> {
    let text = std::fs::read_to_string(path)?;   // io::Error -> AppError
    Ok(text.trim().parse::<i32>()?)               // ParseIntError -> AppError
}
```
A `From` impl per source lets `?` auto-convert, so one function propagates several error kinds through a single unified type.

### 4. thiserror for Libraries, anyhow for Applications
```rust
// Library: a typed, matchable error enum. thiserror derives Display + From.
#[derive(thiserror::Error, Debug)]
pub enum StoreError {
    #[error("key not found: {0}")]
    NotFound(String),
    #[error("backend io failed")]
    Io(#[from] std::io::Error),   // generates the From impl for you
}

// Application: don't care about the concrete type, just want context + a trace.
fn run() -> anyhow::Result<()> {
    let cfg = std::fs::read_to_string("app.toml")
        .map_err(|e| anyhow::anyhow!("reading config: {e}"))?;
    Ok(())
}
```
Libraries expose typed errors so callers can `match`; apps use `anyhow` to bubble anything up with human context. Add context with `.context("...")` from the `anyhow::Context` trait.

### 5. When unwrap / expect Is Acceptable
Fine in tests, examples, prototypes, and where a failure genuinely cannot happen and you can prove it (a regex literal that always compiles, a constant that always parses). Always prefer `expect("why this can't fail")` over bare `unwrap()` so the panic message documents the invariant. Never use them on untrusted input or fallible I/O in library code.

### 6. Option Combinators Over Manual Matching
```rust
let name: Option<&str> = config.get("name");

// Chain instead of nesting match/if-let
let display = name
    .map(str::trim)
    .filter(|s| !s.is_empty())
    .unwrap_or("anonymous");

// Bridge Option <-> Result
let n: i32 = maybe_str.ok_or("missing value")?.parse()?;
```
Use `map`, `and_then`, `filter`, `unwrap_or`, `unwrap_or_else`, and `ok_or` to keep the happy path linear.

## Warning Signs

- `.unwrap()` / `.expect()` on I/O, parsing, or any untrusted input in production code
- Functions returning `Result` whose `Err` type is `String` (unmatchable, loses source)
- `anyhow` leaking into a library's public API where callers need to match on kinds
- Swallowing errors with `let _ = fallible();` or `.ok()` without a reason
- Deeply nested `match` on `Option`/`Result` where combinators or `?` would read better
- `panic!` used for input validation the caller could have handled
