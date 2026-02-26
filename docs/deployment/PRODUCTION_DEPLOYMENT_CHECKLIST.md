# Production Deployment Checklist

Use this checklist before deploying Red Set ProtoCell to production.

## ✅ Pre-Deployment Checklist

### Security Configuration

- [ ] **Environment Variables Set**
  - [ ] `RSP_ENVIRONMENT=production`
  - [ ] `RSP_ALLOWED_ORIGINS` configured with actual domain(s)
  - [ ] `RSP_JWT_SECRET` generated and set (min 32 characters)
  - [ ] `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` set
  - [ ] `RSP_DEMO_PASSWORD` changed from default
  - [ ] All secrets stored in environment variables or secrets manager

- [ ] **Secrets Never Committed**
  - [ ] `.env` file in `.gitignore`
  - [ ] No API keys in source code
  - [ ] No passwords in configuration files
  - [ ] Run: `git log --all --full-history -- "*env*" | grep -i "key\|password\|secret"`

- [ ] **HTTPS Enabled**
  - [ ] SSL/TLS certificates installed
  - [ ] HTTP redirects to HTTPS
  - [ ] HSTS header enabled (automatic with middleware)
  - [ ] Test: `curl -I https://your-domain.com | grep -i strict-transport`

- [ ] **CORS Configured**
  - [ ] `RSP_ALLOWED_ORIGINS` set to specific domains
  - [ ] No wildcards (`*`) in production
  - [ ] Test with browser dev tools

- [ ] **Authentication Enabled**
  - [ ] `RSP_REQUIRE_AUTH=true`
  - [ ] JWT secret is strong and unique
  - [ ] Default admin password changed
  - [ ] Test login flow

- [ ] **Rate Limiting Configured**
  - [ ] `RSP_RATE_LIMIT_PER_MIN` set appropriately
  - [ ] `RSP_RATE_LIMIT_PER_HOUR` set appropriately
  - [ ] Test with load testing tool

### Infrastructure

- [ ] **Database**
  - [ ] PostgreSQL configured for production (recommended over SQLite)
  - [ ] Connection string set and tested
  - [ ] Database backups configured
  - [ ] Test connection: `psql $RSP_POSTGRES_URI -c "SELECT 1"`

- [ ] **Resources**
  - [ ] Sufficient CPU allocated (2+ cores recommended)
  - [ ] Sufficient RAM allocated (4GB+ recommended)
  - [ ] Disk space adequate for logs and sessions
  - [ ] Check: `top`, `free -m`, `df -h`

- [ ] **Networking**
  - [ ] Firewall rules configured
  - [ ] Load balancer configured (if applicable)
  - [ ] DNS records set
  - [ ] Test: `nslookup your-domain.com`

- [ ] **Monitoring**
  - [ ] Health check endpoint accessible
  - [ ] Metrics endpoint accessible (internal only)
  - [ ] Log aggregation configured
  - [ ] Alerts configured

### Code Quality

- [ ] **Tests Passing**
  - [ ] All unit tests pass: `pytest tests/`
  - [ ] Integration tests pass (if applicable)
  - [ ] No known critical bugs
  - [ ] Code coverage ≥ 70%

- [ ] **Security Scans**
  - [ ] CodeQL scan passed
  - [ ] Dependency vulnerability scan: `safety check`
  - [ ] No high/critical vulnerabilities
  - [ ] `pip-audit -r requirements.txt`

- [ ] **Code Quality**
  - [ ] Linting passed: `flake8 app/`
  - [ ] Type checking passed: `mypy app/` (best effort)
  - [ ] Code formatted: `black app/`

### Deployment

- [ ] **Hardened Compose Path Verified**
  - [ ] `docker compose -f docker-compose.production.yml config` succeeds
  - [ ] Required env vars validated before deploy

