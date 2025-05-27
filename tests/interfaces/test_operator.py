import pytest
from findrum.interfaces.operator import Operator

class IncompleteOperator(Operator):
    def run(self, input_data):
        raise NotImplementedError("run must be implemented")

def test_operator_run_not_implemented():
    op = IncompleteOperator()
    with pytest.raises(NotImplementedError):
        op.run("test")

class DummyOperator(Operator):
    def run(self, input_data):
        return f"processed: {input_data}"

def test_operator_run_implemented():
    op = DummyOperator()
    result = op.run("data")
    assert result == "processed: data"