# Incident Response Playbook

Quick reference guide for responding to production incidents.

## 🚨 Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| Primary On-Call | [Name/Slack/Phone] | 24/7 |
| Secondary On-Call | [Name/Slack/Phone] | 24/7 |
| Engineering Manager | [Name/Slack/Phone] | Business hours |
| Security Team | security@example.com | 24/7 |

## Incident Severity Levels

| Severity | Impact | Examples | Response Time |
|----------|--------|----------|---------------|
| **P1 - Critical** | Service completely down or major data loss | API down, data breach, authentication broken | **Immediate** - Page on-call |
| **P2 - High** | Significant degradation affecting many users | High error rates (>5%), slow response times (>2s) | **15 minutes** - Notify on-call |
| **P3 - Medium** | Partial degradation, workarounds available | Single feature broken, elevated error rates (2-5%) | **1 hour** - Standard ticket |
| **P4 - Low** | Minor issues, cosmetic problems | UI glitches, minor performance issues | **Next business day** - Backlog |

## Quick Response Procedures

### P1: Service Down

**Symptoms**:
- `/api/health` returns 5xx or no response
- No successful requests in last 5 minutes
- Multiple user reports of complete service failure

**Immediate Actions**:
```bash
# 1. Check service status
curl https://api.example.com/api/health

# 2. Check server/container status
# Docker:
docker ps | grep rsp-api
docker logs rsp-api --tail 100

# Systemd:
sudo systemctl status rsp-api
sudo journalctl -u rsp-api -n 100 --no-pager

# 3. Check resource usage
top
df -h
free -m

# 4. Restart service if needed
# Docker:
docker-compose restart rsp-api

# Systemd:
sudo systemctl restart rsp-api

# 5. Monitor recovery
watch -n 1 'curl -s https://api.example.com/api/health | jq'
```

**Communication Template**:
```
🚨 INCIDENT ALERT - P1

Service: RSP API
Status: INVESTIGATING / IDENTIFIED / MONITORING / RESOLVED
Impact: Complete service outage
Started: [Timestamp]
Updates: Every 15 minutes or significant changes

Current Status: [Brief description]
Actions Taken: [Brief description]
Next Update: [Time]

#incident-response
```

### P1: Data Breach

**Immediate Actions**:
```bash
# 1. Isolate affected systems
sudo iptables -A INPUT -j DROP  # Block all incoming
sudo iptables -A OUTPUT -j DROP  # Block all outgoing

# 2. Preserve evidence
tar -czf /backup/forensics_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/log/rsp/ \
  /data/rsp_production.db

# 3. Contact security team
# Email: security@example.com
# Subject: URGENT: Suspected Data Breach

# 4. Begin incident log
echo "$(date -Iseconds): Breach detected. System isolated." >> /var/log/rsp/incident.log
```

**Do NOT**:
- Delete logs or evidence
- Communicate publicly without legal review
- Restart systems before forensic analysis

### P2: High Error Rate

**Symptoms**:
- Error rate > 5%
- `/api/metrics` shows high `error_rate`
- Multiple user reports of errors

**Diagnostic Commands**:
```bash
# 1. Check metrics
curl https://api.example.com/api/metrics | jq

# 2. Check recent errors
grep ERROR /var/log/rsp/api.log | tail -50

# 3. Check upstream services
# OpenAI
curl https://status.openai.com/api/v2/status.json

# Anthropic
curl https://status.anthropic.com/api/v2/status.json

# 4. Check database
sqlite3 /data/rsp_production.db "PRAGMA integrity_check;"

# 5. Check disk space
df -h

# 6. Check memory
free -m
```

**Common Causes and Fixes**:
```bash
# Cause: Out of disk space
# Fix: Clean up old files
find /tmp -mtime +7 -delete
find /var/log/rsp -name "*.log.*" -mtime +30 -delete

# Cause: Database locked
# Fix: Restart service
sudo systemctl restart rsp-api

# Cause: Upstream API down
# Fix: Wait for recovery, consider failover
```

### P2: High Latency

**Symptoms**:
- `/api/metrics` shows `average_duration_ms` > 500ms
- Users report slow performance
- Timeouts

