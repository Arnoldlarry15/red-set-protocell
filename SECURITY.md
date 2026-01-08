# Security Policy

## Overview

Red Set ProtoCell (RSP) is a defensive AI red teaming platform designed with security as a core principle. This document outlines our security policies, responsible disclosure procedures, and security best practices for users and contributors.

## Supported Versions

| Version | Supported          | Security Updates |
| ------- | ------------------ | ---------------- |
| 1.0.x   | :white_check_mark: | Active           |
| < 1.0   | :x:                | No longer supported |

## Reporting a Vulnerability

### Responsible Disclosure

We take security seriously. If you discover a security vulnerability in RSP, please report it responsibly.

### How to Report

**Email**: security@[domain].com (replace with actual contact)

**Include**:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fixes (if any)
- Your contact information

**Please DO NOT**:
- Open public GitHub issues for security vulnerabilities
- Disclose the vulnerability publicly before we've had a chance to address it
- Test the vulnerability on systems you don't own

### Response Timeline

- **Within 24 hours**: We'll acknowledge receipt of your report
- **Within 7 days**: We'll provide an initial assessment
- **Within 30 days**: We'll work on a fix and coordinate disclosure
- **After fix**: We'll credit you (if desired) in release notes

### Responsible Disclosure Period

We request a **90-day** disclosure timeline to:
1. Investigate and verify the vulnerability
2. Develop and test a fix
3. Coordinate with affected parties
4. Prepare security advisory
5. Release patch and disclosure

## Security Features

### Built-in Security Mechanisms

#### 1. Ethical Guardrail Governor (EGG)

The EGG is RSP's primary safety mechanism that:

- **Blocks CSAM content**: Prevents child safety violations
- **Blocks bioweapon instructions**: Prevents biological weapon content
- **Blocks real exploits**: Prevents real exploit payloads
- **Blocks real hacking**: Prevents actual attack attempts
- **Cannot be disabled**: EGG is mandatory in production

**Implementation**:
```python
# EGG decisions are FINAL and non-overridable
is_allowed, blocked_info = egg.inspect_prompt(prompt)
if not is_allowed:
    # Prompt is blocked, execution stops
    return blocked_info
```

#### 2. Content Fingerprinting

RSP uses SHA-256 hashing for privacy-preserving logging:

```python
# Blocked content is logged as hash, not plaintext
fingerprint = hashlib.sha256(prompt.encode()).hexdigest()
logger.warning(f"Blocked content fingerprint: {fingerprint}")
```

**Benefits**:
- No storage of actual harmful content
- Audit trail for compliance
- Privacy-preserving incident response

#### 3. Zero-Retention Policy

Enabled by default, zero-retention ensures:

- All session data destroyed after completion
- No persistent storage of prompts or responses
- No long-term data accumulation
- GDPR and privacy compliance

**Usage**:
```bash
# Zero-retention enabled (default)
python -m app.main --backend openai --api-key $KEY --rounds 10

# Disable for debugging only
python -m app.main --backend openai --api-key $KEY --no-zero-retention
```

#### 4. Trust Boundaries

RSP implements strict trust boundaries:

```
┌──────────────────────────────────────┐
│  NO TRUST ASSUMPTIONS                │
├──────────────────────────────────────┤
│  Agents don't trust each other       │
│  Agents don't trust their outputs    │
│  External models treated as untrusted│
│  All outputs require human validation│
└──────────────────────────────────────┘
```

#### 5. Input Validation

All inputs are validated and sanitized:

```python
def validate_api_key(key: str, backend: str) -> bool:
    """Validate API key format."""
    if backend == "openai":
        return key.startswith("sk-") and len(key) > 20
    elif backend == "anthropic":
        return key.startswith("sk-ant-") and len(key) > 20
    return False
```

## Security Best Practices

### For Users

#### 1. API Key Security

**DO**:
- Store API keys in environment variables
- Use `.env` files (add to `.gitignore`)
- Rotate keys regularly
- Use separate keys for testing and production
- Monitor API usage for anomalies

**DON'T**:
- Commit API keys to version control
- Share API keys in chat or email
- Use production keys for development
- Hardcode keys in source code

**Example**:
```bash
# Good: Environment variable
export OPENAI_API_KEY="sk-..."
python -m app.main --backend openai --api-key $OPENAI_API_KEY

# Bad: Hardcoded
python -m app.main --backend openai --api-key "sk-abc123..."
```

#### 2. Database Security

**Sensitive Data**:
- Session databases may contain prompts and responses
- Use zero-retention for sensitive tests
- Encrypt database files at rest
- Secure database file permissions

```bash
# Set restrictive permissions
chmod 600 rsp_session.db

# Use zero-retention for sensitive tests
python -m app.main --backend openai --api-key $KEY --rounds 10
# (Database deleted automatically)
```

#### 3. Network Security

**API Communication**:
- All API calls use HTTPS (enforced by clients)
- No local proxying of API traffic
- Verify TLS certificates (default behavior)

**Firewall Rules**:
```bash
# Allow outbound HTTPS to API endpoints
# OpenAI: api.openai.com:443
# Anthropic: api.anthropic.com:443
```

#### 4. Access Control

**Deployment**:
- Restrict who can run RSP
- Log all session executions
- Monitor for unauthorized use
- Implement role-based access control

**Docker**:
```yaml
# Run as non-root user
services:
  rsp-backend:
    user: "1000:1000"
    read_only: true
    security_opt:
      - no-new-privileges:true
```

