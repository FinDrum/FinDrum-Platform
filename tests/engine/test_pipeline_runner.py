import pytest
import tempfile
from unittest.mock import MagicMock, patch
from findrum.engine.pipeline_runner import PipelineRunner

def test_pipeline_runner_from_yaml_and_run(dummy_pipeline_yaml):
    runner = PipelineRunner.from_yaml(dummy_pipeline_yaml)
    results = runner.override_params({"step1": {"value": 10}}).run()

    assert "step1" in results
    assert "step2" in results
    assert results["step1"] ==  10
    assert results["step2"] ==  3
    assert results["final"] == 13

def test_step_missing_operator_and_datasource():
    pipeline_def = {"pipeline":[{"id": "step1"}]}
    
    runner = PipelineRunner(pipeline_def)
    with pytest.raises(ValueError, match="must have either 'operator' or 'datasource'"):
        runner.run()

def test_datasource_with_depends_on_should_fail():
    pipeline_def = {"pipeline":[{"id": "step1", "datasource": "dummy", "depends_on": "something"}]}
    runner = PipelineRunner(pipeline_def)
    with pytest.raises(ValueError, match="Datasource step 'step1' cannot depend on another step."):
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
    print(results)

    assert runner.results["step1"] == "processed:event_data"
    assert runner.results["step2"] == "processed:None"

def test_step_without_operator_or_datasource_raises():
    runner = PipelineRunner({"pipeline": [{"id": "s1"}]})
    with pytest.raises(ValueError, match="must have either 'operator' or 'datasource'"):
        runner.run()
