# CSS Performance Optimization (Minimal)

## Purpose
Keep style and layout work off the main thread so scrolling and animation hold 60fps, and stop CSS from blocking first paint.

## Core Techniques

### 1. Animate Only `transform` and `opacity`
```css
/* ❌ every frame: layout → paint → composite, on the main thread */
.card { transition: left 200ms, height 200ms; }

/* ✅ compositor-only: no layout, no paint */
.card { transition: transform 200ms, opacity 200ms; }
```
| Property | Cost per frame |
|---|---|
| `transform`, `opacity` | Composite only |
| `background-color`, `box-shadow`, `color` | Paint |
| `width`, `height`, `top`, `margin`, `font-size` | Layout + paint |

A layout-triggering animation must recompute geometry for the subtree 60×/second.
Transform and opacity can be handled by the compositor on its own thread, so they
keep animating even when JS is busy.

### 2. Promote Deliberately with `will-change`
```css
.drawer:hover { will-change: transform; }   /* hint just before it animates */
```
Each promoted layer costs GPU memory (roughly width × height × 4 bytes). Applying
`will-change` to a whole list is how you turn a smooth page into a memory problem.
Add it shortly before the animation and remove it after.

### 3. Contain Layout with `contain` and `content-visibility`
```css
.feed-item {
  content-visibility: auto;
  contain-intrinsic-size: auto 320px;   /* placeholder height, keeps scrollbar sane */
}
```
`content-visibility: auto` skips layout and paint entirely for off-screen items;
on a long feed this can cut initial rendering work by an order of magnitude.
`contain-intrinsic-size` is not optional — without it, unrendered items have zero
height and the scrollbar jumps.

### 4. Avoid Layout Thrashing
```js
// ❌ read → write → read → write forces a reflow per iteration
els.forEach(el => { el.style.height = el.offsetHeight * 2 + "px"; });

// ✅ batch reads, then writes
const hs = els.map(el => el.offsetHeight);
els.forEach((el, i) => { el.style.height = hs[i] * 2 + "px"; });
```
Reading `offsetHeight`/`getBoundingClientRect()` after a write forces synchronous
layout. Interleaving them is usually the real cause of a "slow CSS" complaint.

### 5. Stop CSS Blocking First Paint
Every `<link rel="stylesheet">` in `<head>` is render-blocking. Inline the
above-the-fold rules and load the rest with `media="print" onload="this.media='all'"`,
or scope non-critical sheets with a real media attribute so the browser
deprioritizes them.

### 6. Load Fonts Without Invisible Text
```css
@font-face { font-family: Inter; src: url(inter.woff2) format("woff2"); font-display: swap; }
```
`swap` shows fallback text immediately; the default `block` hides text for up to
3 seconds. Pair with `<link rel="preload" as="font" crossorigin>` for the one
font actually used above the fold.

## Warning Signs

- Transitions on `width`, `height`, `top`, or `left`
- `will-change` in a base class or applied to list items
- Long "Recalculate Style" / "Layout" bars in a performance profile
- A stylesheet larger than ~100 KB with most rules unmatched
- `@import` inside CSS (serializes requests)
- Text invisible for the first second on a cold load
