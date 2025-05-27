import pytest
import yaml
from findrum.registry import registry

class DummyOperator:
    def __init__(self, **params):
        self.params = params

    def run(self, input_data):
        return {"params": self.params, "input": input_data}

class DummyScheduler:
    def register(self, scheduler):
        pass

class DummyTrigger:
    def start(self):
        pass
    
class DummyDataSource:
    def fetch(self):
        pass

@pytest.fixture
def dummy_pipeline_yaml(tmp_path):
    data = {
        "pipeline": [
            {"id": "step1", "operator": "DummyOperator", "params": {"x": 1}},
            {"id": "step2", "operator": "DummyOperator", "depends_on": "step1", "params": {"y": 2}},
        ]
    }
    path = tmp_path / "pipeline.yaml"
    with open(path, "w") as f:
        yaml.dump(data, f)
    return str(path)

@pytest.fixture(autouse=True)
def register_dummy_operator():
    registry.OPERATOR_REGISTRY["DummyOperator"] = DummyOperator
    yield
    registry.OPERATOR_REGISTRY.clear()