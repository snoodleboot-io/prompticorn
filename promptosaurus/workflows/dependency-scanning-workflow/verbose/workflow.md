---
name: "Dependency Scanning"
description: "Identify and manage vulnerabilities in third-party dependencies"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - security-code-review
  - compliance-audit-workflow
---

# Dependency Scanning - Comprehensive Guide

## Overview

Dependency scanning, also known as Software Composition Analysis (SCA), is the process of identifying, analyzing, and managing security vulnerabilities, license compliance issues, and outdated components in third-party dependencies. With modern applications often consisting of 70-90% third-party code, dependency security is crucial for overall application security.

## Prerequisites

### Knowledge Requirements
- Understanding of package management systems
- Knowledge of vulnerability databases (CVE, NVD)
- Familiarity with OWASP A06-2021 (Vulnerable and Outdated Components)
- License compliance basics
- Supply chain security concepts

### Tools and Technologies
- **Open Source Tools**: OWASP Dependency-Check, Snyk Open Source, Safety, npm audit
- **Commercial Tools**: Snyk, WhiteSource, Black Duck, Sonatype Nexus
- **CI/CD Integration**: GitHub Dependabot, GitLab Dependency Scanning
- **Vulnerability Databases**: NVD, CVE, OSV, GitHub Advisory Database

## Dependency Landscape

### Package Ecosystems

```python
ecosystem_tools = {
    "JavaScript/Node.js": {
        "package_file": "package.json",
        "lock_file": "package-lock.json, yarn.lock",
        "tools": ["npm audit", "yarn audit", "snyk", "retire.js"],
        "registry": "npmjs.org"
    },
    "Python": {
        "package_file": "requirements.txt, Pipfile, pyproject.toml",
        "lock_file": "Pipfile.lock, poetry.lock",
        "tools": ["safety", "pip-audit", "bandit"],
        "registry": "pypi.org"
    },
    "Java": {
        "package_file": "pom.xml, build.gradle",
        "lock_file": "gradle.lockfile",
        "tools": ["OWASP Dependency-Check", "Snyk"],
        "registry": "Maven Central"
    },
    "Ruby": {
        "package_file": "Gemfile",
        "lock_file": "Gemfile.lock",
        "tools": ["bundler-audit", "hakiri"],
        "registry": "rubygems.org"
    },
    ".NET": {
        "package_file": "*.csproj, packages.config",
        "lock_file": "packages.lock.json",
        "tools": ["dotnet list package --vulnerable"],
        "registry": "nuget.org"
    },
    "Go": {
        "package_file": "go.mod",
        "lock_file": "go.sum",
        "tools": ["nancy", "gosec"],
        "registry": "proxy.golang.org"
    }
}
```

## Detailed Implementation Steps

### Step 1: Dependency Inventory

**1.1 Create Software Bill of Materials (SBOM)**
```python
import json
import subprocess
from typing import Dict, List

class DependencyInventory:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.dependencies = []
    
    def generate_sbom(self) -> Dict:
        """Generate Software Bill of Materials in SPDX format"""
        sbom = {
            "spdxVersion": "SPDX-2.2",
            "dataLicense": "CC0-1.0",
            "name": "Application SBOM",
            "packages": []
        }
        
        # Detect and scan each ecosystem
        if self.has_file("package.json"):
            sbom["packages"].extend(self.scan_npm())
        
        if self.has_file("requirements.txt"):
            sbom["packages"].extend(self.scan_python())
        
        if self.has_file("pom.xml"):
            sbom["packages"].extend(self.scan_maven())
        
        return sbom
    
    def scan_npm(self) -> List[Dict]:
        """Scan NPM dependencies"""
        result = subprocess.run(
            ["npm", "list", "--json", "--depth=0"],
            capture_output=True,
            text=True
        )
        
        packages = []
        deps = json.loads(result.stdout).get("dependencies", {})
        
        for name, info in deps.items():
            packages.append({
                "name": name,
                "version": info.get("version"),
                "type": "npm",
                "direct": True,
                "license": self.get_license(name, "npm")
            })
        
        return packages
```

**1.2 Dependency Tree Analysis**
```bash
# Visualize dependency tree
npm ls --depth=3
pip show --files <package>
mvn dependency:tree

# Find duplicate dependencies
npm ls --depth=0 | grep -E "deduped|duplicate"

# Check for circular dependencies
madge --circular src/
```

### Step 2: Vulnerability Scanning