- [ ] **Deployment Method**
  - [ ] Docker image built and tested
  - [ ] OR: Systemd service configured
  - [ ] OR: Cloud platform configured
  - [ ] Deployment scripts tested

- [ ] **Rollback Plan**
  - [ ] Previous version tagged
  - [ ] Rollback procedure documented
  - [ ] Rollback tested in staging
  - [ ] Estimated rollback time < 5 minutes

- [ ] **Zero-Downtime**
  - [ ] Blue-green deployment OR rolling update
  - [ ] Health checks configured
  - [ ] Graceful shutdown implemented

### Documentation

- [ ] **Deployment Docs**
  - [ ] [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) reviewed
  - [ ] Environment-specific docs created
  - [ ] Runbook updated

- [ ] **Monitoring Docs**
  - [ ] [MONITORING_GUIDE.md](../guides/MONITORING_GUIDE.md) reviewed
  - [ ] Alert thresholds documented
  - [ ] Dashboard URLs documented

- [ ] **Incident Response**
  - [ ] [INCIDENT_RESPONSE.md](../guides/INCIDENT_RESPONSE.md) reviewed
  - [ ] On-call schedule created
  - [ ] Emergency contacts updated

### Testing

- [ ] **Smoke Tests**
  - [ ] Health checks: `curl https://api.your-domain.com/health` and `curl https://api.your-domain.com/api/health`
  - [ ] Login works
  - [ ] Session start works
  - [ ] Metrics endpoint works (internal)

- [ ] **Load Testing**
  - [ ] Basic load test completed
  - [ ] Performance acceptable under load
  - [ ] No memory leaks detected
  - [ ] Example: `hey -n 1000 -c 10 https://api.your-domain.com/api/health`
  - [ ] Baseline script pass: `python scripts/load_test_baseline.py --base-url https://api.your-domain.com --requests 200 --concurrency 20`

- [ ] **Security Testing**
  - [ ] Penetration test completed (if required)
  - [ ] OWASP Top 10 considered
  - [ ] Rate limiting tested
  - [ ] Authentication tested

## 🚀 Deployment Day Checklist

### Before Deployment

- [ ] **Communication**
  - [ ] Stakeholders notified of deployment window
  - [ ] Status page updated (if applicable)
  - [ ] Support team briefed

- [ ] **Backups**
  - [ ] Database backed up
  - [ ] Configuration backed up
  - [ ] Previous version tagged in Git

- [ ] **Staging Validation**
  - [ ] Deployed to staging
  - [ ] All tests passed in staging
  - [ ] Manual testing completed in staging

### During Deployment

- [ ] **Pre-Deploy**
  - [ ] Verify current system health
  - [ ] Note current metrics (latency, error rate)
  - [ ] Start incident tracker (if using)

- [ ] **Deploy**
  - [ ] Follow deployment procedure
  - [ ] Monitor health checks
  - [ ] Watch error logs
  - [ ] Monitor metrics

- [ ] **Post-Deploy Validation**
  - [ ] Health check returns 200
  - [ ] Metrics look normal
  - [ ] Sample requests succeed
  - [ ] Authentication works
  - [ ] No elevated error rates

### After Deployment

- [ ] **Monitoring**
  - [ ] Monitor for 30 minutes minimum
  - [ ] Check error rates
  - [ ] Check latency
  - [ ] Check memory/CPU usage

- [ ] **Communication**
  - [ ] Announce deployment complete
  - [ ] Update status page
  - [ ] Document any issues

- [ ] **Documentation**
  - [ ] Update deployment log
  - [ ] Note any deviations from plan
  - [ ] Update runbook if needed

## 🔄 Regular Maintenance Checklist

### Daily

- [ ] Check error logs
- [ ] Review metrics dashboard
- [ ] Verify backups ran successfully
- [ ] Check for alerts

### Weekly

- [ ] Review SLO compliance
- [ ] Check for dependency updates
- [ ] Review access logs for anomalies
- [ ] Disk space check

### Monthly

