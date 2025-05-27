import pytest
import logging
import yaml
import tempfile
import os
from unittest.mock import patch, MagicMock

from findrum.registry.Registry import EVENT_TRIGGER_REGISTRY, SCHEDULER_REGISTRY
from findrum.engine.Platform import Platform

class DummyTrigger:
    def __init__(self, config, pipeline_path): pass
    def start(self): pass

class DummyScheduler:
    def __init__(self, config, pipeline_path): pass
    def register(self, scheduler): pass

@pytest.fixture
def temp_pipeline_file():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
        yield f.name
    os.remove(f.name)

def test_register_pipeline_event(temp_pipeline_file):
    EVENT_TRIGGER_REGISTRY["dummy"] = DummyTrigger

    with open(temp_pipeline_file, "w") as f:
        yaml.dump({"event": {"type": "dummy"}}, f)

    platform = Platform(extensions_config=temp_pipeline_file)
    with patch.object(DummyTrigger, 'start') as mock_start:
        platform.register_pipeline(temp_pipeline_file)
        mock_start.assert_called_once()

def test_register_pipeline_scheduler(temp_pipeline_file):
    SCHEDULER_REGISTRY["dummy"] = DummyScheduler

    with open(temp_pipeline_file, "w") as f:
        yaml.dump({"scheduler": {"type": "dummy"}}, f)

    platform = Platform(extensions_config=temp_pipeline_file)
    with patch.object(DummyScheduler, 'register') as mock_register:
        platform.register_pipeline(temp_pipeline_file)
        mock_register.assert_called_once()

def test_register_pipeline_run_directly(temp_pipeline_file):
    pipeline_data = {"pipeline": [{"id": "step", "operator": "DummyOperator", "params": {}}]}
    with open(temp_pipeline_file, "w") as f:
        yaml.dump(pipeline_data, f)

    platform = Platform(extensions_config=temp_pipeline_file)
    with patch("findrum.engine.PipelineRunner.PipelineRunner.run") as mock_run:
        platform.register_pipeline(temp_pipeline_file)
        mock_run.assert_called_once()

def test_register_pipeline_missing_file():
    with patch("findrum.engine.Platform.load_extensions", return_value=None):
        platform = Platform(extensions_config="nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            platform.register_pipeline("nonexistent_pipeline.yaml")

def test_register_pipeline_invalid_trigger(temp_pipeline_file):
    with open(temp_pipeline_file, "w") as f:
        yaml.dump({"event": {"type": "missing"}}, f)

    platform = Platform(extensions_config=temp_pipeline_file)
    with pytest.raises(ValueError, match="Event trigger 'missing' not registered"):
        platform.register_pipeline(temp_pipeline_file)

def test_register_pipeline_invalid_scheduler(temp_pipeline_file):
    with open(temp_pipeline_file, "w") as f:
        yaml.dump({"scheduler": {"type": "missing"}}, f)

    platform = Platform(extensions_config=temp_pipeline_file)
    with pytest.raises(ValueError, match="Scheduler 'missing' not registered"):
        platform.register_pipeline(temp_pipeline_file)

@patch("findrum.engine.Platform.load_extensions", return_value=None)
def test_platform_start(_, caplog):
    platform = Platform(extensions_config="dummy.yaml")
    platform.scheduler = MagicMock()

    with caplog.at_level(logging.INFO):
        platform.start()

    platform.scheduler.start.assert_called_once()
    assert "🔁 Starting..." in caplog.text


