from abc import ABC, abstractmethod

class Operator(ABC):
    """Abstract base class for data processing operators.

    This interface defines a common structure for all operators
    that process input data and potentially produce transformed output.
    """

    def __init__(self, **params):
        """Initialize the operator with optional parameters.

        Args:
            **params: Arbitrary keyword arguments for configuring the operator.
        """
        self.params = params

    @abstractmethod
    def run(self, input_data):
        """Execute the operator's logic on the given input data.

        This method must be implemented by subclasses to define how the operator
        processes the input data.

        Args:
            input_data: The data to be processed by the operator. Type depends on the specific implementation.

        Returns:
            Any: The result of the processing operation. The return type should be defined by the concrete implementation.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement 'run' method.")  # pragma: no cover