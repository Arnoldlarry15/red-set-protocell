# Docker Support for Red Set ProtoCell

This document describes how to use Docker to run Red Set ProtoCell.

## Overview

Red Set ProtoCell now supports Docker deployment with:
- **Backend**: FastAPI server on port 8000
- **Frontend**: React + Vite built as static files served by nginx on port 3000
- **Docker Compose**: Orchestrates both services with automatic networking

## Architecture

```
/
├── backend/
│   ├── app/                  # Application code
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend image definition
│
├── frontend/
│   ├── src/                 # React source code
│   ├── package.json         # Node dependencies
│   └── Dockerfile           # Frontend image (multi-stage build)
│
├── docker-compose.yml       # Service orchestration
└── .env                     # Environment variables (create from .env.example)
```

## Quick Start

### 1. Prerequisites

- Docker Engine 20.10+ or Docker Desktop
- Docker Compose V2

Check your installation:
```bash
docker --version
docker compose version
```

### 2. Configuration

Copy the example environment file and configure it:
```bash
cp .env.example .env
```

Edit `.env` and set your API keys:
```bash
# Required: Set your API keys
OPENAI_API_KEY=sk-your-real-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-real-anthropic-key-here

# Required: Set demo password
RSP_DEMO_PASSWORD=your-secure-password-here

# Optional: Adjust other settings as needed
RSP_ENVIRONMENT=development
RSP_ALLOWED_ORIGINS=http://localhost:3000
RSP_REQUIRE_AUTH=false
```

### 3. Run

Start both services:
```bash
docker compose up --build
```

Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs (development mode only)

### 4. Stop

Stop the services:
```bash
# Stop and keep containers
docker compose stop

# Stop and remove containers
docker compose down

# Stop, remove containers, and delete volumes
docker compose down -v
```

## Services

### Backend (FastAPI)

- **Port**: 8000
- **Tech**: Python 3.11-slim + FastAPI + uvicorn
- **Entry Point**: `uvicorn app.api_server:app --host 0.0.0.0 --port 8000`
- **Health Check**: http://localhost:8000/api/health

### Frontend (React + nginx)

- **Port**: 3000 (mapped to nginx port 80)
- **Tech**: Node 20 Alpine (build) → nginx Alpine (runtime)
- **Build Process**: Multi-stage Docker build
  1. Stage 1: Build static files with Vite
  2. Stage 2: Serve with nginx

## Environment Variables

### Backend Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `RSP_ENVIRONMENT` | Environment mode (`development` or `production`) | `development` | No |
| `RSP_ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` | Yes (prod) |
| `OPENAI_API_KEY` | OpenAI API key | - | Yes* |
| `ANTHROPIC_API_KEY` | Anthropic API key | - | Yes* |
| `RSP_DEMO_PASSWORD` | Demo admin password | - | Yes |
| `RSP_REQUIRE_AUTH` | Enable JWT authentication | `false` | No |
| `RSP_JWT_SECRET` | JWT secret key (32+ chars) | - | Yes (if auth enabled) |
| `RSP_RATE_LIMIT_PER_MIN` | Rate limit per minute | `60` | No |
| `RSP_RATE_LIMIT_PER_HOUR` | Rate limit per hour | `1000` | No |

\* At least one AI provider API key is required

### Frontend Build Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | Backend API URL | `http://localhost:8000` |

## Development vs Production

### Development Mode (Default)

```yaml
# docker-compose.yml is configured for development
services:
  backend:
    environment:
      - RSP_ENVIRONMENT=development
      - RSP_REQUIRE_AUTH=false  # Auth disabled for easier testing
```

Features:
- CORS allows localhost origins
- API documentation enabled at `/api/docs`
- Authentication disabled by default
- Verbose logging

### Production Mode

For production deployment:

1. Update `.env`:
```bash
RSP_ENVIRONMENT=production
RSP_ALLOWED_ORIGINS=https://your-domain.com
RSP_REQUIRE_AUTH=true
RSP_JWT_SECRET=<generate-strong-32+-char-secret>
RSP_DEMO_PASSWORD=<strong-password>
```

2. Generate JWT secret:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

3. Deploy with production settings:
```bash
docker compose up -d
```

## Networking

Services communicate over an internal Docker network:
- **Service Name Resolution**: Frontend can reach backend via `http://backend:8000`
- **External Access**: 
  - Frontend: localhost:3000
  - Backend: localhost:8000

## Volumes

### Persistent Data

```yaml
volumes:
  sessions-data:
    # Stores session databases and telemetry
    # Mounted at /app/sessions in backend container
```

To inspect volume data:
```bash
docker volume ls
docker volume inspect red-set-protocell_sessions-data
```

To backup volume data:
```bash
docker run --rm \
  -v red-set-protocell_sessions-data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/sessions-backup.tar.gz -C /data .
```

## Troubleshooting

### Port Already in Use

If ports 3000 or 8000 are in use, modify `docker-compose.yml`:
```yaml
services:
  backend:
    ports:
      - "9000:8000"  # Use port 9000 instead
  frontend:
    ports:
      - "4000:80"    # Use port 4000 instead
```

### Build Failures

Clear Docker cache and rebuild:
```bash
docker compose build --no-cache
docker compose up
```

### View Logs

```bash
# All services
docker compose logs

# Specific service
docker compose logs backend
docker compose logs frontend

# Follow logs
docker compose logs -f
```

### Container Shell Access

```bash
# Backend
docker compose exec backend /bin/bash

# Frontend
docker compose exec frontend /bin/sh
```

## Deployment Platforms

This Docker setup works on:
- **Local Development**: Docker Desktop (Mac/Windows/Linux)
- **Cloud VMs**: AWS EC2, Google Compute Engine, Azure VMs
- **Container Platforms**: Fly.io, Railway, Render
- **Kubernetes**: Use as base images for Kubernetes deployments
- **AWS ECS/Fargate**: Compatible with ECS task definitions

## Differences from Serverless Deployment

### Serverless (Vercel/Netlify)
- ✅ Zero infrastructure management
- ✅ Automatic scaling
- ❌ Vendor lock-in
- ❌ Cold starts
- ❌ Limited runtime control

### Docker (This Setup)
- ✅ Full control over runtime
- ✅ Consistent everywhere
- ✅ No vendor lock-in
- ✅ Predictable performance
- ❌ You manage infrastructure
- ❌ Manual scaling configuration

Both deployment options are supported. Use serverless for convenience, Docker for sovereignty.

## Security Considerations

1. **Never commit `.env` files** - Use `.gitignore`
2. **Rotate secrets regularly** - Especially `RSP_JWT_SECRET`
3. **Use HTTPS in production** - Place nginx/Caddy/Traefik in front
4. **Enable authentication in production** - Set `RSP_REQUIRE_AUTH=true`
5. **Restrict CORS origins** - Set specific domains in `RSP_ALLOWED_ORIGINS`
6. **Regular updates** - Keep base images updated

```bash
# Update images
docker compose pull
docker compose up -d
```

## Next Steps

- **Production Deployment**: See [deployment guides](../docs/deployment/)
- **Configuration Reference**: See [backend/.env.example](backend/.env.example)
- **API Documentation**: http://localhost:8000/api/docs (dev mode)
- **Architecture**: See [backend/README.md](backend/README.md)

## Support

For issues or questions:
- GitHub Issues: [Report a bug](../../issues)
- Documentation: [Full docs](../docs/)
- Security: See [SECURITY.md](../SECURITY.md)
