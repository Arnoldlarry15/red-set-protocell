"""Tests for the isolated orchestration interface scaffolding.

These tests keep coverage for the newly-added orchestration interface modules
without introducing business logic implementations.
"""

import asyncio

from app.orchestration import (
    AgentDescriptor,
    AgentState,
    ExperimentConfig,
    IterationResult,
    OrchestratorContext,
)
from app.orchestration.agent_manager import SniperLifecycleManager, get_sniper_lifecycle_example_usage


class DummyAgentManager:
    """Minimal stub that satisfies the agent manager interface shape."""

    def __init__(self):
        self._snapshot = {}

    def register(self, name, instance, metadata=None):
        metadata = dict(metadata or {})
        self._snapshot[name] = AgentDescriptor(name=name, instance=instance, metadata=metadata)

    def initialize_all(self):
        for desc in self._snapshot.values():
            desc.state = AgentState.INITIALIZED

    def start_all(self):
        for desc in self._snapshot.values():
            desc.state = AgentState.RUNNING

    def stop_all(self):
        for desc in self._snapshot.values():
            desc.state = AgentState.STOPPED

    def teardown_all(self):
        self._snapshot.clear()

    def get_snapshot(self):
        return dict(self._snapshot)


class DummyExperimentRunner:
    """Minimal stub that satisfies the experiment runner interface shape."""

    def __init__(self):
        self.config = None
        self.stopped = False

    def configure(self, config):
        self.config = config

    async def run(self):
        return [IterationResult(iteration=1, status="ok")]

    async def run_iteration(self, iteration, context=None):
        _ = context
        return IterationResult(iteration=iteration, status="ok")

    def stop(self):
        self.stopped = True


def test_agent_descriptor_defaults_and_states():
    descriptor = AgentDescriptor(name="sniper", instance=object())

    assert descriptor.name == "sniper"
    assert descriptor.state == AgentState.REGISTERED
    assert descriptor.metadata == {}
    assert AgentState.ERROR.value == "error"


def test_experiment_config_defaults():
    config = ExperimentConfig(experiment_id="exp-001")

    assert config.experiment_id == "exp-001"
    assert config.max_iterations == 100
    assert config.stop_on_error is True
    assert config.tags == []
    assert config.parameters == {}


def test_iteration_result_defaults():
    result = IterationResult(iteration=2, status="running")

    assert result.iteration == 2
    assert result.status == "running"
    assert result.started_at
    assert result.ended_at is None
    assert result.metrics == {}
    assert result.error is None


def test_orchestrator_context_container():
    manager = DummyAgentManager()
    runner = DummyExperimentRunner()

    context = OrchestratorContext(agent_manager=manager, experiment_runner=runner)

    assert context.agent_manager is manager
    assert context.experiment_runner is runner


def test_dummy_agent_manager_lifecycle_flow():
    manager = DummyAgentManager()
    agent_instance = object()

    manager.register("spotter", agent_instance, metadata={"role": "evaluator"})
    snapshot = manager.get_snapshot()
    assert "spotter" in snapshot
    assert snapshot["spotter"].metadata["role"] == "evaluator"

    manager.initialize_all()
    assert manager.get_snapshot()["spotter"].state == AgentState.INITIALIZED

    manager.start_all()
    assert manager.get_snapshot()["spotter"].state == AgentState.RUNNING

    manager.stop_all()
    assert manager.get_snapshot()["spotter"].state == AgentState.STOPPED

    manager.teardown_all()
    assert manager.get_snapshot() == {}


class DummySniper:
    """Minimal Sniper-compatible async stub."""

    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.calls = 0

    async def generate_prompt(self, prior_metadata=None):
        _ = prior_metadata
        self.calls += 1
        if self.should_fail:
            raise RuntimeError("boom")
        return f"prompt-{self.calls}", "domain"


def test_sniper_lifecycle_manager_spawn_and_iterations():
    manager = SniperLifecycleManager(default_iterations=2)

    names = manager.spawn_snipers(DummySniper, count=3, name_prefix="sniper")
    assert names == ["sniper_1", "sniper_2", "sniper_3"]

    manager.initialize_all()
    results = asyncio.run(manager.run_all_agents(prior_metadata=[]))

    assert all(snapshot.state == AgentState.COMPLETED for snapshot in manager.get_snapshot().values())
    assert results["sniper_1"]["iterations_requested"] == 2
    assert results["sniper_1"]["iterations_completed"] == 2


def test_sniper_lifecycle_manager_failure_state_tracking():
    manager = SniperLifecycleManager(default_iterations=1)
    manager.register("sniper_bad", DummySniper(should_fail=True))
    manager.initialize_all()

    result = asyncio.run(manager.run_agent("sniper_bad", prior_metadata=[]))

    assert manager.get_snapshot()["sniper_bad"].state == AgentState.FAILED
    assert result["error"] == "boom"


