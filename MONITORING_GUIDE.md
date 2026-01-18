# Monitoring and Observability Guide

This guide covers monitoring, logging, and observability for Red Set ProtoCell in production.

## Table of Contents

- [Overview](#overview)
- [Health Checks](#health-checks)
- [Metrics Collection](#metrics-collection)
- [Logging](#logging)
- [Alerting](#alerting)
- [Error Tracking](#error-tracking)
- [Dashboards](#dashboards)
- [Best Practices](#best-practices)

## Overview

RSP provides production-ready observability features:

- **Health Checks**: Liveness and readiness probes
- **Metrics**: Prometheus-compatible operational metrics
- **Structured Logging**: JSON-formatted logs for easy parsing
- **Request Tracing**: Request IDs and timing information
- **Error Tracking**: Integration points for Sentry/Rollbar/etc.

## Health Checks

### Endpoints

#### Basic Health Check
```bash
GET /api/health
```

**Purpose**: Fast check for load balancers and monitoring  
**Response Time**: < 10ms  
**Use For**: Kubernetes liveness probes, load balancer health checks

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T05:00:00Z",
  "active_sessions": 5,
  "websocket_connections": 12
}
```

#### Detailed Health Check
```bash
GET /api/health/detailed
```

**Purpose**: Comprehensive system status  
**Response Time**: < 100ms  
**Use For**: Monitoring dashboards, diagnostics

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-18T05:00:00Z",
  "active_sessions": 5,
  "websocket_connections": 12,
  "environment": "production",
  "checks": {
    "database": {
      "status": "pass",
      "details": true
    },
    "api_clients": {
      "status": "pass",
      "details": true
    }
  }
}
```

### Health Check Configuration

#### Kubernetes Liveness Probe
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

#### Kubernetes Readiness Probe
```yaml
readinessProbe:
  httpGet:
    path: /api/health/detailed
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

#### AWS Application Load Balancer
```bash
# Target Group Health Check
Protocol: HTTP
Path: /api/health
Interval: 30 seconds
Timeout: 5 seconds
Healthy threshold: 2
Unhealthy threshold: 3
```

## Metrics Collection

### Metrics Endpoint

```bash
GET /api/metrics
```

**Response**:
```json
{
  "requests_total": 15234,
  "requests_by_status": {
    "200": 14890,
    "400": 120,
    "401": 50,
    "429": 100,
    "500": 74
  },
  "requests_by_endpoint": {
    "/api/session/start": 450,
    "/api/health": 13500,
    "/api/metrics": 234
  },
  "total_duration_ms": 456789.5,
  "average_duration_ms": 29.97,
  "errors_total": 74,
  "error_rate": 0.0049,
  "rate_limit_hits": 100,
  "active_sessions": 5,
  "websocket_connections": 12,
  "timestamp": "2026-01-18T05:00:00Z"
}
```

### Key Metrics (SLIs)

#### Availability Metrics
- **requests_total**: Total number of requests processed
- **error_rate**: Percentage of failed requests (target: < 0.01)
- **requests_by_status**: HTTP status code distribution

#### Performance Metrics
- **average_duration_ms**: Average request latency (target: < 100ms)
- **requests_by_endpoint**: Performance per endpoint
- **total_duration_ms**: Cumulative processing time

#### Capacity Metrics
- **rate_limit_hits**: Number of rate-limited requests
- **active_sessions**: Current active red team sessions
- **websocket_connections**: Active WebSocket connections

### Prometheus Integration

#### Prometheus Configuration

```yaml
# prometheus.yml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'rsp-api'
    scrape_interval: 15s
    metrics_path: '/api/metrics'
    static_configs:
      - targets: ['rsp-api:8000']
        labels:
          environment: 'production'
          service: 'rsp-backend'
```

#### Prometheus Alerts

```yaml
# alerts.yml
groups:
  - name: rsp_api_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: error_rate > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }}% (threshold: 5%)"
      
      - alert: HighLatency
        expr: average_duration_ms > 500
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          description: "Average latency is {{ $value }}ms (threshold: 500ms)"
      
      - alert: ServiceDown
        expr: up{job="rsp-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "RSP API service is down"
          description: "The RSP API service has been down for 1 minute"
```

### Grafana Dashboard

#### Import Dashboard JSON

```json
{
  "dashboard": {
    "title": "RSP API Monitoring",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(requests_total[5m])"
          }
        ]
      },
      {
        "title": "Error Rate",
        "targets": [
          {
            "expr": "error_rate"
          }
        ]
      },
      {
        "title": "Average Latency",
        "targets": [
          {
            "expr": "average_duration_ms"
          }
        ]
      },
      {
        "title": "Active Sessions",
        "targets": [
          {
            "expr": "active_sessions"
          }
        ]
      }
    ]
  }
}
```

## Logging

### Log Format

RSP outputs structured JSON logs:

```json
{
  "timestamp": "2026-01-18T05:00:00.123456Z",
  "level": "INFO",
  "logger": "rsp.api.requests",
  "message": "Request completed",
  "request_id": "req_1705554000123",
  "method": "POST",
  "path": "/api/session/start",
  "status_code": 200,
  "duration_ms": 45.67,
  "client_ip": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

### Log Levels

- **DEBUG**: Detailed information for diagnosing issues (development only)
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for potentially problematic situations
- **ERROR**: Error messages for failures

### Log Configuration

```bash
# Set log level via environment variable
RSP_LOG_LEVEL=INFO

# Set log file (optional, defaults to stdout)
RSP_LOG_FILE=/var/log/rsp/api.log
```

### Log Aggregation

#### Filebeat Configuration

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/rsp/*.log
    json.keys_under_root: true
    json.add_error_key: true
    fields:
      service: rsp-api
      environment: production

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
  index: "rsp-logs-%{+yyyy.MM.dd}"

processors:
  - add_host_metadata: ~
  - add_cloud_metadata: ~
```

#### Fluentd Configuration

```conf
<source>
  @type tail
  path /var/log/rsp/*.log
  pos_file /var/log/td-agent/rsp.log.pos
  tag rsp.api
  format json
  time_format %Y-%m-%dT%H:%M:%S.%NZ
</source>

<match rsp.api>
  @type elasticsearch
  host elasticsearch
  port 9200
  logstash_format true
  logstash_prefix rsp-logs
</match>
```

### Log Analysis Queries

#### Elasticsearch/Kibana

```json
// Find errors in last hour
{
  "query": {
    "bool": {
      "must": [
        {"term": {"level": "ERROR"}},
        {"range": {"timestamp": {"gte": "now-1h"}}}
      ]
    }
  }
}

// Find slow requests (>500ms)
{
  "query": {
    "bool": {
      "must": [
        {"range": {"duration_ms": {"gte": 500}}}
      ]
    }
  }
}

// Find rate limit hits
{
  "query": {
    "bool": {
      "must": [
        {"term": {"status_code": 429}}
      ]
    }
  }
}
```

## Alerting

### Alert Channels

#### Email Alerts

```yaml
# alertmanager.yml
receivers:
  - name: 'email'
    email_configs:
      - to: 'ops-team@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'password'
```

#### Slack Alerts

```yaml
receivers:
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL'
        channel: '#alerts'
        title: 'RSP API Alert'
        text: '{{ .CommonAnnotations.summary }}'
```

#### PagerDuty Alerts

```yaml
receivers:
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'YOUR_SERVICE_KEY'
        severity: '{{ .CommonLabels.severity }}'
```

### Alert Rules

#### Critical Alerts (Immediate Response)

```yaml
# Service completely down
- alert: ServiceDown
  expr: up{job="rsp-api"} == 0
  for: 1m
  severity: critical

# High error rate (>5%)
- alert: HighErrorRate
  expr: error_rate > 0.05
  for: 5m
  severity: critical

# No capacity for new connections
- alert: NoCapacity
  expr: websocket_connections >= 95
  for: 2m
  severity: critical
```

#### Warning Alerts (Monitor Closely)

```yaml
# Elevated error rate (2-5%)
- alert: ElevatedErrorRate
  expr: error_rate > 0.02 and error_rate <= 0.05
  for: 10m
  severity: warning

# High latency (>500ms average)
- alert: HighLatency
  expr: average_duration_ms > 500
  for: 5m
  severity: warning

# Many rate limit hits
- alert: HighRateLimitHits
  expr: rate(rate_limit_hits[5m]) > 10
  for: 5m
  severity: warning
```

#### Info Alerts (Awareness)

```yaml
# Unusual traffic spike
- alert: TrafficSpike
  expr: rate(requests_total[5m]) > 100
  for: 10m
  severity: info

# Many active sessions
- alert: ManyActiveSessions
  expr: active_sessions > 50
  for: 15m
  severity: info
```

## Error Tracking

### Sentry Integration

#### Setup

```bash
# Install Sentry SDK
pip install sentry-sdk[fastapi]
```

#### Configuration

```python
# Add to app/api_server.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

if os.getenv("RSP_ENVIRONMENT") == "production":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        traces_sample_rate=0.1,  # 10% of transactions
        environment="production",
        release=f"rsp-backend@{VERSION}",
    )
```

#### Environment Variables

```bash
SENTRY_DSN=https://your-key@sentry.io/project-id
```

### Rollbar Integration

```bash
pip install rollbar
```

```python
import rollbar

rollbar.init(
    access_token=os.getenv("ROLLBAR_TOKEN"),
    environment="production",
)
```

## Dashboards

### Recommended Metrics to Display

#### Operations Dashboard

1. **Availability**
   - Uptime percentage (target: 99.9%)
   - Error rate (target: < 1%)
   - Request success rate

2. **Performance**
   - Average latency (target: < 100ms)
   - 95th percentile latency (target: < 500ms)
   - 99th percentile latency (target: < 1000ms)

3. **Capacity**
   - Active sessions
   - WebSocket connections
   - Rate limit utilization

4. **Traffic**
   - Requests per minute
   - Requests by endpoint
   - Requests by status code

#### Business Dashboard

1. **Usage Metrics**
   - Total sessions started
   - Average session duration
   - Total API calls

2. **User Activity**
   - Active users
   - API key usage
   - Authentication attempts

3. **Resource Consumption**
   - Database size
   - Storage usage
   - Bandwidth usage

## Best Practices

### 1. Monitor What Matters

Focus on metrics that indicate user impact:
- **Latency**: Response time affects user experience
- **Error Rate**: Directly impacts reliability
- **Availability**: Core SLA metric

### 2. Set Appropriate Thresholds

```yaml
# Good thresholds based on SLOs
error_rate: < 1%        # 99% success rate
latency_p95: < 500ms    # Fast for 95% of requests
latency_p99: < 1000ms   # Acceptable for 99%
uptime: > 99.9%         # Maximum 43 minutes downtime/month
```

### 3. Alert on Symptoms, Not Causes

❌ Bad: Alert on high CPU usage  
✅ Good: Alert on high latency (symptom)

### 4. Avoid Alert Fatigue

- Start with fewer, high-confidence alerts
- Tune thresholds based on actual data
- Use "for" clauses to avoid flapping
- Set appropriate severity levels

### 5. Regular Review

- Weekly: Review error logs
- Monthly: Review alert thresholds
- Quarterly: Update runbooks
- Annually: Review SLOs

### 6. Document Everything

- Runbooks for common issues
- Alert response procedures
- Escalation paths
- Contact information

## Incident Response

### Severity Levels

**Critical (P1)**: Service completely down or major functionality broken
- Response time: Immediate
- Escalation: Page on-call engineer

**High (P2)**: Partial service degradation affecting many users
- Response time: 15 minutes
- Escalation: Notify on-call engineer

**Medium (P3)**: Non-critical issues, workarounds available
- Response time: 1 hour
- Escalation: Standard ticket

**Low (P4)**: Minor issues, cosmetic problems
- Response time: Next business day
- Escalation: Regular backlog

### Incident Response Steps

1. **Acknowledge**: Confirm you're investigating
2. **Assess**: Determine scope and severity
3. **Mitigate**: Stop the immediate bleeding
4. **Communicate**: Update stakeholders
5. **Resolve**: Fix the root cause
6. **Document**: Write incident report
7. **Learn**: Conduct blameless postmortem

### On-Call Runbook

See [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md) for detailed runbook.

---

Last Updated: January 2026
Version: 1.0.0