#### 5. Monitoring and Logging

**What to Monitor**:
- EGG block events
- API errors and rate limits
- Unusual scoring patterns
- Execution failures

**Log Analysis**:
```bash
# Check for EGG blocks
grep "EGG blocked" rsp.log

# Check for API errors
grep "ERROR" rsp.log | grep "API"

# Analyze session stats
grep "SESSION COMPLETED" rsp.log
```

### For Developers

#### 1. Secure Coding Practices

**Input Validation**:
```python
def validate_round_number(rounds: int) -> None:
    """Validate rounds parameter."""
    if not isinstance(rounds, int):
        raise TypeError("Rounds must be an integer")
    if rounds < 1 or rounds > 10000:
        raise ValueError("Rounds must be between 1 and 10000")
```

**Error Handling**:
```python
try:
    response = await target.execute(prompt)
except TargetExecutionError as e:
    logger.error(f"Execution failed: {e}")
    # Don't expose internal details in error messages
    raise Exception("Execution failed") from None
```

**Secrets Management**:
```python
# Bad: Hardcoded secret
API_KEY = "sk-abc123..."

# Good: Environment variable
import os
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable required")
```

#### 2. Dependency Security

**Keep Dependencies Updated**:
```bash
# Check for vulnerabilities
pip install safety
safety check

# Update dependencies
pip install --upgrade openai anthropic

# Audit dependencies
pip-audit
```

**Requirements Pinning**:
```txt
# Pin versions for reproducibility
openai==1.12.0
anthropic==0.18.1
```

#### 3. Testing Security

**Security Test Cases**:
```python
def test_egg_blocks_harmful_content():
    """Verify EGG blocks harmful content."""
    egg = EthicalGuardrailGovernor()
    
    # Test CSAM blocking
    is_allowed, _ = egg.inspect_prompt("child explicit content")
    assert not is_allowed
    
    # Test bioweapon blocking
    is_allowed, _ = egg.inspect_prompt("weaponize anthrax")
    assert not is_allowed

def test_api_key_not_logged():
    """Verify API keys are not logged."""
    with LogCapture() as logs:
        target = create_target("openai", api_key="sk-secret123")
        assert "sk-secret123" not in str(logs)
```

#### 4. Code Review Checklist

Before merging code, verify:

- [ ] No hardcoded secrets or API keys
- [ ] Input validation for all user inputs
- [ ] Proper error handling (no info leaks)
- [ ] Security tests included
- [ ] Dependencies are up to date
- [ ] EGG cannot be bypassed
- [ ] No introduction of real exploit capabilities
- [ ] Documentation updated for security-relevant changes

## Vulnerability Disclosure History

### Version 1.0.0 (Current)

No vulnerabilities reported.

### Reporting Format

When we disclose vulnerabilities:

```markdown
### [Severity] Vulnerability Title (CVE-XXXX-XXXXX)

**Affected Versions**: x.x.x - y.y.y
**Fixed In**: z.z.z
**Severity**: High/Medium/Low
**CVSS Score**: 7.5

**Description**:
Brief description of the vulnerability.

**Impact**:
What an attacker could achieve.

**Mitigation**:
How to protect yourself.

**Credit**:
Reported by [Name] (if permission granted).
```

## Security Audits

### Internal Security Review

We conduct regular security reviews:

- **Code Reviews**: All PRs reviewed for security
- **Dependency Audits**: Monthly dependency scans
- **Penetration Testing**: Quarterly internal testing
- **Threat Modeling**: Annual threat model updates

### External Security Audits

We welcome external security audits:

- Contact us to coordinate
- Provide audit reports
- Work together on remediation

## Compliance

### Privacy Compliance

RSP is designed with privacy in mind:

- **GDPR**: Zero-retention policy, data minimization
- **CCPA**: Right to deletion (zero-retention)
- **HIPAA**: No PHI storage in default configuration

### Ethical Compliance

RSP adheres to:

- **Responsible AI Principles**: Defense-only, no harm
- **Research Ethics**: Transparent, auditable
- **Security Research Ethics**: Coordinated disclosure

## Security Resources

### Security Tools

**For Users**:
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)

**For Developers**:
- [Bandit](https://bandit.readthedocs.io/) - Python security linter
- [Safety](https://pyup.io/safety/) - Dependency vulnerability scanner
- [pip-audit](https://pypi.org/project/pip-audit/) - Dependency auditor

### Security Training

Recommended training for contributors:

- OWASP Top 10
- Secure Coding Practices
- Threat Modeling
- Incident Response

## Incident Response

### In Case of Security Incident

1. **Contain**: Stop affected systems
2. **Assess**: Determine scope and impact
3. **Notify**: Inform affected users
4. **Remediate**: Deploy fixes
5. **Review**: Post-incident analysis

### User Notification

In case of a security incident affecting users:

- Email notification to registered users
- GitHub security advisory
- Update on website/documentation
- Remediation instructions

## Security Contact

**Primary Contact**: security@[domain].com

**PGP Key**: [Public key for encrypted communications]

**Response Time**: Within 24 hours

---

## Disclaimer

While RSP is designed with security in mind, no software is perfectly secure. Users are responsible for:

- Proper configuration and deployment
- API key security
- Compliance with applicable laws
- Ethical use of the platform

Use RSP responsibly and ethically.

---

**Last Updated**: January 2026

**Version**: 1.0.0
