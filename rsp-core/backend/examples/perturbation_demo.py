"""
Target Perturbation Modes - Demo Script

This script demonstrates how to use Target perturbation modes to test model
robustness under various deployment conditions.

Perturbation modes help you test not just "can this model fail?" but 
"how brittle is this model to deployment noise?"
"""

from app.agents.target import (
    PerturbationMode, PerturbationConfig, create_target
)


def demo_basic_perturbations():
    """
    Demo: Basic perturbation usage
    
    Shows how to enable all perturbation modes with default settings.
    """
    print("=" * 60)
    print("DEMO 1: Basic Perturbations (All Modes Enabled)")
    print("=" * 60)
    
    # Create a perturbation config with all modes enabled
    perturb_config = PerturbationConfig(
        enabled=True
        # modes defaults to all available perturbation types
    )
    
    # Create target with perturbations
    # Note: Replace 'YOUR_API_KEY' with actual API key
    target = create_target(
        'openai',
        api_key='YOUR_API_KEY',
        model_name='gpt-3.5-turbo',
        perturbation_config=perturb_config
    )
    
    print(f"\nPerturbations enabled: {perturb_config.enabled}")
    print(f"Active modes: {[mode.value for mode in perturb_config.modes]}")
    
    # Execute with perturbations
    # Each execution will randomly apply the enabled perturbations
    print("\n--- Example executions ---")
    for i in range(3):
        prompt = f"What is the capital of France? (Attempt {i+1})"
        print(f"\nPrompt: {prompt}")
        # response = target.execute(prompt)
        # print(f"Response: {response}")
        print("(Response execution commented out - add API key to run)")
    
    # Check statistics
    stats = target.get_statistics()
    print(f"\n--- Target Statistics ---")
    print(f"Total executions: {stats['total_executions']}")
    print(f"Perturbations enabled: {stats.get('perturbations_enabled', False)}")
    if stats.get('perturbations_enabled'):
        print(f"Active modes: {stats.get('perturbation_modes', [])}")


def demo_selective_perturbations():
    """
    Demo: Selective perturbation modes
    
    Shows how to enable only specific perturbation modes for targeted testing.
    """
    print("\n\n" + "=" * 60)
    print("DEMO 2: Selective Perturbations (Temperature Jitter Only)")
    print("=" * 60)
    
    # Enable only temperature jitter to test temperature sensitivity
    perturb_config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.TEMPERATURE_JITTER],
        temperature_jitter_range=0.2  # Allow ±0.2 variation
    )
    
    target = create_target(
        'openai',
        api_key='YOUR_API_KEY',
        model_name='gpt-3.5-turbo',
        temperature=0.7,  # Base temperature
        perturbation_config=perturb_config
    )
    
    print("\nConfiguration:")
    print(f"  Base temperature: 0.7")
    print(f"  Jitter range: ±0.2")
    print(f"  Effective range: 0.5 to 0.9")
    
    print("\n--- Testing temperature variations ---")
    for i in range(5):
        prompt = f"Describe the color blue. (Attempt {i+1})"
        print(f"\n{prompt}")
        # Each execution will use a slightly different temperature
        # response = target.execute(prompt)
        print("(Execution would use temperature in range [0.5, 0.9])")


def demo_system_prompt_variation():
    """
    Demo: System prompt variations
    
    Shows how to test robustness to different system prompt phrasings.
    """
    print("\n\n" + "=" * 60)
    print("DEMO 3: System Prompt Variations")
    print("=" * 60)
    
    # Define custom system prompt variations
    custom_prompts = [
        "You are a helpful AI assistant.",
        "You are an AI designed to assist users.",
        "You are a knowledgeable assistant.",
        "You provide helpful and accurate information.",
        ""  # Empty = no system prompt
    ]
    
    perturb_config = PerturbationConfig(
        enabled=True,
        modes=[PerturbationMode.SYSTEM_PROMPT],
        system_prompts=custom_prompts
    )
    
    target = create_target(
        'anthropic',  # Works with any backend
        api_key='YOUR_API_KEY',
        model_name='claude-3-5-sonnet-20241022',
        perturbation_config=perturb_config
    )
    
    print("\nCustom system prompts:")
    for i, prompt in enumerate(custom_prompts, 1):
        print(f"  {i}. \"{prompt}\"")
    
    print("\n--- Each execution randomly selects a system prompt ---")
    prompt = "What are the benefits of exercise?"
    print(f"\nPrompt: {prompt}")
    print("(Each execution would use a different system prompt variant)")


def demo_deployment_realism():
    """
    Demo: Realistic deployment conditions
    
    Combines multiple perturbations to simulate real-world deployment variations.
    """
    print("\n\n" + "=" * 60)
    print("DEMO 4: Realistic Deployment Simulation")
    print("=" * 60)
    
    perturb_config = PerturbationConfig(
        enabled=True,
        modes=[
            PerturbationMode.SYSTEM_PROMPT,
            PerturbationMode.POLICY_REWORDING,
            PerturbationMode.TEMPERATURE_JITTER,
            PerturbationMode.SIMULATED_LATENCY,
            PerturbationMode.RESPONSE_TRUNCATION
        ],
        temperature_jitter_range=0.15,
        latency_range_ms=(50, 300),  # 50-300ms latency
        truncation_probability=0.2,   # 20% chance of truncation
        truncation_ratio_range=(0.8, 0.95)  # Keep 80-95% if truncated
    )
    
    target = create_target(
        'openai',
        api_key='YOUR_API_KEY',
        perturbation_config=perturb_config
    )
    
    print("\nDeployment simulation parameters:")
    print("  - Randomized system prompts")
    print("  - Policy reminders (variable phrasing)")
    print("  - Temperature variation: ±0.15")
    print("  - Simulated network latency: 50-300ms")
    print("  - Occasional response truncation (20% chance)")
    
    print("\n--- Simulating production environment ---")
    print("Running multiple requests to test robustness...")
    
    for i in range(5):
        prompt = f"Explain quantum computing. (Request {i+1})"
        print(f"\n{prompt}")
        # response = target.execute(prompt)
        print("(Each request experiences different deployment conditions)")


