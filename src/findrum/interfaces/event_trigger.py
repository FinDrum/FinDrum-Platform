from abc import ABC, abstractmethod
import logging
logger = logging.getLogger("findrum")
from findrum.engine.pipeline_runner import PipelineRunner

class EventTrigger(ABC):
    """Abstract base class for event-driven pipeline triggers.

    This class defines the structure for components that trigger
    the execution of a pipeline based on some event or condition.
    """

    def __init__(self, config: dict, pipeline_path: str):
        """Initialize the event trigger with configuration and pipeline path.

        Args:
            config (dict): Configuration parameters for the trigger.
            pipeline_path (str): Path to the pipeline definition (YAML).
        """
        self.config = config
        self.pipeline_path = pipeline_path

    @abstractmethod
    def start(self):
        """Start listening or watching for events.

        This method must be implemented by subclasses to define
        how the trigger starts monitoring for relevant events.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement 'start' method.")  # pragma: no cover

    def _run_pipeline(self, overrides: dict = None):
        """Execute the pipeline with optional parameter overrides.

        This method initializes and runs the pipeline defined at `pipeline_path`.
        Optionally, it can override parameters before execution.

        Args:
            overrides (dict, optional): Parameters to override in the pipeline.
        """
        logger.info(f"📡 Executing pipeline from {self.pipeline_path}")

        runner = PipelineRunner.from_yaml(self.pipeline_path)
        if overrides:
            runner.override_params(overrides)
        runner.run()
