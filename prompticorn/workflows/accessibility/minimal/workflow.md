---
name: "accessibility"
languages: ["python", "typescript", "javascript", "html"]
subagents: ["review", "test"]
---

# Accessibility Testing Workflow (Minimal)

## 1. Identify Compliance Level
Determine target WCAG level (A, AA, AAA) based on requirements.
- Level A: Basic web accessibility (minimum)
- Level AA: Industry standard (recommended)
- Level AAA: Enhanced accessibility (specialized needs)

## 2. Automated Testing
Run automated accessibility checks using tools:
```bash
# Lighthouse CI for web apps
lighthouse --only-categories=accessibility https://your-app.com

# axe-core for component testing
npm install -D @axe-core/cli
axe https://your-app.com --tags wcag2a,wcag2aa

# Pa11y for automated scanning
npm install -g pa11y
pa11y https://your-app.com
```

## 3. Keyboard Navigation Testing
Test all interactive elements without mouse:
- Tab through all focusable elements (forms, buttons, links)
- Verify focus indicators are visible (outline, background change)
- Test keyboard shortcuts (Enter, Space, Escape, Arrow keys)
- Ensure no keyboard traps (can Tab out of all elements)

## 4. Screen Reader Testing
Test with at least one screen reader:
- NVDA (Windows, free), JAWS (Windows, paid), VoiceOver (macOS/iOS)
- Verify all images have alt text describing content
- Check form labels are properly associated with inputs
- Test heading hierarchy (h1 → h2 → h3, no skips)
- Verify ARIA labels on interactive components

## 5. Color Contrast Analysis
Check text contrast ratios meet WCAG standards:
- Normal text: 4.5:1 minimum (AA), 7:1 (AAA)
- Large text (18pt+): 3:1 minimum (AA), 4.5:1 (AAA)
- Use tools: WebAIM Contrast Checker, Chrome DevTools

## 6. Semantic HTML Review
Audit markup for proper semantic structure:
- Use semantic tags: `<nav>`, `<main>`, `<article>`, `<section>`, `<aside>`
- Buttons use `<button>`, links use `<a>` (not div with onClick)
- Forms use proper `<label>` elements with for/id association
- Tables use `<th>` with scope attributes for headers

## 7. Document Findings
Create accessibility audit report:
- List all violations with WCAG criterion reference
- Categorize by severity (blocker, major, minor)
- Provide remediation steps for each issue
- Include screenshots and code examples
