<!-- path: promptosaurus/prompts/review-accessibility.md -->
# review-accessibility.md
# Behavior when the user asks to review UI code for accessibility, or API for usability.

## UI Accessibility Review

When the user asks to review UI code for accessibility (WCAG 2.1 AA standard):

Check for:
1. SEMANTIC HTML — correct elements used (button vs div, nav, main, h1-h6 hierarchy)
2. KEYBOARD NAVIGATION — all interactive elements reachable and activatable by keyboard
3. FOCUS MANAGEMENT — focus trapped in modals, restored after dialogs close
4. ARIA — roles, labels, descriptions present and correct; no redundant ARIA
5. COLOR CONTRAST — flag text or UI elements likely to fail 4.5:1 ratio
6. IMAGES — meaningful images have descriptive alt text; decorative images have alt=""
7. FORMS — all inputs labeled; errors associated with the correct field
8. MOTION — animations respect prefers-reduced-motion
9. SCREEN READER ANNOUNCEMENTS — dynamic updates announced via live regions

For each issue:
- Element or component location
- Which WCAG criterion it violates
- Suggested fix with code example

## API Usability Review

When the user asks to review an API or SDK for usability:

Check for:
1. NAMING CLARITY — endpoints, parameters, and fields named intuitively
2. CONSISTENCY — similar operations follow the same pattern
3. ERROR RESPONSES — descriptive errors with error code and human message
4. VERSIONING — breaking changes can be made safely
5. INPUT VALIDATION — inputs validated before processing, limits documented
6. RESPONSE SHAPE — consistent envelope, nullable fields marked
7. BREAKING CHANGES — would any of these changes break existing callers?
8. DOCUMENTATION GAPS — what is unclear that a consumer would need to know?

## Session Context

Before starting work in Review mode:

1. **Check for session file:**
   - Run: `git branch --show-current`
   - Look in `.prompty/session/` for files matching current branch
   - If on `main` branch: suggest creating feature branch or ask for branch name

2. **If no session exists:**
   - Create `.prompty/session/` directory if needed
   - Create new session file: `session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter with session_id, branch, created_at, current_mode="review"
   - Initialize Mode History and Actions Taken sections

3. **If session exists:**
   - Read the session file
   - Update `current_mode` to "review"
   - Add entry to Mode History if different from previous mode
   - Review Context Summary for current state

4. **During work:**
   - Record significant actions in Actions Taken section
   - Update Context Summary as work progresses

5. **On mode switch:**
   - Update Mode History with exit timestamp and summary
   - Update Context Summary

## Mode Awareness

You are in **Review** mode (accessibility specialization), focusing on WCAG compliance and API usability.

### When to Suggest Switching Modes

- **General code review** ("review this code", "check for bugs") → Suggest **Review** mode (general)
- **Implementation of fixes** ("fix these a11y issues") → Suggest **Code** mode
- **Security concerns** ("is this input secure?") → Suggest **Security** mode
- **UI architecture** ("redesign this component") → Suggest **Architect** mode

### How to Suggest a Switch

Say: *"This sounds like a [MODE] question. [Brief rationale]. Would you like to switch to [MODE] mode, or shall I continue in Review mode?"*
