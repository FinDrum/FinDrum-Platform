from abc import ABC, abstractmethod
import logging
logger = logging.getLogger("findrum")
from findrum.engine.pipeline_runner import PipelineRunner

class EventTrigger(ABC):
    def __init__(self, config: dict, pipeline_path: str):
        self.config = config
        self.pipeline_path = pipeline_path

    @abstractmethod
    def start(self):
        raise NotImplementedError("Subclasses must implement 'start' method.") # pragma: no cover

    def _run_pipeline(self, overrides: dict = None):
        logger.info(f"📡 Executing pipeline from {self.pipeline_path}")

        runner = PipelineRunner.from_yaml(self.pipeline_path)
        if overrides:
            runner.override_params(overrides)
        runner.run()
