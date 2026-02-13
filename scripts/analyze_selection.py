"""
Offline Analysis for Strategy Selection Dynamics

Analyzes logged data to answer:
1. Is selection collapsing? (effective_rank metric)
2. Is behavior dominating? (flip rate with correct normalization)
3. Are traits persisting? (adaptation failure detection)

Dependencies: numpy, matplotlib (for plotting)
"""

import json
import numpy as np

# Import matplotlib conditionally for plotting
try:
    import matplotlib.pyplot as plt
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("Warning: matplotlib not available. Plots will be skipped.")


def analyze_session(filename: str):
    """Analyze a single session's selection history."""

    # Load logs
    with open(filename, 'r') as f:
        logs = [json.loads(line) for line in f]

    print(f"\n=== Analyzing {filename} ===")
    print(f"Total rounds: {len(logs)}")

    # Question 1: Is selection collapsing?
    effective_ranks = [log['effective_rank'] for log in logs]

    if PLOTTING_AVAILABLE:
        plt.figure(figsize=(12, 4))
        plt.plot(effective_ranks)
        plt.axhline(y=2.0, color='r', linestyle='--',
                    label='Concentration threshold')
        plt.xlabel('Round')
        plt.ylabel('Effective Rank')
        plt.title(f'Strategy Diversity Over Time - {filename}')
        plt.legend()
        plt.savefig(f'effective_rank_{filename}.png')
        plt.close()

    print(f"\nMean effective rank: {np.mean(effective_ranks):.2f}")
    concentration_count = sum(1 for er in effective_ranks if er < 2.0)
    print(f"Concentration episodes (effective_rank < 2.0): "
          f"{concentration_count}/{len(effective_ranks)}")

    # Question 2: Is behavior dominating? (TRUE FLIP DETECTION)
    flip_count = 0
    flip_magnitudes = []

    for log in logs:
        candidates = log['candidates']

        # Winner WITH behavior bias
        winner_with_bias = max(candidates, key=lambda c: c['final_weight'])

        # Recompute weights WITHOUT behavior bias (enforce floor)
        weights_no_bias = [max(0.1, c['weight_without_behavior'])
                           for c in candidates]

        # Winner WITHOUT behavior bias
        winner_idx_no_bias = weights_no_bias.index(max(weights_no_bias))

        # True flip: different winners
        if winner_with_bias['strategy'] != candidates[winner_idx_no_bias]['strategy']:
            flip_count += 1

            # Measure magnitude with correct normalization
            prob_with = winner_with_bias['probability']
            total_no_bias = sum(weights_no_bias)
            prob_without = weights_no_bias[winner_idx_no_bias] / total_no_bias

            flip_magnitudes.append(abs(prob_with - prob_without))

    # Verify probability integrity
    for log in logs:
        candidates = log['candidates']
        weights_no_bias = [max(0.1, c['weight_without_behavior'])
                           for c in candidates]
        total = sum(weights_no_bias)
        probs_sum = sum(w / total for w in weights_no_bias)
        assert abs(probs_sum - 1.0) < 1e-6, \
            f"Round {log['round']}: probs sum to {probs_sum}"

    print("✓ All probability distributions valid")

    flip_rate = flip_count / len(logs)
    avg_magnitude = np.mean(flip_magnitudes) if flip_magnitudes else 0.0

    print(f"\nFlip rate (behavior bias changed winner): {flip_rate:.1%}")
    print(f"Average flip magnitude: {avg_magnitude:.3f}")

    if flip_rate < 0.05:
        print("→ Behavior bias too weak (< 5% influence)")
    elif flip_rate > 0.40:
        print("→ Behavior bias dominating (> 40% influence)")
    else:
        print("→ Behavior bias has healthy influence (5-40%)")

    # Question 3: Are traits persisting?
    trait_counts = {}
    window_size = 20

    for i in range(window_size, len(logs)):
        window = logs[i - window_size:i]

        for log in window:
            traits = log.get('behavioral_traits', {})
            for trait, assessment in traits.items():
                key = f"{trait}:{assessment}"
                trait_counts[key] = trait_counts.get(key, 0) + 1

    max_persistence = (max(trait_counts.values()) / window_size
                       if trait_counts else 0.0)

    print(f"\nMax trait persistence (any 20-round window): "
          f"{max_persistence:.0%}")

    if max_persistence > 0.60:
        most_persistent = max(trait_counts, key=trait_counts.get)
        print(f"→ WARNING: {most_persistent} triggering "
              f">{max_persistence:.0%} of rounds")

    return {
        'mean_effective_rank': np.mean(effective_ranks),
        'concentration_rate': concentration_count / len(logs),
        'flip_rate': flip_rate,
        'avg_flip_magnitude': avg_magnitude,
        'max_trait_persistence': max_persistence
    }


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        # Analyze specific session
        analyze_session(sys.argv[1])
    else:
        # Analyze all three experiment sessions
        print("=== 300-Round Experiment Analysis ===")

        sessions = ['A_default', 'B_weighted', 'C_control']
        all_results = {}

        for session in sessions:
            filename = f'selection_history_{session}.jsonl'
            try:
                all_results[session] = analyze_session(filename)
            except FileNotFoundError:
                print(f"\n⚠️ {filename} not found. Run experiment first.")

        # Comparative summary
        if len(all_results) == 3:
            print("\n" + "=" * 60)
            print("COMPARATIVE SUMMARY")
            print("=" * 60)

            for metric in ['mean_effective_rank', 'flip_rate',
                           'avg_flip_magnitude']:
                print(f"\n{metric}:")
                for session, results in all_results.items():
                    print(f"  {session}: {results[metric]:.3f}")
