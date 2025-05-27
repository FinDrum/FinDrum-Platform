import pytest
from findrum.registry import registry

class DummyOperator:
    pass

class DummyScheduler:
    pass

class DummyTrigger:
    pass

class DummyDataSource:
    pass

def test_operator_registry_success():
    registry.OPERATOR_REGISTRY["dummy"] = DummyOperator
    cls = registry.get_operator("dummy")
    assert cls is DummyOperator

def test_operator_registry_failure():
    registry.OPERATOR_REGISTRY.clear()
    with pytest.raises(ValueError, match="Operator 'nonexistent' not found in registry."):
        registry.get_operator("nonexistent")

def test_scheduler_registry_success():
    registry.SCHEDULER_REGISTRY["dummy"] = DummyScheduler
    cls = registry.get_scheduler("dummy")
    assert cls is DummyScheduler

def test_scheduler_registry_failure():
    registry.SCHEDULER_REGISTRY.clear()
    with pytest.raises(ValueError, match="Trigger 'nonexistent' not found in registry."):
        registry.get_scheduler("nonexistent")

def test_trigger_registry_success():
    registry.EVENT_TRIGGER_REGISTRY["dummy"] = DummyTrigger
    cls = registry.get_trigger("dummy")
    assert cls is DummyTrigger

def test_trigger_registry_failure():
    registry.EVENT_TRIGGER_REGISTRY.clear()
    with pytest.raises(ValueError, match="Trigger 'nonexistent' not found in registry."):
        registry.get_trigger("nonexistent")
        
def test_datasource_registry_success():
    registry.DATASOURCE_REGISTRY["dummy"] = DummyDataSource
    cls = registry.get_datasource("dummy")
    assert cls is DummyDataSource

def test_datasource_registry_failure():
    registry.DATASOURCE_REGISTRY.clear()
    with pytest.raises(ValueError, match="Datasource 'nonexistent' not found in registry."):
        registry.get_datasource("nonexistent")