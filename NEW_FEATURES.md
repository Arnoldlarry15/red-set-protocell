# Red Set ProtoCell - New Features Documentation

This document describes the five major enhancements added to RSP to support research labs and safety teams.

## Overview

The following features have been implemented:

1. **Automated Benchmarking Suites** - Compare model versions over time
2. **Stronger Telemetry Abstraction** - Export metrics programmatically (CSV, JSON)
3. **Quantitative Uncertainty Metrics** - Confidence intervals and variance in scores
4. **Formal Mutation Strategy Tuning** - Automatic strategy weighting based on feedback
5. **Official Model Zoo** - Preconfigured reference models for consistent comparisons

---

## 1. Automated Benchmarking Suites

### Overview
Automated test harnesses that compare model versions over time, accelerating scientific evaluation.

### Features
- **Standard Benchmark Configurations**: Quick, standard, comprehensive, and stress benchmarks
- **Automated Execution**: Run benchmarks with consistent configurations
- **Result Storage**: JSON-based storage for benchmark results
- **Version Comparison**: Statistical comparison between model versions
- **Regression Detection**: Automatic detection of performance regressions

### Usage

```python
from app.benchmarking import (
    BenchmarkSuite,
    BenchmarkRunner,
    create_standard_benchmarks,
)
from app.main import setup_system
from app.core.config import get_default_config

# Create benchmark suite
suite = BenchmarkSuite(results_dir="benchmark_results")

# Get standard benchmark config
benchmarks = create_standard_benchmarks()
standard_config = benchmarks['standard']  # 50 rounds

# Setup RSP system
config = get_default_config()
config.target.backend = "openai"
config.target.api_key = "your-api-key"
config.target.model_name = "gpt-3.5-turbo"

orchestrator = setup_system(config)
runner = BenchmarkRunner(orchestrator)

# Run benchmark
result = await runner.run_benchmark(
    config=standard_config,
    model_name="gpt-3.5-turbo",
    model_version="0125",
    backend="openai"
)

# Save result
suite.save_result(result)

# Compare two versions
baseline = suite.load_result(Path("benchmark_v1.json"))
comparison = suite.load_result(Path("benchmark_v2.json"))
report = suite.compare_results(baseline, comparison)

print(report.verdict)  # IMPROVEMENT, REGRESSION, NO SIGNIFICANT CHANGE
print(report.recommendation)
```

### Standard Benchmarks
- **quick**: 10 rounds, 10-minute runtime
- **standard**: 50 rounds, 30-minute runtime
- **comprehensive**: 100 rounds, 1-hour runtime
- **stress**: 200 rounds with concurrency, 2-hour runtime

### Comparison Report Fields
- Score delta and percentage change
- Statistical significance
- Finding deltas (critical, high, medium, low)
- Execution time delta
- Automated verdict and recommendations

---

## 2. Stronger Telemetry Abstraction

### Overview
Programmatic API for extracting metrics in multiple formats for pipeline integration.

### Features
- **Multiple Export Formats**: CSV, JSON, JSON Lines
- **Database Extraction**: Extract metrics from session database
- **Metrics Snapshots**: Capture point-in-time metrics
- **Time Series Export**: Export round-level time series data
- **Flexible Filtering**: Filter by session, model version, etc.

### Usage

```python
from app.telemetry import (
    TelemetryExporter,
    ExportFormat,
    SessionMetricsExtractor,
)

# Export to CSV
exporter = TelemetryExporter(output_dir="exports")
metrics_data = [
    {'round': 1, 'score': 0.23, 'blocked': False},
    {'round': 2, 'score': 0.45, 'blocked': False},
]
filepath = exporter.export(metrics_data, ExportFormat.CSV)

# Export to JSON
session_summary = {
    'session_id': 'rsp_20260109',
    'total_rounds': 50,
    'average_score': 0.34,
}
filepath = exporter.export(session_summary, ExportFormat.JSON)

# Extract from database
extractor = SessionMetricsExtractor(database_path="rsp_session.db")
metrics = extractor.extract_session_metrics('rsp_20260109')

# List all sessions
sessions = extractor.list_sessions(model_version='gpt-3.5-turbo', limit=10)

# Export to string (in-memory)
csv_string = exporter.export_to_string(metrics_data, ExportFormat.CSV)
```

### Export Formats
- **CSV**: For spreadsheet analysis (Excel, Google Sheets)
- **JSON**: For programmatic processing
- **JSON Lines**: For streaming data pipelines

### Extracted Metrics
- Session-level: total rounds, average score, findings distribution
- Round-level: individual round scores, domains, timestamps
- Time series: score evolution over time
- Aggregate: summary statistics across sessions

---

## 3. Quantitative Uncertainty Metrics

### Overview
Confidence intervals and variance estimations for scores, enabling rigorous statistical analysis.

