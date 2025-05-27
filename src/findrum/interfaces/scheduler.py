from abc import ABC, abstractmethod
import logging
logger = logging.getLogger("findrum")
from findrum.engine.pipeline_runner import PipelineRunner

class Scheduler(ABC):
    def __init__(self, config, pipeline_path):
        self.config = config
        self.pipeline_path = pipeline_path

    @abstractmethod
    def register(self, scheduler):
        raise NotImplementedError("Subclasses must implement 'register' method.") # pragma: no cover

    def _run_pipeline(self):
        logger.info(f"🕒 Executing pipeline from {self.pipeline_path}")
        runner = PipelineRunner.from_yaml(self.pipeline_path)
        runner.run()
