from abc import ABC, abstractmethod

class DataSource(ABC):
    """Abstract base class for data sources.

    This interface defines the contract for any data source class
    that is expected to implement a `fetch` method for retrieving data.

    Subclasses should override the `fetch` method to provide their
    specific logic for data retrieval.
    """

    def __init__(self, **kwargs):
        """Initialize the data source.

        Args:
            **kwargs: Arbitrary keyword arguments that may be needed
                      for specific implementations of the data source.
        """
        pass

    @abstractmethod
    def fetch(self):
        """Retrieve data from the source.

        This method must be implemented by all subclasses.

        Raises:
            NotImplementedError: If the subclass does not override this method.
        """
        raise NotImplementedError("Subclasses must implement 'fetch' method.")  # pragma: no cover
