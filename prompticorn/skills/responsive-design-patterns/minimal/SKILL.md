# Responsive Design Patterns (Minimal)

## Purpose
Build layouts that adapt to the space actually available, rather than to a guessed set of device widths.

## Core Techniques

### 1. Mobile-First `min-width` Queries
```css
/* base = smallest screen, unconditional */
.grid { display: grid; gap: 1rem; }

@media (min-width: 48rem) { .grid { grid-template-columns: repeat(2, 1fr); } }
@media (min-width: 64rem) { .grid { grid-template-columns: repeat(3, 1fr); } }
```
Min-width queries are additive: each breakpoint only adds what the wider layout
needs. Max-width queries force you to *undo* desktop styles at every step, so you
write more CSS and every override needs another override. The base layer also
ships as the fallback for anything unexpected.

Use `rem` in queries so the layout responds to the user's font size.

### 2. Container Queries for Components
```css
.card-wrap { container-type: inline-size; }

@container (min-width: 24rem) {
  .card { display: grid; grid-template-columns: 8rem 1fr; }
}
```
A media query asks about the viewport, which a component cannot know is relevant.
The same card in a full-width main region and in a 300px sidebar has identical
viewport width and needs different layouts — that is structurally unsolvable with
media queries. Container queries ask about the parent's width, so a component
becomes genuinely portable.

### 3. Let the Grid Break Itself
```css
.grid {
  display: grid;
  gap: 1rem;
  grid-template-columns: repeat(auto-fit, minmax(min(18rem, 100%), 1fr));
}
```
Zero breakpoints, works at every width. The `min(18rem, 100%)` guard prevents
overflow when the container is narrower than the minimum track.

### 4. Fluid Type with a Clamp
```css
h1 { font-size: clamp(1.75rem, 1.2rem + 2.5vw, 3rem); }
```
Scales continuously between a floor and ceiling instead of jumping at breakpoints.
Keep a `rem` term in the middle so text still responds to browser zoom — a pure
`vw` value fails WCAG resize requirements.

### 5. Handle Touch and Pointer, Not Screen Size
```css
@media (hover: hover) and (pointer: fine) { .row:hover { background: #f5f5f5; } }
```
Small screen does not mean touch, and large screen does not mean mouse. Gate
hover-only affordances on capability so touch users don't get stuck states.

### 6. Respect the Real Viewport and Safe Areas
```css
.sheet {
  height: 100dvh;                                   /* not 100vh */
  padding-bottom: env(safe-area-inset-bottom);
}
```
`100vh` on mobile includes the area under the collapsing browser chrome, so
content is clipped. `dvh` tracks the actual visible viewport.

## Warning Signs

- Breakpoints named after specific phones or exact device widths
- A component that only works in one region of the page
- Horizontal scrollbar at 320px
- `font-size` set in `px`, or in `vw` with no `rem` term
- Hover-only controls with no touch equivalent
- Content hidden with `display: none` at small widths rather than reflowed