### Features
- **Score Uncertainty**: Every score includes uncertainty estimate
- **Confidence Intervals**: Lower and upper bounds for scores
- **Multi-Pass Agreement**: Consistency across multiple evaluations
- **Cross-Spotter Evaluation**: Disagreement detection between configurations
- **Layer-Level Uncertainty**: Uncertainty tracked for L1, L2, L3 layers

### Usage

```python
from app.engines.scoring import ScoringEngine, EvaluationResult

# The scoring engine already supports uncertainty
# Scores automatically include:
# - uncertainty: variance in the score
# - confidence_interval_lower: lower bound
# - confidence_interval_upper: upper bound

# Example evaluation result
result = EvaluationResult(
    l1_linguistic_safety=LayerScore(
        score=0.45,
        confidence=0.85,
        uncertainty=0.08,  # ±0.08
        confidence_interval_lower=0.37,
        confidence_interval_upper=0.53,
        indicators={},
        archetypes=[],
    ),
    # ... other layers ...
    global_score=0.52,
    global_uncertainty=0.06,
    global_confidence_interval=(0.46, 0.58),
    multi_pass_agreement=0.92,  # High agreement = reliable
)

# Interpret uncertainty
if result.global_uncertainty < 0.05:
    print("High confidence in score")
elif result.global_uncertainty < 0.10:
    print("Moderate confidence in score")
else:
    print("Low confidence - requires human review")

# Check agreement
if result.multi_pass_agreement > 0.9:
    print("Consistent evaluation across passes")
elif result.multi_pass_agreement < 0.7:
    print("Ambiguous - low agreement")
```

### Benefits
- **Statistical Rigor**: Enables proper scientific analysis
- **Audit-Friendly**: Shows confidence in assessments
- **Triage Support**: Prioritize low-confidence findings for review
- **Research-Ready**: Supports meta-analysis and comparison studies

### Uncertainty Interpretation
- `uncertainty < 0.05`: High confidence
- `uncertainty 0.05-0.10`: Moderate confidence
- `uncertainty > 0.10`: Low confidence (human review recommended)

---

## 4. Formal Mutation Strategy Tuning

### Overview
Automatic strategy weighting and optimization based on observed effectiveness.

### Features
- **Performance Tracking**: Track success rate for each strategy
- **Automatic Weighting**: Compute optimal weights based on feedback
- **Adaptive Learning**: Adjust weights over time
- **Priority Recommendations**: Suggest which strategies to focus on
- **Effectiveness Classification**: Excellent, Good, Fair, Poor

### Usage

```python
from app.strategy_tuning import (
    MutationStrategyAdvisor,
    StrategyOptimizer,
    OptimizationConfig,
)
from app.engines.mutation import MutationStrategy

# Create advisor
advisor = MutationStrategyAdvisor(
    success_threshold=0.4,  # Scores > 0.4 considered successful
    window_size=20,  # Track recent 20 attempts
)

# Record strategy attempts during session
advisor.record_attempt(MutationStrategy.LEXICAL, score=0.5)
advisor.record_attempt(MutationStrategy.ENCODING, score=0.2)

# Get recommendations
recommendation = advisor.get_recommendation()
print(recommendation.rationale)
print(recommendation.strategy_weights)

# Use optimizer for automatic adaptation
optimizer = StrategyOptimizer(advisor)

# Select strategy adaptively
strategy = optimizer.select_strategy()  # Uses current weights

# Update weights periodically
optimizer.update_weights()  # Adjust based on performance

# Get priority strategies
top_strategies = optimizer.suggest_priority_strategies(top_n=3)
```

### Strategy Effectiveness Levels
- **Excellent**: Success rate > 70%
- **Good**: Success rate 50-70%
- **Fair**: Success rate 30-50%
- **Poor**: Success rate < 30%

### Optimization Configuration
```python
config = OptimizationConfig(
    exploration_rate=0.1,  # 10% random exploration
    learning_rate=0.05,  # Gradual weight adjustment
    min_weight=0.05,  # Minimum weight per strategy
    max_weight=0.5,  # Maximum weight per strategy
)
```

---

## 5. Official Model Zoo

### Overview
Registry of reference models with preconfigured settings for consistent comparisons.

### Features
- **Preconfigured Models**: OpenAI and Anthropic models included
- **Version Tracking**: Track multiple versions per model
- **Model Comparison**: Compare capabilities and specifications
- **Easy Configuration**: Get RSP configs for any model
- **Provider Filtering**: Filter models by provider

### Usage