def test_sniper_lifecycle_manager_per_agent_iterations_and_example_usage():
    manager = SniperLifecycleManager(default_iterations=1)
    manager.register("sniper_custom", DummySniper())
    manager.initialize_all()
    manager.set_iterations("sniper_custom", 4)

    result = asyncio.run(manager.run_agent("sniper_custom", prior_metadata=[]))

    assert result["iterations_requested"] == 4
    assert result["iterations_completed"] == 4

    example = get_sniper_lifecycle_example_usage()
    assert "spawn_snipers" in example
    assert "run_all_agents" in example


class DummyTarget:
    """Minimal Target-compatible async stub."""

    async def execute(self, prompt, **kwargs):
        _ = kwargs
        return f"response-for:{prompt}"


class DummySpotter:
    """Minimal Spotter-compatible async stub with call tracking."""

    def __init__(self, score=0.3):
        self.score = score
        self.calls = 0

    async def evaluate(self, response, attack_domain, prompt):
        _ = response
        _ = attack_domain
        _ = prompt
        self.calls += 1
        return {
            "l1": {"score": self.score},
            "l2": {"score": self.score},
            "l3": {"score": self.score},
            "global_score": self.score,
        }


def test_iterative_loop_engine_max_iterations_and_output_passing(caplog):
    from app.orchestration.experiment_runner import ExperimentConfig, IterativeAttackLoopEngine

    caplog.set_level("INFO")

    sniper = DummySniper()
    target = DummyTarget()
    spotter = DummySpotter(score=0.2)

    engine = IterativeAttackLoopEngine(sniper=sniper, target=target, spotter=spotter)
    engine.configure(
        ExperimentConfig(
            experiment_id="exp-loop-1",
            max_iterations=3,
            parameters={"exploit_score_threshold": 0.9, "failure_threshold": 5},
        )
    )

    results = asyncio.run(engine.run())

    assert len(results) == 3
    assert all(r.status == "completed" for r in results)
    assert spotter.calls == 3
    assert "loop.iteration.spotter_evaluated" in caplog.text


def test_iterative_loop_engine_successful_exploit_stop():
    from app.orchestration.experiment_runner import ExperimentConfig, IterativeAttackLoopEngine

    sniper = DummySniper()
    target = DummyTarget()
    spotter = DummySpotter(score=0.95)

    engine = IterativeAttackLoopEngine(sniper=sniper, target=target, spotter=spotter)
    engine.configure(
        ExperimentConfig(
            experiment_id="exp-loop-2",
            max_iterations=10,
            parameters={"exploit_score_threshold": 0.8, "failure_threshold": 5},
        )
    )

    results = asyncio.run(engine.run())

    assert len(results) == 1
    assert results[0].metrics["global_score"] == 0.95


def test_iterative_loop_engine_failure_threshold_stop():
    from app.orchestration.experiment_runner import ExperimentConfig, IterativeAttackLoopEngine

    failing_sniper = DummySniper(should_fail=True)
    target = DummyTarget()
    spotter = DummySpotter(score=0.1)

    engine = IterativeAttackLoopEngine(sniper=failing_sniper, target=target, spotter=spotter)
    engine.configure(
        ExperimentConfig(
            experiment_id="exp-loop-3",
            max_iterations=10,
            stop_on_error=False,
            parameters={"exploit_score_threshold": 0.99, "failure_threshold": 2},
        )
    )

    results = asyncio.run(engine.run())

    assert len(results) == 2
    assert all(r.status == "failed" for r in results)


def test_experiment_batch_runner_parse_dict_and_json():
    import json

    from app.orchestration.experiment_runner import ExperimentBatchRunner, get_example_experiment_config

    config_dict = get_example_experiment_config()
    configs_from_dict = ExperimentBatchRunner.parse_config(config_dict)
    configs_from_json = ExperimentBatchRunner.parse_config(json.dumps(config_dict))

    assert len(configs_from_dict) == 2
    assert len(configs_from_json) == 2
    assert configs_from_dict[0].experiment_id == "batch_exp_1"


def test_experiment_batch_runner_aggregation_and_metadata_storage():
    from app.orchestration.experiment_runner import (
        ExperimentBatchRunner,
        IterationResult,
        get_example_experiment_config,
    )

    runner = ExperimentBatchRunner()

    async def fake_run_callable(config):
        base = 0.7 if config.experiment_id == "batch_exp_1" else 0.3
        return [
            IterationResult(iteration=1, status="completed", metrics={"global_score": base}),
            IterationResult(iteration=2, status="completed", metrics={"global_score": base + 0.1}),
        ]

    summary = asyncio.run(runner.run_batch(get_example_experiment_config(), fake_run_callable))

    assert summary["total_runs"] == 2
    assert summary["best_run"]["experiment_id"] == "batch_exp_1"
    assert summary["worst_run"]["experiment_id"] == "batch_exp_2"
    assert len(runner.history) == 2
    assert runner.history[0].metadata["tags"]


