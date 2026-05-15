# Metrics Tracking Workflow
name: "metrics-tracking-maintenance"

**Version:** 1.0

### Weekly Metrics Collection (30 min)

```bash
cd /home/john_aven/Documents/software/prompticorn

# Collect all metrics
echo "=== Metrics for Week of $(date +%Y-%m-%d) ===" >> metrics-log.csv

# 1. Test coverage
pytest --cov=prompticorn --cov-report=json -q
cat .coverage.json | jq '.totals.percent_covered' >> metrics-log.csv

# 2. Test count and pass rate
pytest --collect-only -q | wc -l >> metrics-log.csv
pytest -q 2>&1 | grep "passed" >> metrics-log.csv

# 3. Code metrics
wc -l prompticorn/**/*.py >> metrics-log.csv
radon cc prompticorn/ -a -j >> metrics-log.csv

# 4. Dependency count
pip list | grep -v "^-" | wc -l >> metrics-log.csv
```