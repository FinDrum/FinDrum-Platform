import pytest
import yaml
from findrum.registry import registry

class ConstOperator:
    def __init__(self, value):
        self.value = value

    def run(self, input_data):
        print(self.value)
        return self.value

class AddOperator:
    def __init__(self):
        pass

    def run(self, input_data):
        print(input_data)
        return sum(input_data)

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
            {"id": "step1", "operator": "Const", "params": {"value": 2}},
            {"id": "step2", "operator": "Const", "params": {"value": 3}},
            {"id": "final", "operator": "Adder", "depends_on": ["step1", "step2"]}
        ]
    }
    path = tmp_path / "pipeline.yaml"
    with open(path, "w") as f:
        yaml.dump(data, f)
    return str(path)

@pytest.fixture(autouse=True)
def register_dummy_operators():
    registry.OPERATOR_REGISTRY["Const"] = ConstOperator
    registry.OPERATOR_REGISTRY["Adder"] = AddOperator
    yield
    registry.OPERATOR_REGISTRY.clear()