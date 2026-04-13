---
name: "security-hardening-checklist"
description: "Comprehensive checklist for hardening systems against attacks"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - compliance-audit-workflow
  - security-testing-workflow
---

# Security Hardening Checklist - Comprehensive Guide

## Overview

Security hardening is the process of securing systems by reducing their attack surface and vulnerability to threats. This involves implementing security controls, removing unnecessary services, applying patches, and configuring systems according to security best practices.

## Prerequisites

### Knowledge Requirements
- Understanding of operating system security
- Network security fundamentals
- Application security principles
- Compliance requirements
- Risk assessment methodology

### Tools and Resources
- **Benchmarks**: CIS Benchmarks, DISA STIGs
- **Scanning Tools**: Lynis, OpenSCAP, Microsoft Baseline Security Analyzer
- **Configuration Management**: Ansible, Puppet, Chef
- **Compliance Tools**: SCAP, Nessus Compliance Checks

## Operating System Hardening

### Linux Hardening

**1.1 Kernel Security Parameters**
```bash
# /etc/sysctl.conf
# Disable IPv6 if not needed
net.ipv6.conf.all.disable_ipv6 = 1
net.ipv6.conf.default.disable_ipv6 = 1

# Enable SYN cookies
net.ipv4.tcp_syncookies = 1

# Disable source routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv4.conf.default.accept_source_route = 0

# Enable IP spoofing protection
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1

# Disable ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv4.conf.default.accept_redirects = 0

# Enable ExecShield
kernel.exec-shield = 1
kernel.randomize_va_space = 2

# Apply settings
sudo sysctl -p
```

**1.2 User Account Hardening**
```bash
# Password policy configuration
# /etc/pam.d/common-password
password requisite pam_pwquality.so retry=3 minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1

# Account lockout policy
# /etc/pam.d/common-auth
auth required pam_tally2.so onerr=fail audit silent deny=5 unlock_time=900

# Set password aging
for user in $(awk -F: '{print $1}' /etc/passwd); do
  chage --maxdays 90 --mindays 7 --warndays 7 $user
done

# Disable unnecessary system accounts
for user in games news uucp proxy www-data list irc gnats nobody; do
  usermod -L $user
  usermod -s /sbin/nologin $user
done
```

### Windows Hardening

**2.1 Security Policies via Group Policy**
```powershell
# Account Policies
Set-ADDefaultDomainPasswordPolicy -Identity domain.com `
  -MinPasswordLength 14 `
  -PasswordHistoryCount 24 `
  -MaxPasswordAge "90.00:00:00" `
  -MinPasswordAge "1.00:00:00" `
  -LockoutThreshold 5 `
  -LockoutDuration "00:15:00" `
  -ComplexityEnabled $true

# Audit Policies
auditpol /set /category:"Logon/Logoff" /success:enable /failure:enable
auditpol /set /category:"Account Logon" /success:enable /failure:enable
auditpol /set /category:"Account Management" /success:enable /failure:enable
auditpol /set /category:"Object Access" /success:enable /failure:enable
```

**2.2 Windows Services Hardening**
```powershell
# Disable unnecessary services
$services = @(
  "RemoteRegistry",
  "TelnetClient",
  "SNMP",
  "Messenger",
  "Alerter",
  "ClipSrv",
  "Browser"
)

foreach ($service in $services) {
  Stop-Service -Name $service -Force -ErrorAction SilentlyContinue
  Set-Service -Name $service -StartupType Disabled -ErrorAction SilentlyContinue
}

# Configure Windows Firewall
New-NetFirewallRule -DisplayName "Block Inbound" -Direction Inbound -Action Block
New-NetFirewallRule -DisplayName "Allow RDP" -Direction Inbound -Protocol TCP -LocalPort 3389 -Action Allow -RemoteAddress 10.0.0.0/8
```

## Network Hardening

### Firewall Configuration

**3.1 iptables Rules (Linux)**
```bash
#!/bin/bash
# Basic iptables hardening script

# Flush existing rules
iptables -F
iptables -X
iptables -Z

# Default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH from specific subnet
iptables -A INPUT -p tcp -s 10.0.0.0/24 --dport 22 -j ACCEPT

# Allow HTTPS
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Rate limiting
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 -j DROP

# Log dropped packets
iptables -A INPUT -m limit --limit 5/min -j LOG --log-prefix "iptables denied: " --log-level 7

