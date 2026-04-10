---
name: accessibility
description: Review - accessibility
tools: [bash, read]
workflows:
  - accessibility-workflow
---

# Review - Accessibility (Verbose)

Comprehensive accessibility review for UI (WCAG 2.1 AA) and API usability.

## UI Accessibility Review

When reviewing UI code for accessibility, check against WCAG 2.1 AA standard:

### 1. SEMANTIC HTML
Use correct HTML elements for their intended purpose.

❌ **Bad:**
```html
<div onclick="handleClick()">Submit</div>
```

✅ **Good:**
```html
<button onclick="handleClick()">Submit</button>
```

**Why:** Buttons are focusable, activatable by keyboard (Enter/Space), and announced correctly by screen readers. Divs are not.

---

### 2. KEYBOARD NAVIGATION
All interactive elements must be reachable and activatable by keyboard alone.

❌ **Bad:**
```html
<div onclick="openMenu()">Menu</div>
```

✅ **Good:**
```html
<button onclick="openMenu()" aria-expanded="false">Menu</button>
```

**Test:** Can you Tab to it? Can you activate with Enter/Space?

**WCAG:** 2.1.1 Keyboard

---

### 3. FOCUS MANAGEMENT
Focus should be trapped inside modals and restored when closed.

❌ **Bad:**
```javascript
function openModal() {
  document.getElementById('modal').style.display = 'block';
  // Focus escapes modal, keyboard users lost
}
```

✅ **Good:**
```javascript
function openModal() {
  const modal = document.getElementById('modal');
  modal.style.display = 'block';
  modal.querySelector('button').focus();  // Move focus into modal
  trapFocus(modal);  // Prevent focus from leaving
}

function closeModal() {
  document.getElementById('modal').style.display = 'none';
  document.getElementById('open-button').focus();  // Restore focus
}
```

**WCAG:** 2.4.3 Focus Order

---

### 4. ARIA
Use ARIA to communicate state and structure when HTML alone is insufficient.

❌ **Bad:**
```html
<div role="button">Click me</div>  <!-- Missing accessible name -->
```

✅ **Good:**
```html
<button aria-label="Submit form">Click me</button>
```

**Or better — use HTML button:**
```html
<button>Submit form</button>  <!-- No ARIA needed -->
```

**Rule:** No ARIA is better than bad ARIA. Use native HTML first.

**WCAG:** 4.1.2 Name, Role, Value

---

### 5. COLOR CONTRAST
Text must have 4.5:1 contrast ratio against background (3:1 for large text).

❌ **Bad:**
```css
.btn {
  background: #777;  /* Gray */
  color: #999;       /* Light gray - fails 4.5:1 */
}
```

✅ **Good:**
```css
.btn {
  background: #333;  /* Dark gray */
  color: #fff;       /* White - passes 4.5:1 */
}
```

**Tool:** Use contrast checker (e.g., WebAIM Contrast Checker)

**WCAG:** 1.4.3 Contrast (Minimum)

---

### 6. IMAGES
Meaningful images need descriptive alt text. Decorative images need alt="".

❌ **Bad:**
```html
<img src="chart.png" />  <!-- No alt text -->
<img src="logo.png" alt="image" />  <!-- Vague alt -->
```

✅ **Good:**
```html
<img src="chart.png" alt="Sales revenue increased 23% from Q1 to Q2" />
<img src="decorative-line.png" alt="" />  <!-- Decorative, screen reader skips -->
```

**WCAG:** 1.1.1 Non-text Content

---

### 7. FORMS
All inputs must have associated labels. Errors must be associated with fields.

❌ **Bad:**
```html
<input type="text" placeholder="Email" />  <!-- Placeholder is not a label -->
```

✅ **Good:**
```html
<label for="email">Email</label>
<input type="text" id="email" aria-describedby="email-error" />
<span id="email-error" role="alert">Email is required</span>
```

**WCAG:** 1.3.1 Info and Relationships, 3.3.1 Error Identification

---

### 8. MOTION
Animations must respect `prefers-reduced-motion` media query.

❌ **Bad:**
```css
.fade-in {
  animation: fade 0.5s ease-in;
}
```

