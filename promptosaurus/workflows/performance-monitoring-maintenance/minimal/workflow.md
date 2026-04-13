---
name: performance-monitoring-maintenance
type: workflow
category: workflow-patterns
minimal: true
---
# Performance Monitoring Workflow

**Version:** 1.0

### Weekly Performance Check (30 min)

```bash
cd /home/john_aven/Documents/software/promptosaurus

# 1. Test suite performance
time pytest --cov -q

# 2. Code complexity
radon cc promptosaurus/ -a > complexity-report.txt

# 3. Line count and maintainability
radon mi promptosaurus/ > maintainability-report.txt

# 4. Dependency size
pip show -v promptosaurus | grep -i size
```