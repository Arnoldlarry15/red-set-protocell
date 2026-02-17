# Red Set ProtoCell - Installation Guide

This document provides comprehensive installation instructions and runtime dependency information for Red Set ProtoCell (RSP).

## Table of Contents

- [Runtime Dependencies](#runtime-dependencies)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Quick Install Scripts](#quick-install-scripts)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## Runtime Dependencies

### Backend (Python)

Red Set ProtoCell's backend requires Python 3.8+ and the following runtime dependencies:

#### Core Runtime Dependencies

```
python-dateutil>=2.8.2      # Date/time utilities
numpy>=1.20.0,<2.0.0        # Numerical operations and deterministic seeding
aiosqlite>=0.19.0           # Async SQLite support
```

#### API Client Dependencies (Required)

```
openai>=1.0.0               # OpenAI API client (GPT-3.5, GPT-4)
anthropic>=0.7.0            # Anthropic API client (Claude models)
requests>=2.31.0            # HTTP library for custom backends
```

#### Web Server Dependencies

```
fastapi>=0.104.0            # Web framework for API server
uvicorn[standard]>=0.24.0   # ASGI server
gunicorn>=21.2.0            # Production WSGI server
websockets>=12.0            # WebSocket support for real-time updates
pydantic>=2.0.0             # Data validation
PyJWT>=2.8.0                # JWT authentication
```

#### Development Dependencies (Optional)

```
pytest>=7.4.0               # Testing framework
pytest-asyncio>=0.21.0      # Async test support
pytest-cov>=4.1.0           # Coverage reporting
black>=23.7.0               # Code formatting
flake8>=6.1.0               # Linting
mypy>=1.5.0                 # Type checking
```

**Note**: Development dependencies are only needed for running tests or contributing to the codebase.

### Frontend (Node.js)

The web UI requires Node.js 16+ and the following runtime dependencies:

#### Core Runtime Dependencies

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.20.0",
  "axios": "^1.13.5",
  "framer-motion": "^12.29.2",
  "lucide-react": "^0.563.0",
  "react-window": "^2.2.5",
  "recharts": "^3.7.0",
  "@vercel/analytics": "^1.4.1",
  "@types/react-window": "^1.8.8"
}
```

#### Development Dependencies (Optional)

```json
{
  "@types/react": "^18.2.43",
  "@types/react-dom": "^18.2.17",
  "@typescript-eslint/eslint-plugin": "^6.21.0",
  "@typescript-eslint/parser": "^6.21.0",
  "@vitejs/plugin-react": "^4.2.1",
  "eslint": "^8.55.0",
  "eslint-plugin-react-hooks": "^4.6.0",
  "eslint-plugin-react-refresh": "^0.4.5",
  "typescript": "^5.3.3",
  "vite": "^7.3.1"
}
```

---

## System Requirements

### Minimum Requirements

- **OS**: Linux, macOS, or Windows (Windows Subsystem for Linux recommended)
- **Python**: 3.8 or higher
- **Node.js**: 16 or higher (for Web UI)
- **RAM**: 2GB minimum
- **Disk Space**: 500MB for code, variable for session data
- **Network**: Internet connection for API calls

### Recommended Requirements

- **Python**: 3.10 or higher
- **Node.js**: 18 LTS or higher
- **RAM**: 4GB or more
- **Disk Space**: 2GB or more

### API Keys Required

You'll need at least one of the following:
- **OpenAI API Key**: Get from https://platform.openai.com/api-keys
- **Anthropic API Key**: Get from https://console.anthropic.com/
- **OpenRouter API Key**: Get from https://openrouter.ai/

---

## Installation Methods

### Method 1: Standard Installation (Recommended)

This method installs RSP with a Python virtual environment.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell
```

#### Step 2: Backend Setup

```bash
cd backend

# Create a virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install runtime dependencies
pip install -r requirements.txt

# Verify installation
python -m app.main --help
```

#### Step 3: Frontend Setup (Optional - for Web UI)

```bash
cd ../frontend

# Install dependencies
npm install

# Verify installation
npm run build
```

#### Step 4: Configure API Keys

```bash
# Set your API key (choose one)
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export OPENROUTER_API_KEY="sk-or-v1-..."
```

### Method 2: Docker Installation

This method uses Docker to containerize the application.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell
```

#### Step 2: Build and Run with Docker Compose

```bash
# Build the container
docker-compose build

# Run with environment variables
export OPENAI_API_KEY="sk-..."
docker-compose up
```

### Method 3: Quick Web UI Setup

This method uses the provided startup script for both frontend and backend.

#### Step 1: Clone and Prepare

```bash
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell
```

#### Step 2: Set API Keys

```bash
export OPENAI_API_KEY="sk-..."
# Or use .env file (copy from .env.example)
```

#### Step 3: Run Startup Script

```bash
./start-ui.sh
```

The script will:
- Check for Python 3 and Node.js
- Create a Python virtual environment
- Install backend dependencies
- Install frontend dependencies
- Start both servers
- Open the UI at http://localhost:3000

---

## Quick Install Scripts

### Linux/macOS One-Liner

```bash
# Full installation with backend and frontend
curl -fsSL https://raw.githubusercontent.com/Arnoldlarry15/red-set-protocell/main/scripts/quick-install.sh | bash
```

Or manually:

```bash
# Backend only
git clone https://github.com/Arnoldlarry15/red-set-protocell.git && \
cd red-set-protocell/backend && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt

# Then set your API key
export OPENAI_API_KEY="sk-..."

# Run a test
python -m app.main --backend openai --api-key $OPENAI_API_KEY --rounds 5
```

### Windows PowerShell

```powershell
# Clone repository
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Set API key
$env:OPENAI_API_KEY="sk-..."

