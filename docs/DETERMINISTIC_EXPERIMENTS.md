# Running Scripts with Different Backends

## Overview

All RSP scripts now properly read backend configuration from environment variables, allowing you to use OpenRouter, Anthropic, or other backends.

## Affected Scripts

The following scripts have been updated to use `load_config_from_env()`:

- `scripts/run_deterministic_experiment.py` - Deterministic 300-round experiments
- `scripts/run_experiment.py` - 300-round strategy selection experiments  
- `backend/examples/benchmarking.py` - Automated benchmarking
- `backend/examples/time_analytics.py` - Time-based analytics examples

## Usage with OpenRouter

To run any script with OpenRouter:

```bash
cd backend

# Set the backend type and API key
export BACKEND_TYPE=openrouter
export OPENROUTER_API_KEY="<OPENROUTER_API_KEY>"

# Verify environment variables are set
echo $BACKEND_TYPE
echo $OPENROUTER_API_KEY

# Run any script (no --backend or --api-key flags needed!)
PYTHONPATH=$(pwd) python ../scripts/run_deterministic_experiment.py --verify --seed 15
# OR
PYTHONPATH=$(pwd) python ../scripts/run_experiment.py
# OR
python examples/benchmarking.py
# OR
python examples/time_analytics.py
```

## Usage with OpenAI (Default)

```bash
cd backend

# Set OpenAI API key (BACKEND_TYPE defaults to openai if not set)
export OPENAI_API_KEY="<OPENAI_API_KEY>"

# Run any script
PYTHONPATH=$(pwd) python ../scripts/run_deterministic_experiment.py --verify --seed 15
python examples/benchmarking.py
```

## Usage with Anthropic

```bash
cd backend

# Set the backend type and API key
export BACKEND_TYPE=anthropic
export ANTHROPIC_API_KEY="<ANTHROPIC_API_KEY>"

# Run any script
PYTHONPATH=$(pwd) python ../scripts/run_deterministic_experiment.py --verify --seed 15
python examples/time_analytics.py
```

## How It Works

All scripts now use `load_config_from_env()` instead of `get_default_config()`, which means:

1. It reads the `BACKEND_TYPE` environment variable to determine which backend to use
2. It reads the appropriate API key environment variable (`OPENROUTER_API_KEY`, `OPENAI_API_KEY`, etc.)
3. The configuration is automatically applied - no command-line flags needed

## Verifying the Configuration

To verify that your environment is configured correctly:

```bash
cd backend
python -c "from app.core.config import load_config_from_env; import os; os.environ['BACKEND_TYPE']='openrouter'; os.environ['OPENROUTER_API_KEY']='test'; print(load_config_from_env().target.backend)"
```

This should print: `ModelBackend.OPENROUTER`

## Troubleshooting

If you still get "OpenAI key required" errors:

1. **Check environment variables are set**:
   ```bash
   echo $BACKEND_TYPE
   echo $OPENROUTER_API_KEY
   ```

2. **Verify the config loader works**:
   ```bash
   cd backend
   python -c "from app.core.config import load_config_from_env; print(load_config_from_env().target.backend)"
   ```

3. **Make sure you're using the latest version** of the scripts that import `load_config_from_env`:
   - scripts/run_deterministic_experiment.py
   - scripts/run_experiment.py
   - backend/examples/benchmarking.py
   - backend/examples/time_analytics.py

## Verification Script

Run the verification script to check that all scripts are properly configured:

```bash
python scripts/verify_all_scripts.py
```

This will verify:
- All scripts import `load_config_from_env`
- All scripts call `load_config_from_env()` 
- No scripts use `get_default_config`
- Config loader works with all backends

## Available Backends

- `openai` - OpenAI GPT models (default)
- `anthropic` - Anthropic Claude models
- `openrouter` - OpenRouter (access to multiple providers)
- `llama_cpp` - Local GGUF models via llama-cpp-python
- `custom_http` - Custom HTTP API endpoint
