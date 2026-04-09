# Webpage2: Cyberpunk Landing Page

A futuristic, cyberpunk-themed landing page for Promptosaurus featuring neon aesthetics, animated effects, and an exciting visual design.

## Overview

This is a complete redesign of the standard landing page with a focus on:
- **Cyberpunk Aesthetic**: Neon colors (cyan, pink, green) with dark navy backgrounds
- **Animated Effects**: Grid patterns, scanlines, glowing text, pulsing animations
- **Circuit Patterns**: Visual elements inspired by technology and data flows
- **Holographic Design**: Gradient borders and futuristic card layouts
- **Dynamic Content**: Animated counters, smooth scrolls, interactive sections

## Directory Structure

```
webpage2/
├── index.html              # Main landing page (12 sections)
├── css/
│   ├── cyberpunk.css      # Neon colors, effects, and animations
│   └── styles.css         # Layout, components, and utilities
├── js/
│   ├── main.js            # Navigation, interactivity, utilities
│   ├── effects.js         # Visual effects and animations
│   └── metrics.js         # Animated counters and metrics
├── img/
│   └── promptosaurs3.png  # Cybernetic dinosaur hero image
└── README.md              # This file
```

## Features

### Design Elements

#### Colors
- **Primary Dark**: `#0a0e27` - Deep space navy
- **Neon Cyan**: `#00ffff` - Glowing cyan accents
- **Neon Pink**: `#ff006e` - Energy pink highlights
- **Neon Green**: `#00ff41` - System status green
- **Grid Color**: `#1e3a5f` - Subtle blue grid

#### Visual Effects
- Animated grid background with parallax
- Scanline overlay (2-3% opacity) for retro feel
- Glowing text shadows for neon effect
- Pulsing animations on key elements
- Holographic card borders with gradients
- Circuit pattern overlays
- Smooth scroll transitions

### 12 Sections

1. **Navigation** - Sticky navbar with neon accents and scroll spy
2. **Hero** - Cybernetic dinosaur with animated glow rings and floating effect
3. **The Matrix Problem** - 4-card grid showing configuration chaos
4. **Unified Reality** - IR system explanation with 5-layer diagram
5. **System Status** - Animated metrics with progress bars and counters
6. **5 Protocols** - 5 protocol cards with colored borders and hover effects
7. **Neural Pathways** - 5-step quick start flow with code example
8. **Combat Ready** - 6 benefits grid with icons and descriptions
9. **Anomalies Detected** - FAQ accordion with collapsible items
10. **Execute Command** - Final CTA with buttons and command line display
11. **Network Status** - Footer with status indicators and links
12. **Additional Elements** - Scanlines, grid background, global effects

### Interactive Features

- **Scroll Spy Navigation** - Highlights current section in nav
- **Smooth Scrolling** - Animated scroll-to-section navigation
- **FAQ Accordion** - Expandable FAQ items with animation
- **Animated Counters** - Metrics count up when visible
- **Hover Effects** - Cards lift and glow on hover
- **Keyboard Navigation** - Support for keyboard accessibility
- **Easter Egg** - Konami code triggers a system message

## CSS Classes & Utilities

### Text Effects
```css
.neon-text          /* Cyan glow text */
.glowing-text       /* Bright cyan with intense glow */
.glowing-text-secondary  /* Green glow text */
.neon-cyan, .neon-pink, .neon-green  /* Color classes */
```

### Animations
```css
@keyframes neon-pulse     /* Pulsing glow effect */
@keyframes scanline-shift /* Moving scanlines */
@keyframes grid-shift     /* Animated grid */
@keyframes dino-float     /* Dinosaur floating */
@keyframes ring-expand    /* Expanding glow rings */
@keyframes glow-pulse     /* General glow pulse */
@keyframes neon-flicker   /* Subtle text flicker */
```

### Component Classes
```css
.matrix-card       /* Matrix problem cards */
.protocol-card     /* Protocol builder cards */
.metric-card       /* Metrics display cards */
.combat-card       /* Combat ready cards */
.faq-item          /* FAQ accordion items */
.btn               /* Button styling */
.btn-primary       /* Primary CTA button */
.btn-secondary     /* Secondary button */
```

## JavaScript Functions

### Main.js
- `setupNavigation()` - Initialize navigation behavior
- `setupSmoothScroll()` - Enable smooth scrolling to sections
- `setupScrollSpy()` - Highlight current section in nav
- `setupFAQInteractions()` - Initialize FAQ accordion
- `setupButtonInteractions()` - Add ripple effects to buttons
- `setupHoverEffects()` - Configure card hover animations

