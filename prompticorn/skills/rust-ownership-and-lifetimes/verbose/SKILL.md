# Rust Ownership And Lifetimes (Verbose)

## Core Patterns

### Move Semantics as the Default

Every value has exactly one owner. Assigning or passing a non-`Copy` value moves
ownership; the source binding becomes invalid, and the compiler enforces this at
compile time with zero runtime cost.

```rust
fn consume(v: Vec<i32>) -> usize { v.len() }   // takes ownership, drops v at end

fn main() {
    let data = vec![1, 2, 3];
    let n = consume(data);      // data MOVED into consume
    // data is gone here — using it is a compile error
    println!("{n}");
}
```

`Copy` types opt out: they are bit-for-bit duplicated instead of moved, because
they own no heap resource and duplication is trivial. `i32`, `f64`, `bool`,
`char`, raw pointers, shared references `&T`, and tuples/arrays of `Copy` types
are `Copy`. `String`, `Vec<T>`, `Box<T>`, and anything with a `Drop` impl are not.

### Borrowing: Shared vs Exclusive

Borrowing lets a function use a value without taking ownership. The core rule the
borrow checker enforces is **aliasing xor mutability**: at any point a value may
have any number of shared references `&T`, or exactly one exclusive reference
`&mut T`, but never both at once.

```rust
fn describe(s: &str) -> String { format!("{} chars", s.len()) }   // read-only
fn push_bang(s: &mut String) { s.push('!'); }                     // mutate

fn main() {
    let mut msg = String::from("hi");
    println!("{}", describe(&msg));   // shared borrow ends when call returns
    push_bang(&mut msg);              // exclusive borrow, now allowed
    println!("{msg}");
}
```

This rule is why Rust prevents data races at compile time: a race requires two
accesses to the same location where at least one writes, and that is exactly the
`&T` + `&mut T` combination the checker forbids.

### Choosing the Signature Type

The parameter type is an API contract. Pick the least demanding form that works:

| You need to... | Take | Notes |
|---|---|---|
| Read the value | `&T` | Caller keeps ownership |
| Read a string/slice | `&str` / `&[T]` | Accepts more callers than `&String` / `&Vec<T>` |
| Mutate in place | `&mut T` | Caller keeps ownership, sees changes |
| Store or destroy it | `T` | Only when ownership transfer is real |

Returning owned `T` transfers ownership out; returning `&T` ties the result's
lifetime to an input.

### When Lifetimes Are Required

Lifetime elision handles the common cases: one input reference, or a method with
`&self`. You must write lifetimes explicitly when the compiler cannot infer which
input a returned reference borrows from, or when a struct holds a reference.

```rust
// Struct holding a borrow: the annotation says "an Excerpt cannot outlive the
// str it points into."
struct Excerpt<'a> {
    part: &'a str,
}

impl<'a> Excerpt<'a> {
    fn part(&self) -> &str { self.part }   // elision applies to the method
}

fn main() {
    let novel = String::from("Call me Ishmael. Some years ago...");
    let first = novel.split('.').next().unwrap();
    let e = Excerpt { part: first };
    println!("{}", e.part());
}
```

Lifetimes are compile-time-only: they constrain how long borrows may live and are
erased before code generation. They never make anything slower.

### Interior Mutability and Shared Ownership

When single ownership genuinely does not fit — a graph, an observer list, shared
cache — reach for the smart-pointer ladder, one rung at a time.

```rust
use std::cell::RefCell;
use std::rc::Rc;

// A tree node shared and mutated on one thread.
type Node = Rc<RefCell<TreeNode>>;

struct TreeNode {
    value: i32,
    children: Vec<Node>,
}

fn add_child(parent: &Node, value: i32) {
    let child = Rc::new(RefCell::new(TreeNode { value, children: vec![] }));
    parent.borrow_mut().children.push(child);   // runtime-checked exclusive borrow
}
```

