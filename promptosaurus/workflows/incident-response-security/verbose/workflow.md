---
name: incident-response-security
description: "Structured approach to handling security incidents and breaches"
agent: "security"
category: "security"
related_workflows:
  - vulnerability-scanning-workflow
  - compliance-audit-workflow
  - threat-modeling-workflow
---

# Incident Response Security - Comprehensive Guide

## Overview

Incident response is a structured methodology for handling security incidents, breaches, and cyber threats. An effective incident response plan minimizes damage, reduces recovery time and costs, and ensures proper evidence collection for potential legal proceedings.

## Prerequisites

### Organizational Requirements
- Incident Response Team (IRT) established
- Clear escalation procedures
- Communication channels defined
- Legal and PR teams identified
- Insurance policies reviewed

### Technical Requirements
- Forensic tools and software
- Isolated analysis environment
- Evidence storage capabilities
- Backup and recovery systems
- Communication systems (out-of-band)

### Tools and Technologies
- **Forensics**: EnCase, FTK, Volatility, Autopsy
- **Network Analysis**: Wireshark, tcpdump, NetworkMiner
- **SIEM**: Splunk, ELK Stack, QRadar, Sentinel
- **Threat Intelligence**: MISP, ThreatConnect, Recorded Future
- **Orchestration**: Phantom, Demisto, TheHive

## NIST Incident Response Lifecycle

### Phase 1: Preparation

**1.1 Incident Response Plan Development**
```yaml
incident_response_plan:
  team_structure:
    incident_commander: "CISO"
    technical_lead: "Security Engineer"
    communications_lead: "PR Manager"
    legal_advisor: "General Counsel"
    forensics_lead: "Sr. Security Analyst"
    
  contact_list:
    internal:
      - name: "On-call Security"
        phone: "+1-555-0100"
        email: "security@company.com"
    external:
      - name: "FBI Cyber Division"
        phone: "+1-555-FBI-CYBER"
      - name: "Incident Response Retainer"
        phone: "+1-555-IR-HELP"
    
  severity_levels:
    critical:
      description: "Data breach, ransomware, service outage"
      response_time: "15 minutes"
      escalation: "Immediate C-suite notification"
    high:
      description: "System compromise, targeted attack"
      response_time: "1 hour"
      escalation: "CISO notification"
    medium:
      description: "Malware detection, suspicious activity"
      response_time: "4 hours"
      escalation: "Security team lead"
    low:
      description: "Policy violation, false positive"
      response_time: "24 hours"
      escalation: "Security analyst"
```

**1.2 Playbook Development**
```python
playbooks = {
    "ransomware": {
        "detection": ["Encryption activity", "Ransom note", "File extensions changed"],
        "containment": ["Isolate affected systems", "Disable accounts", "Block C2"],
        "eradication": ["Remove malware", "Patch vulnerabilities", "Reset credentials"],
        "recovery": ["Restore from backups", "Validate integrity", "Monitor for reinfection"]
    },
    "data_breach": {
        "detection": ["Unusual data transfer", "Unauthorized access", "Alert from partner"],
        "containment": ["Revoke access", "Reset passwords", "Enable MFA"],
        "investigation": ["Determine scope", "Identify data types", "Timeline analysis"],
        "notification": ["Legal review", "Regulatory filing", "Customer notification"]
    }
}
```

### Phase 2: Detection and Analysis

**2.1 Incident Detection Sources**
```python
detection_sources = [
    {"source": "SIEM Alerts", "reliability": "High", "automation": "Full"},
    {"source": "IDS/IPS", "reliability": "Medium", "automation": "Full"},
    {"source": "Endpoint Detection", "reliability": "High", "automation": "Full"},
    {"source": "User Reports", "reliability": "Low", "automation": "None"},
    {"source": "Threat Intelligence", "reliability": "Medium", "automation": "Partial"},
    {"source": "External Notification", "reliability": "Variable", "automation": "None"}
]
```

**2.2 Initial Triage Process**
```python
def triage_incident(alert):
    triage_checklist = {
        "is_false_positive": check_known_false_positives(alert),
        "affected_systems": identify_affected_systems(alert),
        "data_sensitivity": classify_data_involved(alert),
        "attack_vector": determine_attack_vector(alert),
        "threat_actor": identify_threat_actor_ttp(alert),
        "business_impact": assess_business_impact(alert)
    }
    
    severity = calculate_severity(triage_checklist)
    return {
        "incident_id": generate_incident_id(),
        "severity": severity,
        "checklist": triage_checklist,
        "next_steps": determine_response_actions(severity)
    }
```

