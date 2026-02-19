# Time Tracking in Red Set ProtoCell

**Time as a First-Class Dimension**

Red Set ProtoCell now includes comprehensive time-based analytics to track model behavior over time. This feature makes time an explicit dimension in analysis, enabling detection of fatigue, regressions, and performance drift.

## Overview

Traditional red teaming treats runs as sequences without explicit time tracking. RSP's time analytics addresses three critical questions:

1. **"Does this model get worse after sustained pressure?"** → Fatigue Tracking
2. **"Did yesterday's model actually improve, or just shift failure modes?"** → Regression Detection  
3. **"What are the performance trends over long sessions?"** → Score Drift Analysis

## Features

### 1. Fatigue Tracking

**Purpose**: Detect if a model degrades in quality after many rounds of adversarial testing.

**How it works**:
- Compares scores from early rounds vs. late rounds
- Calculates degradation rate (linear trend)
- Identifies if model "fatigues" under sustained pressure

**Usage**:
```python
from app.analytics.time_tracking import FatigueTracker

tracker = FatigueTracker(database_path='rsp_session.db')
report = tracker.analyze_fatigue(session_id='rsp_20260109_123456')

print(f"Fatigued: {report.is_fatigued}")
print(f"Degradation rate: {report.degradation_rate:.4f} per round")
print(f"Early mean: {report.early_mean:.3f}")
print(f"Late mean: {report.late_mean:.3f}")
print(f"Recommendation: {report.recommendation}")
```

**Example Output**:
```
Fatigued: True
Degradation rate: 0.0042 per round
Early mean: 0.234
Late mean: 0.412
Recommendation: Model shows fatigue: 0.178 score increase from early to late rounds. Consider limiting session length.
```

**What it means**:
- `is_fatigued=True`: Model performance degraded significantly
- Positive degradation rate: Scores increased (worse) over time
- High fatigue score (>0.5): Severe degradation detected

### 2. Regression Detection

**Purpose**: Compare two model versions to determine if changes improved, regressed, or shifted failure modes.

**How it works**:
- Calculates mean scores for each version
- Computes statistical significance of difference
- Detects if variance patterns changed (failure mode shift)

**Usage**:
```python
from app.analytics.time_tracking import RegressionDetector

detector = RegressionDetector(database_path='rsp_session.db')
report = detector.compare_versions(
    baseline='gpt-4-v1',
    comparison='gpt-4-v2'
)

print(f"Verdict: {report.verdict}")
print(f"Score delta: {report.score_delta:+.3f}")
print(f"Is regression: {report.is_regression}")
print(f"Failure mode shift: {report.failure_mode_shift}")
```

**Verdicts**:
- `IMPROVEMENT`: New version has significantly lower scores (better)
- `REGRESSION`: New version has significantly higher scores (worse)
- `NEUTRAL`: Minimal change, neither improvement nor regression
- `SHIFT`: Scores changed but failure patterns shifted

**Example Output**:
```
Verdict: IMPROVEMENT
Score delta: -0.142
Is regression: False
Failure mode shift: False
```

### 3. Score Drift Analysis

**Purpose**: Identify performance trends across sessions or extended testing periods.

**How it works**:
- Calculates trend slope (linear regression)
- Measures variance and volatility
- Classifies drift direction

**Usage**:
```python
from app.analytics.time_tracking import ScoreDriftAnalyzer

analyzer = ScoreDriftAnalyzer(database_path='rsp_session.db')
metrics = analyzer.analyze_drift(session_id='rsp_20260109_123456')

print(f"Drift direction: {metrics.drift_direction.value}")
print(f"Trend slope: {metrics.trend_slope:+.4f}")
print(f"Mean score: {metrics.mean_score:.3f}")
print(f"Std deviation: {metrics.std_deviation:.3f}")
```

**Drift Directions**:
- `IMPROVING`: Scores decreasing over time (better)
- `DEGRADING`: Scores increasing over time (worse)
- `STABLE`: No significant trend
- `VOLATILE`: High variance, no clear trend

**Example Output**:
```
Drift direction: degrading
Trend slope: +0.0038
Mean score: 0.345
Std deviation: 0.089
```

## Integration with Orchestrator

Time analytics are automatically integrated into session statistics:

```python
# Run a session
orchestrator = setup_system(config)
stats = await orchestrator.run_session()

# Time analytics are included in stats
if 'time_analytics' in stats:
    fatigue = stats['time_analytics']['fatigue']
    drift = stats['time_analytics']['drift']
    
    print(f"Fatigue detected: {fatigue['is_fatigued']}")
    print(f"Drift direction: {drift['drift_direction']}")
```

## Database Schema

The database schema has been extended to support time tracking:

```sql
CREATE TABLE rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    round_number INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    attack_domain TEXT NOT NULL,
    target_response TEXT NOT NULL,
    evaluation TEXT NOT NULL,
    global_score REAL NOT NULL,
    blocked_by_egg INTEGER NOT NULL,
    timestamp TEXT NOT NULL,
    model_version TEXT DEFAULT 'unknown',  -- NEW
    session_start_time TEXT                -- NEW
)
```

### New Fields:
- `model_version`: Identifier for the model being tested (e.g., "gpt-4-v1", "claude-3-opus")
- `session_start_time`: ISO timestamp of session start for duration calculations

## Command-Line Usage

### Specify Model Version

```bash
python -m app.main \
    --backend openai \
    --api-key $OPENAI_API_KEY \
    --model gpt-4 \
    --model-version "gpt-4-v1.0-2026-01-09" \
    --rounds 50
```

### Disable Zero-Retention for Analysis

```bash
python -m app.main \
    --backend openai \
    --api-key $OPENAI_API_KEY \
    --no-zero-retention \
    --db-path analysis_session.db \
    --rounds 100
```

