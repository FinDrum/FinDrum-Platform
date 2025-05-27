import pytest
from findrum.registry import Registry

class DummyOperator:
    pass

class DummyScheduler:
    pass

class DummyTrigger:
    pass

class DummyDataSource:
    pass

def test_operator_registry_success():
    Registry.OPERATOR_REGISTRY["dummy"] = DummyOperator
    cls = Registry.get_operator("dummy")
    assert cls is DummyOperator

def test_operator_registry_failure():
    Registry.OPERATOR_REGISTRY.clear()
    with pytest.raises(ValueError, match="Operator 'nonexistent' not found in registry."):
        Registry.get_operator("nonexistent")

def test_scheduler_registry_success():
    Registry.SCHEDULER_REGISTRY["dummy"] = DummyScheduler
    cls = Registry.get_scheduler("dummy")
    assert cls is DummyScheduler

def test_scheduler_registry_failure():
    Registry.SCHEDULER_REGISTRY.clear()
    with pytest.raises(ValueError, match="Trigger 'nonexistent' not found in registry."):
        Registry.get_scheduler("nonexistent")

def test_trigger_registry_success():
    Registry.EVENT_TRIGGER_REGISTRY["dummy"] = DummyTrigger
    cls = Registry.get_trigger("dummy")
    assert cls is DummyTrigger

def test_trigger_registry_failure():
    Registry.EVENT_TRIGGER_REGISTRY.clear()
    with pytest.raises(ValueError, match="Trigger 'nonexistent' not found in registry."):
        Registry.get_trigger("nonexistent")
        
def test_datasource_registry_success():
    Registry.DATASOURCE_REGISTRY["dummy"] = DummyDataSource
    cls = Registry.get_datasource("dummy")
    assert cls is DummyDataSource

def test_datasource_registry_failure():
    Registry.DATASOURCE_REGISTRY.clear()
    with pytest.raises(ValueError, match="Datasource 'nonexistent' not found in registry."):
        Registry.get_datasource("nonexistent")