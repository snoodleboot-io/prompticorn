---
name: secret-management
description: "Secure handling of sensitive credentials and cryptographic keys"
agent: "security"
category: "security"
related_workflows:
  - security-hardening-checklist
  - compliance-audit-workflow
  - security-code-review
---

# Secret Management - Comprehensive Guide

## Overview

Secret management encompasses the secure storage, distribution, rotation, and auditing of sensitive information such as API keys, passwords, certificates, encryption keys, and tokens. Proper secret management is critical for preventing unauthorized access and data breaches.

## Prerequisites

### Knowledge Requirements
- Understanding of encryption principles
- Knowledge of authentication and authorization
- Familiarity with PKI and certificate management
- Understanding of key rotation strategies
- Compliance requirements (GDPR, PCI-DSS, HIPAA)

### Tools and Technologies
- **Secret Vaults**: HashiCorp Vault, AWS Secrets Manager, Azure Key Vault
- **Key Management**: AWS KMS, Google Cloud KMS, Azure Key Vault
- **Certificate Management**: Let's Encrypt, Venafi, DigiCert
- **Secret Scanning**: GitGuardian, TruffleHog, git-secrets
- **Hardware Security**: HSMs, YubiKey, Trusted Platform Modules

## Types of Secrets

### Secret Classification

```python
secret_types = {
    "authentication": {
        "examples": ["passwords", "api_keys", "oauth_tokens", "jwt_secrets"],
        "rotation_frequency": "90 days",
        "storage": "vault",
        "access_pattern": "application runtime"
    },
    "encryption": {
        "examples": ["data_encryption_keys", "master_keys", "key_encryption_keys"],
        "rotation_frequency": "365 days",
        "storage": "HSM or KMS",
        "access_pattern": "cryptographic operations"
    },
    "certificates": {
        "examples": ["tls_certificates", "code_signing_certs", "client_certificates"],
        "rotation_frequency": "90-365 days",
        "storage": "vault with auto-renewal",
        "access_pattern": "service startup"
    },
    "infrastructure": {
        "examples": ["ssh_keys", "database_passwords", "service_accounts"],
        "rotation_frequency": "180 days",
        "storage": "vault with dynamic generation",
        "access_pattern": "on-demand"
    },
    "third_party": {
        "examples": ["payment_gateway_keys", "external_api_tokens", "webhook_secrets"],
        "rotation_frequency": "vendor-dependent",
        "storage": "vault with external sync",
        "access_pattern": "service integration"
    }
}
```

## Detailed Implementation Steps

### Step 1: Secret Discovery and Inventory

