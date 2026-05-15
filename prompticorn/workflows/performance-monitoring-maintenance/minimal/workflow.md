# Performance Monitoring Workflow
name: "performance-monitoring-maintenance"

**Version:** 1.0

### Weekly Performance Check (30 min)

```bash
cd /home/john_aven/Documents/software/prompticorn

# 1. Test suite performance
time pytest --cov -q

# 2. Code complexity
radon cc prompticorn/ -a > complexity-report.txt

# 3. Line count and maintainability
radon mi prompticorn/ > maintainability-report.txt

# 4. Dependency size
pip show -v prompticorn | grep -i size
```