```python
from app.model_zoo import (
    ModelRegistry,
    get_all_reference_models,
)
from app.model_zoo.presets import create_default_registry

# Create registry with all reference models
registry = create_default_registry()

# List all models
all_models = registry.list_models()
for model in all_models:
    print(f"{model.display_name} - {model.description}")

# Get model config for RSP
config = registry.get_model_config(
    model_id="openai-gpt-3.5-turbo",
    version_id="gpt-3.5-turbo-0125"
)

# Use config with RSP
from app.core.config import RSPConfig
rsp_config = RSPConfig()
rsp_config.target.backend = config['backend']
rsp_config.target.model_name = config['model_name']

# Compare multiple models
comparison = registry.compare_models([
    "openai-gpt-3.5-turbo",
    "openai-gpt-4",
    "anthropic-claude-3-opus",
])
print(comparison)

# Filter by provider
from app.model_zoo.registry import ModelProvider
openai_models = registry.list_models(provider=ModelProvider.OPENAI)
```

### Reference Models Included

**OpenAI Models:**
- GPT-3.5 Turbo (16K context)
- GPT-4 (8K context)
- GPT-4 Turbo (128K context)

**Anthropic Models:**
- Claude 3 Haiku (200K context)
- Claude 3 Sonnet (200K context)
- Claude 3 Opus (200K context)

### Model Information Fields
- Display name and description
- Provider and backend type
- API model name
- Version history with release dates
- Capabilities (chat, function-calling, vision, etc.)
- Context window size
- Recommended use cases
- Optional benchmark baselines

---

## Integration Examples

### Complete Benchmark Workflow

```python
from app.benchmarking import BenchmarkSuite, BenchmarkRunner
from app.model_zoo.presets import create_default_registry
from app.telemetry import TelemetryExporter, ExportFormat

# Setup
suite = BenchmarkSuite()
registry = create_default_registry()
exporter = TelemetryExporter()

# Get model config
model_config = registry.get_model_config("openai-gpt-3.5-turbo")

# Run benchmark
result = await runner.run_benchmark(
    config=benchmarks['standard'],
    model_name=model_config['model_name'],
    model_version=model_config['model_version'],
    backend=model_config['backend'],
)

# Save and export
suite.save_result(result)
exporter.export(result.to_dict(), ExportFormat.JSON)
```

### Strategy Tuning in Session

```python
from app.strategy_tuning import MutationStrategyAdvisor, StrategyOptimizer

advisor = MutationStrategyAdvisor()
optimizer = StrategyOptimizer(advisor)

# During RSP session
for round_num in range(max_rounds):
    # Select strategy adaptively
    strategy = optimizer.select_strategy()
    
    # Use strategy in Sniper
    prompt = sniper.generate_with_strategy(strategy)
    
    # Execute and evaluate
    response = await target.execute(prompt)
    evaluation = spotter.evaluate(response)
    
    # Record performance
    advisor.record_attempt(strategy, evaluation.global_score)
    
    # Update weights periodically
    if round_num % 10 == 0:
        optimizer.update_weights()
```

---

## CLI Commands (Future Enhancement)

The features can be integrated into CLI:

```bash
# Run benchmark
python -m app.main benchmark \
  --config standard \
  --model openai-gpt-3.5-turbo \
  --version 0125

# Compare models
python -m app.main compare \
  --baseline benchmark_v1.json \
  --comparison benchmark_v2.json

# Export metrics
python -m app.main export \
  --session rsp_20260109 \
  --format csv \
  --output metrics.csv

# List models
python -m app.main models list --provider openai
```

---

## Files Added

### Benchmarking Module
- `app/benchmarking/__init__.py`
- `app/benchmarking/benchmark_suite.py`
- `app/benchmarking/benchmark_runner.py`

### Telemetry Module
- `app/telemetry/__init__.py`
- `app/telemetry/exporter.py`
- `app/telemetry/extractors.py`

### Strategy Tuning Module
- `app/strategy_tuning/__init__.py`
- `app/strategy_tuning/advisor.py`
- `app/strategy_tuning/optimizer.py`

### Model Zoo Module
- `app/model_zoo/__init__.py`
- `app/model_zoo/registry.py`
- `app/model_zoo/presets.py`

### Examples
- `examples/benchmarking_demo.py`
- `examples/telemetry_export_demo.py`
- `examples/strategy_tuning_demo.py`
- `examples/model_zoo_demo.py`

---

## Backward Compatibility

All new features are:
- **Additive**: No breaking changes to existing APIs
- **Optional**: Can be used independently or ignored
- **Compatible**: Work with existing RSP configurations
- **Minimal**: Small, focused modules with clear interfaces

---

## Testing

Run demos to verify functionality:

```bash
cd rsp-core/backend

# Test benchmarking
python examples/benchmarking_demo.py

# Test telemetry export
python examples/telemetry_export_demo.py

# Test strategy tuning
python examples/strategy_tuning_demo.py

# Test model zoo
python examples/model_zoo_demo.py
```

---

## Next Steps

1. **Integration**: Integrate features into main RSP workflow
2. **CLI Support**: Add command-line interface for new features
3. **Documentation**: Update main README with feature descriptions
4. **Testing**: Add comprehensive unit tests
5. **UI Integration**: Add features to web UI dashboard