# Save rules
iptables-save > /etc/iptables/rules.v4
```

### Network Segmentation

**3.2 VLAN Configuration**
```yaml
vlan_configuration:
  management:
    vlan_id: 10
    subnet: 10.0.10.0/24
    description: "Management network"
    
  production:
    vlan_id: 20
    subnet: 10.0.20.0/24
    description: "Production servers"
    
  dmz:
    vlan_id: 30
    subnet: 10.0.30.0/24
    description: "DMZ for public-facing services"
    
  development:
    vlan_id: 40
    subnet: 10.0.40.0/24
    description: "Development environment"
    
  guest:
    vlan_id: 50
    subnet: 10.0.50.0/24
    description: "Guest network"
```

## Application Hardening

### Web Server Hardening

**4.1 Apache Hardening**
```apache
# /etc/apache2/conf-enabled/security.conf

# Hide version information
ServerTokens Prod
ServerSignature Off

# Disable directory listing
Options -Indexes

# Security headers
Header always set X-Frame-Options "DENY"
Header always set X-Content-Type-Options "nosniff"
Header always set X-XSS-Protection "1; mode=block"
Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
Header always set Content-Security-Policy "default-src 'self'"

# Disable TRACE method
TraceEnable off

# Limit request size
LimitRequestBody 10485760

# Timeout settings
Timeout 60
KeepAliveTimeout 5
MaxKeepAliveRequests 100
```

**4.2 Nginx Hardening**
```nginx
# /etc/nginx/nginx.conf

# Hide version
server_tokens off;

# Security headers
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers on;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;

# Rate limiting
limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;
limit_conn_zone $binary_remote_addr zone=addr:10m;

server {
    limit_req zone=one burst=10 nodelay;
    limit_conn addr 10;
    
    # Disable unnecessary methods
    if ($request_method !~ ^(GET|HEAD|POST)$) {
        return 444;
    }
}
```

### Database Hardening

**5.1 PostgreSQL Hardening**
```sql
-- Enable SSL
ALTER SYSTEM SET ssl = on;

-- Configure authentication
-- pg_hba.conf
# TYPE  DATABASE USER      ADDRESS         METHOD
host    all      all       0.0.0.0/0       reject
hostssl all      all       10.0.0.0/8      scram-sha-256

-- Set password encryption
ALTER SYSTEM SET password_encryption = 'scram-sha-256';

-- Enable logging
ALTER SYSTEM SET logging_collector = on;
ALTER SYSTEM SET log_directory = 'pg_log';
ALTER SYSTEM SET log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log';
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_statement = 'all';

-- Remove default postgres database
DROP DATABASE IF EXISTS postgres;

-- Revoke unnecessary privileges
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE template1 FROM PUBLIC;
```

**5.2 MySQL Hardening**
```sql
-- Remove test database
DROP DATABASE IF EXISTS test;

-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Disable remote root login
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Set secure file privileges
SET GLOBAL local_infile = 'OFF';

-- Enable SSL
SET GLOBAL require_secure_transport = ON;

-- Password validation plugin
INSTALL PLUGIN validate_password SONAME 'validate_password.so';
SET GLOBAL validate_password.policy = STRONG;
SET GLOBAL validate_password.length = 14;

-- Audit plugin
INSTALL PLUGIN audit_log SONAME 'audit_log.so';
SET GLOBAL audit_log_policy = 'ALL';

FLUSH PRIVILEGES;
```

## Cloud Hardening

### AWS Hardening

**6.1 IAM Best Practices**
```python
import boto3

def harden_iam():
    iam = boto3.client('iam')
    
    # Enable MFA for root account
    # (Manual process, check via API)
    
    # Password policy
    iam.update_account_password_policy(
        MinimumPasswordLength=14,
        RequireSymbols=True,
        RequireNumbers=True,
        RequireUppercaseCharacters=True,
        RequireLowercaseCharacters=True,
        AllowUsersToChangePassword=True,
        MaxPasswordAge=90,
        PasswordReusePrevention=24
    )
    
    # Remove unused access keys
    users = iam.list_users()['Users']
    for user in users:
        access_keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
        for key in access_keys:
            key_age = (datetime.now(timezone.utc) - key['CreateDate']).days
            if key_age > 90:
                iam.update_access_key(
                    UserName=user['UserName'],
                    AccessKeyId=key['AccessKeyId'],
                    Status='Inactive'
                )