`Rc<T>` gives shared ownership via reference counting (single thread). `RefCell<T>`
moves the aliasing-xor-mutability check from compile time to runtime — it panics
if you `borrow_mut()` while another borrow is live. Across threads, swap in the
thread-safe pair `Arc<T>` + `Mutex<T>` (or `RwLock<T>`).

```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let counter = Arc::new(Mutex::new(0));
    let mut handles = vec![];
    for _ in 0..4 {
        let c = Arc::clone(&counter);       // clones the pointer, not the data
        handles.push(thread::spawn(move || {
            *c.lock().unwrap() += 1;
        }));
    }
    for h in handles { h.join().unwrap(); }
    println!("{}", *counter.lock().unwrap());   // 4
}
```

`Arc::clone` bumps a reference count; it does not deep-copy the payload. That is
the intended, cheap way to hand shared state to each thread.

### Cloning as a Deliberate Choice

Cloning is not a failure. It is the right call when the value is small, when the
clone lives briefly, or when avoiding it would force a lifetime parameter through
half your codebase for no real gain.

```rust
// Reasonable: a short owned key decouples the entry's lifetime from the map's.
fn cache_key(prefix: &str, id: u64) -> String {
    format!("{prefix}:{id}")
}
```

The clone to scrutinize is the one in a hot loop copying a large buffer, or the
one hiding an ownership model you never designed.

## Common Anti-Patterns

❌ **Cloning to silence the borrow checker without understanding the error.**
```rust
fn totals(items: &[Item]) -> Vec<u32> {
    let items = items.to_vec();   // needless full copy to dodge a borrow
    items.iter().map(|i| i.qty).collect()
}
```
✅ **Borrow through — the read never needed ownership.**
```rust
fn totals(items: &[Item]) -> Vec<u32> {
    items.iter().map(|i| i.qty).collect()
}
```

❌ **Returning a reference to a local — it is dropped at the `}`.**
```rust
fn label() -> &str {
    let s = String::from("temp");
    &s            // ❌ s dies here; the reference would dangle
}
```
✅ **Return the owned value (or a `'static`).**
```rust
fn label() -> String {
    String::from("temp")
}
```

❌ **A struct borrowing data it is the only user of, forcing lifetimes everywhere.**
```rust
struct Report<'a> { title: &'a str }   // now 'a infects every holder of Report
```
✅ **Own the data when the struct outlives or solely uses it.**
```rust
struct Report { title: String }
```

❌ **`Rc<RefCell<T>>` graphs modeling a plain tree**, inviting runtime borrow
panics and reference cycles that leak.
✅ **Use ownership (`Box`/`Vec`) for trees; reserve `Rc`/`RefCell` for true sharing,
and break parent cycles with `Weak<T>`.**

❌ **`Arc<Mutex<T>>` around data confined to one thread** — paying atomics and lock
overhead for nothing.
✅ **Plain `T`, or `Rc<RefCell<T>>` if you need single-thread interior mutability.**

## Ownership Checklist

- [ ] Each function takes the least-demanding type: `&T` / `&mut T` / `T` in that order of preference
- [ ] Signatures use `&str` and `&[T]` rather than `&String` / `&Vec<T>`
- [ ] No `.clone()` whose only purpose is to dodge a borrow you could restructure
- [ ] Lifetimes written only where elision cannot infer them; structs justify any borrow they hold
- [ ] No reference returned to a value dropped at function end
- [ ] `Rc`/`Arc`/`RefCell`/`Mutex` introduced only where single ownership cannot express the design
- [ ] `Arc`/`Mutex` used for cross-thread sharing; `Rc`/`RefCell` kept to one thread
- [ ] Reference cycles broken with `Weak<T>`
- [ ] Any clone in a hot path is small, or justified against the lifetime alternative

See `code-review-practices` for review-comment conventions and `performance-optimization`
for measuring before optimizing away a clone.
