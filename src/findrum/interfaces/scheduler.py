from abc import ABC, abstractmethod
import logging
logger = logging.getLogger("findrum")
from findrum.engine.pipeline_runner import PipelineRunner


class Scheduler(ABC):
    """Abstract base class for pipeline schedulers.

    This class provides a template for schedulers that register
    pipelines to be executed at scheduled intervals or times.
    """

    def __init__(self, config, pipeline_path):
        """Initialize the scheduler with configuration and pipeline path.

        Args:
            config (dict): Configuration settings for the scheduler.
            pipeline_path (str): Path to the pipeline definition (YAML).
        """
        self.config = config
        self.pipeline_path = pipeline_path

    @abstractmethod
    def register(self, scheduler):
        """Register the pipeline to a given scheduler system.

        Subclasses must implement this method to define how the pipeline
        should be scheduled (e.g., using cron, APScheduler, etc.).

        Args:
            scheduler: The scheduler system or object to register the pipeline with.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError("Subclasses must implement 'register' method.")  # pragma: no cover

    def _run_pipeline(self):
        """Execute the pipeline associated with this scheduler.

        This method initializes and runs the pipeline defined in `pipeline_path`.
        """
        logger.info(f"🕒 Executing pipeline from {self.pipeline_path}")
        runner = PipelineRunner.from_yaml(self.pipeline_path)
        runner.run()
