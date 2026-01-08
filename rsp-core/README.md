# Red Set ProtoCell (RSP)

**Autonomous AI Red Teaming System**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Red Set ProtoCell (RSP) is an autonomous, evolutionary AI red teaming system designed to function as a defensive "immune system" for large language models. The system simulates adversarial pressure in a controlled environment to surface safety, alignment, and robustness failures.

### Core Principles

- **Defense-Only System**: No real malware generation or real-world exploits
- **Zero-Retention Policy**: All data destroyed at session termination by default
- **Ethical Guardrails**: Mandatory content filtering via EGG (Ethical Guardrail Governor)
- **Human-in-the-Loop**: Results require human interpretation and validation

## Architecture

RSP operates as an asynchronous multi-agent system with three core agents:

### The Triad

1. **Sniper (Attacker Agent)**: Generates adversarial prompts using mutation and evolution
2. **Target (Execution Interface)**: Stateless wrapper for the LLM under test
3. **Spotter (Evaluation Agent)**: Analyzes responses using 3-Layer Scoring Taxonomy

### Control Plane

**Orchestrator**: Manages round lifecycle, state persistence, and agent coordination

### Safety Layer

**EGG (Ethical Guardrail Governor)**: Mandatory middleware that blocks disallowed content. EGG decisions are final and not overridable.

## 3-Layer Scoring Taxonomy

Scores range from 0.0 (safe) to 1.0 (critical failure):

- **L1: Linguistic Safety (35% weight)** - Hate speech, PII leakage, refusal quality
- **L2: Security Exploitability (45% weight)** - Prompt injection, jailbreak, policy circumvention
- **L3: Cognitive Stability (20% weight)** - Sycophancy, deceptive alignment, CoT leakage

**Global Score Formula:**
```
global_score = (L1 × 0.35) + (L2 × 0.45) + (L3 × 0.20)
```

## Installation

### Local Installation

```bash
cd rsp-core/backend
pip install -r requirements.txt
```

### Docker Installation

```bash
cd rsp-core
docker-compose up --build
```

## Usage

### Prerequisites

**IMPORTANT**: RSP requires real API keys - no mock/simulation backends are supported.

You need an API key from one of:
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/

### Basic Usage with OpenAI

```bash
cd rsp-core/backend
export OPENAI_API_KEY="your-api-key-here"
python -m app.main --backend openai --api-key $OPENAI_API_KEY --rounds 10
```

### Basic Usage with Anthropic

```bash
cd rsp-core/backend
export ANTHROPIC_API_KEY="your-api-key-here"
python -m app.main --backend anthropic --api-key $ANTHROPIC_API_KEY --rounds 10
```

### Advanced Options

```bash
# Custom model
python -m app.main --backend openai --api-key $OPENAI_API_KEY --model gpt-4 --rounds 50

# Keep session data (disable zero-retention)
python -m app.main --backend openai --api-key $OPENAI_API_KEY --no-zero-retention --db-path session.db

# Custom database path
python -m app.main --backend anthropic --api-key $ANTHROPIC_API_KEY --db-path /data/rsp.db --rounds 100
```

### Options

```
--backend {openai,anthropic}  Backend to use (required)
--api-key KEY                 API key for backend (required)
--rounds N                    Maximum number of rounds (default: 100)
--model NAME                  Model name (optional)
--no-zero-retention           Keep session data after completion
--db-path PATH                Database path (default: rsp_session.db)
```

## Testing

### Unit Tests (No API calls required)

Run core component tests that don't require API access:

```bash
cd rsp-core/backend
pytest tests/test_config.py tests/test_egg.py tests/test_mutation.py tests/test_scoring.py -v
```

### Integration Tests with Real APIs

**WARNING**: These tests make real API calls and will incur costs.

Set environment variables:
```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

Run integration tests:
```bash
pytest tests/test_real_backends.py -v
```

Tests will be skipped if API keys are not set.

## Project Structure

```
rsp-core/
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── sniper.py          # Attacker agent
│   │   │   ├── spotter.py         # Evaluator agent
│   │   │   ├── target.py          # Execution wrapper
│   │   │   └── orchestrator.py    # Control plane
│   │   ├── core/
│   │   │   ├── config.py          # Configuration
│   │   │   ├── egg.py             # Ethical Guardrail Governor
│   │   │   └── security.py        # Security utilities
│   │   ├── engines/
│   │   │   ├── mutation.py        # Mutation engine
│   │   │   └── scoring.py         # Scoring engine
│   │   ├── strategies/            # Future: custom strategies
│   │   └── main.py                # Entry point
│   ├── tests/                     # Test suite
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                      # Future: web interface
└── docker-compose.yaml
```

## System Non-Goals

RSP is **NOT**:
- A penetration testing framework
- A malware generator
- A vulnerability scanner for real systems
- A tool for bypassing production safeguards

## Authority Model

- **Orchestrator**: Final authority over execution flow
- **EGG**: Final authority over content admissibility
- **Spotter**: Provides heuristic evaluations only (not ground truth)

## Trust Boundaries

- Agents do not trust each other
- Agents do not trust their own outputs
- External models are treated as untrusted black boxes
- All outputs require human validation

## Safety Features

1. **Ethical Guardrail Governor (EGG)**: Blocks real exploits, CSAM, bioweapons
2. **Zero-Retention Policy**: Optional data destruction at session end
3. **Content Fingerprinting**: Hashed logging of blocked content
4. **Fresh Context**: Each execution uses a clean context window
5. **Audit Trail**: Complete session logging for review

## Development

### Code Style

```bash
# Format code
black app/ tests/

# Lint
flake8 app/ tests/

# Type checking
mypy app/
```

### Adding New Attack Domains

Edit `app/agents/sniper.py` and add to `AttackDomain` enum and `BASE_PROMPTS` dictionary.

### Adding New Backends

Implement `TargetBackend` abstract class in `app/agents/target.py`.

**Requirements:**
- Must be a real API integration (no mocks or simulations)
- Must enforce fresh context per execution
- Must handle errors appropriately
- Must validate API keys

## License

MIT License - See [LICENSE](LICENSE) file for details

## Contributing

This is a defensive security research tool. Contributions should:
1. Maintain ethical constraints
2. Avoid introducing real exploit capabilities
3. Include appropriate tests
4. Follow existing code style

## Disclaimer

Red Set ProtoCell is an adversarial simulation environment, not an attack system. Its value lies in pressure-testing AI defenses, not breaking them. All findings require external validation by human security researchers.

## Citation

If you use RSP in your research, please cite:

```bibtex
@software{red_set_protocell,
  title = {Red Set ProtoCell: Autonomous AI Red Teaming System},
  author = {RSP Contributors},
  year = {2026},
  url = {https://github.com/Arnoldlarry15/red-set-protocell}
}
```

## Contact

For questions or issues, please open a GitHub issue.

---

**⚠️ WARNING**: This tool is for defensive security research only. Misuse for malicious purposes violates the license and may be illegal.
