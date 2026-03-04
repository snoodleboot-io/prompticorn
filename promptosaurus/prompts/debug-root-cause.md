<!-- path: promptosaurus/prompts/debug-root-cause.md -->
# debug-root-cause.md

## Session Setup (REQUIRED FIRST STEP)

Before starting any work in this mode:

1. **Check git branch:**
   ```bash
   git branch --show-current
   ```
   - If on `main`: STOP and create feature branch using naming convention from core-system.md
   - If on feature branch: proceed

2. **Look for existing session:**
   ```bash
   ls .prompty/session/session_*_{current_branch}.md 2>/dev/null || echo "No session found"
   ```
   
3. **If session exists:**
   - Read the YAML frontmatter
   - Update `current_mode` to this mode's name
   - Add entry to Mode History if switching from different mode
   - Review Context Summary to understand current state

4. **If no session exists:**
   - Generate session file: `.prompty/session/session_{YYYYMMDD}_{random}.md`
   - Include YAML frontmatter with `current_mode: "{mode-name}"`
   - Initialize Mode History and Actions Taken sections

5. **During this task:**
   - Record significant actions in Actions Taken
   - Use timestamp format: `### 2026-03-04 14:45 - {mode-name} mode`
   - Update Context Summary when task completes or switching modes

---



[Rest of file content would go here - original content from /mnt/project/debug-root-cause.md with session boilerplate added at top]
