#!/usr/bin/env python3
"""
OpenRouter Backend Example

This example demonstrates how to use the OpenRouter backend with RSP.
OpenRouter provides access to multiple LLM providers through a unified API.

Prerequisites:
1. Install dependencies: pip install openai
2. Get an API key from https://openrouter.ai/
3. Set your API key as an environment variable or pass it directly

Usage:
    # Using environment variable
    export OPENROUTER_API_KEY="sk-or-v1-..."
    python openrouter_example.py
    
    # Or via command line
    python -m app.main --rounds 10 --backend openrouter --api-key "sk-or-v1-..." --model "openai/gpt-3.5-turbo"
"""

import asyncio
import os
from app.factories import TargetFactory


async def test_openrouter_backend():
    """Test OpenRouter backend with various models."""
    
    # Get API key from environment or use a placeholder for testing
    api_key = os.environ.get("OPENROUTER_API_KEY", "your-api-key-here")
    
    if api_key == "your-api-key-here":
        print("[!] Warning: Using placeholder API key. Set OPENROUTER_API_KEY environment variable.")
        print("[!] This example will fail without a valid API key.\n")
    
    # Available models on OpenRouter (examples)
    models = [
        "openai/gpt-3.5-turbo",       # OpenAI GPT-3.5
        "openai/gpt-4",                # OpenAI GPT-4
        "anthropic/claude-3-opus",     # Anthropic Claude 3 Opus
        "anthropic/claude-3-sonnet",   # Anthropic Claude 3 Sonnet
        "google/gemini-pro",           # Google Gemini Pro
        "meta-llama/llama-2-70b-chat", # Meta Llama 2
    ]
    
    print("=" * 60)
    print("OpenRouter Backend Example")
    print("=" * 60)
    print(f"API Key: {'****' if api_key != 'your-api-key-here' else 'Not set'}")
    print(f"Available models: {len(models)}")
    print()
    
    # Test with GPT-3.5 Turbo
    test_model = "openai/gpt-3.5-turbo"
    print(f"Testing with model: {test_model}")
    
    try:
        # Create Target using OpenRouter backend
        target = TargetFactory.create(
            backend_type="openrouter",
            api_key=api_key,
            model_name=test_model,
            max_tokens=100,
            temperature=0.7
        )
        
        backend_info = target.backend.get_backend_info()
        print(f"[OK] Backend created successfully")
        print(f"  Backend Type: {backend_info['backend_type']}")
        print(f"  Model: {backend_info['model_name']}")
        print(f"  Max Tokens: {backend_info['max_tokens']}")
        print(f"  Temperature: {backend_info['temperature']}")
        print()
        
        # Test execution
        if api_key != "your-api-key-here":
            print("Executing test prompt...")
            test_prompt = "Say hello in exactly 5 words."
            response = await target.execute(test_prompt)
            print(f"[OK] Response received: {response}")
        else:
            print("[!] Skipping execution test (no valid API key)")
            
    except ImportError as e:
        print(f"[!] Import Error: {e}")
        print("[!] Install required packages: pip install openai")
    except ValueError as e:
        print(f"[!] Configuration Error: {e}")
    except Exception as e:
        print(f"[!] Error: {e}")
    
    print()
    print("=" * 60)
    print("Example Models Available on OpenRouter:")
    print("=" * 60)
    for model in models:
        print(f"  - {model}")
    print()
    print("For more models, visit: https://openrouter.ai/models")
    print("For API documentation, visit: https://openrouter.ai/docs")


if __name__ == "__main__":
    print(__doc__)
    asyncio.run(test_openrouter_backend())
