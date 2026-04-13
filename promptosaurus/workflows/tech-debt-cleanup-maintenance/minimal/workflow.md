---
name: tech-debt-cleanup-maintenance
type: workflow
category: workflow-patterns
minimal: true
---
# Tech Debt Cleanup Workflow

**Version:** 1.0

### Monthly Tech Debt Review (2 hours)

```bash
cd /home/john_aven/Documents/software/promptosaurus

# 1. Find all TODO comments
grep -r "TODO:" --include="*.py" promptosaurus/ > debt-todos.txt

# 2. Find all FIXME comments  
grep -r "FIXME:" --include="*.py" promptosaurus/ > debt-fixmes.txt

# 3. Find type: ignore patterns
grep -r "type: ignore" --include="*.py" promptosaurus/ > debt-type-ignore.txt

# 4. Find old comments or hacks
grep -r "HACK\|XXX\|KLUDGE" --include="*.py" promptosaurus/ > debt-hacks.txt

# Review all generated files and categorize
```