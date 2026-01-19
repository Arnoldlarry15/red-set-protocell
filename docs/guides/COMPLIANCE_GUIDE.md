# Compliance and Privacy Guide

This guide covers compliance, privacy, and data handling for Red Set ProtoCell.

## Table of Contents

- [Overview](#overview)
- [Privacy Policy Template](#privacy-policy-template)
- [Data Retention](#data-retention)
- [GDPR Compliance](#gdpr-compliance)
- [Data Protection](#data-protection)
- [Audit Logging](#audit-logging)
- [User Rights](#user-rights)
- [Incident Response](#incident-response)

## Overview

Red Set ProtoCell is designed with privacy and compliance in mind:

- **Zero-Retention Policy**: All session data can be automatically deleted
- **Content Fingerprinting**: Privacy-preserving hashed logging
- **Minimal Data Collection**: Only collect what's necessary
- **User Control**: Clear opt-in/opt-out mechanisms
- **Transparent Operations**: Auditable and documented

## Privacy Policy Template

### Data We Collect

**When Using the Service:**
- API request logs (IP address, timestamp, endpoint accessed)
- Session metadata (session IDs, configuration, timestamps)
- LLM prompts and responses (only during active sessions)
- Error logs and diagnostic information

**When Creating an Account:**
- Username and email address
- Hashed password (never stored in plaintext)
- Role and permission settings
- Account creation and last login timestamps

**Automatically Collected:**
- HTTP request headers (User-Agent, etc.)
- Performance metrics (latency, error rates)
- WebSocket connection metadata

### How We Use Your Data

**Primary Purposes:**
- Provide red teaming services
- Improve system performance and reliability
- Debug and troubleshoot issues
- Monitor for abuse and security threats

**Analytics:**
- Aggregate usage statistics (anonymized)
- Performance benchmarking
- Service optimization

### Data Storage and Retention

**Active Sessions:**
- Duration: While session is active
- Location: Server memory and temporary database
- Deletion: Automatic when session ends (if zero-retention enabled)

**User Accounts:**
- Duration: Until account deletion requested
- Location: Secure database with encryption at rest
- Deletion: Within 30 days of request

**Logs:**
- Duration: 90 days (configurable)
- Location: Log aggregation system
- Deletion: Automatic rotation

**Backups:**
- Duration: 30 days (configurable)
- Location: Encrypted backup storage
- Deletion: Automatic rotation

### Data Sharing

We **DO NOT** share your data with third parties, except:

1. **LLM Providers** (OpenAI, Anthropic)
   - Purpose: Process red teaming prompts
   - Data: Prompts and model responses
   - Their policies: See provider privacy policies

2. **Cloud Service Providers** (if applicable)
   - Purpose: Infrastructure hosting
   - Data: Encrypted data at rest
   - Their policies: AWS, Google Cloud, Azure policies

3. **Legal Requirements**
   - When required by law or valid legal process
   - With notice to you unless prohibited

### Your Rights

You have the right to:

- **Access**: Request a copy of your data
- **Correction**: Update incorrect data
- **Deletion**: Request deletion of your data
- **Portability**: Export your data in machine-readable format
- **Objection**: Object to certain data processing
- **Restriction**: Limit how we use your data

### Contact for Privacy Concerns

Email: privacy@[your-domain].com  
Response time: Within 72 hours

## Data Retention

### Retention Policies

```yaml
# Example retention configuration
retention_policies:
  sessions:
    active: "until_complete"
    completed: "immediate" # with zero-retention enabled
    without_zero_retention: "90_days"
  
  logs:
    access_logs: "90_days"
    error_logs: "90_days"
    audit_logs: "365_days"
  
  user_accounts:
    active: "until_deleted"
    inactive: "2_years"
    deleted: "30_days" # grace period
  
  backups:
    daily: "7_days"
    weekly: "30_days"
    monthly: "365_days"
  
  metrics:
    raw: "30_days"
    aggregated: "365_days"
```

### Implementing Retention

#### Automatic Cleanup Script

```python
# scripts/cleanup_old_data.py
"""
Automated data retention enforcement script.
Run daily via cron.
"""

import sqlite3
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

RETENTION_DAYS = {
    'sessions': 90,
    'logs': 90,
    'metrics': 30,
}

def cleanup_old_sessions(db_path: str, days: int = 90):
    """Delete sessions older than specified days."""
    conn = sqlite3.connect(db_path)
    cutoff = datetime.now() - timedelta(days=days)
    
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM sessions WHERE created_at < ?",
        (cutoff.isoformat(),)
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    
    logger.info(f"Deleted {deleted} old sessions (older than {days} days)")
    return deleted

def cleanup_old_logs(log_dir: str, days: int = 90):
    """Delete log files older than specified days."""
    import os
    from pathlib import Path
    
    cutoff = datetime.now() - timedelta(days=days)
    deleted = 0
    
    for log_file in Path(log_dir).glob("*.log*"):
        if log_file.stat().st_mtime < cutoff.timestamp():
            log_file.unlink()
            deleted += 1
    
    logger.info(f"Deleted {deleted} old log files (older than {days} days)")
    return deleted

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Cleanup sessions
    cleanup_old_sessions("/data/rsp_production.db", RETENTION_DAYS['sessions'])
    
    # Cleanup logs
    cleanup_old_logs("/var/log/rsp", RETENTION_DAYS['logs'])
```

#### Cron Configuration

```bash
# /etc/cron.d/rsp-cleanup
# Run daily at 2 AM
0 2 * * * rsp python /opt/rsp/scripts/cleanup_old_data.py >> /var/log/rsp/cleanup.log 2>&1
```

## GDPR Compliance

### Principles

1. **Lawfulness, Fairness, Transparency**
   - Clear privacy policy
   - Transparent data usage
   - Lawful basis for processing

2. **Purpose Limitation**
   - Data used only for stated purposes
   - No secondary uses without consent

3. **Data Minimization**
   - Collect only necessary data
   - Zero-retention by default

4. **Accuracy**
   - Allow users to correct data
   - Regular data validation

5. **Storage Limitation**
   - Automatic data deletion
   - Configurable retention periods

6. **Integrity and Confidentiality**
   - Encryption at rest and in transit
   - Access controls and authentication

7. **Accountability**
   - Audit logs
   - Data processing records
   - Privacy impact assessments

### GDPR Rights Implementation

#### Right to Access (Art. 15)

```python
# API endpoint for data export
@app.get("/api/user/{username}/export")
async def export_user_data(username: str):
    """
    Export all data associated with a user.
    Returns JSON with complete user data.
    """
    data = {
        "user_profile": get_user_profile(username),
        "sessions": get_user_sessions(username),
        "api_usage": get_user_api_usage(username),
        "export_date": datetime.utcnow().isoformat(),
    }
    return data
```

#### Right to Erasure (Art. 17)

```python
# API endpoint for account deletion
@app.delete("/api/user/{username}")
async def delete_user_account(username: str):
    """
    Delete user account and all associated data.
    Implements 30-day grace period.
    """
    # Mark for deletion
    mark_user_for_deletion(username, grace_period_days=30)
    
    # Schedule cleanup job
    schedule_user_deletion(username, delay_days=30)
    
    return {
        "status": "scheduled_for_deletion",
        "deletion_date": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "grace_period_days": 30
    }
```

#### Right to Data Portability (Art. 20)

```python
# API endpoint for data export in machine-readable format
@app.get("/api/user/{username}/export.json")
async def export_user_data_portable(username: str):
    """Export user data in JSON format (data portability)."""
    return export_user_data(username)
```

### Data Processing Records

Maintain records of:
- What data is processed
- Why it's processed
- Who processes it
- Where it's stored
- How long it's retained
- Security measures applied

## Data Protection

### Encryption

#### At Rest

```bash
# SQLite with encryption
pip install sqlcipher3

# PostgreSQL with encryption
# Use encrypted storage volumes
# Enable pgcrypto extension
```

#### In Transit

```nginx
# nginx TLS configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;
```

### Access Controls

```yaml
# Role-based access control matrix
roles:
  observer:
    can: [read_sessions, view_metrics]
    cannot: [start_sessions, delete_data, manage_users]
  
  researcher:
    can: [read_sessions, start_sessions, view_metrics]
    cannot: [delete_data, manage_users]
  
  admin:
    can: [all]
    cannot: []
```

### Sensitive Data Handling

```python
# Never log sensitive data
def sanitize_for_logging(data: dict) -> dict:
    """Remove sensitive fields before logging."""
    sensitive_fields = [
        'password', 'api_key', 'token', 
        'secret', 'authorization'
    ]
    
    sanitized = data.copy()
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = '***REDACTED***'
    
    return sanitized
```

## Audit Logging

### What to Audit

- User authentication attempts (success/failure)
- Account creation and deletion
- Permission changes
- Data access and exports
- Configuration changes
- Administrative actions

### Audit Log Format

```json
{
  "timestamp": "2026-01-18T05:00:00Z",
  "event_type": "user_login",
  "actor": {
    "username": "john.doe",
    "ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0..."
  },
  "action": "login_success",
  "resource": {
    "type": "user_account",
    "id": "john.doe"
  },
  "outcome": "success",
  "metadata": {
    "authentication_method": "jwt"
  }
}
```

### Audit Log Implementation

```python
class AuditLogger:
    """Audit logging for security-relevant events."""
    
    @staticmethod
    def log_event(event_type: str, actor: dict, action: str, 
                   resource: dict, outcome: str, metadata: dict = None):
        """Log an audit event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "resource": resource,
            "outcome": outcome,
            "metadata": metadata or {}
        }
        
        # Write to audit log (separate from application logs)
        logger.info(f"AUDIT: {json.dumps(event)}")
```

## User Rights

### Exercising Rights

Users can exercise their rights by:

1. **Through API**:
   ```bash
   # Export data
   curl -H "Authorization: Bearer $TOKEN" \
     https://api.example.com/api/user/me/export
   
   # Delete account
   curl -X DELETE -H "Authorization: Bearer $TOKEN" \
     https://api.example.com/api/user/me
   ```

2. **Through Dashboard**: Settings → Privacy → [Action]

3. **By Email**: privacy@[your-domain].com

### Response Times

- **Access requests**: Within 30 days
- **Deletion requests**: Within 30 days (plus grace period)
- **Correction requests**: Within 7 days
- **Objection requests**: Within 15 days

## Incident Response

### Data Breach Response Plan

#### Phase 1: Detection (0-1 hour)
1. Identify the breach
2. Assess scope and severity
3. Contain the breach

#### Phase 2: Notification (1-72 hours)
1. Notify supervisory authority (within 72 hours of detection)
2. Notify affected users (if high risk)
3. Document the breach

#### Phase 3: Investigation (1-7 days)
1. Determine root cause
2. Assess data exposed
3. Evaluate risks to individuals

#### Phase 4: Remediation (7-30 days)
1. Fix vulnerabilities
2. Strengthen security
3. Prevent recurrence

#### Phase 5: Documentation (Ongoing)
1. Maintain breach register
2. Document lessons learned
3. Update procedures

### Breach Notification Template

```markdown
Subject: Security Incident Notification

Dear [User],

We are writing to inform you of a security incident that may have affected 
your personal data.

**What Happened:**
[Brief description of the incident]

**What Data Was Affected:**
[List of data types affected]

**What We're Doing:**
[Steps taken to address the incident]

**What You Should Do:**
[Recommended actions for affected users]

**How to Contact Us:**
Email: security@[domain].com
Phone: [phone number]

We take your privacy seriously and sincerely apologize for any concern 
this may cause.

Sincerely,
[Organization]
```

## Compliance Checklist

### Pre-Launch
- [ ] Privacy policy published
- [ ] Data retention policy configured
- [ ] Encryption enabled (at rest and in transit)
- [ ] Access controls implemented
- [ ] Audit logging enabled
- [ ] Breach response plan documented
- [ ] User rights procedures documented
- [ ] Data processing records created

### Ongoing
- [ ] Regular security audits (quarterly)
- [ ] Privacy impact assessments (annually)
- [ ] Staff privacy training (annually)
- [ ] Policy reviews and updates (annually)
- [ ] Audit log reviews (monthly)
- [ ] Vulnerability scanning (weekly)

## Resources

- GDPR Official Text: https://gdpr-info.eu/
- ICO Guide to GDPR: https://ico.org.uk/for-organisations/guide-to-data-protection/guide-to-the-general-data-protection-regulation-gdpr/
- CCPA Compliance: https://oag.ca.gov/privacy/ccpa

---

Last Updated: January 2026
Version: 1.0.0

**Disclaimer**: This guide provides general information and is not legal advice. 
Consult with legal counsel for compliance with specific regulations in your jurisdiction.