**2.1 Multi-Tool Scanning Strategy**
```python
class VulnerabilityScanner:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.vulnerabilities = []
    
    def scan_all_ecosystems(self):
        """Run appropriate scanners for each ecosystem"""
        scanners = {
            "package.json": self.scan_npm,
            "requirements.txt": self.scan_python,
            "pom.xml": self.scan_java,
            "Gemfile": self.scan_ruby,
            "go.mod": self.scan_go
        }
        
        for file_pattern, scanner in scanners.items():
            if self.file_exists(file_pattern):
                results = scanner()
                self.vulnerabilities.extend(results)
    
    def scan_npm(self) -> List[Dict]:
        """Scan NPM dependencies for vulnerabilities"""
        vulnerabilities = []
        
        # npm audit
        npm_result = subprocess.run(
            ["npm", "audit", "--json"],
            capture_output=True,
            text=True
        )
        npm_data = json.loads(npm_result.stdout)
        
        for advisory_id, advisory in npm_data.get("advisories", {}).items():
            vulnerabilities.append({
                "id": advisory_id,
                "package": advisory["module_name"],
                "severity": advisory["severity"],
                "title": advisory["title"],
                "cve": advisory.get("cves", []),
                "fixed_in": advisory.get("patched_versions"),
                "recommendation": advisory.get("recommendation")
            })
        
        # Snyk additional scanning
        snyk_result = subprocess.run(
            ["snyk", "test", "--json"],
            capture_output=True,
            text=True
        )
        
        if snyk_result.returncode == 0:
            snyk_data = json.loads(snyk_result.stdout)
            vulnerabilities.extend(self.parse_snyk_results(snyk_data))
        
        return vulnerabilities
    
    def scan_python(self) -> List[Dict]:
        """Scan Python dependencies"""
        vulnerabilities = []
        
        # Safety check
        safety_result = subprocess.run(
            ["safety", "check", "--json"],
            capture_output=True,
            text=True
        )
        
        # pip-audit
        audit_result = subprocess.run(
            ["pip-audit", "--format", "json"],
            capture_output=True,
            text=True
        )
        
        # Parse and combine results
        vulnerabilities.extend(self.parse_safety_results(safety_result.stdout))
        vulnerabilities.extend(self.parse_pip_audit_results(audit_result.stdout))
        
        return vulnerabilities
```

**2.2 CVE Database Integration**
```python
import requests
from datetime import datetime, timedelta

class CVEChecker:
    def __init__(self):
        self.nvd_api_key = os.environ.get("NVD_API_KEY")
        self.cache = {}
    
    def check_cve(self, cve_id: str) -> Dict:
        """Query NVD for CVE details"""
        if cve_id in self.cache:
            return self.cache[cve_id]
        
        url = f"https://services.nvd.nist.gov/rest/json/cve/1.0/{cve_id}"
        headers = {"apiKey": self.nvd_api_key} if self.nvd_api_key else {}
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            cve_info = {
                "id": cve_id,
                "description": data["result"]["CVE_Items"][0]["cve"]["description"]["description_data"][0]["value"],
                "cvss_score": self.extract_cvss_score(data),
                "severity": self.calculate_severity(data),
                "published_date": data["result"]["CVE_Items"][0]["publishedDate"],
                "last_modified": data["result"]["CVE_Items"][0]["lastModifiedDate"]
            }
            self.cache[cve_id] = cve_info
            return cve_info
        
        return None
    
    def extract_cvss_score(self, cve_data: Dict) -> float:
        """Extract CVSS score from CVE data"""
        try:
            # Try CVSS v3 first
            return cve_data["result"]["CVE_Items"][0]["impact"]["baseMetricV3"]["cvssV3"]["baseScore"]
        except KeyError:
            # Fall back to CVSS v2
            try:
                return cve_data["result"]["CVE_Items"][0]["impact"]["baseMetricV2"]["cvssV2"]["baseScore"]
            except KeyError:
                return 0.0
```

### Step 3: License Compliance