**2.3 Evidence Collection**
```bash
#!/bin/bash
# Forensic evidence collection script

INCIDENT_ID="INC-2024-0412"
EVIDENCE_DIR="/forensics/${INCIDENT_ID}"

# Create evidence directory
mkdir -p ${EVIDENCE_DIR}/{memory,disk,network,logs}

# Capture memory dump
sudo ./lime.ko -o ${EVIDENCE_DIR}/memory/memory.dump

# Capture network connections
netstat -antp > ${EVIDENCE_DIR}/network/connections.txt
lsof -i > ${EVIDENCE_DIR}/network/open_ports.txt

# Capture process list
ps auxf > ${EVIDENCE_DIR}/memory/processes.txt
top -b -n 1 > ${EVIDENCE_DIR}/memory/top_snapshot.txt

# Capture system logs
tar czf ${EVIDENCE_DIR}/logs/system_logs.tar.gz /var/log/

# Create disk image
dd if=/dev/sda of=${EVIDENCE_DIR}/disk/disk.img bs=4M

# Calculate hashes for chain of custody
find ${EVIDENCE_DIR} -type f -exec sha256sum {} \; > ${EVIDENCE_DIR}/evidence_hashes.txt
```

### Phase 3: Containment, Eradication, and Recovery

**3.1 Containment Strategies**
```python
class ContainmentActions:
    def __init__(self, incident):
        self.incident = incident
        self.actions_taken = []
    
    def network_isolation(self, system_id):
        """Isolate system from network"""
        commands = [
            f"sudo iptables -I INPUT -s {system_id} -j DROP",
            f"sudo iptables -I OUTPUT -d {system_id} -j DROP",
            f"vlan isolate {system_id} quarantine"
        ]
        self.execute_commands(commands)
        self.actions_taken.append(f"Network isolation: {system_id}")
    
    def disable_accounts(self, compromised_users):
        """Disable compromised accounts"""
        for user in compromised_users:
            ad_disable(user)
            revoke_tokens(user)
            force_password_reset(user)
            self.actions_taken.append(f"Disabled account: {user}")
    
    def block_indicators(self, iocs):
        """Block malicious indicators"""
        for ioc in iocs:
            if ioc.type == "ip":
                firewall_block(ioc.value)
            elif ioc.type == "domain":
                dns_sinkhole(ioc.value)
            elif ioc.type == "hash":
                edr_block(ioc.value)
            self.actions_taken.append(f"Blocked {ioc.type}: {ioc.value}")
```

**3.2 Eradication Process**
```python
def eradicate_threat(incident):
    eradication_steps = []
    
    # Remove malware
    if incident.malware_present:
        for system in incident.affected_systems:
            scan_result = antivirus_scan(system)
            if scan_result.threats:
                quarantine_threats(scan_result.threats)
                eradication_steps.append(f"Removed {len(scan_result.threats)} threats from {system}")
    
    # Patch vulnerabilities
    vulnerabilities = identify_exploited_vulns(incident)
    for vuln in vulnerabilities:
        patch_status = apply_patch(vuln)
        eradication_steps.append(f"Patched {vuln.cve}: {patch_status}")
    
    # Reset credentials
    compromised_accounts = incident.compromised_accounts
    for account in compromised_accounts:
        reset_password(account)
        revoke_all_sessions(account)
        enable_mfa(account)
        eradication_steps.append(f"Reset credentials: {account}")
    
    return eradication_steps
```

**3.3 Recovery Operations**
```yaml
recovery_checklist:
  validation:
    - verify_malware_removed: true
    - verify_vulnerabilities_patched: true
    - verify_accounts_secured: true
    
  restoration:
    - restore_from_backup:
        backup_date: "2024-04-10"
        systems: ["web-server-01", "db-server-01"]
        validation: "checksum_verified"
    - rebuild_systems:
        systems: ["workstation-042"]
        image: "golden_image_v2.1"
    
  monitoring:
    - enhanced_monitoring_period: "30 days"
    - additional_logging: "enabled"
    - threat_hunting_scheduled: "daily"
    
  verification:
    - functionality_testing: "passed"
    - security_validation: "passed"
    - performance_baseline: "normal"
```

### Phase 4: Post-Incident Activity

