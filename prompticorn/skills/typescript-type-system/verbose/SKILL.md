# TypeScript Type System (Verbose)

## Core Patterns

### unknown Over any

`any` opts a value out of type checking entirely, and that opt-out is contagious —
every expression derived from it is also unchecked. `unknown` is the safe top
type: it holds any value but permits no operation until you narrow it.

```typescript
function handler(raw: unknown): number {
  if (typeof raw === "number") return raw;         // narrowed to number
  if (typeof raw === "string") return raw.length;  // narrowed to string
  throw new TypeError("unsupported");
}
```

Reserve `any` for genuine escape hatches (untyped third-party code) and isolate
it behind a typed wrapper so it cannot leak downstream.

### Narrowing And Type Guards

The compiler narrows a union as you test it — `typeof`, `instanceof`, `in`,
equality, and truthiness all narrow. For reusable checks, write a user-defined
type guard whose return type is a type predicate.

```typescript
interface Cat { meow(): void; }
interface Dog { bark(): void; }

function isCat(a: Cat | Dog): a is Cat {
  return "meow" in a;
}

function speak(a: Cat | Dog): void {
  if (isCat(a)) a.meow();   // a is Cat here
  else a.bark();            // a is Dog here
}
```

### Discriminated Unions And Exhaustiveness

A shared literal field lets the compiler pick the exact variant per branch. Add a
`never` default to force a compile error when a new variant is added later.

```typescript
type Event =
  | { type: "click"; x: number; y: number }
  | { type: "key"; code: string };

function handle(e: Event): void {
  switch (e.type) {
    case "click": return move(e.x, e.y);
    case "key":   return press(e.code);
    default:
      const _exhaustive: never = e;   // compile error if a variant is unhandled
      return _exhaustive;
  }
}
```

### Generics With Constraints And Inference

Generics carry the caller's type through the function; `extends` restricts what a
parameter accepts.

```typescript
function pluck<T, K extends keyof T>(items: T[], key: K): T[K][] {
  return items.map((it) => it[key]);
}

const ages = pluck(users, "age");   // number[], inferred — no annotation needed
```

Inference has limits: TypeScript infers from arguments, not from the expected
return type flowing backward through a generic chain. When inference fails, supply
the type argument explicitly rather than fighting it.

### satisfies

`satisfies` checks a value against a type while preserving the narrower inferred
type — you get validation without widening.

```typescript
const palette = {
  primary: "#0a7",
  danger: "#e33",
} satisfies Record<string, `#${string}`>;

palette.primary.toUpperCase();   // still known to be a string literal, and checked
```

Without `satisfies`, annotating `: Record<string, string>` would widen every value
to `string` and lose the literal keys.

### Structural Typing

TypeScript types are compatible when their shapes are compatible, regardless of
name. A value with extra properties still satisfies a narrower type — except for
fresh object literals, where excess-property checks flag likely typos.

```typescript
interface Named { name: string; }
const full = { name: "Ada", age: 36 };
const n: Named = full;                 // ok — structural

const bad: Named = { name: "Ada", agee: 36 };  // error — excess property on literal
```

### Utility And Mapped Types

Derive types instead of duplicating them. Built-ins cover the common cases:

| Utility | Produces |
|---|---|
| `Partial<T>` | all properties optional |
| `Required<T>` | all properties required |
| `Pick<T, K>` | subset of keys |
| `Omit<T, K>` | all keys except K |
| `Readonly<T>` | immutable view |
| `Record<K, V>` | object type from keys to values |
| `ReturnType<F>` | a function's return type |

A mapped type expresses your own transformations:

```typescript
type Nullable<T> = { [K in keyof T]: T[K] | null };
```

## Common Anti-Patterns

❌ **any as a shortcut**
```typescript
function parse(json: string): any { return JSON.parse(json); }
```
✅ **unknown plus narrowing**
```typescript
function parse(json: string): unknown { return JSON.parse(json); }
```

❌ **Assertion to force a mismatch through**
```typescript
const user = data as User;   // no check — a claim the compiler now trusts blindly
```
✅ **Validate, then the type is earned**
```typescript
if (isUser(data)) { /* data is User here */ }
```

❌ **Optional-bag object where a union belongs**
```typescript
interface Resp { ok?: boolean; data?: string; error?: string; }
```
✅ **Discriminated union — illegal combinations become unrepresentable**
```typescript
type Resp = { ok: true; data: string } | { ok: false; error: string };
```

❌ **Type puzzle nobody can maintain**
```typescript
type DeepKeys<T> = /* five nested conditional + mapped types */ never;
```
✅ **Prefer the simplest type that holds the invariant.** Cleverness costs the
next reader; spend it only where it prevents real bugs.

## Type System Checklist

- [ ] `unknown` (not `any`) at untyped boundaries, narrowed before use
- [ ] `strict` enabled in `tsconfig.json`
- [ ] Unions discriminated by a literal tag, with a `never` exhaustiveness guard
- [ ] Type guards used for reusable runtime narrowing
- [ ] Generics constrained with `extends`; explicit args only where inference fails
- [ ] `satisfies` used to validate without widening literals
- [ ] Types derived via utility/mapped types instead of hand-duplicated
- [ ] `as` assertions justified and rare; no blind `@ts-ignore`
- [ ] Type complexity kept to what the invariant actually needs
