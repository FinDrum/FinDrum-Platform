from abc import ABC, abstractmethod

class DataSource(ABC):
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def fetch(self):
        raise NotImplementedError("Subclasses must implement 'fetch' method.") # pragma: no conver