**3.1 License Detection and Analysis**
```python
class LicenseCompliance:
    def __init__(self):
        self.allowed_licenses = [
            "MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause",
            "ISC", "CC0-1.0", "Unlicense"
        ]
        self.restricted_licenses = [
            "GPL-2.0", "GPL-3.0", "AGPL-3.0", "LGPL-2.1", "LGPL-3.0"
        ]
        self.prohibited_licenses = [
            "PROPRIETARY", "UNKNOWN", "CUSTOM"
        ]
    
    def check_license_compatibility(self, dependencies: List[Dict]) -> Dict:
        """Check license compatibility across dependencies"""
        results = {
            "compliant": [],
            "restricted": [],
            "prohibited": [],
            "unknown": []
        }
        
        for dep in dependencies:
            license_type = dep.get("license", "UNKNOWN")
            
            if license_type in self.allowed_licenses:
                results["compliant"].append(dep)
            elif license_type in self.restricted_licenses:
                results["restricted"].append(dep)
                # Check for viral license implications
                if self.is_viral_license(license_type):
                    dep["warning"] = "Viral license - may affect your code"
            elif license_type in self.prohibited_licenses:
                results["prohibited"].append(dep)
            else:
                results["unknown"].append(dep)
        
        return results
    
    def generate_license_report(self, dependencies: List[Dict]) -> str:
        """Generate license compliance report"""
        report = "# License Compliance Report\n\n"
        
        compliance = self.check_license_compatibility(dependencies)
        
        report += f"## Summary\n"
        report += f"- Total Dependencies: {len(dependencies)}\n"
        report += f"- Compliant: {len(compliance['compliant'])}\n"
        report += f"- Restricted: {len(compliance['restricted'])}\n"
        report += f"- Prohibited: {len(compliance['prohibited'])}\n"
        report += f"- Unknown: {len(compliance['unknown'])}\n\n"
        
        if compliance['prohibited']:
            report += "## ⛔ Prohibited Licenses (Action Required)\n"
            for dep in compliance['prohibited']:
                report += f"- {dep['name']}@{dep['version']}: {dep['license']}\n"
        
        if compliance['restricted']:
            report += "\n## ⚠️  Restricted Licenses (Review Required)\n"
            for dep in compliance['restricted']:
                report += f"- {dep['name']}@{dep['version']}: {dep['license']}\n"
                if 'warning' in dep:
                    report += f"  - Warning: {dep['warning']}\n"
        
        return report
```

### Step 4: Remediation Strategies

**4.1 Automated Remediation**
```python
class DependencyRemediation:
    def __init__(self, vulnerabilities: List[Dict]):
        self.vulnerabilities = vulnerabilities
    
    def generate_remediation_plan(self) -> Dict:
        """Generate prioritized remediation plan"""
        plan = {
            "immediate": [],  # Critical vulnerabilities
            "urgent": [],     # High vulnerabilities
            "planned": [],    # Medium vulnerabilities
            "review": []      # Low vulnerabilities
        }
        
        for vuln in self.vulnerabilities:
            remediation = self.determine_remediation(vuln)
            
            if vuln["severity"] == "critical":
                plan["immediate"].append(remediation)
            elif vuln["severity"] == "high":
                plan["urgent"].append(remediation)
            elif vuln["severity"] == "medium":
                plan["planned"].append(remediation)
            else:
                plan["review"].append(remediation)
        
        return plan
    
    def determine_remediation(self, vulnerability: Dict) -> Dict:
        """Determine best remediation approach"""
        package = vulnerability["package"]
        current_version = vulnerability["version"]
        fixed_version = vulnerability.get("fixed_in")
        
        remediation = {
            "package": package,
            "current_version": current_version,
            "vulnerability": vulnerability["id"],
            "severity": vulnerability["severity"]
        }
        
        if fixed_version:
            # Direct update available
            remediation["action"] = "update"
            remediation["target_version"] = fixed_version
            remediation["command"] = self.get_update_command(package, fixed_version)
        elif self.has_alternative(package):
            # Alternative package available
            alternative = self.get_alternative(package)
            remediation["action"] = "replace"
            remediation["alternative"] = alternative
            remediation["command"] = self.get_replace_command(package, alternative)
        else:
            # No direct fix available
            remediation["action"] = "mitigate"
            remediation["mitigation"] = self.get_mitigation_strategy(vulnerability)
        
        return remediation
    
    def apply_automated_updates(self, plan: Dict, dry_run: bool = True):
        """Apply automated updates for approved remediation"""
        results = []
        
        for remediation in plan["immediate"]:
            if remediation["action"] == "update":
                if dry_run:
                    print(f"[DRY RUN] Would execute: {remediation['command']}")
                else:
                    result = subprocess.run(
                        remediation["command"],
                        shell=True,
                        capture_output=True
                    )
                    results.append({
                        "package": remediation["package"],
                        "status": "success" if result.returncode == 0 else "failed",
                        "output": result.stdout
                    })
        
        return results
```