## Examples

### Example 1: Detect Model Fatigue

```python
import asyncio
from app.main import setup_system
from app.core.config import get_default_config
from app.analytics.time_tracking import FatigueTracker

async def test_fatigue():
    # Run long session
    config = get_default_config()
    config.orchestrator.max_rounds = 100
    config.storage.zero_retention = False
    
    orchestrator = setup_system(config)
    await orchestrator.run_session()
    
    # Analyze fatigue
    tracker = FatigueTracker(config.storage.database_path)
    report = tracker.analyze_fatigue(orchestrator.state_manager.session_id)
    
    if report.is_fatigued:
        print(f"⚠️  Model shows fatigue after {report.rounds_analyzed} rounds")
        print(f"   Degradation: {report.degradation_rate:.4f} per round")

asyncio.run(test_fatigue())
```

### Example 2: Compare Model Versions

```python
from app.analytics.time_tracking import RegressionDetector

# After running sessions with different model versions
detector = RegressionDetector('production.db')

# Compare v1 to v2
report = detector.compare_versions('model-v1', 'model-v2')

if report.verdict == "REGRESSION":
    print(f"⚠️  Regression detected!")
    print(f"   Score increased by {report.score_delta:+.3f}")
elif report.verdict == "IMPROVEMENT":
    print(f"✓ Model improved!")
    print(f"   Score decreased by {abs(report.score_delta):.3f}")
```

### Example 3: Monitor Drift Across Sessions

```python
from app.analytics.time_tracking import ScoreDriftAnalyzer

analyzer = ScoreDriftAnalyzer('monitoring.db')

# Compare multiple sessions
results = analyzer.analyze_session_comparison([
    'session_monday',
    'session_tuesday',
    'session_wednesday'
])

for session_id, metrics in results.items():
    print(f"{session_id}:")
    print(f"  Direction: {metrics.drift_direction.value}")
    print(f"  Mean: {metrics.mean_score:.3f}")
    print(f"  Trend: {metrics.trend_slope:+.4f}")
```

## Best Practices

### 1. Set Meaningful Model Versions

Use descriptive version identifiers that include:
- Model name
- Version number
- Date of deployment
- Configuration details

Example: `gpt-4-turbo-v2024-01-09-temp0.7`

### 2. Disable Zero-Retention for Analysis

When comparing versions or analyzing trends, disable zero-retention:

```python
config.storage.zero_retention = False
config.storage.database_path = 'analysis.db'
```

### 3. Run Sufficient Rounds

For reliable analytics:
- **Fatigue detection**: Minimum 20 rounds
- **Regression detection**: Minimum 10 rounds per version
- **Drift analysis**: Minimum 15 rounds

### 4. Use Consistent Test Conditions

For accurate comparisons:
- Same number of rounds
- Same attack domains
- Same configuration (temperature, max_tokens, etc.)

### 5. Monitor Time Span

Long time spans between rounds can affect results. Keep round execution time consistent.

## Performance Impact

Time analytics have minimal performance impact:
- Analysis is performed after session completion
- No overhead during round execution
- Database queries are optimized with indexes
- Memory usage: < 10MB for analysis

## Troubleshooting

### Issue: "Insufficient data for fatigue analysis"

**Solution**: Run more rounds (minimum 4, recommended 20+)

### Issue: Regression detector returns "INSUFFICIENT_DATA"

**Solution**: Ensure both model versions have recorded rounds in the database

### Issue: Time analytics not appearing in stats

**Solution**: Check that:
1. Zero-retention is disabled or analytics ran before cleanup
2. Database has rounds for the session
3. No exceptions in logs during analytics computation

## API Reference

### FatigueTracker

```python
class FatigueTracker:
    def __init__(self, database_path: str = "rsp_session.db")
    
    def analyze_fatigue(
        self,
        session_id: str,
        fatigue_threshold: float = 0.15
    ) -> FatigueReport
```

### RegressionDetector

```python
class RegressionDetector:
    def __init__(self, database_path: str = "rsp_session.db")
    
    def compare_versions(
        self,
        baseline: str,
        comparison: str,
        significance_threshold: float = 0.05
    ) -> RegressionReport
```

### ScoreDriftAnalyzer

```python
class ScoreDriftAnalyzer:
    def __init__(self, database_path: str = "rsp_session.db")
    
    def analyze_drift(
        self,
        session_id: str,
        window_size: int = 10
    ) -> TimeSeriesMetrics
    
    def analyze_session_comparison(
        self,
        session_ids: List[str]
    ) -> Dict[str, TimeSeriesMetrics]
```

## Future Enhancements

Planned improvements:
- [ ] Real-time fatigue monitoring during sessions
- [ ] Automated regression alerts
- [ ] Time-series visualization dashboard
- [ ] Multi-session trend analysis
- [ ] Anomaly detection in score patterns
- [ ] Export to time-series databases (InfluxDB, Prometheus)

## Related Documentation

- [README.md](../README.md) - Main documentation
- `IMPROVEMENTS.md` (archived reference: ../IMPROVEMENTS.md) - Other enhancements
- `examples/time_analytics.py` (archived reference: ../rsp-core/backend/examples/time_analytics.py) - Example script

## Questions Answered

✅ **"Does this model get worse after sustained pressure?"**
→ Use FatigueTracker to detect degradation over rounds

✅ **"Did yesterday's model actually improve, or just shift failure modes?"**
→ Use RegressionDetector to compare versions objectively

✅ **"What are the performance trends?"**
→ Use ScoreDriftAnalyzer to identify drift direction

---

**Time analytics make RSP uniquely capable of answering temporal questions about model behavior that few other tools address.**
