<!-- path: promptosaurus/prompts/core-conventions-html.md -->
# HTML Conventions

Language:             {{LANGUAGE}}           e.g., HTML5
Version:              {{VERSION}}            e.g., HTML5, HTML4 Strict, XHTML5
Formatter:            {{FORMATTER}}          e.g., prettier, html-beautify, djLint
Linter:               {{LINTER}}             e.g., htmlhint, W3C Validator

## HTML-Specific Rules

### Document Structure
- Always use proper DOCTYPE declaration
- Include lang attribute on <html> element
- Use semantic HTML elements (header, nav, main, article, section, footer)
- Maintain proper heading hierarchy (h1 → h2 → h3, don't skip levels)
- Use `<meta charset="UTF-8">` as first meta tag

### Accessibility (a11y)
- All images must have descriptive alt attributes (empty alt for decorative images)
- Use ARIA attributes only when necessary, prefer semantic HTML
- Ensure form inputs have associated labels
- Maintain keyboard navigation support
- Use sufficient color contrast (WCAG 2.1 AA minimum)
- Provide skip links for keyboard navigation

### Performance
- Minimize DOM depth (avoid unnecessary wrapper elements)
- Use async/defer for external scripts
- Place CSS in <head>, scripts before closing </body>
- Optimize images with appropriate formats (WebP with fallbacks)
- Use lazy loading for below-fold images

### Formatting Standards
- 2 spaces for indentation
- Double quotes for attribute values
- Lowercase tag and attribute names
- Omit optional closing tags only if explicitly configured
- Self-close void elements with space before /> (XHTML5 mode)

### Best Practices
- Don't use inline styles (use CSS classes)
- Avoid deprecated tags and attributes
- Validate HTML before committing
- Use data attributes for JavaScript hooks, not classes
- Keep class names semantic and lowercase with hyphens (kebab-case)

### SEO
- Use descriptive, unique title tags
- Include meta description
- Use canonical URLs
- Implement proper Open Graph tags
- Structure data with Schema.org markup when appropriate

### Security
- Always sanitize user-generated content
- Use Content Security Policy headers
- Implement proper iframe sandbox attributes
- Avoid inline event handlers (onclick, etc.)

## Validation

Before committing HTML:
1. Run through {{LINTER}}
2. Validate with W3C validator
3. Check accessibility with axe or similar tool
4. Test in target browsers
