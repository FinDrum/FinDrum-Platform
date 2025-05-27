import pytest
from unittest.mock import patch, MagicMock
import yaml
from findrum.interfaces.event_trigger import EventTrigger

class IncompleteEventTrigger(EventTrigger):
    pass

def test_event_trigger_start_raises_not_implemented():
    with pytest.raises(TypeError):
        IncompleteEventTrigger(config={}, pipeline_path="dummy.yaml")

class PartialTrigger(EventTrigger):
    def start(self):
        raise NotImplementedError("Subclasses must implement 'start' method.")

def test_event_trigger_start_explicit_raises():
    trig = PartialTrigger(config={}, pipeline_path="dummy.yaml")
    with pytest.raises(NotImplementedError, match="Subclasses must implement 'start' method."):
        trig.start()

class DummyTrigger(EventTrigger):
    def start(self):
        pass

@patch("findrum.interfaces.event_trigger.PipelineRunner")
def test_event_trigger_run_pipeline(mock_runner_class, tmp_path):
    dummy_yaml = tmp_path / "dummy.yaml"
    dummy_yaml.write_text(yaml.dump({"pipeline": []}))

    mock_runner = MagicMock()
    mock_runner_class.from_yaml.return_value = mock_runner

    trigger = DummyTrigger(config={}, pipeline_path=str(dummy_yaml))
    trigger._run_pipeline(overrides={"foo": "bar"})

    mock_runner_class.from_yaml.assert_called_once_with(str(dummy_yaml))
    mock_runner.override_params.assert_called_once_with({"foo": "bar"})
    mock_runner.run.assert_called_once()