def test_evolution_engine_tracks_top_patterns_and_generates_variants():
    from app.orchestration.evolution_engine import EvolutionEngine

    engine = EvolutionEngine(max_patterns=3)
    engine.record_attack("prompt a", "baseline", 0.2)
    engine.record_attack("prompt b", "baseline", 0.9)
    engine.record_attack("prompt c", "baseline", 0.5)
    engine.record_attack("prompt d", "baseline", 0.8)

    top = engine.top_patterns(limit=3)
    assert [p.prompt for p in top] == ["prompt b", "prompt d", "prompt c"]

    variants = engine.generate_variants(limit=1)
    assert variants
    assert variants[0]["source_prompt"] == "prompt b"


def test_evolution_engine_reruns_mutations_and_records_results():
    from app.orchestration.evolution_engine import EvolutionEngine, get_example_mutation_logic

    engine = EvolutionEngine(max_patterns=10)
    engine.record_attack("initial prompt", "seed", 0.6)

    async def fake_evaluator(prompt):
        # Simple deterministic scoring for test purposes
        return {"score": 0.7 if "hypothetical" in prompt.lower() else 0.4}

    recorded = asyncio.run(engine.rerun_variants(fake_evaluator, limit=1, strategy="mutated"))

    assert recorded
    assert all(p.strategy == "mutated" for p in recorded)
    assert any("source_prompt" in p.metadata for p in recorded)

    mutation_examples = get_example_mutation_logic("test prompt")
    assert mutation_examples


def test_mock_environment_basic_actions_and_state_reset():
    from app.orchestration.environment_interface import get_example_mock_environment

    env = get_example_mock_environment()

    state = env.get_state()
    assert state["data"]["step"] == 0
    assert state["data"]["status"] == "ready"

    result_set = env.execute_action({"type": "set", "key": "mode", "value": "attack"})
    assert result_set["status"] == "ok"
    assert result_set["state"]["data"]["mode"] == "attack"

    result_inc = env.execute_action({"type": "increment", "key": "step", "value": 2})
    assert result_inc["state"]["data"]["step"] == 2

    result_delete = env.execute_action({"type": "delete", "key": "mode"})
    assert "mode" not in result_delete["state"]["data"]

    reset = env.reset_environment()
    assert reset["data"]["step"] == 0
    assert reset["data"]["status"] == "ready"


def test_mock_environment_unsupported_action_is_safe():
    from app.orchestration.environment_interface import MockEnvironment

    env = MockEnvironment(initial_state={"counter": 1})
    result = env.execute_action({"type": "unknown", "key": "counter", "value": 99})

    assert result["status"] == "unsupported_action"
    assert result["state"]["data"]["counter"] == 1


def test_iterative_loop_engine_records_replay_log_and_json_output():
    from app.orchestration.experiment_runner import ExperimentConfig, IterativeAttackLoopEngine

    sniper = DummySniper()
    target = DummyTarget()
    spotter = DummySpotter(score=0.4)

    engine = IterativeAttackLoopEngine(sniper=sniper, target=target, spotter=spotter)
    engine.configure(
        ExperimentConfig(
            experiment_id="exp-replay-1",
            max_iterations=2,
            parameters={"exploit_score_threshold": 0.95, "failure_threshold": 5},
        )
    )

    _ = asyncio.run(engine.run())

    replay_log = engine.get_attack_log()
    replay_json = engine.get_attack_log_json()

    assert len(replay_log) == 2
    assert "inputs" in replay_log[0]
    assert "outputs" in replay_log[0]
    assert "decision" in replay_log[0]
    assert "score" in replay_log[0]
    assert replay_json.startswith("[")


def test_iterative_loop_engine_replay_attack_sequence():
    from app.orchestration.experiment_runner import IterativeAttackLoopEngine

    events = [
        {"iteration": 2, "timestamp": "2026-01-01T00:00:02+00:00", "status": "completed", "score": 0.2},
        {"iteration": 1, "timestamp": "2026-01-01T00:00:01+00:00", "status": "completed", "score": 0.4},
    ]

    replayed = IterativeAttackLoopEngine.replay_attack_sequence(events)
    assert [e["iteration"] for e in replayed] == [1, 2]

    replayed_from_json = IterativeAttackLoopEngine.replay_attack_sequence(
        '[{"iteration": 1, "timestamp": "2026-01-01T00:00:01+00:00", "status": "completed", "score": 0.4}]'
    )
    assert replayed_from_json[0]["iteration"] == 1
