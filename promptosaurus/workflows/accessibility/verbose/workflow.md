---
name: accessibility
languages: ["python", "typescript", "javascript", "html"]
subagents: ["review", "test"]
---

# Accessibility Testing Workflow (Comprehensive)

## Overview

Web accessibility ensures people with disabilities can use your application. This includes users with:
- Visual impairments (blindness, low vision, color blindness)
- Motor impairments (unable to use mouse, tremors)
- Hearing impairments (deafness, hard of hearing)
- Cognitive impairments (dyslexia, autism, ADHD)

**Legal compliance:** Many jurisdictions require WCAG 2.1 Level AA compliance (ADA, Section 508, EU Accessibility Act).

---

## Phase 1: Requirements & Planning

### 1.1 Determine WCAG Compliance Level

**WCAG 2.1 Levels:**
- **Level A** (minimum): Basic accessibility, removes major barriers
- **Level AA** (recommended): Industry standard, addresses most barriers
- **Level AAA** (enhanced): Specialized accessibility for specific needs

**Recommendation:** Target WCAG 2.1 Level AA for most applications.

### 1.2 Identify Critical User Flows
List the most important user journeys that MUST be accessible:
- User registration and login
- Primary content consumption (reading articles, watching videos)
- Key transactions (checkout, form submissions)
- Navigation and search

### 1.3 Set Up Testing Environment
Install required tools and browser extensions:
```bash
# Automated testing tools
npm install -D @axe-core/cli @axe-core/playwright
npm install -D lighthouse pa11y eslint-plugin-jsx-a11y

# Python-based tools
pip install axe-selenium-python

# Browser extensions
# - axe DevTools (Chrome/Firefox)
# - WAVE Evaluation Tool (Chrome/Firefox)
# - Lighthouse (Chrome DevTools)
```

---

## Phase 2: Automated Testing

### 2.1 Lighthouse Accessibility Audit

**Run Lighthouse CLI:**
```bash
# Single page audit
lighthouse https://your-app.com \
  --only-categories=accessibility \
  --output html \
  --output-path ./reports/lighthouse-a11y.html

# Multiple pages with CI integration
lighthouse-ci autorun --config=.lighthouserc.json
```

**Lighthouse configuration (.lighthouserc.json):**
```json
{
  "ci": {
    "collect": {
      "url": [
        "https://your-app.com",
        "https://your-app.com/login",
        "https://your-app.com/checkout"
      ],
      "settings": {
        "onlyCategories": ["accessibility"]
      }
    },
    "assert": {
      "assertions": {
        "categories:accessibility": ["error", {"minScore": 0.9}]
      }
    }
  }
}
```

### 2.2 axe-core Integration Testing

**Component testing with Playwright:**
```typescript
// tests/accessibility.spec.ts
import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test('homepage should not have accessibility violations', async ({ page }) => {
  await page.goto('https://your-app.com');
  
  const accessibilityScanResults = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'])
    .analyze();
  
  expect(accessibilityScanResults.violations).toEqual([]);
});

test('form should be keyboard accessible', async ({ page }) => {
  await page.goto('https://your-app.com/signup');
  
  const results = await new AxeBuilder({ page })
    .include('#signup-form')
    .analyze();
  
  expect(results.violations).toEqual([]);
});
```

**CLI scanning with axe:**
```bash
# Scan single page
axe https://your-app.com \
  --tags wcag2a,wcag2aa,wcag21aa \
  --save results.json

# Scan with authentication (using cookies)
axe https://your-app.com/dashboard \
  --load-cookies cookies.json \
  --save dashboard-results.json
```

### 2.3 Pa11y Continuous Integration

**CI configuration (.pa11yci.json):**
```json
{
  "defaults": {
    "standard": "WCAG2AA",
    "runners": ["axe", "htmlcs"],
    "chromeLaunchConfig": {
      "args": ["--no-sandbox"]
    }
  },
  "urls": [
    "https://your-app.com",
    {
      "url": "https://your-app.com/dashboard",
      "actions": [
        "set field #username to testuser",
        "set field #password to testpass",
        "click element #login-button",
        "wait for url to be https://your-app.com/dashboard"
      ]
    }
  ]
}
```

**Run in CI pipeline:**
```bash
pa11y-ci --config .pa11yci.json
```

### 2.4 ESLint Accessibility Linting (React/JSX)

**Install and configure:**
```bash
npm install -D eslint-plugin-jsx-a11y
```