**Diagnostic Commands**:
```bash
# 1. Check current latency
curl -w "@curl-format.txt" -o /dev/null -s https://api.example.com/api/health

# curl-format.txt:
# time_total: %{time_total}\n

# 2. Check system load
uptime
top

# 3. Check database performance
sqlite3 /data/rsp_production.db ".timer on" "SELECT COUNT(*) FROM sessions;"

# 4. Check network
ping -c 5 api.openai.com
traceroute api.openai.com

# 5. Check for rate limiting
curl https://api.example.com/api/metrics | jq .rate_limit_hits
```

**Performance Optimization**:
```bash
# Increase worker count (if CPU available)
# Edit uvicorn command: --workers 8

# Restart with more resources
docker-compose up -d --scale rsp-api=3

# Enable caching (if available)
export RSP_ENABLE_CACHE=true
```

### P3: Single Feature Broken

**Examples**:
- WebSocket connections failing
- Export endpoint returning errors
- Specific model not working

**Diagnostic Approach**:
```bash
# 1. Isolate the issue
# Test specific endpoint
curl -X POST https://api.example.com/api/endpoint -H "Content-Type: application/json" -d '{"test":"data"}'

# 2. Check feature-specific logs
grep "feature_name" /var/log/rsp/api.log | tail -100

# 3. Check dependencies
# For OpenAI issues:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# 4. Test workaround
# Document alternative approach for users
```

## Common Issues and Solutions

### Issue: Authentication Failures

**Symptoms**: 401 errors, "Invalid token" messages

**Checklist**:
```bash
# Check JWT secret is set
env | grep RSP_JWT_SECRET

# Check token expiration
# Decode JWT: https://jwt.io

# Check system time (affects token validation)
date
timedatectl status

# Solution: Ensure RSP_JWT_SECRET is consistent
# Users may need to re-login if secret changed
```

### Issue: Rate Limiting Too Aggressive

**Symptoms**: 429 errors, users reporting blocks

**Checklist**:
```bash
# Check current rate limits
env | grep RSP_RATE_LIMIT

# Check rate limit hits
curl https://api.example.com/api/metrics | jq .rate_limit_hits

# Temporary increase:
export RSP_RATE_LIMIT_PER_MIN=120
export RSP_RATE_LIMIT_PER_HOUR=2000
sudo systemctl restart rsp-api

# Permanent increase: Update .env file
```

### Issue: WebSocket Connection Limit Reached

**Symptoms**: New WebSocket connections rejected, "Server at capacity"

**Checklist**:
```bash
# Check current connections
curl https://api.example.com/api/metrics | jq .websocket_connections

# Check limit
env | grep RSP_MAX_WEBSOCKET_CONNECTIONS

# Increase limit:
export RSP_MAX_WEBSOCKET_CONNECTIONS=200
sudo systemctl restart rsp-api

# Or clean up stale connections by restarting
```

### Issue: Database Locked

**Symptoms**: "Database is locked" errors (SQLite)

**Solution**:
```bash
# Option 1: Restart service (releases locks)
sudo systemctl restart rsp-api

# Option 2: Switch to PostgreSQL for production
# See DEPLOYMENT_GUIDE.md

# Option 3: Check for long-running queries
sudo lsof | grep rsp_production.db
```

### Issue: Out of Memory

**Symptoms**: Service crashes, OOMKilled messages

**Diagnostic**:
```bash
# Check memory usage
free -m
docker stats

# Check OOM kills
dmesg | grep -i oom

# Solution: Increase memory limit
# Docker Compose:
deploy:
  resources:
    limits:
      memory: 8G  # Increase from 4G
```

## Rollback Procedures

### Emergency Rollback (< 5 minutes)

```bash
# 1. Identify working version
docker images rsp-backend
git tag -l

# 2. Rollback
# Docker:
docker-compose down
docker tag rsp-backend:v1.0.0 rsp-backend:latest
docker-compose up -d

# Git:
cd /opt/rsp-core
git checkout v1.0.0
sudo systemctl restart rsp-api

# 3. Verify
curl https://api.example.com/api/health
curl https://api.example.com/api/metrics

# 4. Communicate
# Post in #incident-response:
✅ Rolled back to v1.0.0. Service restored.
```

## Escalation Path

```
Level 1: On-Call Engineer (respond within 15min for P1/P2)
    ↓ (if can't resolve in 30 minutes)
Level 2: Engineering Manager + Senior Engineers
    ↓ (if service impact >1 hour or data breach)
Level 3: CTO + Security Team + Legal (for data breaches)
    ↓ (if major incident >4 hours or customer-facing)
Level 4: CEO + Executive Team
```

