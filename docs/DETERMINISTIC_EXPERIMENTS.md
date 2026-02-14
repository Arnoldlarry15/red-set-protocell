# Running Deterministic Experiments with Different Backends

## Overview

The `run_deterministic_experiment.py` script now properly reads backend configuration from environment variables, allowing you to use OpenRouter, Anthropic, or other backends.

## Usage with OpenRouter

To run deterministic experiments with OpenRouter:

```bash
cd backend

# Set the backend type and API key
export BACKEND_TYPE=openrouter
export OPENROUTER_API_KEY="sk-or-v1-your-actual-key"

# Verify environment variables are set
echo $BACKEND_TYPE
echo $OPENROUTER_API_KEY

# Run the experiment (no --backend or --api-key flags needed!)
PYTHONPATH=$(pwd) python ../scripts/run_deterministic_experiment.py --verify --seed 15
```

## Usage with OpenAI (Default)

```bash
cd backend

# Set OpenAI API key (BACKEND_TYPE defaults to openai if not set)
export OPENAI_API_KEY="sk-your-openai-key"

# Run the experiment
PYTHONPATH=$(pwd) python ../scripts/run_deterministic_experiment.py --verify --seed 15
```

## Usage with Anthropic

```bash
cd backend

# Set the backend type and API key
export BACKEND_TYPE=anthropic
export ANTHROPIC_API_KEY="sk-ant-your-anthropic-key"

# Run the experiment
PYTHONPATH=$(pwd) python ../scripts/run_deterministic_experiment.py --verify --seed 15
```

## How It Works

The script now uses `load_config_from_env()` instead of `get_default_config()`, which means:

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

3. **Make sure you're using the latest version** of the script that imports `load_config_from_env`

## Available Backends

- `openai` - OpenAI GPT models (default)
- `anthropic` - Anthropic Claude models
- `openrouter` - OpenRouter (access to multiple providers)
- `llama_cpp` - Local GGUF models via llama-cpp-python
- `custom_http` - Custom HTTP API endpoint