### Effects.js
- `triggerGlowEffect(element)` - Trigger neon glow animation
- `addHoverGlow(element, color)` - Add hover glow to element
- `animateCounter(element, target, duration)` - Animate number counter
- `addGlowShadow(element, color, intensity)` - Add glowing shadow
- `createDataStream(container)` - Create animated data stream effect
- `initializeScrollReveal()` - Setup scroll-triggered animations

### Metrics.js
- `animateMetrics()` - Trigger metric animations when visible
- `animateCounterValue(element, target, duration)` - Animate counter
- `MetricsSystem` - Class for managing metrics
- `MetricsDashboard` - Class for real-time dashboard

## Responsive Design

The page is fully responsive:
- **Desktop** (1200px+) - Full layout with all effects
- **Tablet** (768px-1199px) - Optimized grid layouts
- **Mobile** (< 768px) - Single column, optimized for touch

Breakpoints:
```css
@media (max-width: 1024px)  /* Large tablet */
@media (max-width: 768px)   /* Tablet & mobile */
@media (max-width: 480px)   /* Small mobile */
```

## Performance Optimizations

- Hardware-accelerated animations (transform, opacity)
- Passive event listeners for scroll performance
- Debounced and throttled functions
- Optimized grid background (SVG pattern fallback possible)
- Minimal repaints with efficient CSS
- RequestAnimationFrame for smooth 60fps animations

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

Features requiring modern CSS:
- CSS Grid
- CSS Custom Properties (variables)
- CSS Animations
- Linear Gradient
- Backdrop Filter (graceful degradation)

## Customization

### Changing Colors

Edit `:root` variables in `cyberpunk.css`:
```css
--color-cyan: #00ffff;      /* Change neon cyan */
--color-pink: #ff006e;      /* Change neon pink */
--color-green: #00ff41;     /* Change neon green */
```

### Adjusting Animations

Modify animation timings in `cyberpunk.css` and JS files:
- Grid shift: `animation: grid-shift 10s linear infinite;`
- Scanlines: `animation: scanline-shift 8s linear infinite;`
- Glow pulse: `animation: neon-pulse 2s ease-in-out infinite;`

### Adding New Sections

1. Add HTML in `index.html`
2. Create CSS in `cyberpunk.css`
3. Add interactions in `main.js` if needed
4. Follow existing section naming conventions

## Deployment

### Local Testing
```bash
# Simple HTTP server
python -m http.server 8000
# or
python3 -m http.server 8000
```

Visit `http://localhost:8000/webpage2/`

### GitHub Pages
The page is GitHub Pages ready:
- No build process required
- Static HTML/CSS/JS
- Compatible with GitHub Pages hosting

Push to repository and enable Pages on the `main` branch.

## Design Philosophy

### Cyberpunk Principles
- **Dark Backgrounds**: Reduces eye strain, emphasizes neon colors
- **Neon Glow**: Creates depth and futuristic feel
- **Circuit Patterns**: Evokes technology and data networks
- **Smooth Animations**: Feels high-tech and responsive
- **Aggressive Color**: Pink, cyan, green create energy
- **Professional Yet Exciting**: Suitable for tech companies

### User Experience
- Clear information hierarchy
- Smooth scroll navigation
- Accessible keyboard shortcuts
- Responsive touch interactions
- Performance-optimized animations
- Light on CPU with GPU acceleration

## Accessibility

The page includes:
- Semantic HTML structure
- ARIA labels where appropriate
- Keyboard navigation support
- Color contrast compliance (mostly)
- Screen reader friendly structure
- Reduced motion support (`prefers-reduced-motion`)
- Focus visible indicators

## Future Enhancements

Possible additions:
- [ ] Three.js background animation
- [ ] WebGL shader effects
- [ ] Real-time metric updates (WebSocket)
- [ ] Dark/Light mode toggle
- [ ] Multi-language support
- [ ] Video background option
- [ ] Advanced motion parallax
- [ ] Interactive 3D dinosaur model
- [ ] Sound effects (optional)

## Browser DevTools Tips

Check these in browser DevTools:
1. **Performance** - Verify smooth 60fps animations
2. **Network** - Check image loading
3. **Lighthouse** - Audit performance, accessibility
4. **Console** - Look for Easter egg message

## License

Part of Promptosaurus project. See main repository for license details.

---

**Built with ❤️ and neon glow**

*System Online. Ready for Deployment.*
