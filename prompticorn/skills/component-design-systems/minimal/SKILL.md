# Component Design Systems (Minimal)

## Purpose
Build a component library whose API survives contact with real product work, so feature teams stop reinventing buttons and forking styles.

## Core Techniques

### 1. Tokens Are the Contract, Components Are Not
```css
/* tokens: stable across rewrites */
:root {
  --color-bg-danger: #b42318;
  --space-3: 0.75rem;
  --radius-md: 6px;
}
.btn--danger { background: var(--color-bg-danger); }
```
Component APIs churn — you will rewrite `<Button>` from class components to hooks to server components. Token *names* outlive all of it, and they are also what design tools, native apps, and email templates consume. Version and review token renames like breaking API changes; treat component refactors as routine.

### 2. Compound Components Instead of Prop Explosion
```tsx
// ❌ every new need adds a prop; 14 props, 2^14 states to reason about
<Select label="Team" options={o} renderOption={f} footerText="..." showClear />

// ✅ structure is composed, not configured
<Select value={v} onChange={set}>
  <Select.Trigger>{v?.name ?? "Pick a team"}</Select.Trigger>
  <Select.List>
    {teams.map(t => <Select.Option key={t.id} value={t}>{t.name}</Select.Option>)}
  </Select.List>
</Select>
```
Shared state moves through context, so consumers arrange the parts without you predicting every layout. The prop-explosion version eventually grows a `renderX` escape hatch for each slot — that is the signal you needed composition three props ago.

### 3. Accept `className`, `ref`, and Rest Props
```tsx
const Button = forwardRef<HTMLButtonElement, Props>(
  ({ variant = "primary", className, ...rest }, ref) => (
    <button ref={ref} className={cx(styles[variant], className)} {...rest} />
  )
);
```
A component that swallows `ref` cannot be a Radix/Floating UI trigger, cannot be measured, and cannot be focused imperatively. This one omission is the most common reason teams fork a design-system component.

### 4. Variants as Data, Not Conditionals
```ts
const button = cva("inline-flex items-center rounded-md", {
  variants: {
    variant: { primary: "bg-brand text-white", ghost: "bg-transparent" },
    size: { sm: "h-8 px-3 text-sm", md: "h-10 px-4" },
  },
  defaultVariants: { variant: "primary", size: "md" },
});
```
A variant map is enumerable — you can render every combination into a visual test page. Nested ternaries in JSX are not.

### 5. Build on Headless Primitives
Keyboard nav, focus trapping, `aria-activedescendant`, typeahead, and scroll locking are months of work and the part users notice when it is wrong. Take Radix, React Aria, or Headless UI for menus, dialogs, comboboxes, and tooltips; spend your budget on tokens and visual polish instead.

### 6. Ship the Docs With the Component
Each component gets a usage page showing every variant, the disabled/loading/error state, and one *anti*-example ("don't use Toast for errors that need action"). Undocumented states get reimplemented locally.

## Warning Signs

- Product teams copy-pasting library components into their own folders
- A component with more than ~8 props, or props named `showX` / `hideY` / `isZVariant`
- Hard-coded hex values or pixel spacing anywhere outside the token file
- `ref` or `className` not forwarded
- Two components that differ only in padding
- Design and code have different names for the same color