✅ **Good:**
```css
@media (prefers-reduced-motion: no-preference) {
  .fade-in {
    animation: fade 0.5s ease-in;
  }
}

@media (prefers-reduced-motion: reduce) {
  .fade-in {
    animation: none;  /* Disable for users who prefer no motion */
  }
}
```

**WCAG:** 2.3.3 Animation from Interactions

---

### 9. SCREEN READER ANNOUNCEMENTS
Dynamic content changes must be announced via live regions.

❌ **Bad:**
```javascript
document.getElementById('message').textContent = 'Item added to cart';
// Screen reader doesn't announce the change
```

✅ **Good:**
```html
<div id="message" role="status" aria-live="polite"></div>
```

```javascript
document.getElementById('message').textContent = 'Item added to cart';
// Screen reader announces: "Item added to cart"
```

**WCAG:** 4.1.3 Status Messages

---

## API Usability Review

When reviewing APIs or SDKs for usability:

### 1. NAMING CLARITY

❌ **Bad:**
```
GET /api/v1/data?id=123&type=user
```

✅ **Good:**
```
GET /api/v1/users/123
```

---

### 2. CONSISTENCY

❌ **Bad:**
```
POST /api/users        # Create user
PUT /api/update-order  # Update order (inconsistent pattern)
```

✅ **Good:**
```
POST /api/users       # Create user
PUT /api/orders/123   # Update order (consistent pattern)
```

---

### 3. ERROR RESPONSES

❌ **Bad:**
```json
{
  "error": "bad request"
}
```

✅ **Good:**
```json
{
  "error": {
    "code": "INVALID_EMAIL",
    "message": "Email format is invalid. Expected format: user@example.com",
    "field": "email"
  }
}
```

---

### 4. VERSIONING

❌ **Bad:**
```
GET /api/users  # No version, breaking changes affect everyone
```

✅ **Good:**
```
GET /api/v1/users  # Versioned, can introduce v2 without breaking v1
```

---

### 5. INPUT VALIDATION

❌ **Bad:**
```json
POST /api/users
{
  "name": "A"  // No length validation
}
```

✅ **Good:**
```json
POST /api/users
{
  "name": "A"  // Returns error: "Name must be at least 2 characters"
}
```

**Document limits:**
- Name: 2-100 characters
- Email: valid email format, max 255 characters

---

### 6. RESPONSE SHAPE

❌ **Bad:**
```json
{
  "id": 123,
  "name": "Alice",
  "email": null  // Nullable not documented
}
```

✅ **Good (with schema):**
```typescript
interface User {
  id: number;
  name: string;
  email: string | null;  // Explicitly nullable
}
```

---

### 7. BREAKING CHANGES

Check if changes break existing callers:

**Breaking:**
- Removing a field
- Renaming a field
- Changing field type (string → number)
- Adding required parameter

**Non-breaking:**
- Adding optional parameter
- Adding new field to response
- Deprecating (but not removing) field

---

### 8. DOCUMENTATION GAPS

Flag missing documentation:
- What does this endpoint do?
- What are valid values for this parameter?
- What's the rate limit?
- What error codes can be returned?

---

## Report Format

For each issue:
- **Element/Component location** (e.g., `src/components/Button.tsx:45`)
- **WCAG criterion violated** (e.g., 2.1.1 Keyboard, 4.1.2 Name/Role/Value)
- **Problem description**
- **Suggested fix with code example**

## Summary Template

```markdown
## Accessibility Summary

**WCAG Level:** AA (target)

**Violations:**
- Level A: N issues (must fix)
- Level AA: N issues (must fix)
- Level AAA: N issues (optional)

**Top Priority Fixes:**
1. [Issue 1 - WCAG criterion]
2. [Issue 2 - WCAG criterion]

**Testing Recommendations:**
- [ ] Test with keyboard only (no mouse)
- [ ] Test with screen reader (NVDA, JAWS, VoiceOver)
- [ ] Run automated scanner (axe, Lighthouse)
- [ ] Test with high contrast mode
- [ ] Test with prefers-reduced-motion enabled
```
