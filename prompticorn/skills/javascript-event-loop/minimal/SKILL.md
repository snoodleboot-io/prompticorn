# JavaScript Event Loop (Minimal)

## Purpose
Predict the order JavaScript runs your code: one call stack, a microtask queue
that drains fully first, and a macrotask queue behind it.

## Core Techniques

### 1. One Call Stack, Run To Completion
JS is single-threaded. A function runs to its end before anything else — no
callback, timer, or promise interrupts synchronous code mid-flight.

### 2. Microtasks Beat Macrotasks
After each synchronous run finishes, the loop drains **all** microtasks
(promise callbacks, `queueMicrotask`) before taking one macrotask (`setTimeout`,
I/O, events).
```javascript
console.log("A");
setTimeout(() => console.log("B"), 0);            // macrotask
Promise.resolve().then(() => console.log("C"));   // microtask
console.log("D");
// Order: A, D, C, B
```

### 3. setTimeout(0) Is Not Immediate
The 0 is a *minimum* delay. The callback is a macrotask: it waits for the stack
to clear and the entire microtask queue to drain first. It can be starved
indefinitely by code that keeps scheduling microtasks.

### 4. await Is Promise Scheduling
`await` splits a function: everything after it becomes a microtask that resumes
when the awaited promise settles.
```javascript
async function run() {
  console.log(1);
  await null;              // suspends here
  console.log(3);          // resumes as a microtask
}
run();
console.log(2);
// Order: 1, 2, 3
```

### 5. Closures Capture Variables, Not Values
A closure holds a reference to the variable. Use `let`/`const` (block-scoped) so
each loop iteration captures its own binding.
```javascript
for (let i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);   // 0, 1, 2
}
// with var: 3, 3, 3 — one shared binding
```

### 6. this Is Set By The Call Site
`this` depends on how a function is called, not where it is defined. Arrow
functions have no own `this` — they capture the surrounding one.
```javascript
const obj = {
  name: "x",
  greetLater() {
    setTimeout(() => console.log(this.name), 0);  // arrow keeps obj as this
  },
};
obj.greetLater();   // "x"
```

## Warning Signs

- Relying on `setTimeout(0)` to run "right after" — microtasks jump ahead
- A tight microtask/promise loop starving timers and rendering
- `var` in a loop that schedules callbacks (all see the final value)
- A method passed as a callback losing its `this` (`arr.forEach(obj.method)`)
- Long synchronous work blocking the single thread (freezes the UI)
- Assuming `await` runs the next line synchronously