# Run a test
python -m app.main --backend openai --api-key $env:OPENAI_API_KEY --rounds 5
```

### Docker One-Liner

```bash
# Clone and run with Docker
git clone https://github.com/Arnoldlarry15/red-set-protocell.git && \
cd red-set-protocell && \
export OPENAI_API_KEY="sk-..." && \
docker-compose up
```

---

## Verification

### Verify Backend Installation

```bash
cd backend
source venv/bin/activate  # Skip if already activated

# Check Python version
python --version  # Should be 3.8 or higher

# Check dependencies
pip list | grep -E "openai|anthropic|fastapi|numpy"

# Run help command
python -m app.main --help

# Run a quick 5-round test (requires API key)
export OPENAI_API_KEY="sk-..."
python -m app.main --backend openai --api-key $OPENAI_API_KEY --rounds 5
```

Expected output should include:
```
╔═══════════════════════════════════════════════════════════╗
║         RED SET PROTOCELL (RSP)                           ║
║         Autonomous AI Red Teaming System                  ║
╚═══════════════════════════════════════════════════════════╝
```

### Verify Frontend Installation

```bash
cd frontend

# Check Node.js version
node --version  # Should be 16 or higher

# Check npm version
npm --version

# Verify dependencies
npm list --depth=0

# Build test
npm run build

# Start dev server
npm run dev
```

The dev server should start at http://localhost:3000 (or similar port).

### Run Tests (Optional)

```bash
cd backend
source venv/bin/activate

# Install dev dependencies if not already installed
pip install pytest pytest-asyncio pytest-cov

# Run test suite
pytest

# Run with coverage
pytest --cov=app --cov-report=term-missing
```

---

## Troubleshooting

### Common Issues

#### 1. Python Version Errors

**Problem**: `ERROR: Python 3.8 or higher is required`

**Solution**:
```bash
# Check your Python version
python3 --version

# Use python3 explicitly
python3 -m venv venv

# Or install Python 3.8+ from python.org
```

#### 2. pip Installation Fails

**Problem**: `pip: command not found` or pip fails to install packages

**Solution**:
```bash
# Update pip
python3 -m pip install --upgrade pip

# Install packages with explicit python
python3 -m pip install -r requirements.txt

# On Ubuntu/Debian, install python3-pip
sudo apt-get install python3-pip python3-venv
```

#### 3. Node.js/npm Not Found

**Problem**: `node: command not found` or `npm: command not found`

**Solution**:
```bash
# Install Node.js from nodejs.org
# Or use a version manager like nvm:

# Install nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Install Node.js LTS
nvm install --lts
nvm use --lts
```

#### 4. API Key Errors

**Problem**: `AuthenticationError: Invalid API key`

**Solution**:
```bash
# Verify your API key format
# OpenAI keys start with: sk-
# Anthropic keys start with: sk-ant-
# OpenRouter keys start with: sk-or-v1-

# Set the correct key
export OPENAI_API_KEY="sk-your-actual-key"

# Verify it's set
echo $OPENAI_API_KEY

# Use explicit --api-key flag
python -m app.main --backend openai --api-key "sk-..." --rounds 5
```

#### 5. Module Import Errors

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Make sure you're in the backend directory
cd backend

# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Run from backend directory with -m flag
python -m app.main --help
```

#### 6. Port Already in Use

**Problem**: `Error: Port 8000 is already in use`

**Solution**:
```bash
# Find process using port
lsof -i :8000  # On Linux/macOS
netstat -ano | findstr :8000  # On Windows

# Kill the process or use a different port
# (Refer to application-specific configuration)
```

#### 7. Windows UTF-8 Encoding Issues

**Problem**: `UnicodeDecodeError` on Windows

**Solution**: This is fixed in the codebase - always specify `encoding='utf-8'` when opening files. If you encounter this, ensure you're using the latest version:

```bash
git pull origin main
```

### Getting Help

If you encounter issues not covered here:

1. **Check the documentation**: See [README.md](README.md) and [docs/](docs/) directory
2. **Search existing issues**: https://github.com/Arnoldlarry15/red-set-protocell/issues
3. **Create a new issue**: Include:
   - Your OS and Python version
   - Full error message
   - Steps to reproduce
   - Output of `pip list` and `python --version`

---

## Next Steps

After installation:

1. **Quick Start**: Follow the [Quick Start guide](README.md#quick-start) to run your first session
2. **Configuration**: See [Configuration](README.md#configuration) for advanced options
3. **Web UI**: Set up the web interface following [WEB_UI_SETUP.md](docs/guides/WEB_UI_SETUP.md)
4. **Deployment**: For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) or [QUICK_DEPLOY.md](QUICK_DEPLOY.md)
5. **Development**: For contributing, see [CONTRIBUTING.md](CONTRIBUTING.md)

---

## Minimal Runtime-Only Installation

If you only need the core runtime without development tools:

```bash
# Clone repository
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install ONLY runtime dependencies (excluding dev tools)
pip install python-dateutil>=2.8.2 \
            numpy>=1.20.0,<2.0.0 \
            aiosqlite>=0.19.0 \
            openai>=1.0.0 \
            anthropic>=0.7.0 \
            requests>=2.31.0 \
            fastapi>=0.104.0 \
            "uvicorn[standard]>=0.24.0" \
            gunicorn>=21.2.0 \
            websockets>=12.0 \
            pydantic>=2.0.0 \
            PyJWT>=2.8.0

# Verify
python -m app.main --help
```

This installs approximately 50-80MB of dependencies (vs 150-200MB with dev tools).

---

## License

MIT License - See [LICENSE](LICENSE) for details.