**1.1 Automated Secret Scanning**
```python
import re
import os
import hashlib
from pathlib import Path
from typing import List, Dict

class SecretScanner:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.secrets_found = []
        self.patterns = self.load_secret_patterns()
    
    def load_secret_patterns(self) -> Dict[str, re.Pattern]:
        """Load regex patterns for different secret types"""
        return {
            "aws_access_key": re.compile(r'AKIA[0-9A-Z]{16}'),
            "aws_secret_key": re.compile(r'[0-9a-zA-Z/+=]{40}'),
            "github_token": re.compile(r'ghp_[0-9a-zA-Z]{36}'),
            "private_key": re.compile(r'-----BEGIN (RSA|DSA|EC) PRIVATE KEY-----'),
            "api_key": re.compile(r'(api[_-]?key|apikey)[\s]*[=:][\s]*["\'][0-9a-zA-Z]{32,}["\']', re.IGNORECASE),
            "password": re.compile(r'(password|passwd|pwd)[\s]*[=:][\s]*["\'][^"\'
]{8,}["\']', re.IGNORECASE),
            "jwt_secret": re.compile(r'(jwt[_-]?secret|secret[_-]?key)[\s]*[=:][\s]*["\'][^"\'
]{16,}["\']', re.IGNORECASE),
            "database_url": re.compile(r'(postgres|mysql|mongodb)://[^@]+@[^
]+'),
            "slack_token": re.compile(r'xox[baprs]-[0-9]{10,12}-[0-9]{10,12}-[a-zA-Z0-9]{24}'),
            "generic_secret": re.compile(r'["\'][0-9a-f]{40}["\']')  # SHA-1 like strings
        }
    
    def scan_file(self, file_path: Path) -> List[Dict]:
        """Scan a single file for secrets"""
        findings = []
        
        # Skip binary files
        if self.is_binary(file_path):
            return findings
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for secret_type, pattern in self.patterns.items():
                        matches = pattern.findall(line)
                        for match in matches:
                            # Don't report obvious placeholders
                            if not self.is_placeholder(match):
                                findings.append({
                                    "file": str(file_path),
                                    "line": line_num,
                                    "type": secret_type,
                                    "match": self.redact_secret(match),
                                    "hash": hashlib.sha256(str(match).encode()).hexdigest()[:10]
                                })
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return findings
    
    def is_placeholder(self, value: str) -> bool:
        """Check if value is likely a placeholder"""
        placeholders = [
            "your-api-key-here",
            "xxxxxxxx",
            "changeme",
            "<your-token>",
            "${API_KEY}",
            "process.env"
        ]
        return any(p in str(value).lower() for p in placeholders)
    
    def redact_secret(self, secret: str) -> str:
        """Redact middle portion of secret for safe display"""
        secret_str = str(secret)
        if len(secret_str) <= 8:
            return "****"
        return secret_str[:4] + "..." + secret_str[-4:]
```

**1.2 Secret Inventory Management**
```yaml
# secrets-inventory.yaml
secrets:
  - id: prod-db-password
    type: database_password
    description: Production database master password
    owner: database-team
    rotation_schedule: quarterly
    last_rotated: 2024-01-15
    vault_path: secret/database/prod/master
    compliance:
      - PCI-DSS
      - SOC2
    
  - id: stripe-api-key
    type: payment_gateway
    description: Stripe payment processing API key
    owner: payments-team
    rotation_schedule: annual
    last_rotated: 2023-10-01
    vault_path: secret/payments/stripe
    compliance:
      - PCI-DSS
    
  - id: jwt-signing-key
    type: cryptographic_key
    description: JWT token signing key
    owner: security-team
    rotation_schedule: biannual
    last_rotated: 2024-02-01
    vault_path: secret/auth/jwt
    algorithm: RS256
    key_size: 2048
```

### Step 2: Secure Storage Implementation

**2.1 HashiCorp Vault Configuration**
```hcl
# vault-config.hcl

storage "consul" {
  address = "127.0.0.1:8500"
  path    = "vault/"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/cert.pem"
  tls_key_file  = "/opt/vault/tls/key.pem"
}

seal "awskms" {
  region = "us-west-2"
  kms_key_id = "arn:aws:kms:us-west-2:account:key/key-id"
}

api_addr = "https://vault.example.com:8200"
cluster_addr = "https://vault.example.com:8201"
```

**2.2 Vault Secret Engine Setup**
```bash
#!/bin/bash
# Initialize Vault secret engines

# Enable KV v2 secret engine
vault secrets enable -path=secret kv-v2

# Enable database secret engine for dynamic credentials
vault secrets enable database

# Configure database connection
vault write database/config/postgresql \
  plugin_name=postgresql-database-plugin \
  allowed_roles="readonly,readwrite" \
  connection_url="postgresql://{{username}}:{{password}}@localhost:5432/mydb" \
  username="vault" \
  password="vault-password"

# Enable AWS secret engine
vault secrets enable aws

# Configure AWS secret engine
vault write aws/config/root \
  access_key=$AWS_ACCESS_KEY_ID \
  secret_key=$AWS_SECRET_ACCESS_KEY \
  region=us-west-2

# Enable PKI secret engine for certificate management
vault secrets enable pki

# Configure PKI
vault write pki/root/generate/internal \
  common_name=example.com \
  ttl=87600h
```