## Communication Templates

### Status Update (Every 15-30 minutes)

```
UPDATE: [Timestamp]

Status: INVESTIGATING | IDENTIFIED | MONITORING | RESOLVED
Impact: [Brief description]
Current State: [What's happening now]
Actions Taken: [What we've done]
Next Steps: [What we're doing next]
ETA: [Best estimate or "Unknown"]
Next Update: [Time]
```

### Resolution Notice

```
✅ RESOLVED: [Incident Title]

Duration: [Start time] - [End time] ([Duration])
Impact: [Brief summary]
Root Cause: [Brief explanation]
Resolution: [What fixed it]

Full postmortem will be shared within 5 business days.

Thank you for your patience.
```

### Postmortem Timeline

- **24 hours**: Initial draft
- **3 days**: Team review
- **5 days**: Published
- **Follow-up meeting**: Within 1 week

## Postmortem Template

```markdown
# Incident Postmortem: [Title]

**Date**: [Date]
**Duration**: [Start] - [End] ([Total duration])
**Severity**: P[1-4]
**Responders**: [Names]

## Summary

[2-3 sentence summary of what happened]

## Impact

- Users affected: [Number or "All"]
- Services affected: [List]
- Data lost: [None / Amount]
- Revenue impact: [Amount or N/A]

## Timeline (UTC)

- [Time]: [Event]
- [Time]: [Event]
- [Time]: [Event]

## Root Cause

[Detailed explanation of what caused the incident]

## Resolution

[What fixed the problem]

## Detection

- How detected: [Alert / User report / Monitoring]
- Time to detect: [Duration]
- Could we detect it faster? [Yes/No - explain]

## Prevention

### Immediate Actions (completed)
- [ ] [Action taken]
- [ ] [Action taken]

### Short-term Fixes (this sprint)
- [ ] [Action with owner and date]
- [ ] [Action with owner and date]

### Long-term Improvements (this quarter)
- [ ] [Action with owner and date]
- [ ] [Action with owner and date]

## Lessons Learned

### What Went Well
- [Thing that helped]
- [Thing that helped]

### What Didn't Go Well
- [Problem encountered]
- [Problem encountered]

### Where We Got Lucky
- [Near miss or fortunate circumstance]

## Action Items

| Action | Owner | Due Date | Status |
|--------|-------|----------|--------|
| [Action] | [Name] | [Date] | [ ] |
| [Action] | [Name] | [Date] | [ ] |
```

## Recovery Verification Checklist

After resolving an incident, verify:

- [ ] `/api/health` returns 200
- [ ] `/api/metrics` shows normal values
- [ ] Error rate < 1%
- [ ] Latency < 100ms average
- [ ] No alerts firing
- [ ] Sample API requests succeed
- [ ] WebSocket connections work
- [ ] Authentication works
- [ ] Status page updated
- [ ] Users notified
- [ ] Incident documented

## On-Call Best Practices

### Before Your Shift
- [ ] Test access to all systems
- [ ] Review recent incidents
- [ ] Check monitoring dashboards
- [ ] Verify contact list is current
- [ ] Test alert notifications

### During Your Shift
- [ ] Acknowledge alerts within 5 minutes
- [ ] Update status every 15-30 minutes for active incidents
- [ ] Document actions in incident log
- [ ] Escalate if stuck for >30 minutes
- [ ] Keep team informed

### After Your Shift
- [ ] Hand off any open incidents
- [ ] Update runbook with new learnings
- [ ] Complete postmortem drafts
- [ ] Log any access issues or needed improvements

## Tools and Resources

### Monitoring
- Metrics Dashboard: https://metrics.example.com/rsp
- Logs Dashboard: https://logs.example.com/rsp
- Status Page: https://status.example.com

### Documentation
- Deployment Guide: [DEPLOYMENT_GUIDE.md](../deployment/DEPLOYMENT_GUIDE.md)
- Monitoring Guide: [MONITORING_GUIDE.md](MONITORING_GUIDE.md)
- Architecture Docs: [Project README](../../README.md)

### Communication
- Incident Channel: #incident-response
- Status Updates: #status-updates
- Team Chat: #rsp-team

---

**Remember**: 
- Stay calm
- Communicate clearly and often
- Document everything
- Ask for help when needed
- Learn from every incident

Last Updated: January 2026