**.eslintrc.json:**
```json
{
  "extends": [
    "plugin:jsx-a11y/recommended"
  ],
  "plugins": ["jsx-a11y"],
  "rules": {
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/anchor-has-content": "error",
    "jsx-a11y/aria-props": "error",
    "jsx-a11y/aria-role": "error",
    "jsx-a11y/heading-has-content": "error",
    "jsx-a11y/label-has-associated-control": "error",
    "jsx-a11y/no-autofocus": "warn"
  }
}
```

---

## Phase 3: Manual Testing

### 3.1 Keyboard Navigation Testing

**Test procedure:**
1. **Navigate without mouse** - Unplug mouse or don't touch trackpad
2. **Tab through all interactive elements:**
   - Forms (inputs, selects, checkboxes, radio buttons)
   - Buttons (submit, cancel, actions)
   - Links (navigation, inline links)
   - Custom controls (dropdowns, modals, tooltips)

3. **Verify focus indicators:**
   - Every focused element has visible outline or background change
   - Focus order is logical (follows visual layout)
   - No focus traps (can Tab in and Tab out of all widgets)

4. **Test keyboard shortcuts:**
   - `Enter` activates buttons and submits forms
   - `Space` toggles checkboxes and activates buttons
   - `Escape` closes modals and dropdowns
   - Arrow keys navigate within custom controls (dropdowns, tabs)

**Common violations:**
- Invisible focus indicators (removed outline without replacement)
- Keyboard traps in modals or dropdowns
- Interactive divs without tabindex or keyboard handlers
- Illogical focus order (jumps around page randomly)

**Example: Accessible modal with focus trap:**
```typescript
// Good: Focus trap keeps Tab within modal
import FocusTrap from 'focus-trap-react';

function Modal({ isOpen, onClose, children }) {
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <FocusTrap>
      <div role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <h2 id="modal-title">Modal Title</h2>
        {children}
        <button onClick={onClose}>Close</button>
      </div>
    </FocusTrap>
  );
}
```

### 3.2 Screen Reader Testing

**Required screen readers:**
- **NVDA** (Windows, free): Download from nvaccess.org
- **JAWS** (Windows, paid): Most popular enterprise screen reader
- **VoiceOver** (macOS/iOS, built-in): Activate with Cmd+F5
- **TalkBack** (Android, built-in): Settings → Accessibility → TalkBack

**Basic screen reader commands:**

**NVDA/JAWS (Windows):**
- Start reading: `Insert + Down Arrow`
- Stop reading: `Ctrl`
- Next heading: `H`
- Next link: `K`
- Next form field: `F`
- Elements list: `Insert + F7`

**VoiceOver (macOS):**
- Start/stop: `Ctrl + Option + A`
- Next item: `Ctrl + Option + Right Arrow`
- Activate: `Ctrl + Option + Space`
- Rotor (navigation): `Ctrl + Option + U`

**Testing checklist:**

1. **Images and icons:**
   ```html
   <!-- Good: Descriptive alt text -->
   <img src="user-avatar.jpg" alt="Profile photo of Jane Smith">
   
   <!-- Good: Decorative images -->
   <img src="decorative-line.svg" alt="" role="presentation">
   
   <!-- Bad: Missing alt text -->
   <img src="important-chart.png">
   ```

2. **Form labels:**
   ```html
   <!-- Good: Explicit label association -->
   <label for="email">Email Address</label>
   <input type="email" id="email" name="email">
   
   <!-- Good: Implicit label -->
   <label>
     Email Address
     <input type="email" name="email">
   </label>
   
   <!-- Bad: Visual label only -->
   <div>Email</div>
   <input type="email" name="email">
   ```

3. **Heading hierarchy:**
   ```html
   <!-- Good: Logical hierarchy -->
   <h1>Page Title</h1>
   <h2>Section 1</h2>
   <h3>Subsection 1.1</h3>
   <h3>Subsection 1.2</h3>
   <h2>Section 2</h2>
   
   <!-- Bad: Skipping levels -->
   <h1>Page Title</h1>
   <h4>This skips h2 and h3</h4>
   ```

4. **ARIA labels for interactive components:**
   ```html
   <!-- Good: Button with clear purpose -->
   <button aria-label="Close dialog">×</button>
   
   <!-- Good: Icon button with text alternative -->
   <button>
     <svg aria-hidden="true"><path d="..."></path></svg>
     <span class="sr-only">Delete item</span>
   </button>
   
   <!-- Bad: Icon button without text -->
   <button><i class="icon-trash"></i></button>
   ```