- [ ] Security updates applied
- [ ] Dependency updates reviewed and applied
- [ ] Certificate expiration check (if applicable)
- [ ] Access audit (review who has access)
- [ ] Cost review

### Quarterly

- [ ] Full security audit
- [ ] Disaster recovery test
- [ ] Performance review
- [ ] Capacity planning
- [ ] Documentation review

## 📋 Rollback Checklist

If deployment fails:

- [ ] **Assess Impact**
  - [ ] What's broken?
  - [ ] How many users affected?
  - [ ] Data loss?

- [ ] **Communicate**
  - [ ] Notify stakeholders
  - [ ] Update status page
  - [ ] Estimate fix time OR rollback

- [ ] **Rollback Decision**
  - [ ] Can it be fixed quickly (< 15 min)?
  - [ ] If NO, rollback
  - [ ] If YES, fix forward

- [ ] **Execute Rollback**
  - [ ] Follow [DEPLOYMENT_GUIDE.md#rollback-procedures](DEPLOYMENT_GUIDE.md#rollback-procedures)
  - [ ] Verify old version works
  - [ ] Monitor metrics
  - [ ] Confirm rollback successful

- [ ] **Post-Rollback**
  - [ ] Communicate completion
  - [ ] Schedule postmortem
  - [ ] Fix issue before retry

## 🎯 Production Readiness Score

Calculate your score:

| Category | Items | Completed | Score |
|----------|-------|-----------|-------|
| Security | 20 | ___ | __% |
| Infrastructure | 10 | ___ | __% |
| Code Quality | 7 | ___ | __% |
| Deployment | 8 | ___ | __% |
| Documentation | 6 | ___ | __% |
| Testing | 8 | ___ | __% |
| **Total** | **59** | **___** | **___%** |

**Recommendation**:
- **100%**: ✅ Ready for production
- **90-99%**: ✅ Ready with minor items
- **80-89%**: ⚠️ Ready with caution
- **< 80%**: ❌ Not ready for production

## 📚 Reference Documents

Before deploying, review:

1. [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment procedures
2. [MONITORING_GUIDE.md](../guides/MONITORING_GUIDE.md) - Monitoring setup
3. [INCIDENT_RESPONSE.md](../guides/INCIDENT_RESPONSE.md) - Incident procedures
4. [SECURITY.md](../../SECURITY.md) - Security practices
5. [SLO_DOCUMENTATION.md](../archive/SLO_DOCUMENTATION.md) - SLO framework
6. [API_DOCUMENTATION.md](../guides/API_DOCUMENTATION.md) - API reference
7. [COMPLIANCE_GUIDE.md](../guides/COMPLIANCE_GUIDE.md) - Privacy & compliance

## 🆘 Emergency Contacts

| Role | Contact | When to Use |
|------|---------|-------------|
| On-Call Engineer | _______________ | Service issues |
| Security Team | security@___.com | Security incidents |
| DevOps Team | devops@___.com | Infrastructure issues |
| Manager | _______________ | Escalation needed |

## 📝 Deployment Log Template

Keep a record of each deployment:

```markdown
# Deployment Log: [Date/Time]

**Version**: v1.x.x → v1.y.y
**Deployer**: [Name]
**Environment**: Production

## Pre-Deployment
- Checklist completed: ✅
- Backups taken: ✅
- Stakeholders notified: ✅

## Deployment
- Started: [Time]
- Completed: [Time]
- Duration: [Minutes]
- Method: [Docker/Systemd/Cloud]

## Post-Deployment
- Health checks: ✅
- Smoke tests: ✅
- Monitoring: ✅

## Issues
[None / List any issues encountered]

## Rollback
[N/A / Rolled back at [Time] due to [Reason]]

## Notes
[Any additional notes or observations]
```

---

**Remember**: It's better to delay a deployment than to deploy unprepared!

Last Updated: January 2026
Version: 1.0.0