```

**6.2 Security Group Hardening**
```python
def harden_security_groups():
    ec2 = boto3.client('ec2')
    
    # Find overly permissive rules
    response = ec2.describe_security_groups()
    
    for sg in response['SecurityGroups']:
        for rule in sg['IpPermissions']:
            # Check for 0.0.0.0/0
            for ip_range in rule.get('IpRanges', []):
                if ip_range['CidrIp'] == '0.0.0.0/0':
                    if rule['FromPort'] not in [80, 443]:  # Only allow HTTP/HTTPS from anywhere
                        print(f"Warning: SG {sg['GroupId']} has overly permissive rule")
                        # Optionally revoke the rule
                        ec2.revoke_security_group_ingress(
                            GroupId=sg['GroupId'],
                            IpPermissions=[rule]
                        )
```

## Container Hardening

### Docker Hardening

**7.1 Dockerfile Best Practices**
```dockerfile
# Use minimal base image
FROM alpine:3.14

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# Install only necessary packages
RUN apk add --no-cache python3 py3-pip && \
    rm -rf /var/cache/apk/*

# Copy and set permissions
COPY --chown=appuser:appuser app /app

# Security configurations
RUN chmod 700 /app && \
    find /app -type f -exec chmod 600 {} \; && \
    find /app -type d -exec chmod 700 {} \;

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 /app/healthcheck.py || exit 1

# Run with read-only root filesystem
ENTRYPOINT ["python3"]
CMD ["/app/main.py"]
```

**7.2 Docker Runtime Security**
```bash
# Run container with security options
docker run \
  --security-opt=no-new-privileges:true \
  --cap-drop=ALL \
  --cap-add=NET_BIND_SERVICE \
  --read-only \
  --tmpfs /tmp:noexec,nosuid,size=100m \
  --memory="512m" \
  --memory-swap="512m" \
  --cpus="0.5" \
  --pids-limit=100 \
  --user 1000:1000 \
  myapp:latest
```

## Monitoring and Compliance

### Security Monitoring Configuration

**8.1 Audit Configuration**
```bash
# /etc/audit/audit.rules

# Monitor authentication events
-w /var/log/faillog -p wa -k auth_failures
-w /var/log/lastlog -p wa -k logins
-w /var/log/tallylog -p wa -k logins

# Monitor user/group changes
-w /etc/passwd -p wa -k passwd_changes
-w /etc/group -p wa -k group_changes
-w /etc/shadow -p wa -k shadow_changes
-w /etc/sudoers -p wa -k sudoers_changes

# Monitor system calls
-a exit,always -F arch=b64 -S execve -k command_execution
-a exit,always -F arch=b64 -S chmod -S fchmod -S fchmodat -k permission_changes

# Make configuration immutable
-e 2
```

## Hardening Validation

### Compliance Scanning

**9.1 CIS Benchmark Validation**
```python
import subprocess
import json

def validate_cis_compliance():
    # Run CIS-CAT or similar tool
    result = subprocess.run(
        ['./cis-cat-lite.sh', '-b', 'benchmarks/CIS_Ubuntu_20.04_Benchmark_v1.0.0'],
        capture_output=True,
        text=True
    )
    
    # Parse results
    compliance_score = parse_cis_results(result.stdout)
    
    if compliance_score < 90:
        print(f"Warning: CIS compliance score {compliance_score}% is below threshold")
        generate_remediation_report()
    
    return compliance_score
```

## Best Practices Summary

### Essential Hardening Checklist

- [ ] Operating System
  - [ ] Latest patches applied
  - [ ] Unnecessary services disabled
  - [ ] Strong password policies enforced
  - [ ] Audit logging enabled
  - [ ] Kernel parameters hardened

- [ ] Network
  - [ ] Firewall configured and enabled
  - [ ] Network segmentation implemented
  - [ ] Unnecessary ports closed
  - [ ] Rate limiting configured
  - [ ] IDS/IPS deployed

- [ ] Applications
  - [ ] Security headers configured
  - [ ] TLS properly configured
  - [ ] Default credentials changed
  - [ ] Error messages sanitized
  - [ ] Input validation implemented

- [ ] Access Control
  - [ ] Principle of least privilege applied
  - [ ] MFA enabled for privileged accounts
  - [ ] Regular access reviews conducted
  - [ ] Service accounts secured
  - [ ] SSH key management implemented

## References

- CIS Benchmarks: https://www.cisecurity.org/
- NIST SP 800-123: Guide to General Server Security
- DISA Security Technical Implementation Guides (STIGs)
- OWASP Security Configuration Cheat Sheet
- NSA Hardening Guides

## Conclusion

Security hardening is an ongoing process that requires regular review and updates. Organizations should implement these controls in a systematic manner, validate their effectiveness, and maintain them through proper change management and monitoring processes.