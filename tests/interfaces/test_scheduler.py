import pytest
import yaml
from unittest.mock import patch, MagicMock
from findrum.interfaces.Scheduler import Scheduler

class IncompleteScheduler(Scheduler):
    pass

def test_scheduler_register_raises_typeerror():
    with pytest.raises(TypeError):
        IncompleteScheduler(config={}, pipeline_path="dummy.yaml")

class PartialScheduler(Scheduler):
    def register(self, scheduler):
        raise NotImplementedError("Subclasses must implement 'register' method.")

def test_scheduler_register_explicit_raises():
    sched = PartialScheduler(config={}, pipeline_path="dummy.yaml")
    with pytest.raises(NotImplementedError, match="Subclasses must implement 'register' method."):
        sched.register("dummy")

class DummyScheduler(Scheduler):
    def register(self, scheduler):
        pass

@patch("findrum.interfaces.Scheduler.PipelineRunner")
def test_scheduler_run_pipeline(mock_runner_class, tmp_path):
    dummy_yaml = tmp_path / "dummy.yaml"
    dummy_yaml.write_text(yaml.dump({"pipeline": []}))

    mock_runner = MagicMock()
    mock_runner_class.from_yaml.return_value = mock_runner

    scheduler = DummyScheduler(config={}, pipeline_path=str(dummy_yaml))
    scheduler._run_pipeline()

    mock_runner_class.from_yaml.assert_called_once_with(str(dummy_yaml))
    mock_runner.run.assert_called_once()