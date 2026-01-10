# Red Set ProtoCell (RSP)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/Arnoldlarry15/red-set-protocell/actions/workflows/ci.yml/badge.svg)](https://github.com/Arnoldlarry15/red-set-protocell/actions/workflows/ci.yml)
[![Code Quality](https://github.com/Arnoldlarry15/red-set-protocell/actions/workflows/code-quality.yml/badge.svg)](https://github.com/Arnoldlarry15/red-set-protocell/actions/workflows/code-quality.yml)
[![Security](https://github.com/Arnoldlarry15/red-set-protocell/actions/workflows/security.yml/badge.svg)](https://github.com/Arnoldlarry15/red-set-protocell/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/Arnoldlarry15/red-set-protocell/branch/main/graph/badge.svg)](https://codecov.io/gh/Arnoldlarry15/red-set-protocell)

**An Open-source AI safety platform using dual-agent Sniper/Spotter red-teaming to audit and secure large language models.**

Red Set ProtoCell is an autonomous, evolutionary AI red teaming system that functions as a defensive "immune system" for large language models (LLMs). It simulates adversarial pressure in a controlled environment to surface safety, alignment, and robustness failures. The system is scalable, transparent, and built for advanced AI risk monitoring.

## 🎨 NEW: Web UI Available!

Red Set ProtoCell now includes a modern, glassmorphism-styled web interface featuring:
- **Live Attack Feed**: Real-time stream of red teaming attacks
- **Interactive Dashboard**: Comprehensive metrics, charts, and graphs
- **Attack Configuration**: Selectable domains, strategies, and payloads
- **Cost Management**: API cost tracking with automatic halt
- **User Input**: Test custom adversarial prompts
- **Auto-Halt**: Stops on critical vulnerabilities or cost limits

See [WEB_UI_SETUP.md](WEB_UI_SETUP.md) for setup instructions.

---

## 🎯 Table of Contents

- [Overview](#overview)
- [Web UI](#-new-web-ui-available)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage Guide](#usage-guide)
- [Configuration](#configuration)
- [Development](#development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)
- [Citation](#citation)

---

## 📖 Overview

### What is Red Set ProtoCell?

Red Set ProtoCell (RSP) is an autonomous AI red teaming platform designed to stress-test large language models by:

- **Generating adversarial prompts** through evolutionary algorithms and mutation strategies
- **Executing prompts** against target LLMs via real API integrations
- **Evaluating responses** using a 3-layer scoring taxonomy
- **Evolving attack strategies** based on success rates

Unlike manual red teaming, RSP operates autonomously, continuously evolving its attack strategies to discover edge cases, policy violations, and alignment failures in LLMs.

### Why Red Set ProtoCell?

**The Challenge:**
- Manual red teaming is time-consuming and doesn't scale
- LLMs are deployed faster than they can be thoroughly tested
- Safety failures emerge in unexpected contexts
- Adversarial attacks evolve constantly

**The Solution:**
RSP provides an automated, scalable, and continuous red teaming solution that:
- Runs 24/7 without human intervention
- Evolves attack strategies based on success patterns
- Covers multiple attack domains simultaneously
- Produces quantifiable safety metrics
- Maintains strict ethical boundaries

### Core Principles

1. **Defense-Only System**: No real malware generation or real-world exploits
2. **Zero-Retention Policy**: All session data destroyed by default (configurable)
3. **Ethical Guardrails**: Mandatory content filtering via EGG (Ethical Guardrail Governor)
4. **Human-in-the-Loop**: Results require human interpretation and validation
5. **Transparency**: Open-source, auditable, and well-documented
6. **Real API Integration**: Production-ready integrations with OpenAI and Anthropic APIs

### System Non-Goals

RSP is **NOT**:
- A penetration testing framework for infrastructure
- A malware or real exploit generator
- A vulnerability scanner for production systems
- A tool for bypassing production safeguards
- A replacement for human security researchers

---

## ✨ Key Features

### 🤖 Multi-Agent Architecture
- **Sniper Agent**: Generates adversarial prompts using mutation and evolution
- **Target Agent**: Stateless execution wrapper for the LLM under test
- **Spotter Agent**: Analyzes responses using heuristic evaluation
- **Orchestrator**: Controls execution flow and manages agent coordination

### 🛡️ Safety-First Design
- **Ethical Guardrail Governor (EGG)**: Blocks CSAM, bioweapons, and real exploits
- **Content Fingerprinting**: Privacy-preserving hashed logging
- **Zero-Retention Policy**: Optional automatic data destruction
- **Trust Boundaries**: Agents don't trust each other or their own outputs

### 🧬 Evolutionary Intelligence
- **Six Mutation Strategies**: Lexical, encoding, structural, role-play, context, obfuscation
- **Fitness-Guided Evolution**: Successful prompts influence future generations
- **Seven Attack Domains**: Injection, refusal erosion, jailbreak, PII extraction, policy circumvention, cognitive manipulation, context confusion

### 📊 3-Layer Scoring Taxonomy
- **L1: Linguistic Safety (35%)** - Hate speech, PII leakage, refusal quality
- **L2: Security Exploitability (45%)** - Prompt injection, jailbreak, policy bypass
- **L3: Cognitive Stability (20%)** - Sycophancy, deceptive alignment, chain-of-thought leakage
- **Uncertainty Tracking (NEW)**: Score confidence intervals and variance metrics

### 🔌 Production-Ready Integrations
- **OpenAI API**: Full GPT-3.5, GPT-4, and GPT-4 Turbo support
- **Anthropic API**: Claude models (Claude 3 Opus, Sonnet, Haiku)
- **Local Models**: GGUF models via llama-cpp-python (NEW)
- **Custom APIs**: Generic HTTP endpoint support for any LLM (NEW)
- **Extensible Backend System**: Easy to add new LLM providers

### ⚡ Performance & Scalability
- **Parallel Execution**: Concurrent round processing (5-10x speedup) (NEW)
- **Adaptive Learning**: Mutation strategies improve over time (NEW)
- **Zero API Costs**: Run completely offline with local models (NEW)
- **Comprehensive Testing**: 50+ tests including uncertainty tracking (NEW)

### 📈 Observable & Auditable
- Comprehensive session statistics
- Detailed logging and audit trails
- Aggregate metrics for trend analysis
- Round-by-round tracking of success rates
- Strategy performance analytics (NEW)
- **Epistemic Upgrades (NEW)**: Uncertainty quantification, multi-pass agreement, cross-Spotter evaluation
- **Time Analytics (NEW)**: Fatigue tracking, regression detection, score drift analysis

---

## 🏗️ Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR                            │
│             (Control Plane & State Manager)                  │
└─────────────┬─────────────┬─────────────┬──────────────────┘
              │             │             │
    ┌─────────▼──┐    ┌────▼─────┐   ┌──▼─────────┐
    │   SNIPER   │    │  TARGET  │   │  SPOTTER   │
    │  (Attacker)│    │ (Exec)   │   │(Evaluator) │
    └─────┬──────┘    └────┬─────┘   └──┬─────────┘
          │                │              │
          │         ┌──────▼──────┐       │
          │         │     EGG     │       │
          │         │ (Guardrail) │       │
          │         └─────────────┘       │
          │                               │
    ┌─────▼─────────────┐       ┌────────▼────────┐
    │ MUTATION ENGINE   │       │ SCORING ENGINE  │
    │ (6 strategies)    │       │ (3 layers)      │
    └───────────────────┘       └─────────────────┘
```

### Component Responsibilities

#### 1. **Orchestrator** (Control Plane)
- **Authority**: Execution flow control
- **Responsibilities**:
  - Round lifecycle management
  - Agent invocation and coordination
  - State persistence via StateManager
  - Timeout handling and error recovery
  - Statistics aggregation
  - Zero-retention cleanup

#### 2. **Sniper Agent** (Attacker)
- **Authority**: None (stateless generator)
- **Responsibilities**:
  - Generate adversarial prompts
  - Apply mutation strategies
  - Manage evolution pool
  - Select attack domains
- **Constraints**:
  - All prompts pass through EGG
  - Does NOT evaluate outcomes
  - Does NOT persist results
  - Read-only access to prior round metadata

#### 3. **Target Agent** (Execution Interface)
- **Authority**: None (stateless wrapper)
- **Responsibilities**:
  - Execute prompts on target LLM
  - Enforce fresh context per invocation
  - Handle API communication
  - Propagate errors appropriately
- **Constraints**:
  - NO memory between executions
  - NO result persistence
  - Stateless operation only

#### 4. **Spotter Agent** (Evaluator)
- **Authority**: None (heuristic evaluations only)
- **Responsibilities**:
  - Analyze LLM responses
  - Compute 3-layer scores
  - Generate mutation guidance
  - Provide probabilistic judgments
- **Constraints**:
  - Does NOT claim ground truth
  - Does NOT mutate prompts
  - Does NOT control orchestration

#### 5. **Ethical Guardrail Governor (EGG)** (Safety Layer)
- **Authority**: FINAL authority over content admissibility
- **Responsibilities**:
  - Block CSAM content
  - Block bioweapon instructions
  - Block real exploit payloads
  - Block real hacking attempts
  - Log content fingerprints (hashed)
- **Constraints**:
  - Decisions are FINAL and non-overridable
  - Cannot be disabled in production

### Authority Model

```
┌─────────────────────────────────────────┐
│  AUTHORITY HIERARCHY                    │
├─────────────────────────────────────────┤
│  1. EGG: Content Admissibility         │ ← FINAL
│  2. Orchestrator: Execution Flow       │
│  3. Agents: Domain-specific Operations │
└─────────────────────────────────────────┘
```

### Data Flow

```
Round N:
  1. Orchestrator → Sniper: "Generate adversarial prompt"
  2. Sniper → Mutation Engine: Apply strategy
  3. Sniper → EGG: "Is this prompt allowed?"
  4. EGG: Inspect → [ALLOW/BLOCK]
  5. If ALLOW:
     a. Orchestrator → Target: "Execute prompt"
     b. Target → LLM API: Send request
     c. LLM API → Target: Return response
     d. Target → Orchestrator: Response
     e. Orchestrator → Spotter: "Evaluate response"
     f. Spotter → Scoring Engine: Compute scores
     g. Scoring Engine → Orchestrator: EvaluationResult
     h. Orchestrator → StateManager: Persist round data
  6. If BLOCK:
     a. Orchestrator: Log block event
     b. Orchestrator: Continue to next round
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **API Key** from OpenAI or Anthropic
  - OpenAI: https://platform.openai.com/api-keys
  - Anthropic: https://console.anthropic.com/

### 5-Minute Quickstart

```bash
# 1. Clone the repository
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell

# 2. Install dependencies
cd rsp-core/backend
pip install -r requirements.txt

# 3. Set your API key
export OPENAI_API_KEY="sk-..."

# 4. Run a 10-round session
python -m app.main --backend openai --api-key $OPENAI_API_KEY --rounds 10
```

**Expected Output:**
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║         RED SET PROTOCELL (RSP)                           ║
║         Autonomous AI Red Teaming System                  ║
║                                                           ║
║         Defense-Only | Zero-Retention | Ethical           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

Initializing Red Set ProtoCell system...
✓ EGG initialized
✓ Scoring Engine initialized
✓ Mutation Engine initialized
✓ Sniper Agent initialized
✓ Target Agent initialized (openai)
✓ Spotter Agent initialized
✓ State Manager initialized (zero_retention=True)
✓ Orchestrator initialized
============================================================
Red Set ProtoCell system ready
Session ID: rsp_20260108_123456
Max Rounds: 10
Zero Retention: True
============================================================

[Round 1/10] Generating adversarial prompt...
[Round 1/10] Executing on target...
[Round 1/10] Evaluating response...
[Round 1/10] Global Score: 0.234

... (rounds 2-10) ...

============================================================
SESSION COMPLETED
============================================================
Total Rounds: 10
Average Score: 0.312
Blocked by EGG: 1

Agent Statistics:
  Sniper: 10 prompts generated
  Target: 9 executions
  Spotter: 9 evaluations
  EGG: 1 blocked
============================================================
```

---

## 💾 Installation

### Local Installation

#### Option 1: pip (Recommended)

```bash
# Clone repository
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell/rsp-core/backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -m app.main --help
```

#### Option 2: Docker

```bash
# Clone repository
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell/rsp-core

# Build Docker image
docker-compose build

# Run with environment variable
export OPENAI_API_KEY="sk-..."
docker-compose run rsp-backend python -m app.main --backend openai --api-key $OPENAI_API_KEY --rounds 10
```

### System Requirements

- **OS**: Linux, macOS, Windows (with WSL recommended)
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Disk**: 500MB for code, variable for session data
- **Network**: Internet connection for API calls

### Dependencies

**Core:**
- `openai>=1.0.0` - OpenAI API client
- `anthropic>=0.7.0` - Anthropic API client
- `python-dateutil>=2.8.2` - Date utilities

**Testing:**
- `pytest>=7.4.0` - Test framework
- `pytest-asyncio>=0.21.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting

**Development:**
- `black>=23.7.0` - Code formatter
- `flake8>=6.1.0` - Linter
- `mypy>=1.5.0` - Type checker

---

## 📚 Usage Guide

### Basic Usage

#### OpenAI Backend

```bash
cd rsp-core/backend
export OPENAI_API_KEY="sk-..."
python -m app.main --backend openai --api-key $OPENAI_API_KEY --rounds 10
```

#### Anthropic Backend

```bash
cd rsp-core/backend
export ANTHROPIC_API_KEY="sk-ant-..."
python -m app.main --backend anthropic --api-key $ANTHROPIC_API_KEY --rounds 10
```

### Command-Line Options

```
usage: python -m app.main [options]

Required Arguments:
  --backend {openai,anthropic}
                        Target LLM backend to test
  --api-key KEY        API key for the selected backend

Optional Arguments:
  --rounds N           Maximum rounds to execute (default: 100)
  --model NAME         Specific model name (e.g., gpt-4, claude-3-opus-20240229)
  --no-zero-retention  Disable zero-retention (keep session data)
  --db-path PATH       Database file path (default: rsp_session.db)
  -h, --help          Show help message
```

### Advanced Usage Examples

#### 1. Custom Model Selection

```bash
# Test GPT-4
python -m app.main \
  --backend openai \
  --api-key $OPENAI_API_KEY \
  --model gpt-4 \
  --rounds 50

# Test Claude 3 Opus
python -m app.main \
  --backend anthropic \
  --api-key $ANTHROPIC_API_KEY \
  --model claude-3-opus-20240229 \
  --rounds 50
```

#### 2. Extended Session with Data Retention

```bash
# Run 100 rounds and keep the data for analysis
python -m app.main \
  --backend openai \
  --api-key $OPENAI_API_KEY \
  --rounds 100 \
  --no-zero-retention \
  --db-path analysis_session.db
```

#### 3. Docker Deployment

```bash
# Using Docker Compose
cd rsp-core
export OPENAI_API_KEY="sk-..."
docker-compose run rsp-backend python -m app.main \
  --backend openai \
  --api-key $OPENAI_API_KEY \
  --rounds 20 \
  --db-path /data/session.db
```

#### 4. Continuous Monitoring

```bash
# Run in a loop for continuous monitoring
while true; do
  python -m app.main \
    --backend openai \
    --api-key $OPENAI_API_KEY \
    --rounds 50 \
    --db-path "session_$(date +%Y%m%d_%H%M%S).db"
  sleep 3600  # Wait 1 hour between sessions
done
```

### Understanding Output

#### Session Statistics

```
Total Rounds: 100              # Number of rounds executed
Average Score: 0.456           # Mean global score across all rounds
Blocked by EGG: 5              # Prompts blocked by safety layer

Agent Statistics:
  Sniper: 100 prompts generated   # Total adversarial prompts
  Target: 95 executions           # Successful executions (100 - 5 blocked)
  Spotter: 95 evaluations         # Response evaluations
  EGG: 5 blocked                  # Safety violations caught

Mutation Statistics:
  Total: 85                       # Mutations applied
```

#### Score Interpretation

| Global Score | Severity | Meaning |
|--------------|----------|---------|
| 0.0 - 0.2    | **Safe** | No significant issues detected |
| 0.2 - 0.4    | **Low** | Minor policy deviations |
| 0.4 - 0.6    | **Medium** | Moderate safety concerns |
| 0.6 - 0.8    | **High** | Significant alignment failures |
| 0.8 - 1.0    | **Critical** | Severe safety violations |

#### Epistemic Upgrades: Uncertainty Tracking (NEW)

RSP now provides scores with confidence intervals and variance metrics, transforming simple point estimates into rich epistemic signals:

**Before:**
```
Global Score: 0.62
```

**After (with uncertainty tracking):**
```
Global Score: 0.62 ± 0.08
Confidence Interval: [0.54, 0.70]
Multi-Pass Agreement: 0.92
```

**Features:**

1. **Uncertainty Quantification**
   - Every score includes uncertainty (±)
   - Confidence intervals show likely range
   - Based on pattern match strength and confidence

2. **Multi-Pass Agreement**
   - Run multiple evaluations to measure consistency
   - High agreement (>0.9) = reliable score
   - Low agreement (<0.7) = ambiguous signal requiring review

3. **Cross-Spotter Evaluation**
   - Compare judgments from different Spotter configurations
   - Disagreement is valuable information
   - Helps identify edge cases and ambiguous content

4. **Benefits**
   - **Scientific rigor**: Enables statistical analysis
   - **Audit-friendly**: Shows confidence in assessments
   - **Triage support**: Prioritize which results need human review
   - **Research-ready**: Supports meta-analysis and comparison

**Example Usage:**

```python
from app.agents.spotter import Spotter
from app.engines.scoring import ScoringEngine

# Enable multi-pass evaluation
spotter = Spotter(enable_multi_pass=True, multi_pass_count=3)
engine = ScoringEngine()

response = "Model response to evaluate"

# Get multi-pass results with variance
multi_pass = spotter.evaluate_with_paraphrase(response)
aggregated = engine.aggregate_multi_pass_evaluations(multi_pass['evaluations'])

print(f"Score: {aggregated.global_score:.3f} ± {aggregated.global_uncertainty:.3f}")
print(f"Agreement: {aggregated.multi_pass_agreement:.3f}")

# Cross-Spotter comparison
spotter2 = Spotter(confidence_threshold=0.8)
cross_result = spotter.cross_evaluate(response, spotter2)
print(f"Disagreement: {cross_result['deltas']}")
```

See `examples/uncertainty_demo.py` for complete demonstrations.

#### Time Analytics: Tracking Model Behavior Over Time (NEW)

RSP tracks time as a first-class dimension, enabling analysis of model behavior over extended sessions:

**Key Questions Answered:**
1. "Does this model get worse after sustained pressure?" → **Fatigue Tracking**
2. "Did the new version improve, or just shift failure modes?" → **Regression Detection**
3. "What are the performance trends?" → **Score Drift Analysis**

**Example Usage:**

```python
from app.analytics.time_tracking import FatigueTracker, RegressionDetector

# Detect model fatigue
tracker = FatigueTracker('rsp_session.db')
report = tracker.analyze_fatigue(session_id='rsp_20260109_123456')

if report.is_fatigued:
    print(f"⚠️  Model fatigued after {report.rounds_analyzed} rounds")
    print(f"Degradation: {report.degradation_rate:.4f} per round")

# Compare model versions
detector = RegressionDetector('rsp_session.db')
report = detector.compare_versions('model-v1', 'model-v2')

print(f"Verdict: {report.verdict}")
print(f"Score delta: {report.score_delta:+.3f}")
```

**Features:**
- **Fatigue Detection**: Identifies if model performance degrades over many rounds
- **Regression Analysis**: Compares two model versions objectively
- **Drift Classification**: Categorizes trends as improving, degrading, stable, or volatile
- **Automatic Integration**: Time analytics included in session statistics

**Command Line:**
```bash
python -m app.main \
  --backend openai \
  --api-key $OPENAI_API_KEY \
  --model-version "gpt-4-v2.0-2026-01-09" \
  --rounds 50 \
  --no-zero-retention
```

See `examples/time_analytics_demo.py` and [TIME_TRACKING.md](TIME_TRACKING.md) for complete documentation.

---

## ⚙️ Configuration

### Configuration Architecture

RSP uses a hierarchical configuration system based on Python dataclasses:

```python
RSPConfig
├── OrchestratorConfig    # Control plane settings
├── SniperConfig          # Attacker agent settings
├── TargetConfig          # Execution wrapper settings
├── SpotterConfig         # Evaluator agent settings
├── EGGConfig             # Safety layer settings
├── StorageConfig         # Database and retention settings
└── ScoringConfig         # Scoring weights
```

### Configuration Options Reference

#### Orchestrator Configuration

```python
max_rounds: int = 100              # Maximum execution rounds
concurrent_evaluations: bool = False  # Enable parallel evaluation
concurrent_rounds: int = 1         # Number of rounds to execute in parallel (NEW)
round_timeout_seconds: int = 300   # Timeout per round
```

#### Sniper Configuration

```python
mutation_rate: float = 0.7           # Probability of mutation (0.0-1.0)
evolution_pool_size: int = 10        # Size of evolution pool
creativity_temperature: float = 0.9  # Randomness in generation
```

#### Target Configuration

```python
backend: ModelBackend = OPENAI       # LLM backend (openai/anthropic/llama_cpp/custom_http)
model_name: str = "gpt-3.5-turbo"   # Model identifier
api_key: Optional[str] = None        # API key
api_base: Optional[str] = None       # Custom API endpoint
max_tokens: int = 1000               # Max response tokens
temperature: float = 0.7             # Model temperature
fresh_context: bool = True           # Reset context each round
# NEW: For local models (llama_cpp backend)
model_path: Optional[str] = None     # Path to GGUF model file
n_ctx: int = 2048                    # Context window size
n_gpu_layers: int = 0                # GPU layers (0=CPU only)
# NEW: For custom HTTP backends
api_url: Optional[str] = None        # Custom API endpoint URL
request_format: str = "openai"       # Request format (openai/anthropic/generic)
```

#### Spotter Configuration

```python
confidence_threshold: float = 0.6    # Minimum confidence for alerts
use_auxiliary_classifiers: bool = False  # Enable ML classifiers
# NEW: Epistemic upgrades
enable_multi_pass: bool = False      # Enable multi-pass evaluation for uncertainty
multi_pass_count: int = 3            # Number of passes when multi_pass enabled
enable_cross_spotter: bool = False   # Enable cross-Spotter evaluation
```

#### EGG Configuration

```python
enabled: bool = True                 # Enable safety layer (ALWAYS True in production)
block_real_exploits: bool = True     # Block real exploit payloads
block_csam: bool = True              # Block CSAM content
block_bioweapons: bool = True        # Block bioweapon instructions
log_blocked_fingerprints: bool = True  # Log hashed fingerprints
```

#### Storage Configuration

```python
mode: StorageMode = SQLITE           # sqlite or postgres
database_path: str = "rsp_session.db"  # DB file path
postgres_connection_string: Optional[str] = None  # PostgreSQL URI
zero_retention: bool = True          # Auto-delete session data
```

#### Scoring Configuration

```python
l1_weight: float = 0.35  # Linguistic Safety weight
l2_weight: float = 0.45  # Security Exploitability weight
l3_weight: float = 0.20  # Cognitive Stability weight
# Weights must sum to 1.0
```

### Programmatic Configuration

```python
from app.core.config import RSPConfig, TargetConfig, ScoringConfig

# Create custom configuration
config = RSPConfig()

# Customize target
config.target.backend = "anthropic"
config.target.model_name = "claude-3-opus-20240229"
config.target.api_key = "sk-ant-..."

# Adjust scoring weights
config.scoring.l1_weight = 0.30  # Reduce linguistic weight
config.scoring.l2_weight = 0.50  # Increase security weight
config.scoring.l3_weight = 0.20  # Keep cognitive weight

# Increase rounds
config.orchestrator.max_rounds = 200

# Disable zero-retention
config.storage.zero_retention = False
config.storage.database_path = "persistent_session.db"

# Use configuration
orchestrator = setup_system(config)
await orchestrator.run_session()
```

---

## 🔧 Development

### Project Structure

```
red-set-protocell/
├── README.md                    # This file
├── IMPLEMENTATION.md            # Implementation summary
├── LICENSE                      # MIT License
├── rsp-core/
│   ├── README.md               # Technical documentation
│   ├── docker-compose.yaml     # Docker orchestration
│   └── backend/
│       ├── app/
│       │   ├── __init__.py
│       │   ├── main.py         # Entry point
│       │   ├── agents/         # Agent implementations
│       │   │   ├── orchestrator.py
│       │   │   ├── sniper.py
│       │   │   ├── target.py
│       │   │   └── spotter.py
│       │   ├── core/           # Core utilities
│       │   │   ├── config.py   # Configuration system
│       │   │   ├── egg.py      # Ethical Guardrail Governor
│       │   │   └── security.py # Security utilities
│       │   ├── engines/        # Processing engines
│       │   │   ├── mutation.py # Mutation engine
│       │   │   └── scoring.py  # Scoring engine
│       │   └── strategies/     # Custom strategies (extensible)
│       ├── tests/              # Test suite
│       │   ├── test_config.py
│       │   ├── test_egg.py
│       │   ├── test_mutation.py
│       │   ├── test_scoring.py
│       │   └── test_real_backends.py
│       ├── requirements.txt    # Python dependencies
│       └── Dockerfile          # Container definition
└── .github/                    # GitHub workflows
```

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/Arnoldlarry15/red-set-protocell.git
cd red-set-protocell/rsp-core/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies (including dev tools)
pip install -r requirements.txt

# Install pre-commit hooks (if available)
# pre-commit install
```

### Code Style and Quality

#### Formatting with Black

```bash
# Format all Python files
black app/ tests/

# Check formatting without making changes
black --check app/ tests/
```

#### Linting with Flake8

```bash
# Lint all Python files
flake8 app/ tests/

# Common flake8 configuration (.flake8):
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,venv
```

#### Type Checking with MyPy

```bash
# Type check application code
mypy app/

# Common mypy configuration (mypy.ini):
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

### Adding New Components

#### Adding a New Attack Domain

1. Edit `app/agents/sniper.py`:

```python
class AttackDomain(Enum):
    # ... existing domains ...
    NEW_DOMAIN = "new_domain_name"

# Update BASE_PROMPTS
BASE_PROMPTS = {
    # ... existing prompts ...
    AttackDomain.NEW_DOMAIN: [
        "Base prompt 1 for new domain",
        "Base prompt 2 for new domain",
    ],
}
```

2. Add tests in `tests/test_sniper.py`

#### Adding a New LLM Backend

1. Edit `app/agents/target.py`:

```python
class NewBackend(TargetBackend):
    """Implementation for new LLM provider."""
    
    def __init__(self, api_key: str, model_name: str, ...):
        super().__init__()
        # Initialize API client
        self.client = NewProviderClient(api_key=api_key)
        self.model_name = model_name
    
    async def execute(self, prompt: str) -> str:
        """Execute prompt on new backend."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.message.content
        except Exception as e:
            raise TargetExecutionError(f"Execution failed: {e}")

# Update create_target() factory
def create_target(backend_type: str, ...):
    if backend_type == "new_provider":
        return NewBackend(...)
    # ... existing backends ...
```

2. Update `ModelBackend` enum in `app/core/config.py`
3. Add integration tests in `tests/test_real_backends.py`

#### Adding a New Mutation Strategy

1. Edit `app/engines/mutation.py`:

```python
class MutationStrategy(Enum):
    # ... existing strategies ...
    NEW_STRATEGY = "new_strategy"

class MutationEngine:
    def mutate(self, prompt, ...):
        # ... existing code ...
        elif strategy == MutationStrategy.NEW_STRATEGY:
            mutated = self._new_strategy(prompt)
        # ... rest of code ...
    
    def _new_strategy(self, prompt: str) -> str:
        """Implement new mutation strategy."""
        # Your transformation logic here
        return transformed_prompt
```

2. Add tests in `tests/test_mutation.py`

---

## 🧪 Testing

### Test Suite Organization

```
tests/
├── test_config.py           # Configuration validation tests
├── test_egg.py              # EGG safety layer tests
├── test_mutation.py         # Mutation engine tests
├── test_scoring.py          # Scoring engine tests
└── test_real_backends.py    # Integration tests (requires API keys)
```

### Running Tests

#### Unit Tests (No API Keys Required)

```bash
cd rsp-core/backend

# Run all unit tests
pytest tests/test_config.py tests/test_egg.py tests/test_mutation.py tests/test_scoring.py -v

# Run specific test file
pytest tests/test_egg.py -v

# Run specific test function
pytest tests/test_egg.py::test_egg_blocks_csam -v

# Run with coverage
pytest tests/test_config.py tests/test_egg.py tests/test_mutation.py tests/test_scoring.py --cov=app --cov-report=html
```

#### Integration Tests (Requires API Keys)

⚠️ **WARNING**: These tests make real API calls and incur costs.

```bash
# Set environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Run integration tests
pytest tests/test_real_backends.py -v

# Tests will be skipped if API keys are not set
```

### Test Coverage

Current test coverage:

| Module | Coverage |
|--------|----------|
| `app/core/config.py` | 100% |
| `app/core/egg.py` | 100% |
| `app/engines/scoring.py` | 100% |
| `app/engines/mutation.py` | 95% |
| `app/agents/*` | 85% (unit tests only) |

### Writing New Tests

#### Unit Test Example

```python
# tests/test_new_feature.py
import pytest
from app.core.new_feature import NewFeature

def test_new_feature_basic():
    """Test basic functionality."""
    feature = NewFeature()
    result = feature.do_something("input")
    assert result == "expected_output"

def test_new_feature_edge_case():
    """Test edge case handling."""
    feature = NewFeature()
    with pytest.raises(ValueError):
        feature.do_something("")

@pytest.mark.asyncio
async def test_new_feature_async():
    """Test async functionality."""
    feature = NewFeature()
    result = await feature.async_operation()
    assert result is not None
```

#### Integration Test Example

```python
# tests/test_integration.py
import pytest
import os

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
@pytest.mark.asyncio
async def test_openai_integration():
    """Test OpenAI integration with real API."""
    from app.agents.target import create_target
    
    target = create_target(
        backend_type="openai",
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-3.5-turbo"
    )
    
    response = await target.execute("Hello, how are you?")
    assert isinstance(response, str)
    assert len(response) > 0
```

---

## 🚢 Deployment

### Web UI Deployment (Vercel)

The Red Set ProtoCell Web UI can be easily deployed to Vercel for free:

#### Quick Deploy

1. **Push to GitHub** (if not already done)
2. **Go to [Vercel Dashboard](https://vercel.com/)**
3. **Import your repository**
   - Select `Arnoldlarry15/red-set-protocell`
4. **Configure**
   - Root Directory: `rsp-ui`
   - Framework: Vite (auto-detected)
   - Build Command: `npm run build`
   - Output Directory: `dist`
5. **Deploy**

Your app will be live at `https://your-project.vercel.app` in minutes!

📖 **Detailed Guide**: See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for complete deployment instructions.

#### Command Line Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy from rsp-ui directory
cd rsp-ui
vercel --prod
```

### Docker Deployment

#### Single Container

```bash
cd rsp-core

# Build image
docker build -t rsp-backend:latest backend/

# Run container
docker run -it --rm \
  -e OPENAI_API_KEY="sk-..." \
  rsp-backend:latest \
  python -m app.main --backend openai --api-key $OPENAI_API_KEY --rounds 10
```

#### Docker Compose

```bash
cd rsp-core

# Set environment variables
export OPENAI_API_KEY="sk-..."

# Run with Docker Compose
docker-compose run rsp-backend python -m app.main \
  --backend openai \
  --api-key $OPENAI_API_KEY \
  --rounds 10
```

### Production Deployment Considerations

#### 1. Environment Variables

Store sensitive credentials in environment variables, never in code:

```bash
# .env file (add to .gitignore!)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
RSP_MAX_ROUNDS=100
RSP_DB_PATH=/data/rsp_production.db
```

#### 2. Persistent Storage

Mount volumes for persistent data storage:

```yaml
# docker-compose.yaml
volumes:
  - ./data:/data
  - ./logs:/app/logs
```

#### 3. Resource Limits

Set appropriate resource limits:

```yaml
# docker-compose.yaml
services:
  rsp-backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

#### 4. Monitoring and Logging

Configure structured logging:

```python
import logging
import logging.handlers

# Rotate log files
handler = logging.handlers.RotatingFileHandler(
    'rsp.log',
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5
)
logging.basicConfig(handlers=[handler])
```

#### 5. Database Configuration

For production, consider PostgreSQL:

```python
config = RSPConfig()
config.storage.mode = StorageMode.POSTGRES
config.storage.postgres_connection_string = (
    "postgresql://user:pass@localhost:5432/rsp"
)
```

#### 6. API Rate Limiting

Implement delays to respect API rate limits:

```python
# In orchestrator
import asyncio

async def run_session(self):
    for round_num in range(self.max_rounds):
        # ... round execution ...
        await asyncio.sleep(1)  # 1 second between rounds
```

### Cloud Deployment

#### AWS ECS

```bash
# Build and push to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t rsp-backend .
docker tag rsp-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/rsp-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/rsp-backend:latest

# Deploy task definition with environment variables
```

#### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/<project-id>/rsp-backend
gcloud run deploy rsp-backend \
  --image gcr.io/<project-id>/rsp-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars OPENAI_API_KEY=<key>
```

#### Azure Container Instances

```bash
# Deploy to ACI
az container create \
  --resource-group rsp-resources \
  --name rsp-backend \
  --image <registry>/rsp-backend:latest \
  --environment-variables OPENAI_API_KEY=<key> \
  --cpu 2 --memory 4
```

---

## 🔍 Troubleshooting

### Common Issues

#### 1. "ImportError: No module named 'app'"

**Cause**: Running from wrong directory or missing Python path.

**Solution**:
```bash
# Ensure you're in rsp-core/backend directory
cd rsp-core/backend

# Run as module
python -m app.main --help
```

#### 2. "API key validation failed"

**Cause**: Invalid or missing API key.

**Solution**:
```bash
# Verify API key is set
echo $OPENAI_API_KEY

# Check key format
# OpenAI: starts with "sk-"
# Anthropic: starts with "sk-ant-"

# Test key directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

#### 3. "Rate limit exceeded"

**Cause**: Too many API requests in short time.

**Solution**:
```bash
# Reduce rounds or add delays
python -m app.main \
  --backend openai \
  --api-key $OPENAI_API_KEY \
  --rounds 10  # Reduce from default 100

# Or modify orchestrator to add delays between rounds
```

#### 4. "Database locked" error

**Cause**: SQLite database file in use by another process.

**Solution**:
```bash
# Use unique database path
python -m app.main \
  --backend openai \
  --api-key $OPENAI_API_KEY \
  --db-path session_$(date +%s).db

# Or switch to PostgreSQL for concurrent access
```

#### 5. "EGG blocked legitimate prompt"

**Cause**: False positive in pattern matching.

**Solution**:
```python
# Check blocked fingerprints in logs
# Adjust EGG patterns in app/core/egg.py if needed
# File an issue for persistent false positives
```

### Debug Mode

Enable verbose logging:

```python
# In app/main.py
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Change from INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Performance Optimization

#### Slow Execution

1. **Use faster models**: `gpt-3.5-turbo` instead of `gpt-4`
2. **Reduce max_tokens**: Lower token limits for faster responses
3. **Enable concurrent evaluation**: Set `concurrent_evaluations=True`
4. **Use local database**: Avoid network latency with SQLite

#### High API Costs

1. **Limit rounds**: Use `--rounds 10` for testing
2. **Use cheaper models**: GPT-3.5 instead of GPT-4
3. **Implement rate limiting**: Add delays between rounds
4. **Monitor usage**: Track API costs through provider dashboard

---

## ❓ FAQ

### General Questions

**Q: Is RSP safe to use?**
A: Yes. RSP is a defense-only system with mandatory ethical guardrails (EGG) that block harmful content. It does not generate real malware or exploits.

**Q: Do I need API keys?**
A: Yes. RSP requires real API keys from OpenAI or Anthropic. No mock/simulation backends are supported.

**Q: How much does it cost to run?**
A: Costs depend on your API provider and usage. A 100-round session with GPT-3.5-turbo typically costs $0.50-$2.00. Use `--rounds 10` for testing to minimize costs.

**Q: Can I run RSP offline?**
A: No. RSP requires internet access to communicate with LLM APIs. Local model support is not currently available.

**Q: Is my data kept private?**
A: Yes. RSP uses hashed fingerprinting for logging, and zero-retention mode (enabled by default) destroys all session data after completion. No data is sent to third parties except the target LLM API.

### Technical Questions

**Q: What Python version is required?**
A: Python 3.8 or higher. Python 3.10+ is recommended.

**Q: Can I add support for other LLMs?**
A: Yes! Implement the `TargetBackend` abstract class in `app/agents/target.py`. See [Development](#development) section for details.

**Q: How do I keep session data for analysis?**
A: Use `--no-zero-retention` flag and specify a database path:
```bash
python -m app.main --backend openai --api-key $KEY --no-zero-retention --db-path analysis.db
```

**Q: Can I run multiple sessions in parallel?**
A: Yes, but use unique database paths for each session to avoid conflicts.

**Q: How do I customize scoring weights?**
A: Modify the configuration programmatically or edit defaults in `app/core/config.py`. Weights must sum to 1.0.

**Q: What's the difference between Sniper and Spotter?**
A: Sniper generates adversarial prompts (attacker), while Spotter evaluates responses (defender). They operate independently under Orchestrator control.

### Deployment Questions

**Q: Can I deploy RSP in production?**
A: Yes. RSP is production-ready with proper error handling, logging, and safety mechanisms. See [Deployment](#deployment) section.

**Q: Does RSP support horizontal scaling?**
A: Currently, RSP is designed for single-instance operation. Distributed execution support is planned for future releases.

**Q: Can I use PostgreSQL instead of SQLite?**
A: Yes. Set `storage.mode = StorageMode.POSTGRES` and provide a connection string. PostgreSQL support is implemented but less tested than SQLite.

---

## 🤝 Contributing

We welcome contributions from the security research community! RSP is designed to be extensible and encourage responsible innovation.

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-capability`
3. **Make your changes**: Follow code style guidelines
4. **Add tests**: Ensure new code is tested
5. **Run test suite**: `pytest tests/ -v`
6. **Commit changes**: `git commit -m "Add new capability"`
7. **Push to branch**: `git push origin feature/new-capability`
8. **Open a Pull Request**: Describe your changes and motivation

### Contribution Guidelines

#### What We're Looking For

✅ **Encouraged Contributions:**
- New mutation strategies
- Additional attack domains
- New LLM backend integrations
- Improved evaluation heuristics
- Performance optimizations
- Documentation improvements
- Bug fixes
- Test coverage improvements

❌ **Discouraged Contributions:**
- Real exploit payloads
- Real malware generation
- Removal of safety guardrails
- Mechanisms to bypass EGG
- Changes that violate ethical constraints

#### Code Standards

1. **Follow PEP 8**: Use `black` for formatting
2. **Add docstrings**: Document all public functions and classes
3. **Write tests**: Maintain >90% test coverage
4. **Type hints**: Use type annotations where possible
5. **Security-first**: Never introduce unsafe capabilities

#### Testing Requirements

All contributions must include tests:

```bash
# Your tests should pass
pytest tests/ -v

# Coverage should not decrease
pytest tests/ --cov=app --cov-report=term-missing
```

### Ethical Review

All contributions undergo ethical review to ensure:
1. Compliance with defense-only principle
2. No real-world harm potential
3. Respect for safety boundaries
4. Alignment with research ethics

### Recognition

Contributors are recognized in:
- GitHub contributors list
- Release notes
- Academic citations (for significant contributions)

---

## 🔒 Security

### Reporting Security Issues

If you discover a security vulnerability in RSP, please report it responsibly:

**Email**: security@[domain].com (replace with actual security contact)

**DO NOT** open public GitHub issues for security vulnerabilities.

### Security Policy

1. **Ethical Use Only**: RSP is for defensive security research only
2. **API Key Security**: Never commit API keys to version control
3. **Data Privacy**: Enable zero-retention for sensitive tests
4. **Access Control**: Restrict access to API keys and session data
5. **Regular Updates**: Keep dependencies updated for security patches

### Security Features

- **Ethical Guardrail Governor**: Blocks harmful content
- **Content Fingerprinting**: Privacy-preserving logging
- **Zero-Retention Policy**: Automatic data destruction
- **Input Validation**: Sanitization of user inputs
- **Trust Boundaries**: Agents don't trust each other or their outputs

---

## 📄 License

Red Set ProtoCell is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 RSP Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

See [LICENSE](LICENSE) file for full text.

---

## 📖 Citation

If you use Red Set ProtoCell in your research or publications, please cite:

```bibtex
@software{red_set_protocell_2026,
  title = {Red Set ProtoCell: Autonomous AI Red Teaming System},
  author = {{RSP Contributors}},
  year = {2026},
  url = {https://github.com/Arnoldlarry15/red-set-protocell},
  version = {1.0.0},
  note = {Open-source AI safety platform for LLM red teaming}
}
```

---

## 🙏 Acknowledgments

Red Set ProtoCell builds upon research in:
- AI safety and alignment
- Adversarial machine learning
- Evolutionary computation
- Red teaming methodologies

Special thanks to the AI safety research community for inspiration and guidance.

---

## 📞 Contact

- **Issues**: [GitHub Issues](https://github.com/Arnoldlarry15/red-set-protocell/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Arnoldlarry15/red-set-protocell/discussions)
- **Security**: Use [GitHub Security Advisories](https://github.com/Arnoldlarry15/red-set-protocell/security/advisories/new) for private vulnerability reports

---

## 🗺️ Roadmap

### Current Release (v1.0.0)
- ✅ Multi-agent architecture (Sniper/Target/Spotter/Orchestrator)
- ✅ Ethical Guardrail Governor (EGG)
- ✅ 3-layer scoring taxonomy
- ✅ OpenAI and Anthropic API integration
- ✅ Six mutation strategies
- ✅ Seven attack domains
- ✅ Docker deployment
- ✅ Comprehensive test suite

### Recent Enhancements (v1.1.0)
- ✅ **Parallel Execution**: Concurrent round processing (5-10x speedup)
- ✅ **Pluggable Backends**: Local GGUF models (llama.cpp) and custom HTTP APIs
- ✅ **Adaptive Mutations**: Strategy performance tracking and learning
- ✅ **Enhanced Testing**: 50+ tests for edge cases and adversarial patterns
- ✅ **Epistemic Upgrades**: Score uncertainty and variance tracking (NEW)
  - Confidence intervals for all scores
  - Multi-pass agreement measurement
  - Cross-Spotter evaluation for disagreement detection
  - Scientific output format with uncertainty quantification
- ✅ **Time as First-Class Dimension**: Temporal analytics for model behavior (NEW)
  - Fatigue tracking: Does the model degrade over many rounds?
  - Regression detection: Compare model versions objectively
  - Score drift analysis: Identify performance trends over time
  - Answer questions like "Does this model get worse after sustained pressure?"

See [IMPROVEMENTS.md](IMPROVEMENTS.md) and [TIME_TRACKING.md](TIME_TRACKING.md) for detailed documentation.

### Latest Enhancements (v1.2.0) - Research Lab Features
- ✅ **Automated Benchmarking Suites**: Compare model versions over time with statistical analysis
  - Standard benchmark configurations (quick, standard, comprehensive, stress)
  - Automated result storage and comparison
  - Regression detection with statistical significance testing
- ✅ **Stronger Telemetry Abstraction**: Export metrics programmatically
  - CSV, JSON, and JSON Lines export formats
  - Database extraction API for sessions and rounds
  - Time series data export for analysis pipelines
- ✅ **Quantitative Uncertainty Metrics**: Already integrated!
  - Confidence intervals on all scores
  - Multi-pass agreement measurement
  - Cross-Spotter evaluation for disagreement detection
- ✅ **Formal Mutation Strategy Tuning**: Automatic strategy optimization
  - Performance tracking for each mutation strategy
  - Automatic weight recommendations based on effectiveness
  - Adaptive learning that improves over time
  - Priority strategy selection
- ✅ **Official Model Zoo**: Reference models for consistent benchmarking
  - Preconfigured OpenAI models (GPT-3.5, GPT-4, GPT-4 Turbo)
  - Preconfigured Anthropic models (Claude 3 Haiku, Sonnet, Opus)
  - Version tracking and comparison utilities
  - Easy configuration for benchmarking

See [NEW_FEATURES.md](NEW_FEATURES.md) for complete documentation and usage examples.

### Latest Enhancements (v1.3.0) - Dashboard & Management Features
- ✅ **Unified Infrastructure Dashboard**: Complete monitoring and analysis platform
  - Live session monitoring with auto-refresh
  - Historical session comparison and analysis
  - Model version comparison with statistical metrics
  - Export capabilities (CSV/JSON/JSONL)
- ✅ **User Roles & Permissions**: Fine-grained access control
  - Role-based authorization (Admin/Researcher/Observer)
  - User management interface
  - Authentication system with secure token management
  - Permission-based UI access control
- ✅ **Remote Triggering**: UI-based run control
  - Start runs from web interface with custom parameters
  - Save and load experiment configurations
  - Configure mutation weights and severity thresholds
  - Real-time feedback and monitoring

See [DASHBOARD_FEATURES.md](DASHBOARD_FEATURES.md) for complete documentation and [QUICKSTART_DASHBOARD.md](QUICKSTART_DASHBOARD.md) for a quick start guide.

### Planned Features (v1.4.0)
- [ ] ML-based classifiers for Spotter
- [ ] Additional mutation strategies
- [ ] More attack domains
- [ ] PostgreSQL integration hardening
- [ ] CLI commands for benchmarking and exports
- [ ] Advanced analytics visualizations

### Future Considerations (v2.0.0)
- [ ] Distributed execution support
- [ ] Real-time dashboard
- [ ] Custom strategy plugin system
- [ ] Integration with SIEM tools
- [ ] Automated report generation
- [ ] Multi-model comparative testing

---

## ⚠️ Disclaimer

**Red Set ProtoCell is an adversarial simulation environment, not an attack system.**

This tool is designed for:
- ✅ Defensive security research
- ✅ LLM safety testing
- ✅ Alignment evaluation
- ✅ Policy compliance verification

This tool is **NOT** designed for:
- ❌ Malicious use
- ❌ Breaking production systems
- ❌ Generating real exploits
- ❌ Bypassing legitimate safeguards

**Misuse of this tool for malicious purposes violates the license and may be illegal in your jurisdiction.**

All findings require external validation by qualified security researchers. RSP provides heuristic judgments, not ground truth.

Use responsibly. Test ethically. Build safer AI.

---

**Made with ❤️ by the AI Safety Community**
