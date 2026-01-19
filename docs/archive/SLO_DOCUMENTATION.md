# Service Level Objectives (SLOs) and SLIs

This document defines the Service Level Indicators (SLIs), Service Level Objectives (SLOs), and Service Level Agreements (SLAs) for Red Set ProtoCell.

## Table of Contents

- [Overview](#overview)
- [Service Level Indicators (SLIs)](#service-level-indicators-slis)
- [Service Level Objectives (SLOs)](#service-level-objectives-slos)
- [Service Level Agreements (SLAs)](#service-level-agreements-slas)
- [Error Budgets](#error-budgets)
- [Measurement and Reporting](#measurement-and-reporting)

## Overview

### Definitions

- **SLI (Service Level Indicator)**: A quantitative measure of service behavior
- **SLO (Service Level Objective)**: Target value or range for an SLI
- **SLA (Service Level Agreement)**: Contract with consequences if SLO is not met

### Philosophy

- **User-centric**: SLIs measure what users experience
- **Achievable**: SLOs are ambitious but realistic
- **Actionable**: Breaches trigger specific responses
- **Balanced**: Not so strict that innovation is impossible

## Service Level Indicators (SLIs)

### 1. Availability

**Definition**: Percentage of successful requests

**Measurement**:
```
Availability = (Successful Requests / Total Requests) × 100%
```

**Success Criteria**:
- HTTP status code 2xx or 3xx
- Response received within timeout (30s)

**Failure Criteria**:
- HTTP status code 5xx
- Timeout (no response in 30s)
- Connection refused

**Data Source**: `/api/metrics` endpoint
```json
{
  "requests_total": 10000,
  "requests_by_status": {
    "200": 9950,
    "400": 20,
    "401": 10,
    "500": 20
  }
}
```

**Calculation**:
```
Success = 200 codes = 9950
Total = 10000
Availability = (9950 / 10000) × 100% = 99.5%
```

### 2. Latency

**Definition**: Time taken to process requests

**Measurements**:
- **P50 Latency**: 50th percentile (median)
- **P95 Latency**: 95th percentile
- **P99 Latency**: 99th percentile

**Data Source**: Request timing logs
```json
{
  "average_duration_ms": 85.5,
  "latency_percentiles": {
    "p50": 65,
    "p95": 450,
    "p99": 980
  }
}
```

### 3. Error Rate

**Definition**: Percentage of requests that result in errors

**Measurement**:
```
Error Rate = (5xx Responses / Total Requests) × 100%
```

**Exclusions**:
- 4xx errors (client errors, not service problems)
- Rate-limited requests (429)

**Data Source**: `/api/metrics`
```json
{
  "error_rate": 0.002  // 0.2%
}
```

### 4. Throughput

**Definition**: Requests processed per second

**Measurement**:
```
Throughput = Total Requests / Time Period (seconds)
```

**Data Source**: Metrics over time window
```json
{
  "requests_per_second": 45.2,
  "period": "last_5_minutes"
}
```

## Service Level Objectives (SLOs)

### Production SLOs

| SLI | Target | Measurement Window | Consequences if Breached |
|-----|--------|-------------------|-------------------------|
| **Availability** | ≥ 99.9% | Rolling 30 days | Incident review, capacity planning |
| **Latency (P50)** | < 100ms | Rolling 7 days | Performance investigation |
| **Latency (P95)** | < 500ms | Rolling 7 days | Optimization required |
| **Latency (P99)** | < 1000ms | Rolling 7 days | Accept or investigate |
| **Error Rate** | < 0.1% | Rolling 24 hours | Incident investigation |

### Development/Staging SLOs

| SLI | Target | Measurement Window |
|-----|--------|-------------------|
| **Availability** | ≥ 95% | Rolling 7 days |
| **Latency (P95)** | < 1000ms | Rolling 7 days |
| **Error Rate** | < 1% | Rolling 24 hours |

### Critical Endpoints

Higher standards for critical paths:

| Endpoint | Availability | Latency (P95) | Error Rate |
|----------|-------------|---------------|------------|
| `/api/health` | ≥ 99.99% | < 10ms | < 0.01% |
| `/api/session/start` | ≥ 99.9% | < 200ms | < 0.1% |
| `/api/session/stop` | ≥ 99.9% | < 100ms | < 0.1% |
| `/api/metrics` | ≥ 99.9% | < 50ms | < 0.1% |

### Dependency SLOs

Understanding upstream dependencies:

| Service | Our Dependency | Their Published SLO |
|---------|---------------|-------------------|
| OpenAI API | Critical | 99.9% availability |
| Anthropic API | Critical | 99.9% availability |
| PostgreSQL | Critical | 99.95% availability (self-managed) |
| Monitoring | Important | 99.5% availability |

**Dependency Math**:
```
Our Target: 99.9%
Dependencies: OpenAI (99.9%) × Database (99.95%) = 99.85%
Result: Achievable, with 0.05% buffer
```

## Service Level Agreements (SLAs)

### Free Tier / Internal Use

**Availability**: 99% monthly uptime (best effort)
- Up to 7.2 hours downtime per month
- No financial compensation

**Support**: Best effort, email only
- Response time: 2 business days

### Standard Tier (Example)

**Availability**: 99.9% monthly uptime
- Up to 43 minutes downtime per month
- **Credit**: 10% monthly fee if breached

**Latency**: P95 < 500ms
- **Credit**: 5% monthly fee if breached

**Support**: Email and chat
- Response time: 4 business hours

### Premium Tier (Example)

**Availability**: 99.95% monthly uptime
- Up to 21 minutes downtime per month
- **Credit**: 25% monthly fee if breached

**Latency**: P95 < 200ms
- **Credit**: 10% monthly fee if breached

**Error Rate**: < 0.05%
- **Credit**: 10% monthly fee if breached

**Support**: 24/7 phone and email
- Response time: 1 hour for P1, 4 hours for P2

### SLA Credits Calculation

```python
# Example credit calculation
def calculate_sla_credit(uptime_percent: float, tier: str) -> float:
    """Calculate SLA credit percentage."""
    
    if tier == "free":
        return 0.0  # No credits for free tier
    
    if tier == "standard":
        if uptime_percent < 99.0:
            return 25.0  # 25% credit
        elif uptime_percent < 99.9:
            return 10.0  # 10% credit
        return 0.0
    
    if tier == "premium":
        if uptime_percent < 99.0:
            return 50.0  # 50% credit
        elif uptime_percent < 99.5:
            return 25.0  # 25% credit
        elif uptime_percent < 99.95:
            return 10.0  # 10% credit
        return 0.0
    
    return 0.0
```

## Error Budgets

### Concept

Error budget = (100% - SLO)

**Example**:
- SLO: 99.9% availability
- Error budget: 0.1% = 43.2 minutes per month

### Using Error Budgets

**When budget is healthy (> 50% remaining)**:
- ✅ Deploy new features
- ✅ Experiment with optimizations
- ✅ Conduct chaos engineering tests
- ✅ Scheduled maintenance

**When budget is low (< 20% remaining)**:
- ⚠️ Freeze non-critical deploys
- ⚠️ Focus on stability
- ⚠️ Defer risky changes
- ⚠️ Increase monitoring

**When budget is exhausted (0% remaining)**:
- 🚫 Feature freeze
- 🚫 Only deploy fixes
- 🚫 Incident review required
- 🚫 Postmortem mandatory

### Error Budget Calculation

```python
from datetime import datetime, timedelta

def calculate_error_budget(
    slo_target: float,  # e.g., 0.999 for 99.9%
    actual_uptime: float,  # e.g., 0.9985 for 99.85%
    time_window_days: int = 30
) -> dict:
    """Calculate error budget metrics."""
    
    # Calculate allowed downtime
    time_window_seconds = time_window_days * 24 * 60 * 60
    allowed_downtime = time_window_seconds * (1 - slo_target)
    
    # Calculate actual downtime
    actual_downtime = time_window_seconds * (1 - actual_uptime)
    
    # Calculate remaining budget
    remaining_budget = allowed_downtime - actual_downtime
    budget_percent = (remaining_budget / allowed_downtime) * 100
    
    return {
        "slo_target": f"{slo_target * 100:.2f}%",
        "actual_uptime": f"{actual_uptime * 100:.2f}%",
        "allowed_downtime_minutes": allowed_downtime / 60,
        "actual_downtime_minutes": actual_downtime / 60,
        "remaining_budget_minutes": remaining_budget / 60,
        "budget_remaining_percent": budget_percent,
        "status": "healthy" if budget_percent > 50 else 
                 "warning" if budget_percent > 20 else 
                 "critical" if budget_percent > 0 else 
                 "exhausted"
    }

# Example
result = calculate_error_budget(
    slo_target=0.999,      # 99.9% SLO
    actual_uptime=0.9985,  # 99.85% actual
    time_window_days=30
)
print(result)
# {
#     "slo_target": "99.90%",
#     "actual_uptime": "99.85%",
#     "allowed_downtime_minutes": 43.2,
#     "actual_downtime_minutes": 64.8,
#     "remaining_budget_minutes": -21.6,
#     "budget_remaining_percent": -50.0,
#     "status": "exhausted"
# }
```

## Measurement and Reporting

### Data Collection

```python
# Collect SLI data from metrics endpoint
import requests
from datetime import datetime, timedelta

def collect_sli_data(api_url: str) -> dict:
    """Collect current SLI metrics."""
    
    response = requests.get(f"{api_url}/api/metrics")
    data = response.json()
    
    # Calculate availability
    total = data["requests_total"]
    errors = data["errors_total"]
    availability = ((total - errors) / total * 100) if total > 0 else 100
    
    # Extract error rate
    error_rate = data["error_rate"] * 100  # Convert to percentage
    
    # Extract latency
    latency = data["average_duration_ms"]
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "availability_percent": availability,
        "error_rate_percent": error_rate,
        "latency_ms": latency,
        "requests_total": total,
    }
```

### Reporting Dashboard

Key metrics to display:

```python
# Dashboard data structure
dashboard = {
    "current_status": {
        "availability": "99.95%",  # Green/Yellow/Red
        "latency_p95": "320ms",    # Green/Yellow/Red
        "error_rate": "0.05%",     # Green/Yellow/Red
    },
    "slo_compliance": {
        "availability": {
            "target": "99.9%",
            "actual": "99.95%",
            "status": "meeting",  # meeting/at-risk/breached
        },
        "latency_p95": {
            "target": "500ms",
            "actual": "320ms",
            "status": "meeting",
        },
        "error_rate": {
            "target": "0.1%",
            "actual": "0.05%",
            "status": "meeting",
        }
    },
    "error_budget": {
        "availability": {
            "allowed_downtime_minutes": 43.2,
            "consumed_downtime_minutes": 11.5,
            "remaining_minutes": 31.7,
            "remaining_percent": 73.4,
            "status": "healthy",  # healthy/warning/critical/exhausted
        }
    },
    "historical_trends": {
        "last_7_days": {
            "availability_avg": 99.94,
            "latency_p95_avg": 340,
            "error_rate_avg": 0.06,
        },
        "last_30_days": {
            "availability_avg": 99.92,
            "latency_p95_avg": 380,
            "error_rate_avg": 0.08,
        }
    }
}
```

### Weekly SLO Report Template

```markdown
# SLO Report: Week of [Date]

## Executive Summary
- ✅ All SLOs met / ⚠️ [N] SLOs at risk / ❌ [N] SLOs breached
- Error budget health: [Healthy/Warning/Critical]
- Action required: [Yes/No - describe if yes]

## Availability
- **Target**: 99.9%
- **Actual**: 99.95%
- **Status**: ✅ Meeting SLO
- **Error Budget Remaining**: 73% (31.7 minutes)

## Latency
- **P50 Target**: < 100ms
- **P50 Actual**: 65ms
- **P95 Target**: < 500ms
- **P95 Actual**: 320ms
- **P99 Target**: < 1000ms
- **P99 Actual**: 890ms
- **Status**: ✅ All targets met

## Error Rate
- **Target**: < 0.1%
- **Actual**: 0.05%
- **Status**: ✅ Meeting SLO

## Incidents
- Total incidents: [N]
- P1/P2 incidents: [N]
- Total downtime: [N] minutes
- Impact on error budget: [N%]

## Trends
- Availability: [Improving/Stable/Degrading]
- Latency: [Improving/Stable/Degrading]
- Error rate: [Improving/Stable/Degrading]

## Action Items
1. [Action item with owner and date]
2. [Action item with owner and date]

## Next Week Focus
- [Priority area]
- [Priority area]
```

### Monthly SLO Review

Conduct monthly reviews:
1. **Assess SLO compliance**: Did we meet our targets?
2. **Review error budget**: How much was consumed?
3. **Analyze trends**: Are metrics improving or degrading?
4. **Adjust SLOs**: Are targets too strict or too lenient?
5. **Plan improvements**: What can we do better?

### Alerting on SLO Breaches

```yaml
# Prometheus alert rules
groups:
  - name: slo_alerts
    rules:
      - alert: AvailabilitySLOAtRisk
        expr: |
          (
            sum(rate(requests_total[30d]))
            - sum(rate(requests_errors[30d]))
          ) / sum(rate(requests_total[30d])) < 0.999
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Availability SLO at risk"
          description: "30-day availability is {{ $value }}% (target: 99.9%)"
      
      - alert: ErrorBudgetExhausted
        expr: |
          (1 - (sum(rate(requests_errors[30d])) / sum(rate(requests_total[30d])))) < 0.999
        labels:
          severity: critical
        annotations:
          summary: "Error budget exhausted"
          description: "Implement feature freeze until budget recovers"
```

## Best Practices

### 1. Start Simple
- Begin with 3-5 key SLIs
- Set achievable SLOs based on current performance
- Iterate and refine over time

### 2. User-Centric
- SLIs should reflect user experience
- Measure what users care about
- Ignore irrelevant metrics

### 3. Make it Visible
- Dashboard accessible to all teams
- Weekly reports
- Real-time status page

### 4. Use Error Budgets
- Balance innovation and reliability
- Make deployment decisions based on budget
- Review budget in every planning meeting

### 5. Review Regularly
- Weekly: Check current status
- Monthly: Review trends and adjust
- Quarterly: Major SLO review and update

### 6. Act on Breaches
- Every breach triggers a review
- Understand root cause
- Implement preventive measures

## Tools and Automation

### Recommended Tools
- **Metrics**: Prometheus + Grafana
- **Alerting**: Alertmanager
- **Incident Management**: PagerDuty, Opsgenie
- **Reporting**: Custom scripts or SLO tracking tools

### Automation
- Automatic SLO compliance calculation
- Weekly report generation
- Error budget tracking
- Alert escalation

---

Last Updated: January 2026
Version: 1.0.0

**Remember**: SLOs are not about perfection. They're about finding the right balance between reliability and velocity.
