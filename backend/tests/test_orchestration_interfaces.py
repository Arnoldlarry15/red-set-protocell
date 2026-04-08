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

    names = manager.spawn_snipers(lambda: DummySniper(), count=3, name_prefix="sniper")
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