**2.3 Application Integration**
```python
import hvac
import os
from functools import lru_cache
from typing import Dict, Any

class VaultClient:
    def __init__(self, vault_url: str = None, vault_token: str = None):
        self.vault_url = vault_url or os.environ.get("VAULT_ADDR")
        self.vault_token = vault_token or self.get_vault_token()
        self.client = hvac.Client(
            url=self.vault_url,
            token=self.vault_token
        )
        
        if not self.client.is_authenticated():
            raise Exception("Failed to authenticate with Vault")
    
    def get_vault_token(self) -> str:
        """Get Vault token using various methods"""
        # Try environment variable
        if os.environ.get("VAULT_TOKEN"):
            return os.environ.get("VAULT_TOKEN")
        
        # Try Kubernetes auth
        if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/token"):
            return self.kubernetes_auth()
        
        # Try AWS IAM auth
        if os.environ.get("AWS_REGION"):
            return self.aws_iam_auth()
        
        raise Exception("No valid authentication method found")
    
    def kubernetes_auth(self) -> str:
        """Authenticate using Kubernetes service account"""
        with open("/var/run/secrets/kubernetes.io/serviceaccount/token", "r") as f:
            jwt = f.read()
        
        response = self.client.auth.kubernetes.login(
            role="my-app",
            jwt=jwt
        )
        return response["auth"]["client_token"]
    
    @lru_cache(maxsize=128)
    def get_secret(self, path: str, key: str = None) -> Any:
        """Retrieve secret from Vault with caching"""
        response = self.client.secrets.kv.v2.read_secret_version(
            path=path
        )
        
        data = response["data"]["data"]
        
        if key:
            return data.get(key)
        return data
    
    def get_dynamic_database_credentials(self, role: str) -> Dict[str, str]:
        """Get temporary database credentials"""
        response = self.client.secrets.database.generate_credentials(
            name=role
        )
        
        return {
            "username": response["data"]["username"],
            "password": response["data"]["password"],
            "lease_id": response["lease_id"],
            "lease_duration": response["lease_duration"]
        }
    
    def renew_lease(self, lease_id: str):
        """Renew a lease for dynamic secrets"""
        return self.client.sys.renew_lease(lease_id=lease_id)
```

### Step 3: Secret Rotation

**3.1 Automated Rotation Strategy**
```python
from datetime import datetime, timedelta
import boto3
import random
import string

class SecretRotation:
    def __init__(self, vault_client, notification_client):
        self.vault = vault_client
        self.notifier = notification_client
        self.rotation_policies = self.load_rotation_policies()
    
    def load_rotation_policies(self) -> Dict:
        """Load rotation policies for different secret types"""
        return {
            "database_password": {
                "frequency_days": 90,
                "complexity": {"length": 32, "special_chars": True},
                "rotation_function": self.rotate_database_password
            },
            "api_key": {
                "frequency_days": 180,
                "complexity": {"length": 40, "special_chars": False},
                "rotation_function": self.rotate_api_key
            },
            "tls_certificate": {
                "frequency_days": 365,
                "warning_days": 30,
                "rotation_function": self.rotate_certificate
            },
            "encryption_key": {
                "frequency_days": 365,
                "key_size": 256,
                "rotation_function": self.rotate_encryption_key
            }
        }
    
    def check_rotation_needed(self, secret_id: str, secret_type: str) -> bool:
        """Check if a secret needs rotation"""
        metadata = self.vault.get_secret_metadata(secret_id)
        last_rotated = metadata.get("last_rotated")
        
        if not last_rotated:
            return True
        
        policy = self.rotation_policies.get(secret_type, {})
        frequency = policy.get("frequency_days", 90)
        
        last_rotated_date = datetime.fromisoformat(last_rotated)
        rotation_due = last_rotated_date + timedelta(days=frequency)
        
        return datetime.now() >= rotation_due
    
    def rotate_database_password(self, connection_info: Dict) -> Dict:
        """Rotate database password"""
        new_password = self.generate_secure_password(
            length=32,
            include_special=True
        )
        
        # Update database password
        try:
            # Connect with current credentials
            conn = self.get_database_connection(connection_info)
            
            # Change password
            query = f"ALTER USER {connection_info['username']} WITH PASSWORD %s"
            conn.execute(query, (new_password,))
            
            # Update in Vault
            self.vault.update_secret(
                path=connection_info['vault_path'],
                data={"password": new_password}
            )
            
            # Update applications (trigger rolling restart)
            self.trigger_application_restart(connection_info['app_name'])
            
            # Notify team
            self.notifier.send(f"Database password rotated for {connection_info['database']}")
            
            return {"status": "success", "rotated_at": datetime.now().isoformat()}
        
        except Exception as e:
            # Rollback if needed
            self.handle_rotation_failure(connection_info, str(e))
            raise
    
    def generate_secure_password(self, length: int = 32, include_special: bool = True) -> str:
        """Generate cryptographically secure password"""
        characters = string.ascii_letters + string.digits
        if include_special:
            characters += "!@#$%^&*()_+-=[]{}|'"
        
        # Use secrets module for cryptographic randomness
        import secrets
        password = ''.join(secrets.choice(characters) for _ in range(length))
        
        # Ensure password meets complexity requirements
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|'" for c in password) if include_special else True
        
        if not (has_upper and has_lower and has_digit and has_special):
            return self.generate_secure_password(length, include_special)
        
        return password
```

