import pytest
import yaml
import tempfile
import os
import logging
from unittest.mock import patch, MagicMock

from findrum.registry.registry import EVENT_TRIGGER_REGISTRY, SCHEDULER_REGISTRY
from findrum.engine.platform import Platform


class DummyScheduler:
    def __init__(self, config, pipeline_path): pass
    def register(self, scheduler): pass


class DummyTrigger:
    def __init__(self, **kwargs):
        self.emit = None
        self.started = False

    def start(self):
        self.started = True


@pytest.fixture
def temp_pipeline_file():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
        yield f.name
    os.remove(f.name)


@pytest.fixture
def temp_event_pipeline_file():
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
        yield f.name
    os.remove(f.name)


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
    with patch("findrum.engine.pipeline_runner.PipelineRunner.run") as mock_run:
        platform.register_pipeline(temp_pipeline_file)
        mock_run.assert_called_once()


def test_register_pipeline_missing_file():
    with patch("findrum.engine.platform.load_extensions", return_value=None):
        platform = Platform(extensions_config="nonexistent.yaml")
        with pytest.raises(FileNotFoundError):
            platform.register_pipeline("nonexistent_pipeline.yaml")


def test_register_pipeline_invalid_scheduler(temp_pipeline_file):
    with open(temp_pipeline_file, "w") as f:
        yaml.dump({"scheduler": {"type": "missing"}}, f)

    platform = Platform(extensions_config=temp_pipeline_file)
    with pytest.raises(ValueError, match="Scheduler 'missing' not registered"):
        platform.register_pipeline(temp_pipeline_file)


@patch("findrum.engine.platform.load_extensions", return_value=None)
def test_platform_start(_, caplog):
    platform = Platform(extensions_config="dummy.yaml")
    platform.scheduler = MagicMock()

    with caplog.at_level(logging.INFO):
        platform.start()

    platform.scheduler.start.assert_called_once()
    assert "🔁 Starting scheduler..." in caplog.text


@patch("findrum.engine.platform.load_extensions", return_value=None)
def test_platform_does_not_block(_, caplog):
    platform = Platform("config.yaml")
    with caplog.at_level(logging.INFO):
        platform.start()
    assert "✅ No active schedulers or triggers. Shutting down." in caplog.text


@patch("findrum.engine.platform.load_extensions", return_value=None)
def test_platform_starts_event_triggers(_, caplog):
    platform = Platform("config.yaml")
    dummy_trigger = DummyTrigger()
    platform.event_instances = {"dummy": dummy_trigger}

    with patch("time.sleep", side_effect=KeyboardInterrupt), caplog.at_level(logging.INFO):
        platform.start()

    assert dummy_trigger.started
    assert "🟢 Event triggers detected. Keeping process alive..." in caplog.text
    assert "⛔ Interrupt received. Exiting." in caplog.text


@patch("findrum.engine.platform.load_extensions", return_value=None)
def test_get_event_key_is_deterministic(_):
    platform = Platform("dummy.yaml")
    event_def = {"type": "minio", "config": {"bucket": "mybucket"}}
    key1 = platform._get_event_key(event_def)
    key2 = platform._get_event_key(event_def)
    assert key1 == key2
    assert isinstance(key1, str)


def test_register_event_pipeline_creates_and_assigns_trigger(temp_event_pipeline_file):
    EVENT_TRIGGER_REGISTRY["dummy"] = DummyTrigger

    with open(temp_event_pipeline_file, "w") as f:
        yaml.dump({"event": {"type": "dummy"}}, f)

    platform = Platform(extensions_config=temp_event_pipeline_file)
    with patch("findrum.engine.pipeline_runner.PipelineRunner.run"):
        platform.register_pipeline(temp_event_pipeline_file)

    assert len(platform.event_instances) == 1
    assert next(iter(platform.event_instances.values())).emit is not None


@patch("findrum.engine.platform.load_extensions", return_value=None)
def test_setup_logging_verbose_mode(_):
    platform = Platform("dummy.yaml", verbose=True)
    logger = logging.getLogger("findrum")
    assert logger.level == logging.INFO