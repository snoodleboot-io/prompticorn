# Rust Error Handling Patterns (Verbose)

## Core Patterns

### Result vs Panic: the Recoverable/Bug Split

Rust splits failure into two categories. `Result<T, E>` represents conditions a
caller can reasonably anticipate and recover from — missing files, malformed
input, a rejected request. `panic!` represents a bug: a violated invariant that
means the program is in a state its author never intended.

```rust
use std::num::ParseIntError;

// Recoverable — the caller decides what to do with a bad value.
fn parse_age(input: &str) -> Result<u8, ParseIntError> {
    input.trim().parse::<u8>()
}

// Bug — a positive worker count is an invariant of a valid config.
fn spawn_workers(count: usize) {
    assert!(count > 0, "worker count must be positive, got {count}");
    // ...
}
```

The test: could a well-written caller do something sensible on failure? If yes,
return `Result`. If the only correct response is "fix the code," panic.

### The `?` Operator

`?` is the propagation primitive. On `Ok(v)` it evaluates to `v`; on `Err(e)` it
returns `Err(e.into())` from the enclosing function. It works on `Option` too,
returning `None` early.

```rust
use std::fs::File;
use std::io::{self, Read};

fn read_username() -> Result<String, io::Error> {
    let mut s = String::new();
    File::open("user.txt")?.read_to_string(&mut s)?;   // two early-return points
    Ok(s.trim().to_string())
}
```

The hidden `.into()` in `?` is the mechanism behind unified error types: as long
as the source error implements `From` into the function's error type, `?`
converts it automatically.

### Converting Errors With `From`

A function that can fail in several ways declares one error type and provides a
`From` impl per source. Then `?` converts each at the call site.

```rust
use std::fmt;

#[derive(Debug)]
enum ConfigError {
    Read(std::io::Error),
    Parse(std::num::ParseIntError),
}

impl fmt::Display for ConfigError {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        match self {
            ConfigError::Read(e) => write!(f, "reading config: {e}"),
            ConfigError::Parse(e) => write!(f, "parsing config: {e}"),
        }
    }
}
impl std::error::Error for ConfigError {}

impl From<std::io::Error> for ConfigError {
    fn from(e: std::io::Error) -> Self { ConfigError::Read(e) }
}
impl From<std::num::ParseIntError> for ConfigError {
    fn from(e: std::num::ParseIntError) -> Self { ConfigError::Parse(e) }
}

fn max_connections(path: &str) -> Result<u32, ConfigError> {
    let raw = std::fs::read_to_string(path)?;   // io::Error -> ConfigError
    let n = raw.trim().parse::<u32>()?;          // ParseIntError -> ConfigError
    Ok(n)
}
```

This is exactly the boilerplate `thiserror` eliminates.

### thiserror for Library Errors

Libraries should expose typed errors so downstream code can match on kinds and
react. `thiserror` derives `Display`, `Error`, and the `From` conversions from
attributes — the hand-written enum above collapses to this:

```rust
#[derive(thiserror::Error, Debug)]
pub enum ConfigError {
    #[error("reading config: {0}")]
    Read(#[from] std::io::Error),          // #[from] generates the From impl

    #[error("parsing config: {0}")]
    Parse(#[from] std::num::ParseIntError),

    #[error("missing required key: {key}")]
    MissingKey { key: String },            // struct variant with named field
}
```

Callers get a stable, exhaustively-matchable API:

```rust
match max_connections("app.toml") {
    Ok(n) => start(n),
    Err(ConfigError::MissingKey { key }) => eprintln!("add {key} to app.toml"),
    Err(e) => eprintln!("config invalid: {e}"),
}
```

### anyhow for Application Errors

Application code at the top of the stack usually does not match on error kinds —
it logs the failure with context and exits or returns an HTTP 500. `anyhow`
provides a single boxed error type plus a `.context()` combinator that builds a
readable causal chain.

```rust
use anyhow::{Context, Result};

fn load_profile(user_id: u64) -> Result<Profile> {
    let path = format!("profiles/{user_id}.json");
    let raw = std::fs::read_to_string(&path)
        .with_context(|| format!("reading profile {user_id}"))?;
    let profile: Profile = serde_json::from_str(&raw)
        .with_context(|| format!("parsing profile {user_id}"))?;
    Ok(profile)
}
```

A failure prints as a chain: `reading profile 42: No such file or directory`.
Rule of thumb: `thiserror` in libraries, `anyhow` in binaries and application
layers. Do not put `anyhow::Error` in a library's public signatures — it robs
callers of the ability to match.

### Option Combinators

Reach for combinators before `match` when transforming optional values; they keep
the happy path linear and the intent obvious.

```rust
fn port_or_default(cfg: &Config) -> u16 {
    cfg.get("port")
        .and_then(|s| s.parse::<u16>().ok())   // Option<&str> -> Option<u16>
        .filter(|&p| p != 0)
        .unwrap_or(8080)
}
```

Bridge the two worlds with `ok_or` / `ok_or_else` (Option → Result) and `.ok()`
(Result → Option, discarding the error):

```rust
let name = cfg.get("name").ok_or(ConfigError::MissingKey { key: "name".into() })?;
```

## Common Anti-Patterns

❌ **`String` as the error type** — unmatchable, and it discards the source error.
```rust
fn load() -> Result<Config, String> {
    std::fs::read_to_string("c.toml").map_err(|e| e.to_string())?;   // lossy
    // ...
}
```
✅ **A typed error (thiserror) preserving the source via `#[from]`.**
```rust
fn load() -> Result<Config, ConfigError> {
    let raw = std::fs::read_to_string("c.toml")?;   // source kept in ConfigError::Read
    // ...
}
```

❌ **`unwrap()` on fallible I/O in production** — one bad file crashes the process.
```rust
let cfg = std::fs::read_to_string("c.toml").unwrap();
```
✅ **Propagate, or `expect` with a proof of why it cannot fail.**
```rust
let cfg = std::fs::read_to_string("c.toml")?;
// or, for a compile-time constant that genuinely always parses:
let port: u16 = "8080".parse().expect("literal 8080 is a valid u16");
```

❌ **`anyhow::Error` in a library's public API**, forcing every caller to treat all
failures as opaque.
✅ **Expose a `thiserror` enum; let the application layer wrap it in `anyhow`.**

❌ **Silently swallowing errors.**
```rust
let _ = write_audit_log(&event);   // failure vanishes
```
✅ **Handle or log it; if truly ignorable, say why.**
```rust
if let Err(e) = write_audit_log(&event) {
    tracing::warn!("audit log dropped: {e}");
}
```

❌ **`panic!` for input validation the caller could handle.**
✅ **Return `Err`; reserve panics for invariants that indicate a bug.**

## Error Handling Checklist

- [ ] Recoverable failures return `Result`; panics reserved for bugs and broken invariants
- [ ] Error propagation uses `?`, not manual `match` + early `return`
- [ ] Library crates expose a typed error enum (via `thiserror`), not `String` or `anyhow`
- [ ] Each source error converts through `From` / `#[from]`, preserving the cause
- [ ] Applications use `anyhow` with `.context()` for readable failure chains
- [ ] `unwrap`/`expect` appear only in tests, examples, or provably-infallible spots
- [ ] Every `expect` message states the invariant that makes failure impossible
- [ ] Optional values use combinators (`map`/`and_then`/`ok_or`) over nested matching
- [ ] No error is silently discarded without a stated reason

See `code-review-practices` for reviewing error paths and `debugging-methodology`
for turning an error chain into a root cause.