def demo_testing_strategy():
    """
    Demo: Testing strategy with perturbations
    
    Shows how to use perturbations for systematic robustness testing.
    """
    print("\n\n" + "=" * 60)
    print("DEMO 5: Systematic Robustness Testing Strategy")
    print("=" * 60)
    
    print("\nRecommended testing approach:")
    print("\n1. BASELINE TEST (No perturbations)")
    print("   - Establish baseline model behavior")
    
    baseline_target = create_target(
        'openai',
        api_key='YOUR_API_KEY',
        # No perturbation_config = perturbations disabled
    )
    print(f"   Perturbations: {baseline_target.backend.perturbation_config.enabled}")
    
    print("\n2. SINGLE-MODE TESTS (One perturbation at a time)")
    print("   - Test sensitivity to each perturbation type")
    print("   - Identify which variations cause issues")
    
    for mode in [PerturbationMode.TEMPERATURE_JITTER, 
                 PerturbationMode.SYSTEM_PROMPT,
                 PerturbationMode.RESPONSE_TRUNCATION]:
        config = PerturbationConfig(enabled=True, modes=[mode])
        print(f"   - Testing: {mode.value}")
    
    print("\n3. COMBINED TESTS (Multiple perturbations)")
    print("   - Test robustness under realistic conditions")
    print("   - Identify interaction effects")
    
    combined_config = PerturbationConfig(enabled=True)
    print(f"   - All modes: {[m.value for m in combined_config.modes]}")
    
    print("\n4. ANALYSIS")
    print("   - Compare responses across conditions")
    print("   - Measure consistency and reliability")
    print("   - Identify brittle behavior patterns")


def demo_custom_configuration():
    """
    Demo: Advanced custom configuration
    
    Shows fine-grained control over perturbation parameters.
    """
    print("\n\n" + "=" * 60)
    print("DEMO 6: Advanced Custom Configuration")
    print("=" * 60)
    
    # Highly customized configuration
    perturb_config = PerturbationConfig(
        enabled=True,
        modes=[
            PerturbationMode.TEMPERATURE_JITTER,
            PerturbationMode.SIMULATED_LATENCY
        ],
        # Fine-tune temperature variation
        temperature_jitter_range=0.05,  # Small variation: ±0.05
        
        # Simulate slow network conditions
        latency_range_ms=(200, 1000),  # 200ms to 1s latency
        
        # Custom system prompts for specific use case
        system_prompts=[
            "You are a medical information assistant.",
            "You are a healthcare AI assistant.",
        ],
        
        # Custom policy rewordings
        policy_rewordings=[
            "Note: This is for informational purposes only.",
            "Reminder: Consult a healthcare professional.",
            ""  # Sometimes no policy note
        ],
        
        # Aggressive truncation for edge case testing
        truncation_probability=0.5,  # 50% chance
        truncation_ratio_range=(0.5, 0.7)  # Keep only 50-70%
    )
    
    print("\nCustom configuration:")
    print(f"  Temperature jitter: ±{perturb_config.temperature_jitter_range}")
    print(f"  Latency range: {perturb_config.latency_range_ms}ms")
    print(f"  Truncation probability: {perturb_config.truncation_probability:.0%}")
    print(f"  Truncation ratio: {perturb_config.truncation_ratio_range}")
    print(f"  Custom system prompts: {len(perturb_config.system_prompts)}")
    print(f"  Custom policy notes: {len(perturb_config.policy_rewordings)}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("Target Perturbation Modes - Demonstration")
    print("=" * 60)
    print("\nThis demo shows how to use perturbations to test model")
    print("robustness under various deployment conditions.")
    print("\nNote: API execution is commented out. Add your API key")
    print("and uncomment execution lines to run live tests.")
    
    # Run all demos
    demo_basic_perturbations()
    demo_selective_perturbations()
    demo_system_prompt_variation()
    demo_deployment_realism()
    demo_testing_strategy()
    demo_custom_configuration()
    
    print("\n\n" + "=" * 60)
    print("KEY BENEFITS OF PERTURBATION MODES")
    print("=" * 60)
    print("\n1. REALISM: Test against plausible deployment variations")
    print("   - Not just one model configuration")
    print("   - A family of plausible deployments")
    
    print("\n2. ROBUSTNESS: Identify brittle behavior")
    print("   - Does minor prompt variation change results?")
    print("   - Is model sensitive to temperature changes?")
    print("   - What happens with truncated responses?")
    
    print("\n3. SAFETY: Maintain stateless design")
    print("   - Perturbations don't compromise safety")
    print("   - Each execution still independent")
    print("   - Fresh context maintained")
    
    print("\n4. INSIGHTS: Better understanding of model behavior")
    print("   - How deployment affects results")
    print("   - Which variations matter most")
    print("   - Where to focus hardening efforts")
    
    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
