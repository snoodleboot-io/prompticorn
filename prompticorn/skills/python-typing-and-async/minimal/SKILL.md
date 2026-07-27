# Python Typing And Async (Minimal)

## Purpose
Use type hints where they catch real bugs, and write async code that actually
runs concurrently — without blocking the one event loop you have.

## Core Techniques

### 1. Type The Boundaries, Not Everything
Types earn their keep on public function signatures, data shapes, and anything
crossing a module boundary. Local throwaway variables rarely need them.
```python
def parse(raw: bytes) -> dict[str, int]: ...
```
Run a checker (`mypy --strict` or `pyright`); hints are documentation until a
tool enforces them.

### 2. Protocol For Structural Typing
Prefer duck-typed contracts over inheritance. A `Protocol` matches anything with
the right shape — no base class required.
```python
from typing import Protocol

class Reader(Protocol):
    def read(self, n: int) -> bytes: ...

def consume(r: Reader) -> bytes:   # accepts files, sockets, BytesIO...
    return r.read(1024)
```

### 3. TypedDict, Literal, And Generics
```python
from typing import TypedDict, Literal

class User(TypedDict):
    id: int
    role: Literal["admin", "member"]   # only these two strings type-check

def first[T](items: list[T]) -> T | None:   # PEP 695 generic
    return items[0] if items else None
```
`TypedDict` types a JSON-ish dict without a class; `Literal` pins a value to a
fixed set; generics preserve the element type through a call.

### 4. Don't Block The Event Loop
`await` yields control; a synchronous call does not. One blocking call freezes
every other task on the loop.
```python
# ❌ blocks the loop — no other coroutine runs during the sleep
time.sleep(5)
# ✅ yields, so the loop services other tasks
await asyncio.sleep(5)
```
Push unavoidable blocking work (CPU, legacy sync I/O) off the loop with
`await asyncio.to_thread(fn, ...)`.

### 5. gather vs TaskGroup
```python
# gather: fan out, collect results in order
results = await asyncio.gather(fetch(a), fetch(b))

# TaskGroup (3.11+): structured — if one task raises, siblings are cancelled
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(fetch(a))
    t2 = tg.create_task(fetch(b))
```
Prefer `TaskGroup`: bare `gather` leaves sibling tasks running after a failure
unless you handle `return_exceptions` yourself.

### 6. GIL: Async Is Not Parallel CPU
The GIL lets one thread run Python bytecode at a time.
- **I/O-bound** → `asyncio` or threads: waiting releases the GIL, so concurrency works.
- **CPU-bound** → `multiprocessing` (or a C extension): only separate processes
  run Python in parallel. Async and threads will not speed up pure computation.

See the `python-runtime` skill for interpreter and memory internals.

## Warning Signs

- `Any` sprinkled to silence the checker instead of a real type
- `requests`, `time.sleep`, or heavy CPU work called inside a coroutine
- Type hints present but no `mypy`/`pyright` in CI
- Bare `asyncio.gather` where a failure should cancel the rest
- Threads used to speed up CPU-bound code (the GIL blocks it)
- A coroutine created but never awaited (`RuntimeWarning: never awaited`)
