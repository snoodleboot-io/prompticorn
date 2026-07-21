# State Management Architecture (Verbose)

## Core Patterns

### Classify State Before Choosing Tools

The single highest-leverage decision is recognizing that most of what teams call
"state" is not client state at all.

| Kind | Lifetime | Owner | Tool |
|---|---|---|---|
| Server cache | Until invalidated | Server | React Query, SWR, RTK Query |
| URL / route | Until navigation | Address bar | Router search params |
| Form draft | Until submit | The form | React Hook Form, Formik |
| Local UI | Until unmount | The component | `useState`, `useReducer` |
| Shared client | Session | A store | Zustand, Redux Toolkit, Jotai |
| Persisted prefs | Across sessions | Storage | localStorage + a store |

Server data is a **cache of something you do not own**. It goes stale, needs
deduping across simultaneous callers, needs retry and backoff, needs revalidation
on focus and reconnect, and needs per-key garbage collection. A reducer provides
none of that. Putting fetched data in Redux means reimplementing a cache badly,
one `FETCH_USERS_SUCCESS` action at a time — which is the actual content of most
"Redux is too much boilerplate" complaints.

```ts
// The whole loading/error/staleness/dedupe/retry machine, declared:
const { data, isPending, error } = useQuery({
  queryKey: ["orders", { status }],
  queryFn: () => fetchOrders({ status }),
  staleTime: 30_000,
});
```

### URL as State

```ts
function useFilters() {
  const [params, setParams] = useSearchParams();
  return {
    status: params.get("status") ?? "open",
    page: Number(params.get("page") ?? 1),
    setStatus(status: string) {
      setParams(prev => {
        const next = new URLSearchParams(prev);
        next.set("status", status);
        next.delete("page");      // reset pagination when the filter changes
        return next;
      });
    },
  };
}
```

Ask: *would a user expect to bookmark or share this?* Filters, sort order, the
open tab, the selected row, pagination — yes. Whether a tooltip is showing — no.
Storing shareable state in a client store is how you end up with support tickets
that say "the link you sent me shows different results."

### Colocation and the Lifting Ladder

```
useState in the component
  → lift to nearest common parent
    → Context (rarely changing, widely read)
      → store with selectors (frequently changing, widely read)
```

Move one rung only when you have a concrete second consumer. The cost of
premature globalization is not performance — it is deletability. Local state is
provably dead when its component is deleted; a global slice can never be proven
unread without auditing the whole app, so it accumulates forever.

### Context Performance

Context propagates by identity, and **has no selector**: every consumer re-renders
when the provider value changes, regardless of which field they read.

```tsx
// ❌ new object every render; every consumer re-renders on every parent render
export function AppProvider({ children }) {
  const [user, setUser] = useState(null);
  return <Ctx.Provider value={{ user, setUser }}>{children}</Ctx.Provider>;
}

// ✅ stable identity, and split by change frequency
const ThemeCtx = createContext<Theme>("light");
const UserCtx  = createContext<UserCtxValue | null>(null);

export function AppProvider({ children }) {
  const [user, setUser] = useState<User | null>(null);
  const userValue = useMemo(() => ({ user, setUser }), [user]);
  return (
    <ThemeCtx.Provider value={theme}>
      <UserCtx.Provider value={userValue}>{children}</UserCtx.Provider>
    </ThemeCtx.Provider>
  );
}
```

A useful split rule: one provider per *change frequency*, not one per domain
concept. Theme changes twice a session; a live cursor position changes 60×/second.
They must not share a provider.

### Store Selectors and Normalization

```ts
const useCart = create<CartState>((set) => ({
  itemsById: {} as Record<string, CartItem>,
  add: (item) =>
    set((s) => ({ itemsById: { ...s.itemsById, [item.id]: item } })),
  setQty: (id, qty) =>
    set((s) => ({ itemsById: { ...s.itemsById, [id]: { ...s.itemsById[id], qty } } })),
}));

// Component subscribes to one scalar, not the whole cart.
const qty = useCart((s) => s.itemsById[id]?.qty ?? 0);
```

Normalize by id when the same entity appears in more than one view. A nested array
forces you to hunt for the entity in every update, and lets two copies of the same
order drift apart.

Return primitives from selectors where you can. A selector returning a fresh
object or array (`s => s.items.filter(...)`) creates a new reference every call and
defeats the equality check, so the component re-renders on unrelated store changes.
Either select the ids and look items up individually, or supply a shallow-equality
comparator.

### Derived State

```ts
// ❌ total can disagree with items forever
const [items, setItems] = useState<Item[]>([]);
const [total, setTotal] = useState(0);

// ✅ impossible to disagree
const items = useCart(s => Object.values(s.itemsById));
const total = items.reduce((sum, i) => sum + i.price * i.qty, 0);
```

Any value computable from other state should be computed. The exception is a
genuinely expensive computation over a large collection — measure first, then
`useMemo`. A reduce over 20 items is cheaper than the memo bookkeeping.

## Common Anti-Patterns

❌ **Server responses in a global client store** — you inherit responsibility for
staleness, dedupe, retries, and invalidation.
✅ A query cache keyed by request; invalidate on mutation.

❌ **`useEffect` that syncs a prop into state** — introduces a render with the old
value and a second render to correct it.
✅ Derive during render, or `key` the component to reset it.

❌ **Filters and tabs in a store** — the URL no longer describes the screen, so
links and reloads lose context.
✅ Search params, with the store reserved for genuinely ephemeral state.

❌ **One giant context for the whole app** — every consumer re-renders on every
change to anything.
✅ Split providers by change frequency; memoize the value object.

❌ **Selecting the whole store** — `const s = useStore()` subscribes to everything.
✅ Narrow selectors returning primitives.

❌ **Denormalized duplicates** — the same order embedded in three arrays, updated
in one.
✅ Entities keyed by id; views hold id lists.

❌ **Reaching for Redux/Zustand on day one** — most apps need a query cache and
`useState`, and never need a client store at all.
✅ Add a store when you have shared, non-server, non-URL state across distant
subtrees — and not before.

## State Management Checklist

- [ ] Every piece of state classified: server / URL / form / local / shared
- [ ] Server data lives in a query cache, not a client store
- [ ] Loading and error states come from the cache, not hand-written booleans
- [ ] Mutations invalidate the affected query keys
- [ ] Shareable state (filters, tab, page, selection) lives in the URL
- [ ] Changing a filter resets pagination
- [ ] State starts local and is lifted only when a second consumer exists
- [ ] Context provider values are memoized
- [ ] Providers split by change frequency, not by domain
- [ ] Store subscriptions use narrow selectors
- [ ] Selectors return primitives or use a shallow comparator
- [ ] Entities normalized by id where shared across views
- [ ] No derived value stored alongside its source
- [ ] No `useEffect` copying props into state
- [ ] Persisted state has a version and a migration path
- [ ] Every global slice has at least two distinct consumers
