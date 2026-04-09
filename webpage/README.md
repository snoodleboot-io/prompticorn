# Promptosaurus Landing Page

Professional dark-themed product landing page for Promptosaurus, targeting senior engineers, technical leaders, and decision-makers.

## 📁 Structure

```
webpage/
├── index.html              # Main landing page
├── css/
│   ├── dark-theme.css     # Color palette and theme variables
│   └── styles.css         # Component styles and layout
├── js/
│   ├── main.js            # Smooth scrolling, animations, navigation
│   └── metrics.js         # Animated counter functionality
├── img/
│   ├── promptosaurs1.png  # Turquoise fire mascot (hero)
│   └── promptosaurs2.png  # Secondary mascot variant
└── README.md              # This file
```

## 🎨 Design

### Color Palette

Dark navy background with electric cyan accents:

- **Primary Background:** `#0f172a` (Navy black)
- **Secondary Background:** `#1a2742` (Slightly lighter navy)
- **Accent Color:** `#00d4ff` (Electric cyan)
- **Text Primary:** `#f0f9ff` (Off-white)
- **Text Secondary:** `#cbd5e1` (Light gray)

### Typography

System font stack for optimal performance:
```css
-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", ...
```

Monospace font stack for code blocks:
```css
'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New'
```

## 📱 Responsive Design

- **Desktop:** Full 12-column grid layouts
- **Tablet:** 2-column grids with optimized spacing
- **Mobile:** Single column with touch-friendly buttons and spacing

Breakpoints:
- `768px` - Tablet
- `480px` - Mobile

## 🎯 Sections

1. **Navigation Bar** - Sticky navbar with smooth scroll links
2. **Hero** - Animated mascot, value prop, CTA buttons
3. **Problem** - 3-column layout describing pain points
4. **Solution** - IR diagram showing transformation to 5 tools
5. **Why It Matters** - 6 cards for technical leaders
6. **Proof** - Metrics with animated counters
7. **Builders** - 5 builder cards (OpenAI, Anthropic, Bedrock, Replicate, Custom)
8. **Quick Start** - Installation and code example
9. **Social Proof** - Stats and testimonial
10. **FAQ** - 6 common questions answered
11. **Final CTA** - Conversion push
12. **Footer** - Links and version info

## ✨ Features

### Animations

- **Smooth Scroll:** Anchor links scroll smoothly to sections
- **Scroll Animations:** Cards fade in and slide up when scrolled into view
- **Hover Effects:** Interactive cards lift on hover
- **Metric Counters:** Animated number increments (uses easing)
- **Logo Bob:** Dinosaur mascot bobs up and down in navbar
- **Glow Effects:** Radial gradients create glowing effects
- **Gradient Animations:** Smooth color transitions

### Performance Optimizations

- **Zero Dependencies:** Pure HTML, CSS, JavaScript
- **Lazy Loading:** Images optimized for web
- **CSS Variables:** Easy theme customization
- **Intersection Observer:** Efficient scroll animations
- **RequestAnimationFrame:** Smooth 60fps animations

## 🚀 Getting Started

### Local Development

Simply open `index.html` in a browser:

```bash
cd webpage
open index.html
# or
firefox index.html
```

Or use a local server:

```bash
python -m http.server 8000
# Visit http://localhost:8000/webpage/
```

### Customization

#### Change Colors

Edit CSS variables in `css/dark-theme.css`:

```css
:root {
    --color-accent-primary: #00d4ff;  /* Change accent color */
    --color-text-primary: #f0f9ff;    /* Change text color */
}
```

#### Update Content

Edit sections in `index.html`:
- Hero headline/subtitle
- Problem descriptions
- Builder names/descriptions
- FAQ questions/answers

#### Modify Images

Replace images in `img/`:
```bash
cp path/to/new/image.png img/promptosaurs1.png
```

## 📊 Metrics Displayed

The landing page showcases these key metrics:

| Metric | Value | Meaning |
|--------|-------|---------|
| Tests Passing | 1,200/1,200 | 100% test success rate |
| Type Errors | 0 | Fully type-safe TypeScript |
| Code Coverage | 93.7% | Comprehensive test coverage |
| Mutation Score | 83.9% | Tests catch real bugs |
| Performance | 100-1,250x | Speed improvements |
| Dev Time | 6 months | Battle-tested |

These counters animate when the page scrolls to the proof section.

## 🔗 Links

All external links:

- **GitHub:** `https://github.com/Kilo-Org/promptosaurus`
- **Documentation:** `https://github.com/Kilo-Org/promptosaurus/tree/main/docs`
- **Issues:** `https://github.com/Kilo-Org/promptosaurus/issues`

Update these in `index.html` if URLs change.

## ♿ Accessibility

- Semantic HTML structure (`<nav>`, `<section>`, `<footer>`)
- Proper heading hierarchy (H1 > H2 > H3)
- Color contrast ratios meet WCAG AA standards
- Alt text for images
- Keyboard-navigable links
- Focus styles on interactive elements

## 📈 SEO

Metadata included:

```html
<meta name="description" content="...">
<meta name="theme-color" content="#0f172a">
<title>Promptosaurus — Unified AI Prompts for Production</title>
```

## 🌐 Deployment

### GitHub Pages

1. Push `webpage/` to repository
2. Enable GitHub Pages in repo settings
3. Set source to `main` branch
4. Site available at `https://username.github.io/promptosaurus/webpage/`

### Other Hosts

Works on any static hosting:
- Netlify
- Vercel
- AWS S3 + CloudFront
- Cloudflare Pages
- Traditional web hosting

## 📦 File Sizes

Optimized for fast loading:

- `index.html` - ~25 KB
- `styles.css` - ~20 KB
- `dark-theme.css` - ~3 KB
- `main.js` - ~4 KB
- `metrics.js` - ~2 KB
- `promptosaurs1.png` - ~436 KB (hero image)
- `promptosaurs2.png` - ~264 KB (secondary)

**Total uncompressed:** ~754 KB
**Typical gzipped load:** ~150-200 KB

Load time: < 3s on 4G connection

## 🔧 Development

### Adding New Sections

1. Add HTML to `index.html`
2. Add CSS class to `styles.css`
3. Use consistent naming: `section`, `card`, etc.
4. Ensure responsive grid layouts

### Adding Animations

Use the provided animation patterns:

```css
/* Fade in and slide up */
@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.element {
    animation: fadeUp 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### Testing Responsive Design

Use browser DevTools:

1. Open DevTools (F12)
2. Toggle Device Toolbar (Ctrl+Shift+M)
3. Test common breakpoints:
   - iPhone SE (375px)
   - iPad (768px)
   - Desktop (1200px)

## 📝 Notes

- Pure HTML/CSS/JS (no build process needed)
- Dinosaur mascot animation can be customized
- Dark theme is set globally and applies to all sections
- All metrics are hardcoded (can be made dynamic with API calls)
- Email signup not implemented (can be added with Mailchimp/similar)

## 📄 License

Same as Promptosaurus (MIT License)

---

Built for engineers, by engineers. Shipping production-grade infrastructure.
