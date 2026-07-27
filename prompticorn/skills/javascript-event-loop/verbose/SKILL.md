# JavaScript Event Loop (Verbose)

## Core Patterns

### One Thread, One Call Stack

JavaScript executes on a single thread with one call stack. A function pushed onto
the stack runs to completion before the engine does anything else — no timer,
promise, or event handler can interrupt synchronous code partway. Concurrency
comes from *scheduling* callbacks to run later, never from preemption.

### The Loop: Macrotasks And Microtasks

The event loop repeats a simple cycle:

1. Run one **macrotask** (the current script, a `setTimeout` callback, an I/O event, a DOM event).
2. Drain the **entire microtask queue** — every promise reaction and `queueMicrotask` callback, including any queued while draining.
3. (Browser) Render if needed.
4. Repeat.

The key asymmetry: one macrotask per turn, but *all* microtasks before the next
macrotask.

```javascript
console.log("script start");

setTimeout(() => console.log("timeout"), 0);          // macrotask

Promise.resolve()
  .then(() => console.log("promise 1"))               // microtask
  .then(() => console.log("promise 2"));              // microtask (queued later)

console.log("script end");

// script start, script end, promise 1, promise 2, timeout
```

### Why setTimeout(0) Is Not Immediate

The delay argument is a *minimum*, not a guarantee. The callback becomes a
macrotask, so it cannot run until the current stack unwinds and the whole
microtask queue is empty. Browsers also clamp nested timers to about 4ms after
several levels. If you need "after the current work, before the next macrotask," a
microtask (`queueMicrotask` or `Promise.resolve().then`) is the right tool;
`setTimeout` is strictly later.

### await Desugars To Promise Reactions

An `async` function runs synchronously up to its first `await`. At that point it
returns a pending promise to the caller; the code after the `await` is scheduled
as a microtask that resumes when the awaited value settles.

```javascript
async function seq() {
  console.log("a");
  await Promise.resolve();
  console.log("c");        // microtask continuation
}

console.log("start");
seq();
console.log("b");
// start, a, b, c
```

Two awaits mean two microtask hops. This is why a tight `for await` loop yields to
the microtask queue on every iteration.

### Microtask Starvation

Because the loop drains microtasks completely before the next macrotask, a
callback that keeps scheduling microtasks can starve timers, I/O, and rendering
indefinitely.

```javascript
function spin() {
  Promise.resolve().then(spin);   // the loop never reaches a macrotask or a paint
}
```

Break long work into macrotasks (`setTimeout`) or yield to rendering so the page
stays responsive.

### Closures Capture Bindings

A closure closes over the *variable*, not a snapshot of its value. With `var`
(function-scoped) every iteration shares one binding; with `let`/`const`
(block-scoped) each iteration gets a fresh one.

```javascript
const fns = [];
for (let i = 0; i < 3; i++) fns.push(() => i);
console.log(fns.map((f) => f()));   // [0, 1, 2]

// with var: [3, 3, 3] — one shared i, already incremented to 3
```

### How this Is Bound

`this` is determined by the call, resolved in this order:

1. `new Fn()` — `this` is the fresh instance.
2. `fn.call(obj)` / `fn.apply(obj)` / `fn.bind(obj)` — explicit.
3. `obj.method()` — `this` is `obj` (implicit).
4. Plain `fn()` — `undefined` in strict mode, the global object otherwise.
5. Arrow function — no own `this`; it uses the enclosing lexical `this`.

```javascript
class Timer {
  constructor() { this.n = 0; }
  startBroken() { setInterval(function () { this.n++; }, 1000); } // this is wrong
  startFixed()  { setInterval(() => { this.n++; }, 1000); }       // arrow keeps instance
}
```

## Common Anti-Patterns

❌ **Assuming setTimeout(0) runs before promise callbacks**
```javascript
setTimeout(() => console.log("first?"), 0);
Promise.resolve().then(() => console.log("actually first"));
```
✅ **Use a microtask when you mean "right after current work"**
```javascript
queueMicrotask(() => console.log("right after"));
```

❌ **var in a loop that schedules callbacks**
```javascript
for (var i = 0; i < 3; i++) setTimeout(() => console.log(i), 0);  // 3, 3, 3
```
✅ **Block-scope the loop variable**
```javascript
for (let i = 0; i < 3; i++) setTimeout(() => console.log(i), 0);  // 0, 1, 2
```

❌ **Losing this by detaching a method**
```javascript
button.addEventListener("click", obj.handle);   // this is the element, not obj
```
✅ **Bind or wrap in an arrow**
```javascript
button.addEventListener("click", (e) => obj.handle(e));
```

❌ **Long synchronous work on the one thread**
```javascript
for (let i = 0; i < 1e9; i++) total += i;   // UI frozen until this finishes
```
✅ **Chunk it, or offload to a Web Worker / worker thread.**

## Event Loop Checklist

- [ ] Ordering reasoned about as: sync → all microtasks → one macrotask → repeat
- [ ] Microtasks (promises) understood to run before any `setTimeout`
- [ ] `setTimeout(0)` treated as "later," never "immediately"
- [ ] No unbounded microtask chains that starve timers and rendering
- [ ] `let`/`const` in loops that capture the index in a callback
- [ ] `this` verified against the call site; arrows used to preserve lexical `this`
- [ ] Long CPU work chunked or moved to a worker to keep the thread free
