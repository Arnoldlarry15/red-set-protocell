#!/usr/bin/env python3
"""
Example: Using New Features in Red Set ProtoCell

This script demonstrates the new improvements:
1. Parallel execution for faster processing
2. Custom HTTP backend support
3. Adaptive mutation strategy learning
"""

import asyncio
from app.core.config import RSPConfig, ModelBackend
from app.engines.mutation import MutationEngine
from app.agents.target import create_target


def example_1_parallel_execution():
    """Example 1: Enable parallel execution for faster sessions."""
    print("=" * 60)
    print("Example 1: Parallel Execution")
    print("=" * 60)

    config = RSPConfig()

    # Enable parallel execution (5 rounds at once)
    config.orchestrator.concurrent_rounds = 5
    config.orchestrator.max_rounds = 50

    print(f"Configuration:")
    print(f"  Max rounds: {config.orchestrator.max_rounds}")
    print(f"  Concurrent rounds: {config.orchestrator.concurrent_rounds}")
    print(f"  Expected speedup: ~{config.orchestrator.concurrent_rounds}x")
    print()

    # This would be used in setup_system()
    # orchestrator = setup_system(config)
    # await orchestrator.run_session()


def example_2_local_model():
    """Example 2: Use local GGUF model with llama.cpp."""
    print("=" * 60)
    print("Example 2: Local GGUF Model")
    print("=" * 60)

    # Note: This requires llama-cpp-python to be installed
    # and a GGUF model file available

    config = RSPConfig()
    config.target.backend = ModelBackend.LLAMA_CPP
    config.target.model_path = "/path/to/your/model.gguf"
    config.target.n_ctx = 2048
    config.target.n_gpu_layers = 35  # GPU acceleration

    print(f"Configuration:")
    print(f"  Backend: {config.target.backend.value}")
    print(f"  Model path: {config.target.model_path}")
    print(f"  Context size: {config.target.n_ctx}")
    print(f"  GPU layers: {config.target.n_gpu_layers}")
    print(f"  Benefits:")
    print(f"    - Zero API costs")
    print(f"    - Complete privacy")
    print(f"    - Offline operation")
    print()


def example_3_custom_http_api():
    """Example 3: Use custom HTTP API endpoint."""
    print("=" * 60)
    print("Example 3: Custom HTTP API")
    print("=" * 60)

    # Example: Using Ollama local API
    try:
        target = create_target(
            backend_type='custom_http',
            api_url='http://localhost:11434/api/generate',
            request_format='generic',
            max_tokens=500
        )

        print(f"Configuration:")
        print(f"  Backend: custom_http")
        print(f"  API URL: http://localhost:11434/api/generate")
        print(f"  Request format: generic")
        print(f"  Use cases:")
        print(f"    - Local Ollama server")
        print(f"    - vLLM inference server")
        print(f"    - text-generation-webui")
        print(f"    - Custom model APIs")
        print()

        # Test execution
        print("Backend created successfully!")

    except Exception as e:
        print(f"Note: Backend creation requires 'requests' package")
        print(f"Install with: pip install requests")
    print()


def example_4_adaptive_mutations():
    """Example 4: Enable adaptive mutation learning."""
    print("=" * 60)
    print("Example 4: Adaptive Mutation Strategies")
    print("=" * 60)

    # Create mutation engine with adaptive mode
    engine = MutationEngine(mutation_rate=0.8)
    engine.enable_adaptive_mode()

    print("Mutation engine with adaptive learning:")
    print(f"  Mutation rate: {engine.mutation_rate}")
    print(f"  Adaptive mode: {engine.adaptive_mode}")
    print()

    # Simulate some mutations and learning
    from app.engines.mutation import MutationStrategy

    print("Simulating strategy learning...")

    # Train with performance data
    for i in range(5):
        engine.update_strategy_performance(
            MutationStrategy.LEXICAL_VARIATION,
            0.85
        )
        engine.update_strategy_performance(
            MutationStrategy.ROLE_PLAY_FRAMING,
            0.65
        )
        engine.update_strategy_performance(
            MutationStrategy.OBFUSCATION,
            0.45
        )

    # Get statistics
    stats = engine.get_statistics()

    print("\nStrategy Performance:")
    for strategy, score in stats['strategy_performance'].items():
        print(f"  {strategy}: {score:.2f}")

    print("\nBenefit: System learns which strategies work best")
    print("         and automatically favors them over time.")
    print()


def example_5_combined():
    """Example 5: Combine all improvements together."""
    print("=" * 60)
    print("Example 5: Combined Configuration")
    print("=" * 60)

    config = RSPConfig()

    # Parallel execution
    config.orchestrator.concurrent_rounds = 3
    config.orchestrator.max_rounds = 30

    # Local model (or custom API)
    config.target.backend = ModelBackend.CUSTOM_HTTP
    config.target.api_url = 'http://localhost:8000/v1/completions'
    config.target.request_format = 'openai'

    print("Combined Configuration:")
    print(f"  Parallelism: {config.orchestrator.concurrent_rounds} concurrent rounds")
    print(f"  Backend: {config.target.backend.value}")
    print(f"  API: {config.target.api_url}")
    print()
    print("Expected Benefits:")
    print(f"  - {config.orchestrator.concurrent_rounds}x faster execution")
    print(f"  - Zero API costs with local model")
    print(f"  - Learning mutation strategies")
    print(f"  - Comprehensive test coverage")
    print()


def main():
    """Run all examples."""
    print("\n")
    print("=" * 60)
    print("Red Set ProtoCell - New Features Examples")
    print("=" * 60)
    print()

    example_1_parallel_execution()
    example_2_local_model()
    example_3_custom_http_api()
    example_4_adaptive_mutations()
    example_5_combined()

    print("=" * 60)
    print("For more details, see IMPROVEMENTS.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