5. **Live regions for dynamic content:**
   ```html
   <!-- Good: Announce status updates -->
   <div role="status" aria-live="polite" aria-atomic="true">
     Form submitted successfully!
   </div>
   
   <!-- Good: Alert for errors -->
   <div role="alert" aria-live="assertive">
     Error: Email address is required
   </div>
   ```

### 3.3 Color Contrast Analysis

**WCAG contrast requirements:**
- **Normal text** (< 18pt, < 14pt bold):
  - Level AA: 4.5:1 minimum
  - Level AAA: 7:1 minimum
- **Large text** (≥ 18pt, ≥ 14pt bold):
  - Level AA: 3:1 minimum
  - Level AAA: 4.5:1 minimum
- **UI components and graphics:**
  - Level AA: 3:1 minimum

**Testing tools:**
- **WebAIM Contrast Checker:** webaim.org/resources/contrastchecker/
- **Chrome DevTools:** Inspect element → Styles → Color picker shows contrast ratio
- **Colour Contrast Analyser (CCA):** Desktop app by TPGi

**Example: Check all text colors:**
```bash
# Extract all colors from CSS
grep -Eo 'color:\s*#[0-9a-fA-F]{3,6}' styles.css | sort -u

# Common violations:
# - Gray text on white background (#767676 on #FFFFFF = 4.54:1, just barely passing AA)
# - Light text on colored backgrounds
# - Placeholder text (often fails contrast)
```

**Fix common violations:**
```css
/* Bad: Insufficient contrast (3.2:1) */
.text-muted {
  color: #999999; /* on white background */
}

/* Good: Sufficient contrast (4.6:1) */
.text-muted {
  color: #757575; /* darker gray on white */
}

/* Bad: Placeholder fails contrast */
input::placeholder {
  color: #CCCCCC; /* 1.6:1 on white - FAIL */
}

/* Good: Placeholder meets minimum */
input::placeholder {
  color: #757575; /* 4.6:1 on white - PASS */
}
```

---

## Phase 4: Semantic HTML Review

### 4.1 Proper Element Usage

**Interactive elements:**
```html
<!-- Good: Semantic button -->
<button type="button" onclick="handleClick()">Click Me</button>

<!-- Bad: Div as button -->
<div onclick="handleClick()">Click Me</div>
<!-- Missing: role, tabindex, keyboard handler, focus indicator -->

<!-- Good: Semantic link -->
<a href="/page">Go to Page</a>

<!-- Bad: Button styled as link -->
<button onclick="navigate('/page')">Go to Page</button>
<!-- Use <a> for navigation, <button> for actions -->
```

**Landmark regions:**
```html
<!-- Good: Semantic landmarks -->
<header>
  <nav aria-label="Main navigation">
    <ul><li><a href="/">Home</a></li></ul>
  </nav>
</header>

<main>
  <article>
    <h1>Article Title</h1>
    <p>Content...</p>
  </article>
  
  <aside aria-label="Related articles">
    <h2>Related</h2>
    <ul><li><a href="/related">Link</a></li></ul>
  </aside>
</main>

<footer>
  <p>&copy; 2026 Company Name</p>
</footer>

<!-- Bad: Generic divs -->
<div class="header">
  <div class="nav">...</div>
</div>
<div class="content">...</div>
<div class="footer">...</div>
```

### 4.2 Form Accessibility

**Label association:**
```html
<!-- Good: Explicit label with for/id -->
<label for="username">Username</label>
<input type="text" id="username" name="username" required>

<!-- Good: Fieldset for radio groups -->
<fieldset>
  <legend>Choose your subscription</legend>
  <label>
    <input type="radio" name="plan" value="free">
    Free Plan
  </label>
  <label>
    <input type="radio" name="plan" value="pro">
    Pro Plan ($10/mo)
  </label>
</fieldset>

<!-- Good: Error messages -->
<label for="email">Email</label>
<input 
  type="email" 
  id="email" 
  name="email" 
  aria-describedby="email-error"
  aria-invalid="true"
>
<span id="email-error" role="alert">
  Please enter a valid email address
</span>
```

### 4.3 Table Accessibility

```html
<!-- Good: Data table with proper headers -->
<table>
  <caption>User Activity Report</caption>
  <thead>
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Email</th>
      <th scope="col">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Jane Smith</td>
      <td>jane@example.com</td>
      <td>Active</td>
    </tr>
  </tbody>
</table>

<!-- Good: Complex table with headers -->
<table>
  <caption>Sales by Region and Quarter</caption>
  <thead>
    <tr>
      <th scope="col">Region</th>
      <th scope="col">Q1</th>
      <th scope="col">Q2</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">North</th>
      <td>$1.2M</td>
      <td>$1.5M</td>
    </tr>
    <tr>
      <th scope="row">South</th>
      <td>$800K</td>
      <td>$950K</td>
    </tr>
  </tbody>
</table>
```

