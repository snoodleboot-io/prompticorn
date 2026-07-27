# Rust Ownership And Lifetimes (Minimal)

## Purpose
Move, borrow, or clone deliberately, and satisfy the borrow checker by fixing the design it is complaining about — not by scattering `.clone()`.

## Core Techniques

### 1. Know Whether a Value Moves or Copies
```rust
let s = String::from("hi");
let t = s;              // MOVE: s is now invalid, t owns the heap buffer
// println!("{s}");     // ❌ borrow of moved value

let n = 5;
let m = n;              // COPY: i32 is Copy, n still valid
```
Types that are cheap and stack-only (`i32`, `bool`, `char`, `&T`, small tuples of these) implement `Copy` and are duplicated. Everything owning a heap resource (`String`, `Vec`, `Box`) moves.

### 2. Borrow Instead of Taking Ownership
```rust
fn len(s: &String) -> usize { s.len() }   // reads, does not consume
let s = String::from("hi");
let n = len(&s);                           // s still usable afterward
```
Take `&T` when you only need to read, `&mut T` when you must mutate, and `T` by value only when the function truly needs to own or destroy it. Prefer `&str` over `&String` and `&[T]` over `&Vec<T>` in signatures.

### 3. Respect Aliasing XOR Mutability
```rust
let mut v = vec![1, 2, 3];
let a = &v;          // any number of shared &T ...
let b = &v;          // ... simultaneously is fine
println!("{a:?} {b:?}");
let m = &mut v;      // exactly one &mut T, and no live &T at the same time
m.push(4);
```
At any moment a value has either many readers or one writer, never both. Most borrow-checker errors are this rule surfacing a real data-race-shaped bug.

### 4. Add Lifetimes Only When Elision Can't
```rust
// Elided: compiler infers output borrows from &self / the single input
fn first(s: &str) -> &str { s.split(' ').next().unwrap() }

// Explicit: output borrows from one of TWO inputs, so you must say which
fn longest<'a>(x: &'a str, y: &'a str) -> &'a str {
    if x.len() > y.len() { x } else { y }
}
```
Lifetimes are needed when a returned reference could come from more than one input, or when a struct stores a reference. They never change runtime behavior — they only let the compiler check that no reference outlives its data.

### 5. Reach for Rc / Arc / RefCell / Mutex Only When Needed
| Need | Type |
|---|---|
| Single owner (default) | `T` / `Box<T>` |
| Shared ownership, single thread | `Rc<T>` |
| Shared ownership, across threads | `Arc<T>` |
| Interior mutability, single thread | `RefCell<T>` (panics on aliasing violation at runtime) |
| Interior mutability, across threads | `Mutex<T>` / `RwLock<T>` |

Combine them: `Rc<RefCell<T>>` for a shared-mutable graph node on one thread, `Arc<Mutex<T>>` for shared-mutable state across threads. Each layer trades a compile-time guarantee for a runtime check — add them only when a single owner genuinely cannot work.

### 6. Sometimes Cloning Is the Right Answer
A `.clone()` that removes a borrow spanning a large scope, or copies a small value like a `String` key, is often cheaper than the lifetime plumbing needed to avoid it. Clone when the value is small or the alternative distorts your API; redesign when you are cloning a big buffer inside a hot loop.

## Warning Signs

- `.clone()` sprinkled to silence the borrow checker without asking why the borrow existed
- Returning a reference to a local (`&` to something dropped at function end)
- Fighting lifetimes on a struct that holds `&T` — often it should own the data instead
- `Rc<RefCell<T>>` webs modeling what should be a tree with clear ownership
- `RefCell` borrow panics at runtime — an aliasing bug the compiler would have caught with plain `&mut`
- `Arc<Mutex<T>>` around data that is never actually shared between threads
