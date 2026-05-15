# Tech Debt Cleanup Workflow
name: "tech-debt-cleanup-maintenance"

**Version:** 1.0

### Monthly Tech Debt Review (2 hours)

```bash
cd /home/john_aven/Documents/software/prompticorn

# 1. Find all TODO comments
grep -r "TODO:" --include="*.py" prompticorn/ > debt-todos.txt

# 2. Find all FIXME comments  
grep -r "FIXME:" --include="*.py" prompticorn/ > debt-fixmes.txt

# 3. Find type: ignore patterns
grep -r "type: ignore" --include="*.py" prompticorn/ > debt-type-ignore.txt

# 4. Find old comments or hacks
grep -r "HACK\|XXX\|KLUDGE" --include="*.py" prompticorn/ > debt-hacks.txt

# Review all generated files and categorize
```