### Step 4: Access Control and Auditing

**4.1 Policy-Based Access Control**
```hcl
# vault-policies.hcl

# Developer read-only policy
path "secret/data/dev/*" {
  capabilities = ["read", "list"]
}

path "secret/metadata/dev/*" {
  capabilities = ["list"]
}

# Production read policy for applications
path "secret/data/prod/+/+" {
  capabilities = ["read"]
  required_parameters = ["app_name"]
  allowed_parameters = {
    "app_name" = []
  }
  min_wrapping_ttl = "1h"
  max_wrapping_ttl = "24h"
}

# Security team admin policy
path "secret/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/policies/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "auth/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

path "sys/audit/*" {
  capabilities = ["read", "list"]
}
```

**4.2 Audit Logging**
```python
class SecretAuditLogger:
    def __init__(self, audit_backend: str = "splunk"):
        self.backend = audit_backend
        self.audit_client = self.initialize_audit_client()
    
    def log_secret_access(self, event: Dict):
        """Log secret access event"""
        audit_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "secret_access",
            "user": event.get("user"),
            "secret_path": event.get("path"),
            "action": event.get("action"),  # read, write, delete, list
            "source_ip": event.get("source_ip"),
            "user_agent": event.get("user_agent"),
            "success": event.get("success"),
            "error": event.get("error") if not event.get("success") else None,
            "metadata": {
                "app_name": event.get("app_name"),
                "environment": event.get("environment"),
                "request_id": event.get("request_id")
            }
        }
        
        # Send to audit backend
        self.audit_client.send(audit_event)
        
        # Check for suspicious activity
        if self.is_suspicious(audit_event):
            self.alert_security_team(audit_event)
    
    def is_suspicious(self, event: Dict) -> bool:
        """Detect suspicious secret access patterns"""
        suspicious_patterns = [
            # Multiple failed attempts
            lambda e: not e["success"] and self.count_recent_failures(e["user"]) > 5,
            # Access from unusual location
            lambda e: self.is_unusual_location(e["source_ip"], e["user"]),
            # Access outside business hours
            lambda e: self.is_outside_business_hours(e["timestamp"]),
            # Bulk secret access
            lambda e: e["action"] == "list" and self.count_recent_lists(e["user"]) > 10
        ]
        
        return any(pattern(event) for pattern in suspicious_patterns)
```

### Step 5: Emergency Access (Break Glass)