**4.1 Lessons Learned Meeting**
```markdown
# Incident Post-Mortem: INC-2024-0412

## Timeline
- **T+0:00** - Initial alert from SIEM (SQL injection attempt)
- **T+0:15** - Triage completed, elevated to High severity
- **T+0:30** - Incident Response Team activated
- **T+1:00** - Containment actions initiated
- **T+2:30** - Threat actor expelled from environment
- **T+6:00** - Systems restored to operation
- **T+24:00** - Enhanced monitoring enabled

## What Went Well
- Rapid detection (15 minutes from compromise to alert)
- Effective containment prevented lateral movement
- Clear communication throughout incident

## What Needs Improvement
- Playbook for SQL injection was outdated
- Backup restoration took longer than RTO
- Legal notification process was unclear

## Action Items
1. Update SQL injection playbook - Due: 2024-04-20
2. Test backup restoration quarterly - Due: Q2 2024
3. Document legal notification workflow - Due: 2024-04-25
4. Implement automated containment for this attack pattern - Due: 2024-05-01
```

## Advanced Incident Response Scenarios

### Ransomware Response
```python
def ransomware_response(detection_alert):
    # Immediate containment
    affected_systems = identify_encryption_activity()
    for system in affected_systems:
        network_isolate(system)
        suspend_processes(system)
        capture_memory_dump(system)
    
    # Identify ransomware strain
    ransom_note = extract_ransom_note()
    malware_hash = calculate_file_hash()
    ransomware_family = identify_ransomware(ransom_note, malware_hash)
    
    # Check for decryptor
    if decryptor_available(ransomware_family):
        decrypt_files(decryptor_tool)
    else:
        # Restore from backups
        validate_backup_integrity()
        restore_from_backup()
    
    # Threat hunt for persistence
    hunt_for_backdoors()
    check_scheduled_tasks()
    analyze_registry_modifications()
```

### Supply Chain Attack Response
```python
def supply_chain_incident(vendor_notification):
    # Identify affected components
    affected_software = parse_vendor_notification(vendor_notification)
    our_systems = inventory_scan(affected_software)
    
    # Impact assessment
    for system in our_systems:
        data_processed = assess_data_exposure(system)
        downstream_systems = trace_connections(system)
        risk_score = calculate_supply_chain_risk(data_processed, downstream_systems)
    
    # Containment and remediation
    if risk_score == "critical":
        immediate_isolation(our_systems)
        vendor_patch = wait_for_vendor_patch()
        apply_patch(vendor_patch)
    else:
        implement_compensating_controls()
        monitor_closely(our_systems)
```

## Metrics and KPIs

### Incident Response Metrics
```python
incident_metrics = {
    "MTTD": "Mean Time to Detect: 45 minutes",
    "MTTA": "Mean Time to Acknowledge: 15 minutes",
    "MTTC": "Mean Time to Contain: 2 hours",
    "MTTR": "Mean Time to Recover: 6 hours",
    "incidents_per_month": 12,
    "false_positive_rate": "23%",
    "automation_rate": "67%",
    "lessons_learned_implemented": "89%"
}
```

## Regulatory Reporting Requirements

### GDPR Breach Notification
- **Timeline**: 72 hours to supervisory authority
- **Contents**: Nature of breach, affected individuals, likely consequences, measures taken
- **User Notification**: Without undue delay if high risk

### HIPAA Breach Notification
- **Timeline**: 60 days to affected individuals
- **HHS Notification**: 60 days for >500 records, annual for <500
- **Media Notice**: Required for breaches affecting >500 in a state

### PCI-DSS Incident Reporting
- **Timeline**: Immediately to card brands and acquirer
- **Forensic Investigation**: PFI required for Level 1-2 merchants
- **Compliance Validation**: Required post-incident

## Best Practices

### Preparation Phase
- ✓ Regular tabletop exercises (quarterly)
- ✓ Playbook updates based on threat intelligence
- ✓ Retainer with incident response firm
- ✓ Out-of-band communication channels
- ✓ Evidence preservation capabilities

### During Incident
- ✓ Document everything with timestamps
- ✓ Preserve evidence before remediation
- ✓ Communicate status updates regularly
- ✓ Consider legal implications
- ✓ Monitor for threat actor return

### Post-Incident
- ✓ Conduct thorough post-mortem
- ✓ Update security controls
- ✓ Share threat intelligence
- ✓ Test improved processes
- ✓ Recognize team performance

## References

- NIST SP 800-61r2: Computer Security Incident Handling Guide
- SANS Incident Handler's Handbook
- CISA Incident Response Playbooks
- FIRST CSIRT Services Framework
- ISO/IEC 27035: Incident Management

## Conclusion

Effective incident response requires preparation, practice, and continuous improvement. By following established frameworks, maintaining comprehensive playbooks, and learning from each incident, organizations can minimize the impact of security incidents and strengthen their overall security posture.