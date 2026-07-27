# TypeScript Type System (Minimal)

## Purpose
Use the type system to make illegal states unrepresentable, while keeping types
simple enough that the next reader can follow them.

## Core Techniques

### 1. unknown, Not any
`any` disables checking and spreads silently. `unknown` accepts anything but
forces you to narrow before use.
```typescript
function parse(raw: string): unknown { return JSON.parse(raw); }

const data = parse(input);
if (typeof data === "object" && data !== null && "id" in data) {
  // safe to use data.id here
}
```

### 2. Discriminated Unions + Narrowing
Give each variant a literal tag; `switch` on it and the compiler narrows the type
in each branch.
```typescript
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "rect"; w: number; h: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.r ** 2;   // s is the circle variant
    case "rect":   return s.w * s.h;
  }
}
```

### 3. Generics With Constraints
Type parameters preserve the caller's type; `extends` bounds what they accept.
```typescript
function prop<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];   // return type is exactly the field's type
}
```

### 4. satisfies
Validate a value against a type without widening its inferred type away.
```typescript
const routes = {
  home: "/",
  user: "/users/:id",
} satisfies Record<string, string>;
// routes.home is still the literal "/", and checked against the constraint
```

### 5. Structural Typing
Types match by shape, not by name. Anything with the required members fits — you
do not declare that you implement an interface, you merely match it.
```typescript
interface Point { x: number; y: number; }
const p = { x: 1, y: 2, label: "origin" };
const q: Point = p;   // extra label is fine; shape includes x and y
```

### 6. Lean On Utility Types
`Partial<T>`, `Pick<T, K>`, `Omit<T, K>`, `Readonly<T>`, `Record<K, V>`, and
`ReturnType<F>` derive types from existing ones — one source of truth beats two
hand-maintained copies.

## Warning Signs

- `any` used where `unknown` + narrowing would do
- Type assertions (`as Foo`) papering over a real mismatch
- Conditional/mapped-type "puzzles" nobody on the team can read
- Optional bags of `?` fields instead of a discriminated union
- Duplicated interfaces that could be derived with utility types
- `@ts-ignore` instead of fixing or narrowing the type

See the general-practice conventions for broader code-quality guidance.