### Step 5: Continuous Monitoring

**5.1 CI/CD Integration**
```yaml
# GitHub Actions Workflow
name: Dependency Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 8 * * MON'  # Weekly scan

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run OWASP Dependency Check
        uses: dependency-check/dependency-check-action@v2
        with:
          project: 'MyApp'
          path: '.'
          format: 'ALL'
          args: >
            --enableRetired
            --enableExperimental
      
      - name: NPM Audit
        if: hashFiles('package.json') != ''
        run: |
          npm audit --audit-level=moderate
          npm audit fix --dry-run
      
      - name: Python Safety Check
        if: hashFiles('requirements.txt') != ''
        run: |
          pip install safety
          safety check --json > safety-report.json
      
      - name: License Check
        run: |
          npm install -g license-checker
          license-checker --onlyAllow 'MIT;Apache-2.0;BSD-3-Clause;ISC'
      
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: security-reports
          path: |
            dependency-check-report.*
            safety-report.json
      
      - name: Comment PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('dependency-check-report.json');
            const data = JSON.parse(report);
            
            if (data.vulnerabilities.length > 0) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: `⚠️ Security vulnerabilities found in dependencies!`
              });
            }
```

**5.2 Dependency Update Policies**
```json
// .github/dependabot.yml
{
  "version": 2,
  "updates": [
    {
      "package-ecosystem": "npm",
      "directory": "/",
      "schedule": {
        "interval": "weekly",
        "day": "monday",
        "time": "08:00"
      },
      "open-pull-requests-limit": 10,
      "reviewers": ["security-team"],
      "labels": ["dependencies", "security"],
      "ignore": [
        {
          "dependency-name": "aws-sdk",
          "versions": ["2.x"]
        }
      ],
      "allow": [
        {
          "dependency-type": "direct"
        },
        {
          "dependency-type": "production"
        }
      ]
    }
  ]
}
```

## Best Practices

### Dependency Management Best Practices

1. **Use Lock Files**
   - Always commit lock files (package-lock.json, Pipfile.lock)
   - Ensures reproducible builds
   - Prevents supply chain attacks

2. **Minimize Dependencies**
   - Audit dependency necessity
   - Remove unused dependencies
   - Consider implementing simple functions yourself

3. **Pin Versions**
   - Use exact versions in production
   - Allow ranges only in development
   - Review changes before updating

4. **Regular Updates**
   - Schedule weekly dependency reviews
   - Prioritize security updates
   - Test thoroughly before deploying

5. **Supply Chain Security**
   - Verify package integrity
   - Use private registries for internal packages
   - Implement package signing where possible

## Metrics and Reporting

### Key Performance Indicators

```python
class DependencyMetrics:
    def calculate_metrics(self, scan_results: Dict) -> Dict:
        return {
            "total_dependencies": len(scan_results["dependencies"]),
            "direct_dependencies": len([d for d in scan_results["dependencies"] if d["direct"]]),
            "vulnerable_dependencies": len(scan_results["vulnerabilities"]),
            "critical_vulnerabilities": len([v for v in scan_results["vulnerabilities"] if v["severity"] == "critical"]),
            "outdated_percentage": self.calculate_outdated_percentage(scan_results),
            "license_compliance_score": self.calculate_license_compliance(scan_results),
            "mean_time_to_remediate": self.calculate_mttr(scan_results),
            "dependency_freshness_score": self.calculate_freshness(scan_results)
        }
```

## References and Resources

### Standards and Guidelines
- OWASP Top 10 2021 - A06: Vulnerable and Outdated Components
- NIST SP 800-161: Supply Chain Risk Management
- ISO/IEC 27036: Information Security for Supplier Relationships
- CIS Software Supply Chain Security Guide

### Vulnerability Databases
- National Vulnerability Database (NVD)
- CVE Database
- GitHub Advisory Database
- OSV (Open Source Vulnerabilities)
- Snyk Vulnerability Database

## Conclusion

Dependency scanning is a critical component of modern application security. By implementing comprehensive scanning, maintaining up-to-date dependencies, and following secure development practices, organizations can significantly reduce their exposure to supply chain attacks and known vulnerabilities. Regular scanning, automated remediation, and continuous monitoring ensure that third-party components remain secure throughout the application lifecycle.