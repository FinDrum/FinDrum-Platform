import pytest
import tempfile
from unittest.mock import MagicMock, patch
from findrum.engine.pipeline_runner import PipelineRunner


def test_pipeline_runner_from_yaml_and_run(dummy_pipeline_yaml):
    runner = PipelineRunner.from_yaml(dummy_pipeline_yaml)
    results = runner.run()

    assert "step1" in results
    assert "step2" in results
    assert results["step1"] == 2
    assert results["step2"] == 3
    assert results["final"] == 5


def test_step_missing_operator_and_datasource():
    pipeline_def = {"pipeline": [{"id": "step1"}]}
    runner = PipelineRunner(pipeline_def)
    with pytest.raises(ValueError, match="must have either 'operator' or 'datasource'"):
        runner.run()


def test_from_yaml_invalid_structure():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("- not a dict")
        path = f.name

    with pytest.raises(ValueError, match="must contain a valid dictionary with pipeline definition."):
        PipelineRunner.from_yaml(path)


def test_event_trigger_emits_and_runs_steps(monkeypatch):
    class DummyTrigger:
        def __init__(self, **kwargs):
            self.emit = None

        def start(self):
            if self.emit:
                self.emit("event_data")

    class DummyOperator:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self, input_data):
            return f"processed:{input_data}"

    monkeypatch.setattr("findrum.engine.pipeline_runner.get_trigger", lambda name: DummyTrigger)
    monkeypatch.setattr("findrum.engine.pipeline_runner.get_operator", lambda name: DummyOperator)
    monkeypatch.setattr("findrum.engine.pipeline_runner.get_datasource", lambda name: DummyOperator)

    pipeline_def = {
        "event": {"type": "dummy"},
        "pipeline": [
            {"id": "step1", "operator": "dummy", "depends_on": "dummy"},
            {"id": "step2", "operator": "dummy"},
        ]
    }

    runner = PipelineRunner(pipeline_def)
    results = runner.run()
    assert runner.results["step1"] == "processed:event_data"
    assert runner.results["step2"] == "processed:None"


def test_step_without_operator_or_datasource_raises():
    runner = PipelineRunner({"pipeline": [{"id": "s1"}]})
    with pytest.raises(ValueError, match="must have either 'operator' or 'datasource'"):
        runner.run()


def test_run_with_data(monkeypatch):
    class DummyOperator:
        def __init__(self, **kwargs): pass
        def run(self, input_data): return input_data + 1

    monkeypatch.setattr("findrum.engine.pipeline_runner.get_operator", lambda name: DummyOperator)

    pipeline_def = {
        "pipeline": [
            {"id": "step1", "operator": "dummy", "params": {}}
        ]
    }

    runner = PipelineRunner(pipeline_def)
    result = runner.run_with_data(10)
    assert result["step1"] == 11


def test_resolve_input_with_multiple_dependencies(monkeypatch):
    class DummyOperator:
        def __init__(self, **kwargs): pass
        def run(self, input_data): return sum(input_data)

    monkeypatch.setattr("findrum.engine.pipeline_runner.get_operator", lambda name: DummyOperator)

    pipeline_def = {
        "pipeline": [
            {"id": "a", "operator": "dummy", "params": {}},
            {"id": "b", "operator": "dummy", "params": {}},
            {"id": "c", "operator": "dummy", "depends_on": ["a", "b"]}
        ]
    }

    runner = PipelineRunner(pipeline_def)
    runner.results = {"a": 1, "b": 2}
    runner._run_step(runner.pipeline_steps[2])
    assert runner.results["c"] == 3


def test_resolve_input_with_no_dependencies(monkeypatch):
    class DummyOperator:
        def __init__(self, **kwargs): pass
        def run(self, input_data): return input_data if input_data else "no input"

    monkeypatch.setattr("findrum.engine.pipeline_runner.get_operator", lambda name: DummyOperator)

    pipeline_def = {
        "pipeline": [
            {"id": "alone", "operator": "dummy", "params": {}}
        ]
    }

    runner = PipelineRunner(pipeline_def)
    runner.run()
    assert runner.results["alone"] == "no input"
