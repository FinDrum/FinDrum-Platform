import sys
import types
import tempfile
import yaml
from findrum.loader.load_extensions import load_extensions
from findrum.registry import registry

dummy_module = types.ModuleType("dummy_module")

class DummyOperator:
    pass
class DummyScheduler:
    pass
class DummyTrigger:
    pass

dummy_module.DummyOperator = DummyOperator

dummy_module.DummyScheduler = DummyScheduler

dummy_module.DummyTrigger = DummyTrigger

sys.modules["dummy_module"] = dummy_module

def test_load_extensions_success():
    config = {
        "operators": ["dummy_module.DummyOperator"],
        "schedulers": ["dummy_module.DummyScheduler"],
        "triggers": ["dummy_module.DummyTrigger"]
    }

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".yaml", delete=False) as f:
        yaml.dump(config, f)
        temp_path = f.name

    registry.OPERATOR_REGISTRY.clear()
    registry.SCHEDULER_REGISTRY.clear()
    registry.EVENT_TRIGGER_REGISTRY.clear()

    load_extensions(temp_path)

    assert registry.OPERATOR_REGISTRY["DummyOperator"] is DummyOperator
    assert registry.SCHEDULER_REGISTRY["DummyScheduler"] is DummyScheduler
    assert registry.EVENT_TRIGGER_REGISTRY["DummyTrigger"] is DummyTrigger
