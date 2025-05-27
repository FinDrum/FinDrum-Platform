from abc import ABC, abstractmethod

class Operator(ABC):
    def __init__(self, **params):
        self.params = params

    @abstractmethod
    def run(self, input_data):
        pass