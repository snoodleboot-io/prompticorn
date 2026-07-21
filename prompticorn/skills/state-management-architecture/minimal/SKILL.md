# State Management Architecture (Minimal)

## Purpose
Decide where each piece of application state lives, so you don't end up with a global store that is 80% cached server responses.

## Core Techniques

### 1. Classify Before You Choose a Library
| Kind | Example | Lives in |
|---|---|---|
| Server cache | user list, order detail | React Query / SWR / RTK Query |
| URL | filters, page, selected tab | router search params |
| Form draft | in-progress inputs | form library, local |
| Local UI | dropdown open, hover | `useState` in the component |
| Shared client | theme, cart, undo stack | Zustand / Redux / Context |

Most "we regret Redux" stories are really "we put server data in Redux." Fetched
data is a *cache* — it needs staleness, revalidation, dedupe, and retries, none of
which a reducer gives you and all of which you will hand-roll badly.

### 2. Put Filters in the URL, Not in a Store
```ts
const [params, setParams] = useSearchParams();
const status = params.get("status") ?? "open";
```
URL state is free persistence, free sharing, free back-button support, and it
survives reload. State that a user would reasonably expect to bookmark belongs
there — anything else silently breaks link-sharing.

### 3. Derive; Don't Store Derived Values
```ts
// ❌ two sources of truth, guaranteed to drift
const [items, setItems] = useState([]);
const [total, setTotal] = useState(0);

// ✅ one source, computed at render
const total = items.reduce((s, i) => s + i.price * i.qty, 0);
```
Only memoize after measuring. `useMemo` on a 20-item reduce costs more than it saves.

### 4. Colocate, Then Lift Only on Demand
Start with `useState` in the component that uses it. Lift when a second component
genuinely needs it; go global only when the consumers are far apart in the tree.
Premature globalization is what makes state hard to delete later — you can never
prove nothing reads it.

### 5. Context Re-Renders Every Consumer
```tsx
// ❌ rebuilt every render → new identity → every consumer re-renders
const value = { user, setUser };
return <Ctx.Provider value={value}>{children}</Ctx.Provider>;

// ✅ stable identity across renders
const value = useMemo(() => ({ user, setUser }), [user]);
```
Context has no selector mechanism: any change re-renders all consumers. Split
rarely-changing state (theme) from frequently-changing state (cursor position)
into separate providers, or use a store with selectors.

### 6. Select Narrowly in Stores
```ts
// ❌ re-renders on any store change
const store = useStore();
// ✅ re-renders only when this user's name changes
const name = useStore(s => s.users[id]?.name);
```

## Warning Signs

- `isLoading` / `error` booleans hand-written next to every fetch
- Filter or tab state that resets on reload and can't be linked to
- Two fields that must be updated together to stay consistent
- A global store slice read by exactly one component
- `useEffect` that copies a prop into state
- Context provider value constructed inline in JSX
