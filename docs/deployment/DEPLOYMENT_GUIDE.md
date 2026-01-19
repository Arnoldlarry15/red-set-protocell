# Production Deployment Guide

This guide covers deploying Red Set ProtoCell in production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Configuration](#environment-configuration)
- [Deployment Options](#deployment-options)
- [Security Checklist](#security-checklist)
- [Monitoring Setup](#monitoring-setup)
- [Rollback Procedures](#rollback-procedures)
- [Disaster Recovery](#disaster-recovery)

## Prerequisites

- Python 3.8+ runtime environment
- HTTPS-enabled web server or reverse proxy (nginx, Apache, or cloud load balancer)
- API keys from OpenAI or Anthropic
- PostgreSQL database (recommended for production) or SQLite for single-instance deployments
- SSL/TLS certificates for HTTPS

## Environment Configuration

### Required Environment Variables

```bash
# Application Environment
RSP_ENVIRONMENT=production  # REQUIRED: Enables production security features

# CORS Configuration
RSP_ALLOWED_ORIGINS=https://app.example.com,https://dashboard.example.com
# REQUIRED in production: Comma-separated list of allowed origins

# API Keys (NEVER commit these)
OPENAI_API_KEY=sk-...  # Your OpenAI API key
ANTHROPIC_API_KEY=sk-ant-...  # Your Anthropic API key

# JWT Configuration
RSP_JWT_SECRET=your-very-long-random-secret-key-here  # REQUIRED
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
RSP_JWT_EXPIRATION_HOURS=24  # Token expiration time

# Authentication
RSP_REQUIRE_AUTH=true  # Enable JWT authentication (recommended)
RSP_DEMO_PASSWORD=changeme  # Change the demo admin password

# API Keys for programmatic access (optional)
RSP_API_KEYS=key1:admin,key2:researcher  # format: key:role,key:role

# Rate Limiting
RSP_RATE_LIMIT_PER_MIN=60  # Requests per minute per IP
RSP_RATE_LIMIT_PER_HOUR=1000  # Requests per hour per IP

# Database Configuration
RSP_DB_PATH=/data/rsp_production.db  # For SQLite
# OR
RSP_POSTGRES_URI=postgresql://user:pass@localhost:5432/rsp  # For PostgreSQL
```

### Optional Configuration

```bash
# Logging
RSP_LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
RSP_LOG_FILE=/var/log/rsp/api.log

# WebSocket Limits
RSP_MAX_WEBSOCKET_CONNECTIONS=100

# Session Storage
RSP_SESSIONS_DIR=/data/sessions
```

### Creating `.env` File

```bash
# Create .env file (NEVER commit this file!)
cat > /app/.env << 'EOF'
RSP_ENVIRONMENT=production
RSP_ALLOWED_ORIGINS=https://your-domain.com
OPENAI_API_KEY=sk-your-key-here
RSP_JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
RSP_REQUIRE_AUTH=true
RSP_DEMO_PASSWORD=$(python -c "import secrets; print(secrets.token_urlsafe(16))")
EOF

# Secure the file
chmod 600 /app/.env
```

## Deployment Options

### Option 1: Docker (Recommended)

#### 1. Build Docker Image

```bash
cd rsp-core
docker build -t rsp-backend:latest backend/
```

#### 2. Run with Environment File

```bash
docker run -d \
  --name rsp-api \
  --env-file /path/to/.env \
  -p 8000:8000 \
  -v /data/rsp:/data \
  --restart unless-stopped \
  rsp-backend:latest
```

#### 3. Docker Compose

```yaml
version: '3.8'

services:
  rsp-api:
    image: rsp-backend:latest
    env_file:
      - .env
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
      - ./logs:/var/log/rsp
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - rsp-api
```

### Option 2: Systemd Service

#### 1. Create Service File

```bash
sudo cat > /etc/systemd/system/rsp-api.service << 'EOF'
[Unit]
Description=Red Set ProtoCell API Server
After=network.target

[Service]
Type=simple
User=rsp
Group=rsp
WorkingDirectory=/opt/rsp-core/backend
EnvironmentFile=/opt/rsp-core/.env
ExecStart=/opt/rsp-core/venv/bin/uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/data/rsp /var/log/rsp

[Install]
WantedBy=multi-user.target
EOF
```

#### 2. Enable and Start

```bash
sudo systemctl daemon-reload
sudo systemctl enable rsp-api
sudo systemctl start rsp-api
sudo systemctl status rsp-api
```

### Option 3: Cloud Platforms

#### AWS Elastic Beanstalk

```bash
# Install EB CLI
pip install awsebcli

# Initialize
cd rsp-core/backend
eb init -p python-3.11 rsp-backend

# Create environment
eb create rsp-production \
  --envvars RSP_ENVIRONMENT=production,RSP_ALLOWED_ORIGINS=https://app.example.com

# Deploy
eb deploy
```

#### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/rsp-backend

# Deploy
gcloud run deploy rsp-backend \
  --image gcr.io/PROJECT-ID/rsp-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars RSP_ENVIRONMENT=production \
  --set-env-vars RSP_ALLOWED_ORIGINS=https://app.example.com \
  --set-secrets OPENAI_API_KEY=openai-key:latest \
  --set-secrets RSP_JWT_SECRET=jwt-secret:latest
```

#### Azure Container Instances

```bash
az container create \
  --resource-group rsp-resources \
  --name rsp-backend \
  --image rsp-backend:latest \
  --dns-name-label rsp-api \
  --ports 8000 \
  --environment-variables \
    RSP_ENVIRONMENT=production \
    RSP_ALLOWED_ORIGINS=https://app.example.com \
  --secure-environment-variables \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    RSP_JWT_SECRET=$RSP_JWT_SECRET
```

### Option 4: Serverless Deployment (Vercel)

Red Set ProtoCell supports deployment on Vercel using serverless Python functions.

See [Vercel Serverless Guide](./VERCEL_SERVERLESS_GUIDE.md) for detailed instructions.

**Quick Deploy:**

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from repository root
vercel --prod
```

**Key Features:**
- ✅ Serverless API functions
- ✅ React + Vite frontend with zero CORS issues
- ✅ Auto-scaling and pay-per-request pricing
- ✅ Production-ready security

### Option 5: Serverless Deployment (Netlify)

Red Set ProtoCell also supports deployment on Netlify using serverless Python functions.

See [Netlify Deployment Guide](./netlify.md) for detailed instructions.

**Quick Deploy:**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize and deploy
netlify init
netlify deploy --prod
```

**Key Features:**
- ✅ Clearer function boundaries
- ✅ Easy debugging
- ✅ Auto-scaling serverless functions
- ✅ Compatible with same codebase as Vercel

**No Vendor Lock-In:** Red Set ProtoCell supports both Vercel and Netlify using the same project files. Choose what works best for you, or use both!

## Security Checklist

Before deploying to production:

- [ ] All secrets in environment variables or secrets manager
- [ ] `RSP_ENVIRONMENT=production` is set
- [ ] `RSP_ALLOWED_ORIGINS` is configured with specific domains
- [ ] `RSP_JWT_SECRET` is set to a strong random value
- [ ] API keys are NOT in source code or `.env.example`
- [ ] HTTPS is enabled and enforced
- [ ] Firewall rules restrict access to necessary ports only
- [ ] Rate limiting is configured appropriately
- [ ] Authentication is enabled (`RSP_REQUIRE_AUTH=true`)
- [ ] Database is backed up regularly
- [ ] Logs are being collected and monitored
- [ ] Security headers are enabled (automatic with middleware)
- [ ] Dependencies are up to date (`pip list --outdated`)
- [ ] Vulnerability scans have been run (`safety check`)

## Monitoring Setup

### Health Checks

Configure your load balancer or monitoring system to check:

```bash
# Basic health check (fast, minimal overhead)
curl https://api.example.com/api/health

# Detailed health check (includes component status)
curl https://api.example.com/api/health/detailed
```

Expected responses:
- HTTP 200 = Healthy
- HTTP 5xx = Unhealthy

### Metrics Endpoint

RSP exposes Prometheus-compatible metrics:

```bash
curl https://api.example.com/api/metrics
```

Returns:
- `requests_total` - Total number of requests
- `requests_by_status` - Breakdown by HTTP status code
- `requests_by_endpoint` - Breakdown by endpoint
- `average_duration_ms` - Average request duration
- `error_rate` - Percentage of failed requests
- `rate_limit_hits` - Number of rate limit violations

### Integration with Monitoring Tools

#### Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'rsp-api'
    scrape_interval: 30s
    static_configs:
      - targets: ['api.example.com:8000']
    metrics_path: '/api/metrics'
```

#### Datadog

```python
# Install datadog agent on host
# Configure to scrape /api/metrics endpoint
```

#### New Relic

```python
# Install New Relic Python agent
pip install newrelic

# Run with agent
NEW_RELIC_CONFIG_FILE=newrelic.ini \
  newrelic-admin run-program uvicorn app.api_server:app
```

### Log Aggregation

RSP outputs structured JSON logs. Configure your log aggregation:

#### Example: Filebeat + Elasticsearch

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/rsp/*.log
    json.keys_under_root: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]
```

## Rollback Procedures

### Docker Rollback

```bash
# List previous images
docker images rsp-backend

# Tag current as backup
docker tag rsp-backend:latest rsp-backend:backup

# Rollback to previous version
docker pull rsp-backend:v1.0.0
docker tag rsp-backend:v1.0.0 rsp-backend:latest

# Restart container
docker-compose down
docker-compose up -d
```

### Systemd Rollback

```bash
# Stop service
sudo systemctl stop rsp-api

# Restore previous version
cd /opt/rsp-core
git checkout v1.0.0

# Reinstall dependencies if needed
source venv/bin/activate
pip install -r backend/requirements.txt

# Start service
sudo systemctl start rsp-api
```

### Cloud Platform Rollback

#### AWS Elastic Beanstalk
```bash
eb deploy --version previous-version-label
```

#### Google Cloud Run
```bash
gcloud run services update-traffic rsp-backend \
  --to-revisions=PREVIOUS-REVISION=100
```

## Disaster Recovery

### Backup Strategy

#### Database Backups

```bash
# SQLite backup
cp /data/rsp_production.db /backups/rsp_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump -U rsp_user -h localhost rsp > /backups/rsp_$(date +%Y%m%d).sql
```

#### Automated Backup Script

```bash
#!/bin/bash
# /opt/rsp-core/scripts/backup.sh

BACKUP_DIR=/backups/rsp
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /data/rsp_production.db $BACKUP_DIR/db_$DATE.db

# Backup sessions
tar -czf $BACKUP_DIR/sessions_$DATE.tar.gz /data/sessions

# Backup configuration
cp /opt/rsp-core/.env $BACKUP_DIR/env_$DATE

# Keep only last 30 days
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

#### Schedule with Cron

```bash
# Add to crontab
0 2 * * * /opt/rsp-core/scripts/backup.sh >> /var/log/rsp/backup.log 2>&1
```

### Recovery Procedures

#### Database Recovery

```bash
# Stop service
sudo systemctl stop rsp-api

# Restore database
cp /backups/rsp_20260118.db /data/rsp_production.db

# Restore sessions
tar -xzf /backups/sessions_20260118.tar.gz -C /

# Start service
sudo systemctl start rsp-api
```

#### Full System Recovery

1. Provision new server/container
2. Install dependencies
3. Restore backup files
4. Configure environment variables
5. Start services
6. Verify health checks
7. Update DNS/load balancer

### Testing Recovery

```bash
# Regularly test recovery procedures
# Schedule quarterly disaster recovery drills

# Test script
#!/bin/bash
echo "=== Disaster Recovery Test ==="
echo "1. Provisioning test environment..."
echo "2. Restoring latest backup..."
echo "3. Starting services..."
echo "4. Running health checks..."
echo "5. Verifying functionality..."
echo "=== Test Complete ==="
```

## Performance Optimization

### Recommended Settings

```bash
# Uvicorn workers (1-2x CPU cores)
uvicorn app.api_server:app --workers 4

# Connection limits
RSP_MAX_WEBSOCKET_CONNECTIONS=100

# Rate limiting (adjust based on capacity)
RSP_RATE_LIMIT_PER_MIN=60
RSP_RATE_LIMIT_PER_HOUR=1000
```

### Load Testing

```bash
# Install hey (HTTP load generator)
go install github.com/rakyll/hey@latest

# Test API endpoints
hey -n 1000 -c 10 -m GET https://api.example.com/api/health

# Expected results:
# - 99% requests < 100ms
# - 0% errors
# - Rate limiting kicks in appropriately
```

## Troubleshooting

### Common Issues

#### Issue: CORS errors
**Solution**: Verify `RSP_ALLOWED_ORIGINS` includes your frontend domain

#### Issue: Authentication failures
**Solution**: Check `RSP_JWT_SECRET` is set and tokens haven't expired

#### Issue: Rate limiting too aggressive
**Solution**: Increase `RSP_RATE_LIMIT_PER_MIN` or `RSP_RATE_LIMIT_PER_HOUR`

#### Issue: High memory usage
**Solution**: Reduce `RSP_MAX_WEBSOCKET_CONNECTIONS` or add more resources

### Debug Mode

```bash
# Enable debug logging (development only!)
RSP_LOG_LEVEL=DEBUG uvicorn app.api_server:app
```

## Support

For production deployment support:
- GitHub Issues: https://github.com/Arnoldlarry15/red-set-protocell/issues
- Security Issues: Use GitHub Security Advisories
- Documentation: See README.md and SECURITY.md

---

Last Updated: January 2026
Version: 1.0.0
