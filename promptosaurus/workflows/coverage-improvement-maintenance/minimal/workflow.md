# Coverage Improvement Workflow
name: "coverage-improvement-maintenance"

**Version:** 1.0

### Weekly Coverage Check (20 min)

```bash
cd /home/john_aven/Documents/software/promptosaurus

# Generate coverage report
pytest --cov=promptosaurus --cov-report=html --cov-report=term -q

# View results
open htmlcov/index.html  # or browse to it

# Check per-module breakdown
cat .coverage

# Identify lowest coverage modules
pytest --cov=promptosaurus --cov-report=term-missing -q | grep -E "^promptosaurus.*[0-9]{1,2}%"
```