---

## Phase 5: Documentation & Reporting

### 5.1 Accessibility Audit Report Template

```markdown
# Accessibility Audit Report

**Application:** [App Name]
**Date:** YYYY-MM-DD
**WCAG Version:** 2.1
**Target Level:** AA
**Auditor:** [Name]

## Executive Summary
- Total violations: [X]
- Blocker issues: [X] (prevent usage for some users)
- Major issues: [X] (significant barriers)
- Minor issues: [X] (inconveniences)

## Test Coverage
- Pages tested: [X]
- Automated tools: axe, Lighthouse, Pa11y
- Manual tests: Keyboard navigation, NVDA screen reader
- Browsers tested: Chrome, Firefox, Safari

## Critical Violations

### 1. Missing Form Labels (WCAG 1.3.1, 3.3.2)
**Severity:** Blocker
**Impact:** Screen reader users cannot identify form fields
**Location:** /signup page, all input fields
**Evidence:**
```html
<!-- Current (incorrect) -->
<input type="text" name="username" placeholder="Enter username">

<!-- Required fix -->
<label for="username">Username</label>
<input type="text" id="username" name="username" placeholder="Enter username">
```
**Remediation:** Add explicit `<label>` elements with for/id association

### 2. Insufficient Color Contrast (WCAG 1.4.3)
**Severity:** Major
**Impact:** Low vision users cannot read text
**Location:** All pages, .text-muted class
**Current:** #999999 on #FFFFFF = 2.8:1 (FAIL)
**Required:** 4.5:1 minimum for normal text
**Remediation:** Change color to #757575 (4.6:1 contrast)

[Continue with all violations...]

## Recommendations
1. Integrate axe-core into CI pipeline (prevent regressions)
2. Add accessibility testing to PR checklist
3. Provide accessibility training for developers
4. Establish accessibility champion role
```

### 5.2 Ongoing Accessibility Monitoring

**CI/CD integration:**
```yaml
# .github/workflows/accessibility.yml

on: [push, pull_request]

jobs:
  a11y:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run Lighthouse CI
        run: |
          npm install -g @lhci/cli
          lhci autorun --config=.lighthouserc.json
      
      - name: Run axe tests
        run: npm run test:a11y
      
      - name: Fail if accessibility score < 90
        run: |
          score=$(jq '.categories.accessibility.score' lighthouse-results.json)
          if (( $(echo "$score < 0.9" | bc -l) )); then
            echo "Accessibility score $score is below 0.9"
            exit 1
          fi
```

**Pre-commit hooks:**
```bash
# .husky/pre-commit
npm run lint:a11y  # ESLint with jsx-a11y rules
```

---

## Common Violations & Fixes

| Violation | WCAG Criterion | Fix |
|-----------|----------------|-----|
| Missing alt text | 1.1.1 | Add descriptive alt attribute to all images |
| Low contrast | 1.4.3 | Ensure 4.5:1 ratio for text, 3:1 for UI components |
| Missing form labels | 1.3.1, 3.3.2 | Add `<label>` with for/id association |
| Keyboard trap | 2.1.2 | Ensure Tab can exit all interactive elements |
| Missing focus indicator | 2.4.7 | Add visible outline or background on :focus |
| Skipped heading levels | 1.3.1 | Use h1→h2→h3 hierarchy, no skipping |
| Button without accessible name | 4.1.2 | Add aria-label or text content to button |
| Incorrect ARIA usage | 4.1.2 | Use semantic HTML instead, or fix ARIA attributes |
| Missing language attribute | 3.1.1 | Add `<html lang="en">` |
| Auto-playing media | 1.4.2 | Provide pause button, don't autoplay |

---

## Resources

**Standards:**
- WCAG 2.1 Guidelines: w3.org/WAI/WCAG21/quickref/
- ARIA Authoring Practices: w3.org/WAI/ARIA/apg/

**Tools:**
- axe DevTools: deque.com/axe/devtools/
- WAVE: wave.webaim.org
- Lighthouse: developers.google.com/web/tools/lighthouse

**Testing:**
- Screen readers: nvaccess.org (NVDA), apple.com/voiceover
- Contrast checker: webaim.org/resources/contrastchecker/
- Color blindness simulator: colororacle.org