**5.1 Break Glass Procedures**
```python
class BreakGlassAccess:
    def __init__(self, vault_client, audit_logger):
        self.vault = vault_client
        self.audit = audit_logger
        self.emergency_vault_path = "secret/emergency/break-glass"
    
    def request_emergency_access(self, requester: str, justification: str) -> str:
        """Request emergency access to secrets"""
        request_id = self.generate_request_id()
        
        # Log the request
        self.audit.log_emergency_request({
            "request_id": request_id,
            "requester": requester,
            "justification": justification,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Generate temporary elevated token
        token = self.vault.create_orphan_token(
            policies=["emergency-access"],
            ttl="1h",
            metadata={
                "request_id": request_id,
                "requester": requester,
                "purpose": "emergency-access"
            }
        )
        
        # Notify security team immediately
        self.notify_security_team({
            "alert": "EMERGENCY ACCESS GRANTED",
            "requester": requester,
            "justification": justification,
            "token_ttl": "1 hour",
            "request_id": request_id
        })
        
        # Store break-glass event
        self.vault.write_secret(
            path=f"{self.emergency_vault_path}/{request_id}",
            data={
                "requester": requester,
                "justification": justification,
                "granted_at": datetime.utcnow().isoformat(),
                "token_accessor": token["auth"]["accessor"]
            }
        )
        
        return token["auth"]["client_token"]
    
    def revoke_emergency_access(self, request_id: str, reason: str):
        """Revoke emergency access"""
        # Get the token accessor
        emergency_data = self.vault.read_secret(
            f"{self.emergency_vault_path}/{request_id}"
        )
        
        # Revoke the token
        self.vault.revoke_token_accessor(
            emergency_data["token_accessor"]
        )
        
        # Log revocation
        self.audit.log_emergency_revocation({
            "request_id": request_id,
            "reason": reason,
            "revoked_at": datetime.utcnow().isoformat()
        })
```

## Best Practices

### Secret Management Best Practices

1. **Never Store Secrets in Code**
   - Use environment variables or secret management systems
   - Scan repositories for secrets before commit
   - Use pre-commit hooks to prevent secret commits

2. **Implement Defense in Depth**
   - Encrypt secrets at rest
   - Encrypt secrets in transit
   - Use hardware security modules for critical keys

3. **Follow Principle of Least Privilege**
   - Grant minimum necessary access
   - Use time-bound access tokens
   - Implement just-in-time access

4. **Regular Rotation**
   - Automate rotation where possible
   - Set maximum age policies
   - Test rotation procedures regularly

5. **Comprehensive Auditing**
   - Log all secret access
   - Monitor for anomalies
   - Regular access reviews

## Compliance and Standards

### Regulatory Requirements

- **PCI-DSS**: Requirement 8.2.4 - Change passwords at least every 90 days
- **HIPAA**: §164.308(a)(4) - Access management for ePHI
- **GDPR**: Article 32 - Implementation of appropriate security measures
- **SOC 2**: CC6.1 - Logical and physical access controls

## Metrics and Monitoring

### Key Performance Indicators

```python
secret_management_kpis = {
    "secrets_without_rotation": 0,  # Target
    "average_secret_age_days": 45,
    "failed_rotation_attempts": 0,
    "secrets_accessed_per_day": 1500,
    "time_to_rotate_minutes": 5,
    "compliance_score": 100,
    "hardcoded_secrets_found": 0
}
```

## References

- NIST SP 800-57: Recommendation for Key Management
- OWASP Key Management Cheat Sheet
- Cloud Security Alliance - Key Management Guidance
- HashiCorp Vault Best Practices
- AWS Secrets Manager User Guide

## Conclusion

Effective secret management is foundational to application and infrastructure security. By implementing proper secret storage, rotation, access controls, and monitoring, organizations can significantly reduce the risk of credential compromise and data breaches. The key is to automate as much as possible while maintaining strict controls and comprehensive audit trails.